from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

# Function to get the next available screenshot filename in the specified folder
def get_next_screenshot_filename(folder, index):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return os.path.join(folder, f"screenshot_{index:03}.jpg")

# Ask user for inputs before running the program
url = input("Enter the URL you want to open: ")
try:
    total_pages = int(input("Enter the total number of pages: "))
except ValueError:
    print("Invalid input. Please enter a valid number.")
    exit()

folder_location = input("Enter the folder location where screenshots will be saved: ")
type_choice = input("Is it a Volume or a Chapter? (Enter 'Volume' or 'Chapter'): ").strip().lower()

if type_choice not in ['volume', 'chapter']:
    print("Invalid choice. Please enter 'Volume' or 'Chapter'.")
    exit()

type_number = input(f"Enter the {type_choice.capitalize()} number: ")

# Construct the download folder path
download_folder = os.path.join(folder_location, f"{type_choice}_{type_number}")

print(f"\nURL: {url}")
print(f"Total pages: {total_pages}")
print(f"Download folder: {download_folder}")
print(f"Selected type: {type_choice.capitalize()}")
print(f"Selected number: {type_number}")

# Path to the AdBlocker extension (.crx file)
adblocker_extension_path = r"E:\Projects\manga_dl\uBlock0_1.60.0.chromium\uBlock0.chromium.crx"

# Set up Chrome options
options = Options()
options.add_extension(adblocker_extension_path)  # Add the AdBlocker extension

# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Maximize the browser window to full screen
driver.maximize_window()

# Wait for the extension to fully load
time.sleep(5)  # Increased wait time for extension loading

# Open the provided URL
driver.get(url)

# Wait for the page to load
time.sleep(2)

# Locate and click the "Horizontal Follow" button
try:
    horizontal_button = WebDriverWait(driver, 20).until(  # Increased wait time
        EC.element_to_be_clickable((By.XPATH, "//div[text()='Horizontal Follow']"))
    )
    horizontal_button.click()
    print("Clicked the 'Horizontal Follow' button.")
except Exception as e:
    print(f"Button click error: {e}")

# Wait briefly after clicking
time.sleep(2)

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
        screenshot_filename = get_next_screenshot_filename(download_folder, current_page)
        image_element.screenshot(screenshot_filename)
        print(f"Screenshot of page {current_page} saved as {screenshot_filename}.")

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
                time.sleep(3)  # Increased wait time for better loading
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
