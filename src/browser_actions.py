from src.browser_manager import browser_manager
from src.models import Page
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class BrowserActions:
    def get_current_page(self, pages, applications_pages):
        js_code = self._generate_selector_check_js(applications_pages)
        selector_results = self.driver.execute_script(js_code)

        for page in pages:
            app_id = str(page.get('application_id'))
            page_selectors = page.get('identifying_selectors', [])
            all_match = True
            for selector in page_selectors:
                alias = selector.get('alias')
                required_visible = selector.get('visible', None)
                result = selector_results.get(app_id, {}).get(alias, {})
                exists = result.get('existing', False)
                visible = result.get('visible', False)
                if required_visible is not None:
                    if not exists or visible != required_visible:
                        all_match = False
                        break
                else:
                    if not exists:
                        all_match = False
                        break
            if all_match:
                return page
        return None
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

    def _find_selector(self, page, alias):
        selectors = page.identifying_selectors + (page.interactive_selectors or [])
        for selector in selectors:
            if selector.get('alias') == alias:
                return selector.get('xpath')
        return None

    def check_selectors(self, applications_pages):
        js_code = self._generate_selector_check_js(applications_pages)
        return self.driver.execute_script(js_code)

    @staticmethod
    def _generate_selector_check_js(applications_pages):
        js = '''
function isElementVisible(el) {
    if (!el || !(el instanceof Element)) return false;
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
        for app_id, pages in applications_pages.items():
            js += f"result['{app_id}'] = {{}};\n"
            for page_id, selectors in pages.items():
                for selector in selectors:
                    alias = selector.get('alias')
                    xpath = selector.get('xpath')
                    js += f"try {{\n"
                    js += f"  var el = document.evaluate(\"{xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;\n"
                    js += f"  var exists = !!el;\n"
                    js += f"  var vis = exists ? isElementVisible(el) : false;\n"
                    js += f"  result['{app_id}']['{alias}'] = {{existing: exists, visible: vis}};\n"
                    js += f"}} catch (e) {{\n"
                    js += f"  result['{app_id}']['{alias}'] = {{existing: false, visible: false}};\n"
                    js += f"}}\n"
        js += "return result;"
        return js

    # Add more methods as needed for selector checks, etc.
