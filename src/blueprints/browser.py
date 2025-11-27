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

    # Gather all unique xpaths and build mapping for output
    pages = Page.query.all()
    selector_set = set()
    # Structure: {app_id: {page_id: {alias: {wanted, actual}}}}
    output = {}
    selector_map = {}  # xpath -> (app_id, page_id, alias, wanted_visible)
    for page in pages:
        app_id = str(page.application_id)
        page_id = str(page.id)
        if app_id not in output:
            output[app_id] = {}
        if page_id not in output[app_id]:
            output[app_id][page_id] = {}
        for selector in page.identifying_selectors or []:
            alias = selector.get('alias')
            xpath = selector.get('xpath')
            wanted_visible = selector.get('visible', None)
            if xpath:
                selector_set.add(xpath)
                # For mapping back after JS execution
                selector_map[(app_id, page_id, alias)] = (xpath, wanted_visible)
                output[app_id][page_id][alias] = {
                    "wanted": {"visible": wanted_visible},
                    "actual": None  # to be filled after JS
                }

    selectors = list(selector_set)
    js_code = BrowserActions._generate_selector_check_js(selectors)
    try:
        selector_results = driver.execute_script(js_code)
        print(selector_results)
    except Exception:
        print("\n--- JS CODE DUMP ---\n" + js_code + "\n--- END JS CODE DUMP ---\n")
        raise

    # Fill in actual results
    for (app_id, page_id, alias), (xpath, wanted_visible) in selector_map.items():
        actual = selector_results.get(xpath, {})
        output[app_id][page_id][alias]["actual"] = actual

    return jsonify(output)

@bp.route('/<string:session_id>/get-current-page', methods=['GET'])
def get_current_page(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404

    from src.browser_actions import BrowserActions
    actions = BrowserActions(driver)
    # Get all pages as dicts
    
    pages = [page.to_dict() for page in Page.query.all()]
    matched_pages = actions.get_current_pages(pages)
    if matched_pages:
        return jsonify(matched_pages)
    
    return jsonify([]), 200

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


# New endpoint: cleaned DOM (removes <script> and <img> tags)
@bp.route('/<string:session_id>/cleaned-dom', methods=['GET'])
def get_cleaned_dom(session_id):
    driver = browser_manager.get_session(session_id)
    if not driver:
        return jsonify({'error': 'Session not found'}), 404
    actions = BrowserActions(driver)
    dom, error = actions.get_dom()
    if error:
        return jsonify({'error': error}), 500
    # Clean DOM: remove <script> and <img> tags
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(dom, 'html.parser')
        # Remove all <script> tags
        for script in soup.find_all('script'):
            script.decompose()
        # Remove all <img> tags
        for img in soup.find_all('img'):
            img.decompose()
        # Remove all <style> tags
        for style in soup.find_all('style'):
            style.decompose()
        # Remove all <link> tags
        for link in soup.find_all('link'):
            link.decompose()
        # Remove content of all <svg> tags (keep empty svg)
        for svg in soup.find_all('svg'):
            svg.clear()
        # Format output (pretty-print)
        cleaned_dom = soup.prettify()
    except Exception as e:
        return jsonify({'error': f'Failed to clean DOM: {e}'}), 500
    return Response(cleaned_dom, mimetype='text/html')

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