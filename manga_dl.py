import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Function to get the next available screenshot filename in the specified folder
def get_next_screenshot_filename(folder, index):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return os.path.join(folder, f"page_{index}.jpg")

# Function to start the download process
def start_download():
    global url, total_pages, folder_location, type_choice, type_number

    # Retrieve user inputs from Tkinter fields
    url = url_entry.get()
    total_pages = int(pages_entry.get())
    folder_location = folder_entry.get()
    type_choice = type_var.get().lower()
    type_number = number_entry.get()

    # Construct the download folder path
    download_folder = os.path.join(folder_location, f"{type_choice}_{type_number}")

    print(f"\nURL: {url}")
    print(f"Total pages: {total_pages}")
    print(f"Download folder: {download_folder}")
    print(f"Selected type: {type_choice.capitalize()}")
    print(f"Selected number: {type_number}")

    # Set up Chrome options
    adblocker_extension_path = r"E:\Projects\manga_dl\uBlock0_1.60.0.chromium\uBlock0.chromium.crx"
    options = Options()
    options.add_extension(adblocker_extension_path)  # Add the AdBlocker extension

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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
    messagebox.showinfo("Download Complete", "All screenshots have been captured.")

    # Close the browser once done
    driver.quit()

# Function to browse and select folder location
def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_selected)

# Initialize Tkinter window
root = tk.Tk()
root.title("Manga Downloader")

# URL input
tk.Label(root, text="Enter URL:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5)

# Total pages input
tk.Label(root, text="Total Pages:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
pages_entry = tk.Entry(root, width=10)
pages_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

# Folder location input
tk.Label(root, text="Download Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_folder).grid(row=2, column=2, padx=5, pady=5)

# Type selection (Volume/Chapter)
tk.Label(root, text="Type (Volume/Chapter):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
type_var = tk.StringVar(value="Volume")
tk.Radiobutton(root, text="Volume", variable=type_var, value="Volume").grid(row=3, column=1, sticky=tk.W)
tk.Radiobutton(root, text="Chapter", variable=type_var, value="Chapter").grid(row=3, column=2, sticky=tk.W)

# Type number input
tk.Label(root, text="Volume/Chapter Number:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
number_entry = tk.Entry(root, width=10)
number_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

# Start button
start_button = tk.Button(root, text="Start Download", command=start_download, bg="green", fg="white")
start_button.grid(row=5, column=0, columnspan=3, pady=10)

# Run the Tkinter loop
root.mainloop()
