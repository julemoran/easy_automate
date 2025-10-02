from flask import Blueprint, jsonify, request, Response
from src.browser_manager import browser_manager
from src.models import db, Page, Application
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

bp = Blueprint('mcp', __name__)

# MCP is a "Meta Control Plane" for an AI to control the browser.
# It is a simplified interface that manages its own session.
_mcp_session_id = None

@bp.route('/session/open', methods=['POST'])
def open_mcp_session():
    """Opens a new browser session for the MCP to use."""
    global _mcp_session_id
    if _mcp_session_id and browser_manager.get_session(_mcp_session_id):
        return jsonify({'error': 'MCP session already open'}), 400

    data = request.get_json() or {}
    timeout = data.get('timeout')
    _mcp_session_id = browser_manager.create_session(timeout=timeout)
    return jsonify({'session_id': _mcp_session_id}), 201

@bp.route('/session/close', methods=['POST'])
def close_mcp_session():
    """Closes the MCP's browser session."""
    global _mcp_session_id
    if not _mcp_session_id or not browser_manager.get_session(_mcp_session_id):
        return jsonify({'error': 'MCP session not found or already closed'}), 404

    browser_manager.close_session(_mcp_session_id)
    _mcp_session_id = None
    return '', 204

def _get_driver():
    """Helper to get the driver for the MCP session."""
    if not _mcp_session_id:
        raise ConnectionError("MCP session not open")
    driver = browser_manager.get_session(_mcp_session_id)
    if not driver:
        raise ConnectionError("MCP session not found")
    return driver

@bp.route('/navigate', methods=['POST'])
def navigate_to_page():
    """Navigates to a page by its ID."""
    try:
        driver = _get_driver()
    except ConnectionError as e:
        return jsonify({'error': str(e)}), 400

    data = request.get_json() or {}
    page_id = data.get('page_id')
    if not page_id:
        return jsonify({'error': 'Missing page_id'}), 400

    page = Page.query.get_or_404(page_id)
    if not page.can_be_navigated_to or not page.url:
        return jsonify({'error': 'Page cannot be navigated to'}), 400

    driver.get(page.url)
    return '', 204

@bp.route('/wait-for-page', methods=['POST'])
def wait_for_page():
    """Waits for a page to load by checking for its identifying selectors."""
    try:
        driver = _get_driver()
    except ConnectionError as e:
        return jsonify({'error': str(e)}), 400

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

@bp.route('/current-page', methods=['GET'])
def get_current_page():
    """Identifies the current page by checking for identifying selectors."""
    try:
        driver = _get_driver()
    except ConnectionError as e:
        return jsonify({'error': str(e)}), 400

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

@bp.route('/screenshot', methods=['GET'])
def take_screenshot():
    """Takes a screenshot of the current browser view."""
    try:
        driver = _get_driver()
    except ConnectionError as e:
        return jsonify({'error': str(e)}), 400

    try:
        screenshot_data = driver.get_screenshot_as_png()
    except Exception as e:
        return jsonify({'error': f'Failed to take screenshot: {str(e)}'}), 500

    return Response(screenshot_data, mimetype='image/png')

@bp.route('/dom', methods=['GET'])
def get_dom():
    """Gets the DOM of the current page."""
    try:
        driver = _get_driver()
    except ConnectionError as e:
        return jsonify({'error': str(e)}), 400

    try:
        dom = driver.page_source
    except Exception as e:
        return jsonify({'error': f'Failed to get DOM: {str(e)}'}), 500

    return Response(dom, mimetype='text/html')

@bp.route('/pages', methods=['POST'])
def create_page():
    data = request.get_json() or {}

    required_fields = ['name', 'application_id', 'identifying_selectors']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if not Application.query.get(data['application_id']):
        return jsonify({'error': 'Application not found'}), 404

    page = Page(
        name=data['name'],
        application_id=data['application_id'],
        url=data.get('url'),
        can_be_navigated_to=data.get('can_be_navigated_to', False),
        identifying_selectors=data['identifying_selectors'],
        interactive_selectors=data.get('interactive_selectors', [])
    )

    db.session.add(page)
    db.session.commit()

    return jsonify(page.to_dict()), 201

@bp.route('/pages', methods=['GET'])
def get_pages():
    pages = Page.query.all()
    return jsonify([page.to_dict() for page in pages])

@bp.route('/pages/<int:id>', methods=['GET'])
def get_page(id):
    page = Page.query.get_or_404(id)
    return jsonify(page.to_dict())

@bp.route('/pages/<int:id>', methods=['PUT'])
def update_page(id):
    page = Page.query.get_or_404(id)
    data = request.get_json() or {}

    page.name = data.get('name', page.name)
    page.url = data.get('url', page.url)
    page.can_be_navigated_to = data.get('can_be_navigated_to', page.can_be_navigated_to)
    page.identifying_selectors = data.get('identifying_selectors', page.identifying_selectors)
    page.interactive_selectors = data.get('interactive_selectors', page.interactive_selectors)

    db.session.commit()
    return jsonify(page.to_dict())

@bp.route('/pages/<int:id>', methods=['DELETE'])
def delete_page(id):
    page = Page.query.get_or_404(id)
    db.session.delete(page)
    db.session.commit()
    return '', 204