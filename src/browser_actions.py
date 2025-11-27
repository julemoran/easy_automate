from src.browser_manager import browser_manager
from src.models import Page
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class BrowserActions:

    def __init__(self, driver):
        self.driver = driver

    def navigate_to_page(self, page_id):
        page = Page.query.get_or_404(page_id)
        if not page.can_be_navigated_to or not page.url:
            return False, 'Page cannot be navigated to'
        self.driver.get(page.url)
        return True, None

    def click_element(self, page_id, alias):
        page = Page.query.get_or_404(page_id)
        xpath = self._find_selector(page, alias)
        if not xpath:
            return False, 'Selector alias not found on page'
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            element.click()
        except NoSuchElementException:
            return False, 'Element not found'
        return True, None

    def set_element_value(self, page_id, alias, value):
        page = Page.query.get_or_404(page_id)
        xpath = self._find_selector(page, alias)
        if not xpath:
            return False, 'Selector alias not found on page'
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            element.clear()
            element.send_keys(value)
        except NoSuchElementException:
            return False, 'Element not found'
        return True, None

    def get_element_value(self, page_id, alias):
        page = Page.query.get_or_404(page_id)
        xpath = self._find_selector(page, alias)
        if not xpath:
            return None, 'Selector alias not found on page'
        try:
            element = self.driver.find_element(By.XPATH, xpath)
            value = element.get_attribute('value') or element.text
        except NoSuchElementException:
            return None, 'Element not found'
        return value, None

    def wait_for_page(self, page_id, timeout=10):
        page = Page.query.get_or_404(page_id)
        try:
            wait = WebDriverWait(self.driver, timeout)
            for selector in page.identifying_selectors:
                wait.until(EC.presence_of_element_located((By.XPATH, selector['xpath'])))
        except TimeoutException:
            return False, 'Timeout waiting for page to load'
        return True, None

    def take_screenshot(self):
        try:
            screenshot_data = self.driver.get_screenshot_as_png()
        except Exception as e:
            return None, f'Failed to take screenshot: {str(e)}'
        return screenshot_data, None

    def get_dom(self):
        try:
            dom = self.driver.page_source
        except Exception as e:
            return None, f'Failed to get DOM: {str(e)}'
        return dom, None
    
    def get_current_pages(self, pages):
        # Exclude pages with no identifying selectors
        filtered_pages = [page for page in pages if page.get('identifying_selectors')]

        # Collect all unique xpaths from all identifying selectors of all filtered pages
        all_xpaths = set()
        for page in filtered_pages:
            for selector in page.get('identifying_selectors', []):
                xpath = selector.get('xpath')
                if xpath:
                    all_xpaths.add(xpath)

        # Check all selectors at once
        selector_results = self.check_selectors(list(all_xpaths))

        matched_pages = []
        for page in filtered_pages:
            all_match = True
            for selector in page.get('identifying_selectors', []):
                xpath = selector.get('xpath')
                if not xpath:
                    all_match = False
                    break
                result = selector_results.get(xpath, {})
                exists = result.get('existing', False)
                visible = result.get('visible', False)
                required_visible = selector.get('visible', None)
                # Normalize required_visible to boolean if it's a string
                if isinstance(required_visible, str):
                    if required_visible.lower() == 'true':
                        required_visible = True
                    elif required_visible.lower() == 'false':
                        required_visible = False
                # Must exist
                if not exists:
                    all_match = False
                    break
                # If visible is set, must match
                if required_visible is not None and visible != required_visible:
                    all_match = False
                    break
            if all_match:
                matched_pages.append(page)
        return matched_pages

    def _find_selector(self, page, alias):
        selectors = page.identifying_selectors + (page.interactive_selectors or [])
        for selector in selectors:
            if selector.get('alias') == alias:
                return selector.get('xpath')
        return None

    def check_selectors(self, selectors):
        js_code = self._generate_selector_check_js(selectors)
        return self.driver.execute_script(js_code)

    @staticmethod
    def _generate_selector_check_js(selectors):
        js = '''
function isElementVisible(el) {
    if (!el) return false; 
    if (el.nodeType == Node.TEXT_NODE) return isElementVisible(el.parentElement);
    if (!(el instanceof Element)) return false;
    if (!document.documentElement.contains(el)) return false;
    if (el.getClientRects().length === 0) return false;
    for (let cur = el; cur; cur = cur.parentElement) {
        const s = window.getComputedStyle(cur);
        if (s.display === 'none' || s.visibility === 'hidden') return false;
        if (cur.hasAttribute && cur.getAttribute('aria-hidden') === 'true') return false;
        if (parseFloat(s.opacity) === 0) return false;
    }
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    return true;
}
var result = {};
'''
        def js_escape(s):
            # Only escape backslashes and double quotes for JS string
            return s.replace('\\', r'\\').replace('"', r'\\"')

        for xpath in selectors:
            escaped_xpath = js_escape(xpath)
            # Always use double quotes for JS object keys to avoid issues with single quotes in XPath
            js += "try {\n"
            js += '  var xpath = "{}";\n'.format(escaped_xpath)
            js += "  var el = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;\n"
            js += "  var exists = !!el;\n"
            js += "  var vis = exists ? isElementVisible(el) : false;\n"
            js += "  result[\"{}\"] = {{existing: exists, visible: vis, xpath }};\n".format(escaped_xpath)
            js += "} catch (e) {\n"
            js += '  console.error("Error evaluating XPath {}:", e);\n'.format(escaped_xpath)
            js += "  result[\"{}\"] = {{existing: false, visible: false, error: String(e)}};\n".format(escaped_xpath)
            js += "}\n"
        js += "return result;"
        return js

    # Add more methods as needed for selector checks, etc.
