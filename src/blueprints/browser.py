from src.browser_actions import BrowserActions
import uuid
import os
import base64
from flask import Blueprint, jsonify, request, Response
from src.browser_manager import browser_manager
from src.models import Page
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

bp = Blueprint('browser', __name__)

@bp.route('/open', methods=['POST'])
def open_session():
    data = request.get_json() or {}
    timeout = data.get('timeout')  # Defaults to None if not present
    session_id = browser_manager.create_session(timeout=timeout)
    return jsonify({'session_id': session_id}), 201

@bp.route('/<string:session_id>/close', methods=['POST'])
def close_session(session_id):
    browser_manager.close_session(session_id)
    return '', 204

@bp.route('/<string:session_id>/navigate', methods=['POST'])
def navigate_to_page(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404
    actions = BrowserActions(driver)
    data = request.get_json() or {}
    page_id = data.get('page_id')
    if not page_id:
        return jsonify({'error': 'Missing page_id'}), 400
    success, error = actions.navigate_to_page(page_id)
    if not success:
        return jsonify({'error': error}), 400
    return '', 204

def _find_selector(page, alias):
    selectors = page.identifying_selectors + (page.interactive_selectors or [])
    for selector in selectors:
        if selector.get('alias') == alias:
            return selector.get('xpath')
    return None

@bp.route('/<string:session_id>/click', methods=['POST'])
def click_element(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404
    actions = BrowserActions(driver)
    data = request.get_json() or {}
    page_id = data.get('page_id')
    alias = data.get('selector_alias')
    if not page_id or not alias:
        return jsonify({'error': 'Missing page_id or selector_alias'}), 400
    success, error = actions.click_element(page_id, alias)
    if not success:
        return jsonify({'error': error}), 404
    return '', 204

@bp.route('/<string:session_id>/set-value', methods=['POST'])
def set_element_value(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404
    actions = BrowserActions(driver)
    data = request.get_json() or {}
    page_id = data.get('page_id')
    alias = data.get('selector_alias')
    value = data.get('value')
    if not page_id or not alias or value is None:
        return jsonify({'error': 'Missing page_id, selector_alias, or value'}), 400
    success, error = actions.set_element_value(page_id, alias, value)
    if not success:
        return jsonify({'error': error}), 404
    return '', 204

@bp.route('/<string:session_id>/get-value', methods=['POST'])
def get_element_value(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404
    actions = BrowserActions(driver)
    data = request.get_json() or {}
    page_id = data.get('page_id')
    alias = data.get('selector_alias')
    if not page_id or not alias:
        return jsonify({'error': 'Missing page_id or selector_alias'}), 400
    value, error = actions.get_element_value(page_id, alias)
    if error:
        return jsonify({'error': error}), 404
    return jsonify({'value': value})

@bp.route('/<string:session_id>/wait-for-page', methods=['POST'])
def wait_for_page(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404
    actions = BrowserActions(driver)
    data = request.get_json() or {}
    page_id = data.get('page_id')
    timeout = data.get('timeout', 10)
    if not page_id:
        return jsonify({'error': 'Missing page_id'}), 400
    success, error = actions.wait_for_page(page_id, timeout)
    if not success:
        return jsonify({'error': error}), 408
    return '', 204

@bp.route('/<string:session_id>/checkSelectors', methods=['GET'])
def check_selectors(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404

    # Gather selectors grouped by application and page
    applications_pages = {}
    pages = Page.query.all()
    for page in pages:
        app_id = str(page.application_id)
        if app_id not in applications_pages:
            applications_pages[app_id] = {}
        applications_pages[app_id][str(page.id)] = page.identifying_selectors or []

    # Generate JS and execute in browser
    js_code = BrowserActions._generate_selector_check_js(applications_pages)
    selector_results = driver.execute_script(js_code)

    return jsonify(selector_results)

@bp.route('/<string:session_id>/get-current-page', methods=['GET'])
def get_current_page(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404

    pages = [p for p in Page.query.all()]
    applications_pages = {}
    for page in pages:
        app_id = str(page.application_id)
        if app_id not in applications_pages:
            applications_pages[app_id] = {}
        applications_pages[app_id][str(page.id)] = page.identifying_selectors or []

    actions = BrowserActions(driver)
    matched_page = actions.get_current_page(
        [p.to_dict() for p in pages], applications_pages)
    if matched_page:
        return jsonify(matched_page)
    return jsonify({'error': 'No matching page found'}), 404

@bp.route('/<string:session_id>/screenshot', methods=['GET'])
def take_screenshot(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404
    actions = BrowserActions(driver)
    screenshot_data, error = actions.take_screenshot()
    if error:
        return jsonify({'error': error}), 500
    return Response(screenshot_data, mimetype='image/png')

@bp.route('/<string:session_id>/dom', methods=['GET'])
def get_dom(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404
    actions = BrowserActions(driver)
    dom, error = actions.get_dom()
    if error:
        return jsonify({'error': error}), 500
    return Response(dom, mimetype='text/html')