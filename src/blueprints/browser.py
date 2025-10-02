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

    data = request.get_json() or {}
    page_id = data.get('page_id')
    if not page_id:
        return jsonify({'error': 'Missing page_id'}), 400

    page = Page.query.get_or_404(page_id)
    if not page.can_be_navigated_to or not page.url:
        return jsonify({'error': 'Page cannot be navigated to'}), 400

    driver.get(page.url)
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

    data = request.get_json() or {}
    page_id = data.get('page_id')
    alias = data.get('selector_alias')
    if not page_id or not alias:
        return jsonify({'error': 'Missing page_id or selector_alias'}), 400

    page = Page.query.get_or_404(page_id)
    xpath = _find_selector(page, alias)
    if not xpath:
        return jsonify({'error': 'Selector alias not found on page'}), 404

    try:
        element = driver.find_element(By.XPATH, xpath)
        element.click()
    except NoSuchElementException:
        return jsonify({'error': 'Element not found'}), 404

    return '', 204

@bp.route('/<string:session_id>/set-value', methods=['POST'])
def set_element_value(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404

    data = request.get_json() or {}
    page_id = data.get('page_id')
    alias = data.get('selector_alias')
    value = data.get('value')
    if not page_id or not alias or value is None:
        return jsonify({'error': 'Missing page_id, selector_alias, or value'}), 400

    page = Page.query.get_or_404(page_id)
    xpath = _find_selector(page, alias)
    if not xpath:
        return jsonify({'error': 'Selector alias not found on page'}), 404

    try:
        element = driver.find_element(By.XPATH, xpath)
        element.clear()
        element.send_keys(value)
    except NoSuchElementException:
        return jsonify({'error': 'Element not found'}), 404

    return '', 204

@bp.route('/<string:session_id>/get-value', methods=['POST'])
def get_element_value(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404

    data = request.get_json() or {}
    page_id = data.get('page_id')
    alias = data.get('selector_alias')
    if not page_id or not alias:
        return jsonify({'error': 'Missing page_id or selector_alias'}), 400

    page = Page.query.get_or_404(page_id)
    xpath = _find_selector(page, alias)
    if not xpath:
        return jsonify({'error': 'Selector alias not found on page'}), 404

    try:
        element = driver.find_element(By.XPATH, xpath)
        value = element.get_attribute('value') or element.text
    except NoSuchElementException:
        return jsonify({'error': 'Element not found'}), 404

    return jsonify({'value': value})

@bp.route('/<string:session_id>/wait-for-page', methods=['POST'])
def wait_for_page(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404

    data = request.get_json() or {}
    page_id = data.get('page_id')
    timeout = data.get('timeout', 10)
    if not page_id:
        return jsonify({'error': 'Missing page_id'}), 400

    page = Page.query.get_or_404(page_id)

    try:
        wait = WebDriverWait(driver, timeout)
        for selector in page.identifying_selectors:
            wait.until(EC.presence_of_element_located((By.XPATH, selector['xpath'])))
    except TimeoutException:
        return jsonify({'error': 'Timeout waiting for page to load'}), 408

    return '', 204

@bp.route('/<string:session_id>/get-current-page', methods=['GET'])
def get_current_page(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404

    pages = Page.query.all()
    for page in pages:
        is_current_page = True
        for selector in page.identifying_selectors:
            try:
                driver.find_element(By.XPATH, selector['xpath'])
            except NoSuchElementException:
                is_current_page = False
                break
        if is_current_page:
            return jsonify(page.to_dict())

    return jsonify({'error': 'No matching page found'}), 404

@bp.route('/<string:session_id>/screenshot', methods=['GET'])
def take_screenshot(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404

    try:
        screenshot_data = driver.get_screenshot_as_png()
    except Exception as e:
        return jsonify({'error': f'Failed to take screenshot: {str(e)}'}), 500

    return Response(screenshot_data, mimetype='image/png')

@bp.route('/<string:session_id>/dom', methods=['GET'])
def get_dom(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404

    try:
        dom = driver.page_source
    except Exception as e:
        return jsonify({'error': f'Failed to get DOM: {str(e)}'}), 500

    return Response(dom, mimetype='text/html')