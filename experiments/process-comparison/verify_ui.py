"""Author-only browser control. Requires separately approved Playwright setup."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

URL = Path(__file__).with_name('ui.html').resolve().as_uri()


def probe(browser, variant, case):
    page = browser.new_page()
    try:
        page.goto(URL + '?variant=' + variant)
        page.get_by_label('Quantity').fill('3')
        page.get_by_role('button', name='Save order').click()
        if case == 'ui-double':
            # A real second click while enabled; disabled clean button is not clicked.
            button = page.get_by_role('button', name='Save order')
            if button.is_enabled():
                button.click()
        expect(page.get_by_role('status')).to_have_text('Saved')
        # Allow both scheduled completions before checking duplicate absence.
        # This delay belongs to the author control, not a candidate solution.
        page.wait_for_timeout(300)
        expect(page.locator('#orders li')).to_have_count(1)
        expect(page.locator('#orders li')).to_have_text(['Quantity: 3'])
    finally:
        page.close()


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    try:
        for case in ('ui-double', 'ui-value'):
            probe(browser, 'clean', case)
            try:
                probe(browser, case, case)
            except AssertionError:
                print(case, 'detected')
            else:
                raise AssertionError(case + ' survived')
    finally:
        browser.close()
