from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def login(driver):
    driver.get("https://app.cosmosid.com/search")
    print("[INFO] Navigating to CosmosID login page.")
    time.sleep(2)  # Wait for page to load

    # Handle announcement dialog if it appears
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                    "//button[contains(text(), 'Close') or contains(text(), 'Dismiss') or contains(text(), 'OK')]"))).click()
        print("[INFO] Announcement dialog closed.")
    except:
        print("[INFO] No announcement dialog found.")

    # Handle login form
    try:
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='email' or @name='username' or @placeholder='Email address']")))
        email_field.send_keys("demo_estee2@cosmosid.com")
        print("[INFO] Email entered.")

        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='password' or @name='password' or @placeholder='Password']")))
        password_field.send_keys("xyzfg321")
        print("[INFO] Password entered.")

        # Click login button
        login_button = WebDriverWait(driver, 12).until(EC.element_to_be_clickable((By.ID, "sign-in-form--submit")))
        login_button.click()
        print("[INFO] Login button clicked.")
    except Exception as e:
        print("[ERROR] Error during login:", str(e))

    time.sleep(5)  # Wait for login to complete