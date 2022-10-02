from contextlib import contextmanager

from playwright.sync_api import sync_playwright, Page


@contextmanager
def open_browser_page() -> Page:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()


