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

def get_next_screenshot_filename(folder, index):
    """
    Generate the next available filename for a screenshot.
    """
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"page_{index}.jpg")

def initialize_driver():
    """
    Set up and return a Selenium Chrome WebDriver with an adblocker extension.
    """
    options = Options()
    adblocker_extension_path = r"E:\Projects\manga_dl\uBlock0_1.60.0.chromium\uBlock0.chromium.crx"
    options.add_extension(adblocker_extension_path)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    time.sleep(5)  # Allow the extension to load
    return driver

def navigate_to_page(driver, url):
    """
    Open the URL in the driver and navigate to the manga page.
    """
    try:
        driver.get(url)
        time.sleep(2)  # Allow the page to load

        horizontal_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Horizontal Follow']"))
        )
        horizontal_button.click()
        print("Clicked the 'Horizontal Follow' button.")
        time.sleep(2)  # Wait briefly after clicking
    except Exception as e:
        print(f"Error navigating to page: {e}")

def capture_screenshot(driver, folder, page_number):
    """
    Capture a screenshot of the manga page.
    """
    try:
        active_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ds-item.active"))
        )
        image_element = active_container.find_element(By.CSS_SELECTOR, ".image-horizontal")

        if image_element.tag_name == "img":
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".ds-item.active img[src]"))
            )

        screenshot_filename = get_next_screenshot_filename(folder, page_number)
        image_element.screenshot(screenshot_filename)
        print(f"Screenshot of page {page_number} saved as {screenshot_filename}.")
    except Exception as e:
        print(f"Error capturing screenshot for page {page_number}: {e}")

def click_next_button(driver, page_number, total_pages):
    """
    Click the 'Next' button to navigate to the next manga page.
    """
    if page_number < total_pages:
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.nabu.nabu-left.hoz-next"))
            )
            driver.execute_script("arguments[0].click();", next_button)
            print(f"Clicked the 'Next' button for page {page_number}.")
            time.sleep(3)  # Wait for the next page to load
        except Exception as e:
            print(f"Failed to locate or click the 'Next' button for page {page_number}. Error: {e}")

def start_download():
    """
    Start the manga download process.
    """
    url = url_entry.get()
    total_pages = int(pages_entry.get())
    folder_location = folder_entry.get()
    type_choice = type_var.get().lower()
    type_number = number_entry.get()

    download_folder = os.path.join(folder_location, f"{type_choice}_{type_number}")
    print(f"\nStarting download:\nURL: {url}\nTotal pages: {total_pages}\nDownload folder: {download_folder}")

    driver = initialize_driver()
    navigate_to_page(driver, url)

    for current_page in range(1, total_pages + 1):
        capture_screenshot(driver, download_folder, current_page)
        click_next_button(driver, current_page, total_pages)

    print("All screenshots captured.")
    messagebox.showinfo("Download Complete", "All screenshots have been captured.")
    driver.quit()

def browse_folder():
    """
    Open a folder dialog to select a download folder.
    """
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_selected)

# Tkinter GUI setup
root = tk.Tk()
root.title("Manga Downloader")

tk.Label(root, text="Enter URL:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Total Pages:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
pages_entry = tk.Entry(root, width=10)
pages_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

tk.Label(root, text="Download Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_folder).grid(row=2, column=2, padx=5, pady=5)

tk.Label(root, text="Type (Volume/Chapter):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
type_var = tk.StringVar(value="Volume")
tk.Radiobutton(root, text="Volume", variable=type_var, value="Volume").grid(row=3, column=1, sticky=tk.W)
tk.Radiobutton(root, text="Chapter", variable=type_var, value="Chapter").grid(row=3, column=2, sticky=tk.W)

tk.Label(root, text="Volume/Chapter Number:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
number_entry = tk.Entry(root, width=10)
number_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

start_button = tk.Button(root, text="Start Download", command=start_download, bg="green", fg="white")
start_button.grid(row=5, column=0, columnspan=3, pady=10)

root.mainloop()
