from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

# Function to get the next available screenshot filename in the 'manga' folder
def get_next_screenshot_filename():
    # Create 'manga' folder if it doesn't exist
    if not os.path.exists("manga"):
        os.makedirs("manga")

    i = 1
    while os.path.exists(f"manga/screenshot_{i}.jpg"):
        i += 1
    return f"manga/screenshot_{i}.jpg"

# Path to the AdBlocker extension (.crx file)
adblocker_extension_path = r"E:\Projects\manga_dl\uBlock0_1.60.0.chromium\uBlock0.chromium.crx"

# Set up Chrome options
options = Options()
options.add_extension(adblocker_extension_path)  # Add the AdBlocker extension

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Maximize the browser window to full screen
driver.maximize_window()

# Ask the user for a URL
url = input("Enter the URL you want to open: ")

# Open the provided URL
driver.get(url)

# Wait for the page to load
time.sleep(2)  # Adjust if needed

# Locate and click the "Horizontal Follow" button
try:
    horizontal_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[text()='Horizontal Follow']"))
    )
    horizontal_button.click()
    print("Clicked the 'Horizontal Follow' button.")
except Exception as e:
    print(f"Button click error: {e}")

# Wait briefly after clicking
time.sleep(2)

# Locate the manga canvas element
try:
    manga_canvas = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "canvas.image-horizontal"))
    )

    # Get the next available filename
    screenshot_filename = get_next_screenshot_filename()

    # Take a screenshot of the canvas element
    manga_canvas.screenshot(screenshot_filename)
    print(f"Screenshot of the manga image saved as {screenshot_filename} in the 'manga' folder.")
except Exception as e:
    print(f"Error capturing manga image: {e}")

# Wait briefly before clicking 'Next'
time.sleep(1)

# Locate and click the 'Next' button
try:
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#divslide > div.navi-buttons.hoz-controls.hoz-controls-rtl > a.nabu.nabu-left.hoz-next"))
    )

    # Click the 'Next' button using JavaScript
    driver.execute_script("arguments[0].click();", next_button)
    print("Clicked the 'Next' button.")
except Exception as e:
    print(f"Error clicking 'Next' button: {e}")

# Stop the script after clicking 'Next' for debugging
print("Stopped for debugging. Check the browser for further inspection.")

# Keep the browser open for inspection
input("Press Enter to close the browser...")

# Close the browser once done
driver.quit()
