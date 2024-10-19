from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
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
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH,
                                                                   "//button[contains(text(), 'Close') or contains(text(), 'Dismiss') or contains(text(), 'OK')]"))).click()
        print("[INFO] Dialog closed successfully.")
    except TimeoutException:
        pass  # Ignore if no dialog found


# Refresh page and check if the refresh is successful
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
        login(driver)


# Navigate and handle exporting TSV files
def scrape_data(driver):
    try:
        handle_dialogs(driver)  # Handle dialogs if any appear
        # Locate folder names in the table
        folders = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr td a"))
        )
        print(f"[INFO] Found {len(folders)} folders.")

        for index in range(len(folders)):
            try:
                # Re-locate the folder elements before each interaction
                folders = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr td a"))
                )

                # Ensure the folder element is clickable before processing
                folder = folders[index]
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"(//table//tbody//tr//td//a)[{index + 1}]")))

                print(f"[INFO] Scraping folder {folder.text}")
                process_folder(driver, folder)

            except StaleElementReferenceException as e:
                print(
                    f"[WARNING] Stale element detected while processing folder: {str(e)}. Retrying folder identification.")
                refresh_and_validate(driver, "search")
                continue  # Retry locating folders

            except Exception as e:
                print(f"[ERROR] Unable to process folder: {folder.text if folder else 'Unknown'}. Error: {str(e)}")

    except Exception as e:
        print("[ERROR] Problem In Root Folder:", str(e))


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
            time.sleep(2)

        # Locate the samples
        samples = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
        print(f"[INFO] Found {len(samples)} samples in folder: {folder_name}")

        for index in range(len(samples)):
            # for index in range(1):
            # Re-locate the sample element by index
            samples = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
            sample = samples[index]
            # print(f"[INFO] Processing sample: {sample.text}")

            # Process the sample
            process_sample(driver, sample)



    except Exception as e:
        print(f"[ERROR] Error processing folder '{folder_name}': {str(e)}")

    finally:
        print(f"[INFO] Finished processing folder: {folder_name}. Back to Root Folder")
        driver.get("https://app.cosmosid.com/search")  # Use direct navigation instead of driver.back()
        time.sleep(2)


# Process each sample and handle exporting
def process_sample(driver, sample):
    try:
        handle_dialogs(driver)  # Handle dialogs if any appear
        sample_name = sample.text
        print(f"[INFO] Processing sample: {sample_name}")
        sample.click()
        time.sleep(2)  # Allow time for the sample page to load

        # Ensure we're not stuck on a "data:," page
        if driver.current_url.startswith("data:,"):
            print("[WARNING] Page URL turned into 'data:,' likely indicating an issue. Refreshing the page.")
            refresh_and_validate(driver)

        try:
            # Wait for the selection field to be clickable and click it to open the dropdown
            selection_field = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='analysis-select']"))
            )

            # Read the current value of the selection field
            current_value = selection_field.text
            print(f"[INFO] Current selection: {current_value}")

            if current_value == "Bacteria":
                print("[INFO] Bacteria selected Already.")

                # Retry mechanism for taxonomy switcher button
                taxonomy_switcher_clicked = False
                retry_count = 3
                switcher_ids = ["artifact-select-button-biom", "artifact-select-button-kepler-biom"]
                for attempt in range(retry_count):
                    for switcher_id in switcher_ids:
                        try:
                            taxonomy_switcher_btn = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.ID, switcher_id))
                            )
                            taxonomy_switcher_btn.click()
                            taxonomy_switcher_clicked = True
                            print(f"[INFO] Taxonomy switcher button with ID '{switcher_id}' clicked.")
                            time.sleep(2)  # Allow the switcher to load
                            break
                        except TimeoutException:
                            print(
                                f"[WARNING] Attempt {attempt + 1}/{retry_count} - Failed to click taxonomy switcher button with ID '{switcher_id}'. Retrying with next ID...")
                    if taxonomy_switcher_clicked:
                        break
                    time.sleep(2)  # Allow some time before retrying

                if not taxonomy_switcher_clicked:
                    print("[ERROR] Unable to click taxonomy switcher button after multiple attempts.")
                    return

                # Initialize the variable to store the working index
                working_taxonomy_index = None

                # Try multiple attempts to locate and click the taxonomy options select label
                for attempt in [2, 1]:  # Trying index 2 first, then index 1 if necessary
                    try:
                        taxonomy_options_select_label = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, f"(//div[@id='artifact-options-select'])[{attempt}]"))
                        )
                        taxonomy_options_select_label.click()
                        working_taxonomy_index = attempt  # Store the working index
                        print(f"[INFO] Taxonomy options select label clicked using attempt index {attempt}.")
                        break
                    except TimeoutException:
                        print(
                            f"[WARNING] Attempt to click taxonomy level with index {attempt} failed. Trying next index...")

                # If a working index was found, proceed with dropdown options
                if working_taxonomy_index is not None:
                    # Wait for the dropdown options to be visible
                    dropdown_options = WebDriverWait(driver, 15).until(
                        EC.visibility_of_all_elements_located((By.XPATH, "//ul[@role='listbox']//li"))
                    )
                    print(f"[INFO] Found {len(dropdown_options)} dropdown options.")

                    # Iterate through taxonomy levels
                    for i in range(len(dropdown_options)):
                        # for i in range(2):
                        # Re-locate the dropdown options to avoid stale element reference
                        dropdown_options = WebDriverWait(driver, 15).until(
                            EC.visibility_of_all_elements_located((By.XPATH, "//ul[@role='listbox']//li"))
                        )
                        option = dropdown_options[i]
                        print(f"[INFO] Taxonomy option: {option.text}")
                        option.click()
                        time.sleep(1)  # Wait for the selection to be processed

                        try:
                            # Wait for the "Export current results" button to be clickable and click it
                            export_button = WebDriverWait(driver, 15).until(
                                EC.element_to_be_clickable((By.XPATH,
                                                            "//button[contains(@class, 'MuiButton-root') and contains(., 'Export current results')]"))
                            )
                            export_button.click()
                            print("[INFO] 'Export current results' button clicked.")
                        except Exception as e:
                            print(f"[ERROR] Export current results: {str(e)}")

                        # Re-click the taxonomy options select label to open the dropdown again
                        try:
                            taxonomy_options_select_label = WebDriverWait(driver, 15).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, f"(//div[@id='artifact-options-select'])[{working_taxonomy_index}]"))
                            )
                            taxonomy_options_select_label.click()
                            print(
                                f"[INFO] Taxonomy options select label clicked again using stored index {working_taxonomy_index}.")
                        except TimeoutException:
                            print(
                                f"[ERROR] Unable to re-click taxonomy options select label using stored index {working_taxonomy_index}.")
                else:
                    print("[ERROR] No valid taxonomy options select label index found. Cannot proceed.")

            else:
                try:
                    # Wait for the "Export current results" button to be clickable and click it
                    export_button = WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    "//button[contains(@class, 'MuiButton-root') and contains(., 'Export current results')]"))
                    )
                    export_button.click()
                    print("[INFO] 'Export current results' button clicked.")
                except Exception as e:
                    print(f"[ERROR] Export current results: {str(e)}")

            time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Error interacting with the selection field: {str(e)}")

    except Exception as e:
        print(f"[ERROR] Error processing sample {str(e)}")

    finally:
        print(f"[INFO] Finished processing sample {sample_name} , Back to Nested Folder")
        # driver.get(driver.current_url.split('/nested')[0])  # Refresh by going back to a stable parent URL
        driver.back()
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

# Retrieve and print the current value in the field
# current_value_element = driver.find_element(By.XPATH, "(//div[@id='artifact-options-select'])[2]")
# current_value = current_value_element.text
# print(f"[INFO] Current selection after clicking: {current_value}")
