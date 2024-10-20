from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Define the URL to be opened
url = "https://mangareader.to/read/look-back-55492/en/volume-1"

# Set up Chrome options
options = Options()
options.add_argument("--start-maximized")  # Open browser in maximized mode

# Initialize the Chrome WebDriver using the ChromeDriverManager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the URL
driver.get(url)

# Wait for the element with class "hoz-total-image" to be present
wait = WebDriverWait(driver, 20)

# Find the element with class "hoz-total-image" and retrieve its text
try:
    total_image_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hoz-total-image")))
    total_image_text = total_image_element.text
    print(f"Text inside element with class 'hoz-total-image': {total_image_text}")
except Exception as e:
    print(f"Error: {e}")

# Close the browser
driver.quit()
