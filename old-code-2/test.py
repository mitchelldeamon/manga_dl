import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


def create_driver(window_width, window_height):
    """Initialize and return a Chrome WebDriver with specified options."""
    adblock_path = os.getenv('ADBLOCK_PATH')
    if not adblock_path:
        raise ValueError(
            "Environment variable 'ADBLOCK_PATH' is not set or empty.")

    options = Options()
    options.add_extension(adblock_path)
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    driver.set_window_size(window_width, window_height)
    time.sleep(5)  # Allow adblock extension to load
    return driver


def wait_for_element(driver, by, value, timeout=20, click=False):
    """Wait for an element to be present and optionally click it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        print(f"Element found: {element.get_attribute('outerHTML')}")
        if click:
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", element)
            print("Scrolled to element")
            try:
                element.click()
                print("Native click successful")
            except Exception as e:
                print(f"Native click failed: {e}")
                driver.execute_script("arguments[0].click();", element)
                print("JavaScript click executed")
        return element
    except Exception as e:
        print(f"Error waiting for element {value}: {e}")
        return None


def navigate_and_prepare(driver, url):
    """Navigate to the URL and prepare the page for screenshot capture."""
    try:
        driver.get(url)
        time.sleep(2)  # Wait for initial load
        wait_for_element(driver, By.XPATH,
                         "//div[text()='Horizontal Follow']", click=True)
        print("Navigated and set to 'Horizontal Follow' view.")
    except Exception as e:
        print(f"Navigation error: {e}")


def preload_all_pages(driver, total_pages):
    """Quickly click through all pages to load them, then return to start."""
    try:
        # Click through to the last page
        for _ in range(total_pages - 1):  # -1 because we're already on page 1
            next_button = wait_for_element(
                driver, By.CSS_SELECTOR, "a.nabu.nabu-left.hoz-next", 5, click=True)
            if not next_button:
                print("Could not find next button during preload")
                break
            time.sleep(0.1)  # Minimal delay during preload

        # Click back to the first page
        for _ in range(total_pages - 1):
            prev_button = wait_for_element(
                driver, By.CSS_SELECTOR, "a.nabu.nabu-right.hoz-prev", 5, click=True)
            if not prev_button:
                print("Could not find previous button during return")
                break
            time.sleep(0.1)  # Minimal delay during return

        print("Completed preloading all pages and returned to start")
    except Exception as e:
        print(f"Error during page preloading: {e}")


def capture_and_save_screenshot(element, folder, page_number):
    """Capture a screenshot of the given element and save it to the specified folder."""
    filename = os.path.join(folder, f"{page_number}.jpg")
    os.makedirs(folder, exist_ok=True)
    try:
        element.screenshot(filename)
        print(f"Screenshot saved: {filename}")
    except Exception as e:
        print(f"Error capturing screenshot: {e}")


def process_page(driver, folder, page_number, total_pages, delay):
    """Capture screenshot and click 'Next' to proceed to the next page."""
    active_container = wait_for_element(
        driver, By.CSS_SELECTOR, ".ds-item.active", 10)
    if active_container:
        image_element = active_container.find_element(
            By.CSS_SELECTOR, ".image-horizontal")
        capture_and_save_screenshot(image_element, folder, page_number)

        if page_number < total_pages:
            next_button = wait_for_element(
                driver, By.CSS_SELECTOR, "a.nabu.nabu-left.hoz-next", 10, click=True)
            if next_button:
                print(f"Proceeded to page {page_number + 1}.")
                time.sleep(delay)
            else:
                print(f"Failed to navigate to page {page_number + 1}.")


def start_download():
    """Start the download process for the manga pages."""
    url, total_pages, folder, volume_chapter, number, width, height, delay = get_gui_inputs()
    download_folder = os.path.join(
        folder, f"{volume_chapter.lower()}-{number}")

    driver = create_driver(width, height)
    navigate_and_prepare(driver, url)

    # Preload all pages before capturing screenshots
    preload_all_pages(driver, total_pages)

    # Start capturing screenshots
    for page_num in range(1, total_pages + 1):
        process_page(driver, download_folder, page_num, total_pages, delay)
        update_progress(page_num, total_pages)

    messagebox.showinfo("Download Complete",
                        "All screenshots have been captured.")
    driver.quit()


def get_gui_inputs():
    """Retrieve inputs from the GUI."""
    url = url_entry.get()
    total_pages = int(pages_entry.get()) - 1
    folder = folder_entry.get()
    volume_chapter = type_combobox.get()
    number = number_combobox.get()
    width = int(width_entry.get())
    height = int(height_entry.get())
    delay = delay_slider.get() / 1000  # Convert from milliseconds to seconds
    return url, total_pages, folder, volume_chapter, number, width, height, delay


def update_progress(current_page, total_pages):
    """Update the progress bar based on the current page."""
    progress_bar['value'] = (current_page / total_pages) * 100
    root.update_idletasks()


def browse_folder():
    """Open a folder dialog to select a download folder."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_selected)


# Tkinter GUI setup
root = tk.Tk()
root.title("Manga Downloader")

# GUI Elements
tk.Label(root, text="Enter URL:").grid(
    row=0, column=0, padx=5, pady=5, sticky=tk.W)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Total Pages:").grid(
    row=1, column=0, padx=5, pady=5, sticky=tk.W)
pages_entry = tk.Entry(root, width=10)
pages_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Download Folder:").grid(
    row=2, column=0, padx=5, pady=5, sticky=tk.W)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_folder).grid(
    row=2, column=2, padx=5, pady=5)

tk.Label(root, text="Type:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
type_combobox = ttk.Combobox(root, width=10, values=["Volume", "Chapter"])
type_combobox.grid(row=3, column=1, padx=5, pady=5)
type_combobox.current(0)

tk.Label(root, text="Volume/Chapter Number:").grid(row=4,
                                                   column=0, padx=5, pady=5, sticky=tk.W)
number_combobox = ttk.Combobox(root, width=10, values=[
                               str(i) for i in range(1, 101)])
number_combobox.grid(row=4, column=1, padx=5, pady=5)
number_combobox.current(0)

tk.Label(root, text="Window Width:").grid(
    row=5, column=0, padx=5, pady=5, sticky=tk.W)
width_entry = tk.Entry(root, width=10)
width_entry.grid(row=5, column=1, padx=5, pady=5)
width_entry.insert(0, "1450")

tk.Label(root, text="Window Height:").grid(
    row=6, column=0, padx=5, pady=5, sticky=tk.W)
height_entry = tk.Entry(root, width=10)
height_entry.grid(row=6, column=1, padx=5, pady=5)
height_entry.insert(0, "1934")

tk.Label(root, text="Delay between 'Next' clicks (ms):").grid(
    row=7, column=0, padx=5, pady=5, sticky=tk.W)
delay_slider = tk.Scale(root, from_=0, to=2000,
                        orient="horizontal", length=200)
delay_slider.grid(row=7, column=1, padx=5, pady=5)
delay_slider.set(100)

progress_bar = ttk.Progressbar(
    root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=8, column=0, columnspan=3, pady=10)

start_button = tk.Button(root, text="Start Download",
                         command=start_download, bg="green", fg="white")
start_button.grid(row=9, column=0, columnspan=3, pady=10)

root.mainloop()
