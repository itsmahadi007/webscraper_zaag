from selenium import webdriver

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')  # Maximize window to handle dynamic elements better
    driver = webdriver.Chrome(options=options)
    print("[INFO] Selenium driver set up successfully.")
    return driver