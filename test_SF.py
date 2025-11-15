import os
import logging
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as selenium_exceptions
import time
import tempfile


# Configure logging - 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)
logger = logging.getLogger(__name__)

developer_mode = True


# provide reusable driver fixture
# 提供可重用的 selenium driver 状态
# fixture can inject state into each test function
# 固定物件可以将状态注入到每个测试函数中
# Can be a generator that yields the state
@pytest.fixture(scope="function")
def driver():

    if not developer_mode:
        logger.info("🚀 Running in Standard Mode: Use official env configuration")

        service = Service(
            # 提交最终代码脚本时,请将驱动路径换回官方路径"C:\\Users\\86153\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver.exe"
            # change to offical path when submit the final code script
            executable_path="C:\\Users\\86153\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver.exe"
        )
        driver = webdriver.Chrome(service=service)

    # customize driver for my local environment
    # =======

    if developer_mode:
        logger.info("🚀 Running in Developer Mode: Use local env configuration")

        service = Service(executable_path="D:\\ChromeDriver\\chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.binary_location = "D:\\ChromeDriver\\chrome-win64\\chrome.exe"

        # hide webdriver env feature
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        )
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-web-security")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--no-sandbox")
        # options.add_argument("--start-maximized")
        options.add_argument("--window-size=1200,800")
        # options.add_argument("--user-data-dir=/dev/null")
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "useAutomationExtension"]
        )

        # temp user-data-dir
        # temp_profile = tempfile.mkdtemp()
        # options.add_argument(f"--user-data-dir={temp_profile}")
        # options.add_argument("--incognito")

        # new chrome
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")

        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
            },
        )

        # rebuild chrome env to new state
        # driver.delete_all_cookies()
        # driver.execute_script("window.localStorage.clear();")
        # driver.execute_script("window.sessionStorage.clear();")

    # =======

    driver.get("https://www.sf-express.com/")
    driver.maximize_window()
    driver.implicitly_wait(10)
    
    yield driver

    logger.info("Test complete, waiting for 4 seconds before closing the browser...")
    # sleep(4)
    # input("Press Enter to close the browser...")

    # exit driver when test is done
    driver.quit()


class TestBaiDuMap:


    # test-code-start

    # 请在此处插入Selenium+Pytest代码
    
    def waiting_for_page_load(self, driver, timeout=10):
        """Wait for the page to load completely.

        Args:
        driver (webdriver): The Selenium WebDriver instance.
        timeout (int): Maximum time to wait for the page to load.
        """
        logger.info("waiting for page to load...")
        WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info("page load complete!")
    
    
    # test-code-end

    @staticmethod
    def take_screenshot(driver, file_name):
        timestamp = datetime.now().strftime("%H%M%S%d%f")[:-3]
        timestamped_file_name = f"{timestamp}_{file_name}"
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
        screenshot_file_path = os.path.join(screenshots_dir, timestamped_file_name)
        driver.save_screenshot(screenshot_file_path)