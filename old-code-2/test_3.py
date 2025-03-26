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


def extract_url_info(url):
    """Extract content type and number from the URL."""
    url_parts = url.split('/')
    last_segment = url_parts[-1]  # e.g., "chapter-12"
    if "chapter" in last_segment:
        content_type = "chapter"
    elif "volume" in last_segment:
        content_type = "volume"
    else:
        raise ValueError("Could not determine content type from URL.")

    try:
        number = int(last_segment.split('-')[-1])  # Extract number as integer
    except ValueError:
        raise ValueError(f"Invalid number in URL segment: {last_segment}")
    base_url = '/'.join(url_parts[:-1])  # Everything before the last segment
    print(
        f"Extracted: type={content_type}, number={number}, base_url={base_url}")
    return content_type, number, base_url


def generate_next_url(base_url, content_type, current_number):
    """Generate the URL for the next chapter or volume."""
    next_number = current_number + 1
    next_url = f"{base_url}/{content_type}-{next_number}"
    print(
        f"Generated next URL: {next_url} (from number {current_number} to {next_number})")
    return next_url


def get_total_pages(driver):
    """Extract the total number of pages from the webpage."""
    try:
        # First attempt: Use the original class name with increased timeout
        page_count_element = wait_for_element(
            driver, By.CLASS_NAME, "hoz-total-image", timeout=30)
        if page_count_element is None:
            print("Falling back to CSS selector due to missing 'hoz-total-image'.")
            # Fallback: Use provided CSS selector
            page_count_element = wait_for_element(
                driver,
                By.CSS_SELECTOR,
                "div.navi-buttons:nth-child(3) > div:nth-child(2) > span:nth-child(1) > span:nth-child(2)",
                timeout=30
            )
            if page_count_element is None:
                raise ValueError(
                    "Failed to locate page count element using both class and CSS selector.")

        total_pages = int(page_count_element.text)
        if total_pages <= 0:
            raise ValueError(f"Invalid page count ({total_pages}) detected.")
        print(f"Extracted total pages: {total_pages}")
        return total_pages
    except Exception as e:
        print(f"Error extracting total pages: {e}")
        raise  # Re-raise to be handled by the caller


def is_404_page(driver):
    """Check if the current page is a 404 error page."""
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(), '404')]"))
        )
        print("404 error page detected.")
        return True
    except Exception:
        return False


def navigate_and_prepare(driver, url):
    """Navigate to the URL and prepare the page for screenshot capture."""
    try:
        driver.get(url)
        time.sleep(2)  # Wait for initial load
        if is_404_page(driver):
            return False
        wait_for_element(driver, By.XPATH,
                         "//div[text()='Horizontal Follow']", click=True)
        print("Navigated and set to 'Horizontal Follow' view.")
        return True
    except Exception as e:
        print(f"Navigation error: {e}")
        return False


def preload_all_pages(driver, total_pages):
    """Quickly click through all pages to load them, stopping before the last click."""
    try:
        for _ in range(total_pages - 2):  # -2 to account for starting on page 1
            next_button = wait_for_element(
                driver, By.CSS_SELECTOR, "a.nabu.nabu-left.hoz-next", 1, click=True)
            if not next_button:
                print("Could not find next button during preload")
                break
            time.sleep(0.1)  # Minimal delay during preload
        print("Completed preloading all pages")
    except Exception as e:
        print(f"Error during page preloading: {e}")


def capture_and_save_screenshot(element, folder, page_number, total_pages):
    """Capture a screenshot of the given element and save it with zero-padded numbering."""
    padded_page_number = f"{page_number:03d}"  # Assumes max 999 pages
    filename = os.path.join(folder, f"{padded_page_number}.jpg")
    os.makedirs(folder, exist_ok=True)
    try:
        element.screenshot(filename)
        print(f"Screenshot saved: {filename}")
    except Exception as e:
        print(f"Error capturing screenshot: {e}")


def process_page_reverse(driver, folder, page_number, total_pages, delay):
    """Capture screenshot of the current page and click 'Prev' to go back."""
    active_container = wait_for_element(
        driver, By.CSS_SELECTOR, ".ds-item.active", 10)
    if active_container:
        image_element = active_container.find_element(
            By.CSS_SELECTOR, ".image-horizontal")
        capture_and_save_screenshot(
            image_element, folder, page_number, total_pages)
        time.sleep(delay)  # Delay before moving to the next (previous) page
        prev_button = wait_for_element(
            driver, By.CSS_SELECTOR, "a.nabu.nabu-right.hoz-prev", 1, click=True)
        if prev_button:
            print(f"Captured page {page_number} and moved to previous page.")
        else:
            print(f"Failed to navigate back from page {page_number}.")


def download_chapter(driver, url, folder, content_type, number, delay):
    """Download all pages for a single chapter or volume."""
    download_folder = os.path.join(folder, f"{content_type.lower()}-{number}")
    if not navigate_and_prepare(driver, url):
        return False

    # Will raise an exception if page count fails
    total_pages = get_total_pages(driver)
    preload_all_pages(driver, total_pages)
    last_page_num = total_pages - 1
    process_page_reverse(driver, download_folder,
                         last_page_num, total_pages, delay)

    for page_num in range(total_pages - 2, 0, -1):
        process_page_reverse(driver, download_folder,
                             page_num, total_pages, delay)

    process_page_reverse(driver, download_folder, 1, total_pages, 0)
    return True


def start_download():
    """Start the download process for all manga chapters or volumes."""
    url, folder, width, height, delay = get_gui_inputs()
    content_type, number, base_url = extract_url_info(url)
    driver = create_driver(width, height)

    total_chapters_processed = 0
    current_number = number
    current_url = url

    while True:
        print(f"Processing {content_type} {current_number}: {current_url}")
        try:
            success = download_chapter(
                driver, current_url, folder, content_type, current_number, delay)
            if success:
                total_chapters_processed += 1
                current_number += 1  # Increment only on success
                current_url = generate_next_url(
                    base_url, content_type, current_number - 1)  # Pass previous number
            else:
                print(
                    f"Stopped at {content_type} {current_number} due to 404 or navigation failure.")
                break
        except Exception as e:
            print(
                f"Stopped at {content_type} {current_number} due to error: {e}")
            break

        update_progress(total_chapters_processed, total_chapters_processed + 1)

    messagebox.showinfo("Download Complete",
                        f"Captured {total_chapters_processed} {content_type}s.")
    driver.quit()


def get_gui_inputs():
    """Retrieve inputs from the GUI."""
    url = url_entry.get()
    folder = folder_entry.get()
    width = int(width_entry.get())
    height = int(height_entry.get())
    delay = delay_slider.get() / 1000  # Convert from milliseconds to seconds
    return url, folder, width, height, delay


def update_progress(current_step, total_steps):
    """Update the progress bar based on the current step."""
    progress_bar['value'] = (current_step / total_steps) * 100
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
root.geometry("500x300")  # Fixed size
root.resizable(False, False)  # Disable resizing

root.columnconfigure(1, weight=1)

tk.Label(root, text="Enter Starting URL:").grid(
    row=0, column=0, padx=5, pady=5, sticky=tk.W)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

tk.Label(root, text="Download Folder:").grid(
    row=1, column=0, padx=5, pady=5, sticky=tk.W)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
tk.Button(root, text="Browse", command=browse_folder).grid(
    row=1, column=2, padx=5, pady=5, sticky=tk.E)

tk.Label(root, text="Window Width:").grid(
    row=2, column=0, padx=5, pady=5, sticky=tk.W)
width_entry = tk.Entry(root, width=10)
width_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
width_entry.insert(0, "1450")

tk.Label(root, text="Window Height:").grid(
    row=3, column=0, padx=5, pady=5, sticky=tk.W)
height_entry = tk.Entry(root, width=10)
height_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
height_entry.insert(0, "1934")

tk.Label(root, text="Delay between 'Prev' clicks (ms):").grid(
    row=4, column=0, padx=5, pady=5, sticky=tk.W)
delay_slider = tk.Scale(root, from_=0, to=2000,
                        orient="horizontal", length=200)
delay_slider.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
delay_slider.set(100)

progress_bar = ttk.Progressbar(
    root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=5, column=0, columnspan=3, pady=10, sticky=tk.EW)

start_button = tk.Button(root, text="Start Download",
                         command=start_download, bg="green", fg="white")
start_button.grid(row=6, column=0, columnspan=3, pady=10)

root.mainloop()
