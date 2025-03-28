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

# Constants
ADBLOCK_PATH = os.getenv('ADBLOCK_PATH')
if not ADBLOCK_PATH:
    raise ValueError(
        "Environment variable 'ADBLOCK_PATH' is not set or empty.")


def let_page_load():
    loading = time.sleep(10)
    return loading


def create_driver(window_width, window_height):
    """Initialize and return a Chrome WebDriver with specified options."""
    options = Options()
    options.add_extension(ADBLOCK_PATH)
    options.add_argument("--window-position=-40,-40")
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    driver.set_window_size(window_width, window_height)
    return driver


def wait_for_element(driver, by, value, timeout=2, click=False):
    """Wait for an element to be present and optionally click it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        # print(f"Element found: {element.get_attribute('outerHTML')}")

        if click:
            # Scroll the element into view before clicking to avoid interception
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", element)
            print("Scrolled to element")

            # try:
            #     element.click()  # Try a native click
            #     print("Native click successful")
            # except Exception as e:
            #     print(f"Native click failed: {e}")
            # Fallback to JS click
            driver.execute_script("arguments[0].click();", element)
            print("JavaScript click executed")

        return element
    except Exception as e:
        print(f"Error waiting for element {value}: {e}")
        return None


def extract_url_info(url):
    """Extract content type and number from the URL."""
    url_parts = url.split('/')
    last_segment = url_parts[-1]

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
    return content_type, number, base_url


def generate_next_url(base_url, content_type, current_number):
    """Generate the URL for the next chapter or volume."""
    next_number = current_number + 1
    return f"{base_url}/{content_type}-{next_number}"


def get_total_pages(driver):
    """Extract the total number of pages from the webpage."""

    print("loading page for 10 seconds")
    let_page_load()

    try:
        # Try to find the page count element using the first method
        page_count_element = wait_for_element(
            driver, By.CLASS_NAME, "hoz-total-image", timeout=2
        )

        if page_count_element is None:
            print("Falling back to alternate method due to missing 'hoz-total-image'.")

            # Fallback: Use an alternate method (CSS Selector or XPath)
            page_count_element = wait_for_element(
                driver,
                By.CSS_SELECTOR,
                "div.navi-buttons:nth-child(3) > div:nth-child(2) > span:nth-child(1) > span:nth-child(2)",
                timeout=2
            )
            if page_count_element is None:
                raise ValueError(
                    "Failed to locate page count element using both methods.")

        # Extract the total page count
        total_pages = int(page_count_element.text)

        if total_pages <= 0:
            raise ValueError(f"Invalid page count ({total_pages}) detected.")

        print(f"Extracted total pages: {total_pages}")
        return total_pages

    except Exception as e:
        print(f"Error extracting total pages: {e}")
        raise  # Re-raise the exception to be handled by the caller


def is_404_page(driver):
    """Check if the current page is a 404 error page."""
    try:
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[3]/div[4]/div/div/div[2]"))
        )
        return True
    except Exception:
        return False


def navigate_and_prepare(driver, url):
    """Navigate to the URL and prepare the page for screenshot capture."""
    driver.get(url)
    if is_404_page(driver):
        return False
    wait_for_element(driver, By.XPATH,
                     "//div[text()='Horizontal Follow']", click=True)
    return True


# def preload_all_pages(driver, total_pages):
#     """Cycle through all pages to ensure full preloading."""
#     try:
#         for _ in range(total_pages - 1):  # Forward cycle
#             next_button = wait_for_element(
#                 driver, By.CSS_SELECTOR, "a.nabu.nabu-left.hoz-next", timeout=2, click=True)
#             if not next_button:
#                 return False
#             time.sleep(0.1)

#         for _ in range(total_pages - 1):  # Backward cycle
#             prev_button = wait_for_element(
#                 driver, By.CSS_SELECTOR, "a.nabu.nabu-right.hoz-prev", timeout=2, click=True)
#             if not prev_button:
#                 return False
#             time.sleep(0.1)
#         return True
#     except Exception as e:
#         print(f"Error during page preloading: {e}")
#         return False


# this is something to do with the loading screen <iframe src="about:blank" style="position: absolute; width: 1px; height: 1px; display: none; opacity: 0;"></iframe>


def capture_and_save_screenshot(element, folder, page_number):
    """Capture a screenshot of the given element and save it with zero-padded numbering."""
    filename = os.path.join(folder, f"{page_number:03d}.jpg")
    os.makedirs(folder, exist_ok=True)
    try:
        time.sleep(3)
        element.screenshot(filename)
        print(f"Screenshot saved: {filename}")
    except Exception as e:
        print(f"Error capturing screenshot: {e}")


# def process_page_forward(driver, folder, page_number, total_pages, delay):
# def process_page_forward(driver, folder, page_number, total_pages):
#     """Capture screenshot and click 'Next' to move forward."""

#     # Debugging print statement to check which pages are being processed
#     print(f"Processing page: {page_number} / {total_pages - 1}")

#     # Ensure we do not take a duplicate screenshot on the last valid page
#     if page_number < total_pages:
#         active_container = wait_for_element(
#             driver, By.CSS_SELECTOR, ".ds-item.active", timeout=10
#         )

#         if active_container:
#             max_retries = 5
#             for attempt in range(max_retries):
#                 try:
#                     image_element = active_container.find_element(
#                         By.CSS_SELECTOR, ".image-horizontal"
#                     )
#                     capture_and_save_screenshot(
#                         image_element, folder, page_number)
#                     break  # Exit loop if element is found and screenshot is captured
#                 except Exception as e:
#                     if attempt < max_retries - 1:
#                         print(
#                             f"Retry {attempt + 1}/{max_retries} for '.image-horizontal'")
#                         driver.refresh()
#                         time.sleep(10)  # Brief delay before retrying
#                         continue
#                     else:
#                         print(
#                             f"Failed to locate '.image-horizontal' after {max_retries} attempts: {str(e)}")
#                         input("Pausing for debugging. Press Enter to continue...")
#                         raise Exception(
#                             f"Failed to locate '.image-horizontal' after {max_retries} attempts: {str(e)}")

#             # Only click "Next" if we are NOT on the last valid page
#             if page_number < total_pages - 1:
#                 next_button = wait_for_element(
#                     driver, By.CSS_SELECTOR, "a.nabu.nabu-left.hoz-next", timeout=1, click=True
#                 )


def process_page_forward(driver, folder, page_number, total_pages):
    """Capture screenshot and click 'Next' to move forward."""
    print(f"Processing page: {page_number} / {total_pages - 1}")

    if page_number < total_pages:
        max_retries = 5
        same_page_retries = 0  # Track how many times we retry on the same page
        last_url = driver.current_url  # Store the initial page URL

        for attempt in range(max_retries):
            try:
                # Ensure the active container is loaded
                active_container = wait_for_element(
                    driver, By.CSS_SELECTOR, ".ds-item.active", timeout=10
                )

                if not active_container:
                    raise Exception("Active container not found.")

                # Now check for the image element inside the container
                image_element = active_container.find_element(
                    By.CSS_SELECTOR, ".image-horizontal"
                )
                if not image_element:
                    raise Exception("Image element not found.")

                capture_and_save_screenshot(image_element, folder, page_number)
                break  # Successfully captured the screenshot, exit retry loop

            except Exception as e:
                if attempt < max_retries - 1:
                    print(
                        f"Retry {attempt + 1}/{max_retries} for '.image-horizontal'")

                    # **Check if we are stuck on the same page**
                    current_url = driver.current_url
                    if current_url == last_url:
                        same_page_retries += 1
                    else:
                        same_page_retries = 0  # Reset if page actually changes

                    if same_page_retries >= 3:  # If stuck, log error and break
                        print(
                            "Detected repeated retries on the same page. Moving forward.")
                        break
                    time.sleep(5)
                    driver.refresh()
                    time.sleep(5)  # Short pause to allow the refresh

                    # **Wait again for the content to load**
                    wait_for_element(driver, By.CSS_SELECTOR,
                                     ".ds-item.active", timeout=15)
                    time.sleep(3)  # Additional buffer to ensure stability
                else:
                    print(
                        f"Failed to locate '.image-horizontal' after {max_retries} attempts: {str(e)}")
                    input("Pausing for debugging. Press Enter to continue...")
                    raise Exception(
                        f"Failed to locate '.image-horizontal' after {max_retries} attempts: {str(e)}")

        # Click "Next" if not on the last page
        if page_number < total_pages - 1:
            next_button = wait_for_element(
                driver, By.CSS_SELECTOR, "a.nabu.nabu-left.hoz-next", timeout=5, click=True
            )


# def download_chapter(driver, url, folder, content_type, number, delay):


def download_chapter(driver, url, folder, content_type, number):
    """Download all pages for a single chapter or volume."""
    formatted_number = f"{int(number):03d}"
    download_folder = os.path.join(
        folder, f"{content_type.lower()}-{formatted_number}")
    if not navigate_and_prepare(driver, url):
        return False

    total_pages = get_total_pages(driver)
    # if not preload_all_pages(driver, total_pages):
    #     return False

    for page_num in range(1, total_pages):
        process_page_forward(driver, download_folder,
                             #  page_num, total_pages, delay)
                             page_num, total_pages)

    return True


def start_download():
    """Start the download process for all manga chapters or volumes."""
    # url, folder, width, height, delay = get_gui_inputs()
    url, folder, width, height = get_gui_inputs()
    content_type, number, base_url = extract_url_info(url)
    driver = create_driver(width, height)

    total_chapters_processed = 0
    current_number = number
    current_url = url

    while True:
        print(f"Processing {content_type} {current_number}: {current_url}")
        try:
            success = download_chapter(
                # driver, current_url, folder, content_type, current_number, delay)
                driver, current_url, folder, content_type, current_number)
            if success:
                total_chapters_processed += 1
                current_number += 1
                current_url = generate_next_url(
                    base_url, content_type, current_number - 1)
            else:
                print(
                    f"Stopped at {content_type} {current_number} due to failure.")
                break
        except Exception as e:
            print(f"Error occurred at {content_type} {current_number}: {e}")
            break

        # update_progress(total_chapters_processed, total_chapters_processed + 1)

    messagebox.showinfo("Download Complete",
                        f"Captured {total_chapters_processed} {content_type}s.")
    driver.quit()


def get_gui_inputs():
    """Retrieve inputs from the GUI."""
    url = url_entry.get()
    folder = folder_entry.get()
    width = int(width_entry.get())
    height = int(height_entry.get())
    # delay = delay_slider.get() / 1000
    # return url, folder, width, height, delay
    return url, folder, width, height


# def update_progress(current_step, total_steps):
#     """Update the progress bar based on the current step."""
#     progress_bar['value'] = (current_step / total_steps) * 25
#     root.update_idletasks()


def browse_folder():
    """Open a folder dialog to select a download folder."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_selected)


# Tkinter GUI setup
root = tk.Tk()
root.title("Manga Downloader")
root.geometry("500x175")  # Fixed size
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

# Corrected placement of Browse button
browse_button = tk.Button(root, text="Browse", command=browse_folder)
browse_button.grid(row=1, column=2, padx=5, pady=5, sticky=tk.E)

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

# tk.Label(root, text="Delay between 'Next' clicks (ms):").grid(
#     row=4, column=0, padx=5, pady=5, sticky=tk.W)
# delay_slider = tk.Scale(root, from_=0, to=2000,
#                         orient="horizontal", length=200)
# delay_slider.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
# delay_slider.set(100)

# progress_bar = ttk.Progressbar(
#     root, orient="horizontal", length=400, mode="determinate")
# progress_bar.grid(row=5, column=0, columnspan=3, pady=10, sticky=tk.EW)

start_button = tk.Button(root, text="Start Download",
                         command=start_download, bg="green", fg="white")
start_button.grid(row=6, column=0, columnspan=3, pady=10)

root.mainloop()
