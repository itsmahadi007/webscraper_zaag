from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
from handle_dialogs import handle_dialogs
from navigation_utils import refresh_and_validate
from process_sample import process_sample


def scrape_data(driver):
    try:
        handle_dialogs(driver)  # Handle dialogs if any appear
        # Locate folder names in the table
        folders = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "table tbody tr td a")
            )
        )
        print(f"[INFO] Found {len(folders)} folders.")

        for index in range(len(folders)):
            try:
                # Re-locate the folder elements before each interaction
                folders = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "table tbody tr td a")
                    )
                )
                folder = folders[index]
                print(f"[INFO] Processing folder: {folder.text}")
                process_folder(driver, folder)

            except StaleElementReferenceException as e:
                print(
                    f"[WARNING] Stale element detected while processing folder: {str(e)}. Retrying folder identification."
                )
                refresh_and_validate(driver, "search")
                continue  # Retry locating folders
            except Exception as e:
                print(
                    f"[ERROR] Unable to process folder: {folder.text if folder else 'Unknown'}. Error: {str(e)}"
                )

    except Exception as e:
        print("[ERROR] Problem In Root Folder:", str(e))


def process_folder(driver, folder):
    try:
        handle_dialogs(driver)  # Handle dialogs if any appear
        folder.click()
        time.sleep(3)  # Allow time for the page to load

        # Ensure we're not stuck on a "data:," page
        if driver.current_url.startswith("data:,"):
            refresh_and_validate(driver)

        # Locate samples
        samples = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
        for index in range(len(samples)):
            # Re-locate the sample element by index to avoid stale element issues
            samples = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
            sample = samples[index]
            print(f"[INFO] Processing sample: {sample.text}")

            # Process the sample
            process_sample(driver, sample)
        print(f"[INFO] Finished processing folder: {folder.text}")

    except Exception as e:
        print(f"[ERROR] Error processing folder '{folder.text}': {str(e)}")

    finally:
        print(
            f"[INFO] Finished processing folder: {folder.text}. Navigating back to Root Folder."
        )
        driver.get(
            "https://app.cosmosid.com/search"
        )  # Use direct navigation instead of driver.back()
        time.sleep(2)
