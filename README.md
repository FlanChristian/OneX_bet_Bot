# OneX_bet_Bot

Bet slip bot creator.

## 1xbet Scraper

### Introduction
This script allows you to scrape sports betting information from the 1xbet website. It utilizes Selenium, a powerful tool for automating web browsers, to extract data such as game names, dates, and links.

### Prerequisites
Before running the script, ensure you have the following installed on your computer:

- Python 3.x
- Selenium
- GeckoDriver (for Firefox)

You can install Selenium via pip:
```bash
pip install selenium
```

You can install GeckoDriver using the WebDriver Manager for Python:
```bash
pip install webdriver-manager
```

### Setup
1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Ensure you have Mozilla Firefox installed on your computer.
4. Download the GeckoDriver executable compatible with your Firefox version and operating system from the [official website](https://github.com/mozilla/geckodriver/releases).
5. Place the GeckoDriver executable in a directory that is included in your system's PATH environment variable, or specify the path to the executable in the script.

### Usage
1. Open a terminal or command prompt.
2. Navigate to the project directory.
3. Run the script using the following command: python testBot.py
4. Follow the prompts to interact with the script and scrape sports betting information from the 1xbet website.

### Notes
- By default, the script runs with Firefox in headless mode. You can uncomment the `options.add_argument("--headless")` line in the script if you want to run it in visible mode.
- Make sure to comply with the website's terms of service and use the script responsibly.

### Troubleshooting
If you encounter any issues, feel free to open an issue in this repository.
