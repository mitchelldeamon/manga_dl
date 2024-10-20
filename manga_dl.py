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
def get_next_screenshot_filename(index):
    # Create 'manga' folder if it doesn't exist
    if not os.path.exists("manga"):
        os.makedirs("manga")

    return f"manga/screenshot_{index:03}.jpg"

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
        EC.element_to_be_clickable((By.XPATH, "//div[text()='Horizontal Follow']"))
    )
    horizontal_button.click()
    print("Clicked the 'Horizontal Follow' button.")
except Exception as e:
    print(f"Button click error: {e}")

# Wait briefly after clicking
time.sleep(2)

# Ask the user for the total number of pages
try:
    total_pages = int(input("Enter the total number of pages: "))
    print(f"Total number of pages: {total_pages}")
except ValueError:
    print("Invalid input. Please enter a valid number.")
    driver.quit()
    exit()

# Loop through each page and take screenshots
for current_page in range(1, total_pages + 1):
    try:
        print(f"Attempting to capture screenshot for page {current_page}...")

        # Wait for the active image container
        active_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ds-item.active"))
        )

        # Look for an <img> or <canvas> within the active container
        image_element = active_container.find_element(By.CSS_SELECTOR, ".image-horizontal")

        # If it's an <img>, wait for the 'src' attribute to be loaded
        if image_element.tag_name == "img":
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".ds-item.active img[src]"))
            )

        # Take a screenshot of the image element
        screenshot_filename = get_next_screenshot_filename(current_page)
        image_element.screenshot(screenshot_filename)
        print(f"Screenshot of page {current_page} saved as {screenshot_filename} in the 'manga' folder.")

        # Click the 'Next' button if not on the last page
        if current_page < total_pages:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.nabu.nabu-left.hoz-next"))
                )

                # Click the 'Next' button using JavaScript
                driver.execute_script("arguments[0].click();", next_button)
                print(f"Clicked the 'Next' button for page {current_page}.")

                # Wait briefly for the next page to load
                time.sleep(2)
            except Exception as e:
                print(f"Failed to locate or click the 'Next' button for page {current_page}. Error: {e}")

    except Exception as e:
        print(f"Error on page {current_page}: {e}")
        break

print("All screenshots captured.")

# Keep the browser open for inspection
input("Press Enter to close the browser...")

# Close the browser once done
driver.quit()
