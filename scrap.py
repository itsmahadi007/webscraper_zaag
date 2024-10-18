from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time


# Set up Selenium driver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')  # Maximize window to handle dynamic elements better
    driver = webdriver.Chrome(options=options)
    print("[INFO] Selenium driver set up successfully.")
    return driver


# Login to the CosmosID portal
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


# Handle potential dialogs during navigation
def handle_dialogs(driver):
    try:
        # Example: Close popup if it appears
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,
                                                                   "//button[contains(text(), 'Close') or contains(text(), 'Dismiss') or contains(text(), 'OK')]"))).click()
        print("[INFO] Dialog closed successfully.")
    except:
        pass  # Ignore if no dialog found


# Navigate and handle exporting TSV files
def scrape_data(driver):
    try:
        # Locate folder names in the table
        folders = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr td a")))
        print(f"[INFO] Found {len(folders)} folders.")
    except Exception as e:
        print("[ERROR] No folders found or unable to locate folders:", str(e))
        folders = []

    for folder in folders:
        process_folder(driver, folder)


# Process each folder
def process_folder(driver, folder):
    try:
        handle_dialogs(driver)  # Handle dialogs if any appear
        folder_name = folder.text
        print(f"[INFO] Processing folder: {folder_name}")
        folder.click()
        time.sleep(3)  # Allow time for the page to load

        # Ensure we're not stuck on a "data:," page
        if driver.current_url.startswith("data:,"):
            print("[WARNING] Page URL turned into 'data:,' likely indicating an issue. Refreshing the page.")
            driver.refresh()
            time.sleep(3)

        # Locate samples in the nested folder
        samples = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
        print(f"[INFO] Found {len(samples)} samples in folder: {folder_name}")

        for sample in samples:
            process_sample(driver, sample)
            driver.back()


    except Exception as e:
        print(f"[ERROR] Error processing folder '{folder_name}': {str(e)}")

    finally:
        driver.back()  # Go back to the root folder view
        time.sleep(2)


# Process each sample and handle exporting
def process_sample(driver, sample):
    try:
        handle_dialogs(driver)  # Handle dialogs if any appear
        sample_name = sample.text
        print(f"[INFO] Processing sample: {sample_name}")
        sample.click()
        time.sleep(3)  # Allow time for the sample page to load

        # Ensure we're not stuck on a "data:," page
        if driver.current_url.startswith("data:,"):
            print("[WARNING] Page URL turned into 'data:,' likely indicating an issue. Refreshing the page.")
            driver.refresh()
            time.sleep(3)

        try:
            # Wait for the selection field to be clickable and click it to open the dropdown
            selection_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='analysis-select']"))
            )

            # Read the current value of the selection field
            current_value = selection_field.text
            print(f"[INFO] Current selection: {current_value}")

            if current_value == "Bacteria":
                print("[INFO] Bacteria selected Already.")

                # Wait for the button to be clickable and click it
                taxonomy_switcher_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@id='artifact-select-button-kepler-biom']"))
                )
                taxonomy_switcher_btn.click()
                print("[INFO] Taxonomy switcher button clicked.")
                time.sleep(2)

                # Wait for the taxonomy options select label to be clickable and click it
                taxonomy_options_select_label = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "(//div[@id='artifact-options-select'])[2]"))
                    # Adjust the index as needed
                )
                taxonomy_options_select_label.click()
                print("[INFO] Taxonomy options select label clicked.")
                time.sleep(2)

                # Wait for the dropdown options to be visible
                dropdown_options = WebDriverWait(driver, 10).until(
                    EC.visibility_of_all_elements_located((By.XPATH, "//ul[@role='listbox']//li"))
                )
                print(f"[INFO] Found {len(dropdown_options)} dropdown options.")

                # Retrieve and print the text of each option
                for option in dropdown_options:
                    print(f"[INFO] Taxonomy option: {option.text}")
                    option.click()
                    time.sleep(2)  # Wait for the selection to be processed

                    # Retrieve and print the current value in the field
                    current_value_element = driver.find_element(By.XPATH, "(//div[@id='artifact-options-select'])[2]")
                    current_value = current_value_element.text
                    print(f"[INFO] Current selection after clicking: {current_value}")

                    try:
                        # Wait for the "Export current results" button to be clickable and click it
                        export_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH,
                                                        "//button[contains(@class, 'MuiButton-root') and contains(., 'Export current results')]"))
                        )
                        export_button.click()
                        print("[INFO] 'Export current results' button clicked.")
                    except Exception as e:
                        print(f"[ERROR] Export current results: {str(e)}")

                time.sleep(2)



        except Exception as e:
            print(f"[ERROR] Error interacting with the selection field: {str(e)}")

        # # Check for bacteria results and click EXPORT button
        # if "Bacteria" in driver.page_source:
        #     try:
        #         export_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='EXPORT']")))
        #         export_button.click()
        #         print("[INFO] EXPORT button clicked.")
        #
        #         # Wait for the export options to be visible and click All TSV Tables
        #         tsv_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='All TSV Tables']")))
        #         tsv_option.click()
        #         print("[INFO] All TSV Tables export selected. Waiting for completion...")
        #         time.sleep(300)  # Wait for TSV generation (5 minutes)
        #         print(f"[INFO] TSV export completed for sample: {sample_name}")
        #     except Exception as e:
        #         print(f"[ERROR] Error during export for sample '{sample_name}': {str(e)}")

    except Exception as e:
        print(f"[ERROR] Error processing sample '{sample_name}': {str(e)}")

    finally:
        driver.back()  # Go back to the folder view
        time.sleep(2)


# Main execution
if __name__ == "__main__":
    print("[INFO] Starting scraper.")
    driver = setup_driver()

    try:
        login(driver)
        scrape_data(driver)
    finally:
        driver.quit()
        print("[INFO] Selenium driver closed.")
