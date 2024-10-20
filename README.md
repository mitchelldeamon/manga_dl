# Manga Downloader Automation

This Python project automates the process of downloading manga pages
from a given URL, capturing screenshots, and saving them in a designated
folder. The project includes a Tkinter-based GUI for user input and progress tracking.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [How to Run](#how-to-run)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Additional Notes](#additional-notes)
- [License](#license)

## Prerequisites

1. Python 3.7+ - Make sure Python is installed on your system.
2. Git - Required to clone the repository.
3. Chrome Browser - Required for web scraping and automation.
4. ChromeDriver - Use `webdriver_manager` to automate Chrome installation.
5. Tkinter - A built-in Python library for GUI development.
6. dotenv - For loading environment variables.

## Setup

### 1. Clone the Repository

Clone the repository to your local machine:

`git clone https://github.com/mitchelldeamon/manga_dl.git`

`cd manga_dl`

### 2. Create a Virtual Environment

It is recommended to use a virtual environment:

`python -m venv .venv`

Activate the virtual environment:

- On Windows: `.venv\Scripts\activate`
- On macOS/Linux: `source .venv/bin/activate`

### 3. Install the Requirements

Install the required dependencies using the `requirements.txt` file:

`pip install -r requirements.txt`

### 4. Create `.crx`

1. Unzip `uBlock0_1.60.0.chromium.zip`
2. Double click and enter `uBlock0_1.60.0.chromium`
3. Using that folder, open chrome and go to `chrome://extensions/`
4. Click `Load unpacked` and select `uBlock0_1.60.0.chromium`
5. Under `All Extension` find `uBlock Origin 1.60.0`
6. Click `Details`
7. Click `Pack Extension`
8. Choose the same directory as `uBlock0_1.60.0.chromium`
9. Close Chrome (You can remove the extension now if you want)
10. This creates a `uBlock0_1.60.0.chromium\uBlock0.chromium.crx` that you will use for the `path_to_adblock_extension`

### 5. Set Up Environment Variables

Create a `.env` file in the project directory to store your environment variables:

`ADBLOCK_PATH=path_to_adblock_extension`

- Replace `path_to_adblock_extension` with the full path to your AdBlock extension file.

### 6. Verify ChromeDriver Installation

Ensure that ChromeDriver is correctly installed and matches the installed version of Chrome:

`pip install webdriver-manager`

## How to Run

To run the automation script, execute the following command:

`python manga_downloader.py`

## How It Works

### 1. Launch GUI:

- The script launches a Tkinter-based GUI for user input, where you can enter the URL, set the number of pages, select the download folder, and configure window dimensions and delay settings.

### 2. Start the Download:

- When you click 'Start Download', the script initializes a Chrome WebDriver, navigates to the specified URL, and sets the page view to 'Horizontal Follow'.

### 3. Capture and Save Screenshots:

- The script captures screenshots of the specified number of manga pages, saving them in the chosen folder.

### 4. Update Progress:

- A progress bar in the GUI updates as the download progresses, and a message is displayed upon completion.

### 5. Navigate to the Next Page:

- The script clicks the 'Next' button to proceed to the next page, capturing a screenshot of each page in sequence.

## Troubleshooting

- Issue: Chrome not launching properly.
  Solution: Ensure that Chrome and ChromeDriver are installed and their versions match.

- Issue: Environment variable 'ADBLOCK_PATH' is not set.
  Solution: Check if the `.env` file is correctly set up and located in the project directory.

- Issue: GUI not displaying properly.
  Solution: Ensure Tkinter is installed and functioning correctly on your system.

- Issue: Errors related to ChromeDriver version.
  Solution: Reinstall ChromeDriver using `webdriver_manager` to match your Chrome version.

## Additional Notes

- Security: Avoid sharing your `.env` file publicly, as it contains sensitive information like the path to your ad-blocker extension.
- GUI Responsiveness: The GUI may become unresponsive during the download process due to long-running operations.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
