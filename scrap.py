from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import asyncio
import time
from bs4 import BeautifulSoup

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
    time.sleep(2) # Wait for page to load

    # Handle announcement dialog if it appears
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close') or contains(text(), 'Dismiss') or contains(text(), 'OK')]"))).click()
        print("[INFO] Announcement dialog closed.")
    except:
        print("[INFO] No announcement dialog found.")

    # Handle potential dialogs/popups by clicking through them
    try:
        # Use explicit waiting to ensure the email and password fields are present
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @name='username' or @placeholder='Email address']")))
        email_field.send_keys("demo_estee2@cosmosid.com")
        print("[INFO] Email entered.")

        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @name='password' or @placeholder='Password']")))
        password_field.send_keys("xyzfg321")
        print("[INFO] Password entered.")

        # Get login button by ID
        login_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "sign-in-form--submit")))
        login_button.click()
        print("[INFO] Login button clicked using ID.")
    except Exception as e:
        print("[ERROR] Error during login:", str(e))

    time.sleep(5) # Wait for login

    # Handle additional popup dialog after login
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close') or contains(text(), 'Dismiss') or contains(text(), 'OK')]"))).click()
        print("[INFO] Post-login dialog closed.")
    except:
        print("[INFO] No post-login dialog found.")

# Handle potential dialogs during navigation
def handle_dialogs(driver):
    try:
        # Example: Close popup if it appears
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close') or contains(text(), 'Dismiss') or contains(text(), 'OK')]"))).click()
        print("[INFO] Dialog closed successfully.")
    except:
        pass  # Ignore if no dialog found

# Scrape the data and save it to CSV
async def scrape_data(driver):
    # Create CSV file
    with open('cosmosid_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Folder Name', 'Sample Name', 'Taxonomy Level', 'Headers', 'Rows'])
        print("[INFO] CSV file created.")

        try:
            # Locate folder names in the table
            folders = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr td a")))
            print(f"[INFO] Found {len(folders)} folders.")
        except Exception as e:
            print("[ERROR] No folders found or unable to locate folders:", str(e))
            folders = []

        for folder in folders:
            handle_dialogs(driver)  # Handle dialogs if any appear
            folder_name = folder.text
            print(f"[INFO] Processing folder: {folder_name}")
            folder.click()
            time.sleep(2)  # Allow time for the page to load
            samples = driver.find_elements(By.CSS_SELECTOR, ".sample-class")
            print(f"[INFO] Found {len(samples)} samples in folder: {folder_name}")
            for sample in samples:
                handle_dialogs(driver)  # Handle dialogs if any appear
                sample_name = sample.text
                print(f"[INFO] Processing sample: {sample_name}")
                sample.click()
                time.sleep(2)  # Allow time for the sample page to load
                # Check for bacteria results
                if "Bacteria" in driver.page_source:
                    taxonomy_switcher = driver.find_element(By.CSS_SELECTOR, ".taxonomy-switcher")
                    levels = taxonomy_switcher.find_elements(By.TAG_NAME, "option")
                    print(f"[INFO] Found {len(levels)} taxonomy levels for sample: {sample_name}")
                    for level in levels:
                        handle_dialogs(driver)  # Handle dialogs if any appear
                        level_name = level.text
                        print(f"[INFO] Processing taxonomy level: {level_name} for sample: {sample_name}")
                        level.click()
                        time.sleep(2)
                        page_html = driver.page_source
                        soup = BeautifulSoup(page_html, 'html.parser')
                        table_data = extract_table_data(soup)

                        # Write to CSV
                        writer.writerow([folder_name, sample_name, level_name, table_data['headers'], table_data['rows']])
                        print(f"[INFO] Data written to CSV for taxonomy level: {level_name} in sample: {sample_name}")

# Extract table data using BeautifulSoup
def extract_table_data(soup):
    table = soup.find('table', {'class': 'results-table'})
    if table:
        headers = [header.text.strip() for header in table.find_all('th')]
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all('td')
            rows.append([cell.text.strip() for cell in cells])
        print(f"[INFO] Extracted table data with {len(rows)} rows.")
        return {"headers": headers, "rows": rows}
    else:
        print("[INFO] No table data found.")
        return {"headers": [], "rows": []}

# Main execution
if __name__ == "__main__":
    print("[INFO] Starting scraper.")
    driver = setup_driver()

    try:
        login(driver)
        asyncio.run(scrape_data(driver))
    finally:
        driver.quit()
        print("[INFO] Selenium driver closed.")
