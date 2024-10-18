from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import csv
import asyncio
import time
from bs4 import BeautifulSoup


# Set up Selenium driver
def setup_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    return driver


# Login to the CosmosID portal
def login(driver):
    driver.get("https://app.cosmosid.com/search")
    time.sleep(2)  # Wait for page to load

    # Update the selector for username and password fields and login button
    try:
        driver.find_element(By.ID, "username").send_keys("demo_estee2@cosmosid.com")
        driver.find_element(By.ID, "password").send_keys("xyzfg321")
        driver.find_element(By.XPATH,
                            "//button[contains(text(), 'Log in')]" or "//button[contains(text(), 'Sign in')]").click()
    except Exception as e:
        print("Error during login:", str(e))

    time.sleep(5)  # Wait for login


# Scrape the data and save it to CSV
async def scrape_data(driver):
    # Create CSV file
    with open('cosmosid_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Folder Name', 'Sample Name', 'Taxonomy Level', 'Headers', 'Rows'])

        folders = driver.find_elements(By.CSS_SELECTOR, ".folder-class")  # Example selector

        for folder in folders:
            folder_name = folder.text
            folder.click()
            samples = driver.find_elements(By.CSS_SELECTOR, ".sample-class")
            for sample in samples:
                sample_name = sample.text
                sample.click()
                # Check for bacteria results
                if "Bacteria" in driver.page_source:
                    taxonomy_switcher = driver.find_element(By.CSS_SELECTOR, ".taxonomy-switcher")
                    levels = taxonomy_switcher.find_elements(By.TAG_NAME, "option")
                    for level in levels:
                        level_name = level.text
                        level.click()
                        time.sleep(2)
                        page_html = driver.page_source
                        soup = BeautifulSoup(page_html, 'html.parser')
                        table_data = extract_table_data(soup)

                        # Write to CSV
                        writer.writerow(
                            [folder_name, sample_name, level_name, table_data['headers'], table_data['rows']])


# Extract table data using BeautifulSoup
def extract_table_data(soup):
    table = soup.find('table', {'class': 'results-table'})
    if table:
        headers = [header.text for header in table.find_all('th')]
        rows = []
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            rows.append([cell.text for cell in cells])
        return {"headers": headers, "rows": rows}
    else:
        return {"headers": [], "rows": []}


# Main execution
if __name__ == "__main__":
    driver = setup_driver()

    try:
        login(driver)
        asyncio.run(scrape_data(driver))
    finally:
        driver.quit()
