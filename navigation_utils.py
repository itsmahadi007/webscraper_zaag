from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def refresh_and_validate(driver, expected_url_fragment=None):
    driver.refresh()
    time.sleep(3)  # Allow some time for the refresh to complete

    # Check for 'data:,' issue and handle it
    if driver.current_url.startswith("data:,"):
        print("[WARNING] Page URL turned into 'data:,' again after refresh. Retrying refresh...")
        driver.refresh()
        time.sleep(3)

    # Validate expected page content (optional)
    if expected_url_fragment and expected_url_fragment not in driver.current_url:
        print("[ERROR] Unexpected page URL after refresh, possible session timeout. Attempting re-login...")
        # Import login dynamically to prevent circular dependency
        from login import login
        login(driver)