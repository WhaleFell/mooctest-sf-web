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


class TestSF:

    # test-code-start

    # 请在此处插入Selenium+Pytest代码

    def waiting_for_page_load(self, driver, timeout=10):
        """Wait for the page to load completely - 等待页面完全加载

        Args:
        driver (webdriver): The Selenium WebDriver instance.
        timeout (int): Maximum time to wait for the page to load.
        """
        logger.info("waiting for page to load...")
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logger.info("page load complete!")

    def agree_cookie_policy(self, driver):
        """Agree to the cookie policy on the website - 同意网站的cookie政策

        Args:
            driver (webdriver): The Selenium WebDriver instance.
        """
        try:
            logger.info("Agreeing to cookie policy...")
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div/section[1]/div/div/div[2]/div[2]")
                )
            )
            cookie_button.click()
            logger.info("Cookie policy agreed successfully.")
        except selenium_exceptions.TimeoutException:
            logger.warning("Cookie policy button not found or not clickable.")
        except Exception as e:
            logger.error(f"Error while agreeing to cookie policy: {str(e)}")

    @pytest.mark.parametrize(
        "origin_city,origin_district,origin_detail,destination_city,destination_district,destination_detail,case_id",
        [
            (
                "广州市",
                "黄埔区",
                "黄埔东苑",
                "南京市",
                "鼓楼区",
                "南京大学",
                "SF_R001_001",
            ),
            (
                "南京市",
                "鼓楼区",
                "南京大学",
                "广州市",
                "黄埔区",
                "黄埔东苑",
                "SF_R001_002",
            ),
        ],
    )
    def test_SF_R001(
        self,
        driver,
        origin_city,
        origin_district,
        origin_detail,
        destination_city,
        destination_district,
        destination_detail,
        case_id,
    ):
        """Test SF R001: Freight timeliness query function
        测试顺丰 R001：运费时效查询功能

        Test steps - 测试步骤:
        1. Click service support button - 点击服务支持按钮
        2. Navigate to freight timeliness page - 进入运费时效页面
        3. Input origin information - 输入始发地信息
        4. Input destination information - 输入目的地信息
        5. Input package dimensions and weight - 输入包裹尺寸和重量
        6. Select send date - 选择寄件日期
        7. Click query button - 点击查询按钮
        8. Take screenshot of results - 截图保存结果
        """
        self.waiting_for_page_load(driver)
        self.agree_cookie_policy(driver)

        # XPath dictionary for element locators - XPath 元素定位器字典
        # 等待人工填充 - Waiting for manual filling
        XPATHS = {
            "service_support_button": '//a[text()="服务支持"]',  # 服务支持按钮
            "freight_timeliness_menu": '//li[contains(text(), "运费时效")]',  # 运费时效菜单
            "origin_select_box": '//*[@id="origion"]/div[1]/div/div[1]',  # 始发地选择框
            # 输入城市 (比如广州市)
            "origin_input": '//*[@id="origincityPicker"]/div[2]/input',  # 始发地输入框
            "origin_district_option": '//div[@class="address-name" and contains(., "{district}")]',  # 始发地地区选项（需要动态替换地区名）
            "origin_detail_address": '//*[@id="origion"]/div/div/div[2]/figure/input',  # 始发地详细地址输入框
            "destination_select_box": '//*[@id="dests"]/div/div/div[1]',  # 目的地选择框
            "destination_input": '//*[@id="destsCityPicker"]/div[2]/input',  # 目的地输入框 输入城市
            "destination_district_option": '//div[@class="address-name" and contains(., "{district}")]',  # 目的地地区选项（需要动态替换地区名）
            "destination_detail_address": '//*[@id="dests"]/div/div/div[2]/figure/input',  # 目的地详细地址输入框
            "weight_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[3]/figure/div/input',  # 重量输入框
            "length_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[4]/figure/div/div[1]/input',  # 长度输入框
            "width_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[4]/figure/div/div[2]/input',  # 宽度输入框
            "height_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[4]/figure/div/div[3]/input',  # 高度输入框
            "send_time_control": '//*[@id="datetime"]/div/div[2]/input',  # 寄件时间控件
            "date_16_option": "/html/body/div[7]/div[1]/div/div[3]/table[1]/tbody/tr[5]/td[1]",  # 日期16选项
            "confirm_button": "/html/body/div[7]/div[2]/button[2]",  # 确定按钮
            "query_button": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[2]/button',  # 查询按钮
        }

        wait_time = 2

        try:
            logger.info(f"开始执行测试用例: {case_id}")
            logger.info(
                f"测试参数 - 始发地: {origin_city} {origin_district} {origin_detail}, "
                f"目的地: {destination_city} {destination_district} {destination_detail}"
            )

            # Step 1: Click service support button - 点击【服务支持】按钮
            logger.info("Step 1: 点击【服务支持】按钮")
            service_support_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["service_support_button"]))
            )
            service_support_btn.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 2: Click freight timeliness menu - 点击【运费时效】菜单
            logger.info("Step 2: 点击左侧菜单栏的【运费时效】")
            freight_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, XPATHS["freight_timeliness_menu"])
                )
            )
            freight_menu.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 3: Input origin information - 输入始发地信息
            logger.info(f"Step 3: 输入始发地信息 - {origin_city} {origin_district}")
            origin_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["origin_select_box"]))
            )
            origin_box.click()
            time.sleep(wait_time)

            origin_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["origin_input"]))
            )
            origin_input.clear()
            origin_input.send_keys(origin_city)
            time.sleep(wait_time)

            origin_district_xpath = XPATHS["origin_district_option"].replace(
                "{district}", origin_district
            )
            origin_district_elem = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, origin_district_xpath))
            )
            origin_district_elem.click()
            time.sleep(wait_time)

            origin_detail_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, XPATHS["origin_detail_address"])
                )
            )
            origin_detail_input.clear()
            origin_detail_input.send_keys(origin_detail)
            time.sleep(wait_time)

            # Step 4: Input destination information - 输入目的地信息
            logger.info(
                f"Step 4: 输入目的地信息 - {destination_city} {destination_district}"
            )
            dest_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["destination_select_box"]))
            )
            dest_box.click()
            time.sleep(wait_time)

            dest_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["destination_input"]))
            )
            dest_input.clear()
            dest_input.send_keys(destination_city)
            time.sleep(wait_time)

            dest_district_xpath = XPATHS["destination_district_option"].replace(
                "{district}", destination_district
            )
            dest_district_elem = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, dest_district_xpath))
            )
            dest_district_elem.click()
            time.sleep(wait_time)

            dest_detail_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, XPATHS["destination_detail_address"])
                )
            )
            dest_detail_input.clear()
            dest_detail_input.send_keys(destination_detail)
            time.sleep(wait_time)

            # Step 5: Input package dimensions and weight - 输入包裹尺寸和重量
            logger.info("Step 5: 输入重量和体积信息")
            weight_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["weight_input"]))
            )
            weight_input.clear()
            weight_input.send_keys("5")
            time.sleep(wait_time)

            length_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["length_input"]))
            )
            length_input.clear()
            length_input.send_keys("20")
            time.sleep(wait_time)

            width_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["width_input"]))
            )
            width_input.clear()
            width_input.send_keys("15")
            time.sleep(wait_time)

            height_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["height_input"]))
            )
            height_input.clear()
            height_input.send_keys("25")
            time.sleep(wait_time)

            # Step 6: Select send date - 选择寄件日期
            logger.info("Step 6: 选择寄件日期为16号")
            time_control = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["send_time_control"]))
            )
            time_control.click()
            time.sleep(wait_time)

            date_16 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["date_16_option"]))
            )
            date_16.click()
            time.sleep(wait_time)

            confirm_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["confirm_button"]))
            )
            confirm_btn.click()
            time.sleep(wait_time)

            # Step 7: Click query button - 点击查询按钮
            logger.info("Step 7: 点击【查询】按钮")
            query_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["query_button"]))
            )
            query_btn.click()
            time.sleep(wait_time)
            time.sleep(2)

            # Step 8: Take screenshot - 截图保存查询结果
            logger.info(f"Step 8: 截图保存查询结果 - {case_id}")
            self.take_screenshot(driver, f"{case_id}.png")

            logger.info(f"✅ 测试用例 {case_id} 执行完成")

        except selenium_exceptions.TimeoutException as e:
            logger.error(f"❌ 超时异常: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise
        except Exception as e:
            logger.error(f"❌ 测试执行失败: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise

    def test_SF_R002(self, driver):
        """Test SF R002: Freight timeliness query from Hong Kong to Nanjing
        测试顺丰 R002：香港到南京的运费时效查询功能

        Test steps - 测试步骤:
        1. Click service support button - 点击服务支持按钮
        2. Navigate to freight timeliness page - 进入运费时效页面
        3. Select origin: Hong Kong - Kowloon City - 选择始发地：香港-九龙城区
        4. Select destination: Nanjing - Gulou District - 选择目的地：南京-鼓楼区
        5. Input package dimensions and weight - 输入包裹尺寸和重量
        6. Click "Now" button for send time - 点击寄件时间【此刻】按钮
        7. Click query button - 点击查询按钮
        8. Scroll to express product section and take screenshot - 滚动到快递产品区域并截图
        """
        self.waiting_for_page_load(driver)
        self.agree_cookie_policy(driver)

        # XPath dictionary for element locators - XPath 元素定位器字典
        # 等待人工填充 - Waiting for manual filling
        XPATHS = {
            "service_support_button": '//a[text()="服务支持"]',  # 服务支持按钮
            "freight_timeliness_menu": '//li[contains(text(), "运费时效")]',  # 运费时效菜单
            "origin_select_box": '//*[@id="origion"]/div[1]/div/div[1]',  # 始发地选择框
            "hk_macau_taiwan_tab": '//*[@id="origincityPicker"]/div[1]/ul/li[2]',  # 港澳台标签
            "hongkong_option": '//*[@id="origincityPicker"]/div[3]/div[2]/ul/li[2]/span',  # 香港选项
            "kowloon_city_district": '//*[@id="origincityPicker"]/div[3]/div[2]/ul/li[6]',  # 九龙城区选项
            "destination_select_box": '//*[@id="dests"]/div[1]/div/div[1]',  # 目的地选择框
            # 点击热门城市
            "hot_city": '//*[@id="destsCityPicker"]/div[3]/div[1]/ul/li[1]',
            "hot_city_nanjing": '//*[@id="destsCityPicker"]/div[3]/div[2]/ul/li[8]',  # 热门城市南京选项
            "gulou_district": '//*[@id="destsCityPicker"]/div[3]/div[2]/ul/li[4]',  # 鼓楼区选项
            "weight_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[3]/figure/div/input',  # 重量输入框
            "length_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[4]/figure/div/div[1]/input',  # 长度输入框
            "width_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[4]/figure/div/div[2]/input',  # 宽度输入框
            "height_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[4]/figure/div/div[3]/input',  # 高度输入框
            "send_time_control": '//*[@id="datetime"]/div/div[2]/input',  # 寄件时间控件
            "send_time_now_button": "/html/body/div[7]/div[2]/button[1]",  # 寄件时间【此刻】按钮
            "query_button": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[2]/button',  # 查询按钮
            "express_product_section": '//*[@id="chn"]/div/div[2]/div/div[2]/div[2]',  # 快递产品区域
        }

        wait_time = 2
        case_id = "SF_R002_001"

        try:
            logger.info(f"开始执行测试用例: {case_id}")
            logger.info("测试参数 - 始发地: 香港 九龙城区, 目的地: 南京市 鼓楼区")

            # Step 1: Click service support button - 点击【服务支持】按钮
            logger.info("Step 1: 点击【服务支持】按钮")
            service_support_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["service_support_button"]))
            )
            service_support_btn.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 2: Click freight timeliness menu - 点击【运费时效】菜单
            logger.info("Step 2: 点击左侧菜单栏的【运费时效】")
            freight_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, XPATHS["freight_timeliness_menu"])
                )
            )
            freight_menu.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 3: Select origin - Hong Kong, Kowloon City - 选择始发地：香港-九龙城区
            logger.info("Step 3: 选择始发地 - 香港 九龙城区")
            origin_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["origin_select_box"]))
            )
            origin_box.click()
            time.sleep(wait_time)

            # Click Hong Kong Macau Taiwan tab - 点击【港澳台】
            logger.info("点击【港澳台】标签")
            hk_macau_taiwan = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["hk_macau_taiwan_tab"]))
            )
            hk_macau_taiwan.click()
            time.sleep(wait_time)

            # Click Hong Kong - 点击香港
            logger.info("点击香港")
            hongkong = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["hongkong_option"]))
            )
            hongkong.click()
            time.sleep(wait_time)

            # Click Kowloon City District - 点击九龙城区
            logger.info("点击九龙城区")
            kowloon_city = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["kowloon_city_district"]))
            )
            kowloon_city.click()
            time.sleep(wait_time)

            # Step 4: Select destination - Nanjing, Gulou District - 选择目的地：南京-鼓楼区
            logger.info("Step 4: 选择目的地 - 南京市 鼓楼区")
            dest_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["destination_select_box"]))
            )
            dest_box.click()
            time.sleep(wait_time)

            # Click hot city Nanjing - 点击热门城市的南京市
            logger.info("点击热门城市的【南京市】")
            nanjing = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["hot_city_nanjing"]))
            )
            nanjing.click()
            time.sleep(wait_time)

            # Click Gulou District - 点击鼓楼区
            logger.info("点击鼓楼区")
            gulou = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["gulou_district"]))
            )
            gulou.click()
            time.sleep(wait_time)

            # Step 5: Input package dimensions and weight - 输入包裹尺寸和重量
            logger.info("Step 5: 输入重量和体积信息")
            weight_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["weight_input"]))
            )
            weight_input.clear()
            weight_input.send_keys("5")
            time.sleep(wait_time)

            length_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["length_input"]))
            )
            length_input.clear()
            length_input.send_keys("20")
            time.sleep(wait_time)

            width_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["width_input"]))
            )
            width_input.clear()
            width_input.send_keys("15")
            time.sleep(wait_time)

            height_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["height_input"]))
            )
            height_input.clear()
            height_input.send_keys("25")
            time.sleep(wait_time)

            # Step 6: Click send time control and then click "Now" button
            # 点击寄件时间控件，然后点击【此刻】按钮
            logger.info("Step 6: 点击寄件时间控件")
            time_control = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["send_time_control"]))
            )
            time_control.click()
            time.sleep(wait_time)

            logger.info("点击【此刻】按钮")
            now_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["send_time_now_button"]))
            )
            now_button.click()
            time.sleep(wait_time)

            # Step 7: Click query button - 点击查询按钮
            logger.info("Step 7: 点击【查询】按钮")
            query_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["query_button"]))
            )
            query_btn.click()
            time.sleep(wait_time)
            time.sleep(2)

            # Step 8: Scroll to express product section and take screenshot
            # 滚动到快递产品区域并截图
            logger.info("Step 8: 滚动到快递产品区域")
            express_product = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, XPATHS["express_product_section"])
                )
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", express_product)
            time.sleep(wait_time)

            logger.info(f"截图保存查询结果 - {case_id}")
            self.take_screenshot(driver, f"{case_id}.png")

            logger.info(f"✅ 测试用例 {case_id} 执行完成")

        except selenium_exceptions.TimeoutException as e:
            logger.error(f"❌ 超时异常: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise
        except Exception as e:
            logger.error(f"❌ 测试执行失败: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise

    def test_SF_R003(self, driver):
        """Test SF R003: Freight timeliness query from Hong Kong to Nanjing with custom datetime
        测试顺丰 R003：香港到南京的运费时效查询功能（自定义日期时间）

        Test steps - 测试步骤:
        1. Click service support button - 点击服务支持按钮
        2. Navigate to freight timeliness page - 进入运费时效页面
        3. Select origin: Hong Kong - Kowloon City - 选择始发地：香港-九龙城区
        4. Select destination: Nanjing - Gulou District - 选择目的地：南京-鼓楼区
        5. Input weight only (no dimensions) - 仅输入重量（不输入体积）
        6. Input custom send date and time - 输入自定义寄件日期和时间
        7. Click query button - 点击查询按钮
        8. Scroll to express product section and take screenshot - 滚动到快递产品区域并截图
        """
        self.waiting_for_page_load(driver)
        self.agree_cookie_policy(driver)

        # XPath dictionary for element locators - XPath 元素定位器字典
        # 复用已有的 XPATH - Reuse existing XPATHs
        XPATHS = {
            "service_support_button": '//a[text()="服务支持"]',  # 服务支持按钮
            "freight_timeliness_menu": '//li[contains(text(), "运费时效")]',  # 运费时效菜单
            "origin_select_box": '//*[@id="origion"]/div[1]/div/div[1]',  # 始发地选择框
            "hk_macau_taiwan_tab": '//*[@id="origincityPicker"]/div[1]/ul/li[2]',  # 港澳台标签
            "hongkong_option": '//*[@id="origincityPicker"]/div[3]/div[2]/ul/li[2]/span',  # 香港选项
            "kowloon_city_district": '//*[@id="origincityPicker"]/div[3]/div[2]/ul/li[6]',  # 九龙城区选项
            "destination_select_box": '//*[@id="dests"]/div[1]/div/div[1]',  # 目的地选择框
            "hot_city_nanjing": '//*[@id="destsCityPicker"]/div[3]/div[2]/ul/li[8]',  # 热门城市南京选项
            "gulou_district": '//*[@id="destsCityPicker"]/div[3]/div[2]/ul/li[4]',  # 鼓楼区选项
            "weight_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[3]/figure/div/input',  # 重量输入框
            "send_time_control": '//*[@id="datetime"]/div/div[2]/input',  # 寄件时间控件
            "date_input": "/html/body/div[7]/div[1]/div/div[1]/span[1]/div/input",  # 日期输入框
            "time_input": "/html/body/div[7]/div[1]/div/div[1]/span[2]/div[1]/input",  # 时间输入框
            "confirm_button": "/html/body/div[7]/div[2]/button[2]",  # 确定按钮
            "query_button": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[2]/button',  # 查询按钮
            "express_product_section": '//*[@id="chn"]/div/div[2]/div/div[2]/div[2]',  # 快递产品区域
        }

        wait_time = 2
        case_id = "SF_R003_001"

        try:
            logger.info(f"开始执行测试用例: {case_id}")
            logger.info(
                "测试参数 - 始发地: 香港 九龙城区, 目的地: 南京市 鼓楼区, 重量: 100, 日期时间: 2025-11-17 15:00:00"
            )

            # Step 1: Click service support button - 点击【服务支持】按钮
            logger.info("Step 1: 点击【服务支持】按钮")
            service_support_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["service_support_button"]))
            )
            service_support_btn.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 2: Click freight timeliness menu - 点击【运费时效】菜单
            logger.info("Step 2: 点击左侧菜单栏的【运费时效】")
            freight_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, XPATHS["freight_timeliness_menu"])
                )
            )
            freight_menu.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 3: Select origin - Hong Kong, Kowloon City - 选择始发地：香港-九龙城区
            logger.info("Step 3: 选择始发地 - 香港 九龙城区")
            origin_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["origin_select_box"]))
            )
            origin_box.click()
            time.sleep(wait_time)

            # Click Hong Kong Macau Taiwan tab - 点击【港澳台】
            logger.info("点击【港澳台】标签")
            hk_macau_taiwan = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["hk_macau_taiwan_tab"]))
            )
            hk_macau_taiwan.click()
            time.sleep(wait_time)

            # Click Hong Kong - 点击香港
            logger.info("点击香港")
            hongkong = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["hongkong_option"]))
            )
            hongkong.click()
            time.sleep(wait_time)

            # Click Kowloon City District - 点击九龙城区
            logger.info("点击九龙城区")
            kowloon_city = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["kowloon_city_district"]))
            )
            kowloon_city.click()
            time.sleep(wait_time)

            # Step 4: Select destination - Nanjing, Gulou District - 选择目的地：南京-鼓楼区
            logger.info("Step 4: 选择目的地 - 南京市 鼓楼区")
            dest_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["destination_select_box"]))
            )
            dest_box.click()
            time.sleep(wait_time)

            # Click hot city Nanjing - 点击热门城市的南京市
            logger.info("点击热门城市的【南京市】")
            nanjing = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["hot_city_nanjing"]))
            )
            nanjing.click()
            time.sleep(wait_time)

            # Click Gulou District - 点击鼓楼区
            logger.info("点击鼓楼区")
            gulou = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["gulou_district"]))
            )
            gulou.click()
            time.sleep(wait_time)

            # Step 5: Input weight only (no dimensions) - 仅输入重量（不输入体积）
            logger.info("Step 5: 输入重量信息（重量: 100，体积不输入）")
            weight_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["weight_input"]))
            )
            weight_input.clear()
            weight_input.send_keys("100")
            time.sleep(wait_time)

            # Step 6: Input custom send date and time - 输入自定义寄件日期和时间
            logger.info("Step 6: 输入寄件日期和时间（2025-11-17 15:00:00）")
            time_control = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["send_time_control"]))
            )
            time_control.click()
            time.sleep(wait_time)

            # Input date - 输入日期
            logger.info("输入日期: 2025-11-17")
            date_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["date_input"]))
            )
            date_input.clear()
            date_input.send_keys("2025-11-17")
            time.sleep(wait_time)

            # Input time - 输入时间
            logger.info("输入时间: 15:00:00")
            time_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["time_input"]))
            )
            time_input.clear()
            time_input.send_keys("15:00:00")
            time.sleep(wait_time)

            # Click confirm button - 点击确定按钮
            logger.info("点击【确定】按钮")
            confirm_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["confirm_button"]))
            )
            confirm_btn.click()
            time.sleep(wait_time)

            # Step 7: Click query button - 点击查询按钮
            logger.info("Step 7: 点击【查询】按钮")
            query_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["query_button"]))
            )
            query_btn.click()
            time.sleep(wait_time)
            time.sleep(2)

            # Step 8: Scroll to express product section and take screenshot
            # 滚动到快递产品区域并截图
            logger.info("Step 8: 滚动到快递产品区域")
            express_product = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, XPATHS["express_product_section"])
                )
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", express_product)
            time.sleep(wait_time)

            logger.info(f"截图保存查询结果（包含寄件时间和快递产品信息） - {case_id}")
            self.take_screenshot(driver, f"{case_id}.png")

            logger.info(f"✅ 测试用例 {case_id} 执行完成")

        except selenium_exceptions.TimeoutException as e:
            logger.error(f"❌ 超时异常: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise
        except Exception as e:
            logger.error(f"❌ 测试执行失败: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise

    @pytest.mark.parametrize(
        "weight,length,width,height,case_id",
        [
            ("19", "5", "8", "6", "SF_R004_001"),
            ("20", "5", "8", "6", "SF_R004_002"),
            ("19", "100", "80", "90", "SF_R004_003"),
            ("20", "100", "80", "90", "SF_R004_004"),
        ],
    )
    def test_SF_R004(self, driver, weight, length, width, height, case_id):
        """Test SF R004: Freight timeliness query with large package option
        测试顺丰 R004：大件（20kg+）运费时效查询功能

        Test steps - 测试步骤:
        1. Click service support button - 点击服务支持按钮
        2. Navigate to freight timeliness page - 进入运费时效页面
        3. Select origin: Hong Kong - Kowloon City - 选择始发地：香港-九龙城区
        4. Select destination: Nanjing - Gulou District - 选择目的地：南京-鼓楼区
        5. Input weight and dimensions - 输入重量和体积
        6. Input custom send date and time - 输入自定义寄件日期和时间
        7. Click query button - 点击查询按钮
        8. Click large package button - 点击【大件（20kg+）】按钮
        9. Take screenshot including weight, dimensions and large package section - 截图保存结果
        """
        self.waiting_for_page_load(driver)
        self.agree_cookie_policy(driver)

        # XPath dictionary for element locators - XPath 元素定位器字典
        # 复用已有的 XPATH - Reuse existing XPATHs
        XPATHS = {
            "service_support_button": '//a[text()="服务支持"]',
            "freight_timeliness_menu": '//li[contains(text(), "运费时效")]',
            "origin_select_box": '//*[@id="origion"]/div[1]/div/div[1]',
            "hk_macau_taiwan_tab": '//*[@id="origincityPicker"]/div[1]/ul/li[2]',
            "hongkong_option": '//*[@id="origincityPicker"]/div[3]/div[2]/ul/li[2]/span',
            "kowloon_city_district": '//*[@id="origincityPicker"]/div[3]/div[2]/ul/li[6]',
            "destination_select_box": '//*[@id="dests"]/div[1]/div/div[1]',
            "hot_city_nanjing": '//*[@id="destsCityPicker"]/div[3]/div[2]/ul/li[8]',
            "gulou_district": '//*[@id="destsCityPicker"]/div[3]/div[2]/ul/li[4]',
            "weight_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[3]/figure/div/input',
            "length_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[4]/figure/div/div[1]/input',
            "width_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[4]/figure/div/div[2]/input',
            "height_input": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[1]/ul/li[4]/figure/div/div[3]/input',
            "send_time_control": '//*[@id="datetime"]/div/div[2]/input',
            "date_input": "/html/body/div[7]/div[1]/div/div[1]/span[1]/div/input",
            "time_input": "/html/body/div[7]/div[1]/div/div[1]/span[2]/div[1]/input",
            "confirm_button": "/html/body/div[7]/div[2]/button[2]",
            "query_button": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[2]/button',
            "large_package_button": '//*[@id="chn"]/div/div[2]/div/div[2]/div[2]/ul[2]/li[2]',
            "large_package_section": "",
        }

        wait_time = 2

        try:
            logger.info(f"开始执行测试用例: {case_id}")
            logger.info(
                f"测试参数 - 始发地: 香港 九龙城区, 目的地: 南京市 鼓楼区, "
                f"重量: {weight}, 长: {length}, 宽: {width}, 高: {height}, "
                f"日期时间: 2025-11-18 08:00:00"
            )

            # Step 1: Click service support button - 点击【服务支持】按钮
            logger.info("Step 1: 点击【服务支持】按钮")
            service_support_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["service_support_button"]))
            )
            service_support_btn.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 2: Click freight timeliness menu - 点击【运费时效】菜单
            logger.info("Step 2: 点击左侧菜单栏的【运费时效】")
            freight_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, XPATHS["freight_timeliness_menu"])
                )
            )
            freight_menu.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 3: Select origin - Hong Kong, Kowloon City - 选择始发地：香港-九龙城区
            logger.info("Step 3: 选择始发地 - 香港 九龙城区")
            origin_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["origin_select_box"]))
            )
            origin_box.click()
            time.sleep(wait_time)

            # Click Hong Kong Macau Taiwan tab - 点击【港澳台】
            logger.info("点击【港澳台】标签")
            hk_macau_taiwan = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["hk_macau_taiwan_tab"]))
            )
            hk_macau_taiwan.click()
            time.sleep(wait_time)

            # Click Hong Kong - 点击香港
            logger.info("点击香港")
            hongkong = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["hongkong_option"]))
            )
            hongkong.click()
            time.sleep(wait_time)

            # Click Kowloon City District - 点击九龙城区
            logger.info("点击九龙城区")
            kowloon_city = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["kowloon_city_district"]))
            )
            kowloon_city.click()
            time.sleep(wait_time)

            # Step 4: Select destination - Nanjing, Gulou District - 选择目的地：南京-鼓楼区
            logger.info("Step 4: 选择目的地 - 南京市 鼓楼区")
            dest_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["destination_select_box"]))
            )
            dest_box.click()
            time.sleep(wait_time)

            # Click hot city Nanjing - 点击热门城市的南京市
            logger.info("点击热门城市的【南京市】")
            nanjing = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["hot_city_nanjing"]))
            )
            nanjing.click()
            time.sleep(wait_time)

            # Click Gulou District - 点击鼓楼区
            logger.info("点击鼓楼区")
            gulou = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["gulou_district"]))
            )
            gulou.click()
            time.sleep(wait_time)

            # Step 5: Input weight and dimensions - 输入重量和体积
            logger.info(
                f"Step 5: 输入重量和体积信息（重量: {weight}, 长: {length}, 宽: {width}, 高: {height}）"
            )
            weight_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["weight_input"]))
            )
            weight_input.clear()
            weight_input.send_keys(weight)
            time.sleep(wait_time)

            length_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["length_input"]))
            )
            length_input.clear()
            length_input.send_keys(length)
            time.sleep(wait_time)

            width_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["width_input"]))
            )
            width_input.clear()
            width_input.send_keys(width)
            time.sleep(wait_time)

            height_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["height_input"]))
            )
            height_input.clear()
            height_input.send_keys(height)
            time.sleep(wait_time)

            # Step 6: Input custom send date and time - 输入自定义寄件日期和时间
            logger.info("Step 6: 输入寄件日期和时间（2025-11-18 08:00:00）")
            time_control = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["send_time_control"]))
            )
            time_control.click()
            time.sleep(wait_time)

            # Input date - 输入日期
            logger.info("输入日期: 2025-11-18")
            date_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["date_input"]))
            )
            date_input.clear()
            date_input.send_keys("2025-11-18")
            time.sleep(wait_time)

            # Input time - 输入时间
            logger.info("输入时间: 08:00:00")
            time_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATHS["time_input"]))
            )
            time_input.click()
            time_input.clear()
            time.sleep(1)
            time_input.clear()
            time.sleep(1)
            time_input.send_keys("08:00:00")
            time.sleep(wait_time)

            # Click confirm button - 点击确定按钮
            logger.info("点击【确定】按钮")
            confirm_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["confirm_button"]))
            )
            confirm_btn.click()
            time.sleep(wait_time)

            # Step 7: Click query button - 点击查询按钮
            logger.info("Step 7: 点击【查询】按钮")
            query_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["query_button"]))
            )
            query_btn.click()
            time.sleep(wait_time)
            time.sleep(2)

            # Step 8: Click large package button - 点击【大件（20kg+）】按钮
            logger.info("Step 8: 点击【大件（20kg+）】按钮")
            if XPATHS["large_package_button"]:
                large_package_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, XPATHS["large_package_button"])
                    )
                )
                large_package_btn.click()
                time.sleep(wait_time)
                time.sleep(2)
            else:
                logger.warning("⚠️ 大件（20kg+）按钮的XPATH未填充，跳过点击操作")

            # Step 9: Scroll to large package section and take screenshot
            # 滚动到大件产品区域并截图
            logger.info("Step 9: 滚动到大件产品区域")
            if XPATHS["large_package_section"]:
                large_package_section = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, XPATHS["large_package_section"])
                    )
                )
                driver.execute_script(
                    "arguments[0].scrollIntoView(true);", large_package_section
                )
                time.sleep(wait_time)
            else:
                logger.warning("⚠️ 大件产品区域的XPATH未填充，跳过滚动操作")

            logger.info(f"截图保存查询结果（包含重量、体积和大件产品信息） - {case_id}")
            self.take_screenshot(driver, f"{case_id}.png")

            logger.info(f"✅ 测试用例 {case_id} 执行完成")

        except selenium_exceptions.TimeoutException as e:
            logger.error(f"❌ 超时异常: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise
        except Exception as e:
            logger.error(f"❌ 测试执行失败: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise

    @pytest.mark.parametrize(
        "service_name,case_id",
        [
            ("保价", "SF_R005_001"),
            ("代收贷款", "SF_R005_002"),
            ("签单返还", "SF_R005_003"),
            ("包装服务", "SF_R005_004"),
        ],
    )
    def test_SF_R005(self, driver, service_name, case_id):
        """Test SF R005: Other services navigation and screenshot
        测试顺丰 R005：其他服务导航和截图功能

        Test steps - 测试步骤:
        1. Click service support button - 点击服务支持按钮
        2. Navigate to freight timeliness page - 进入运费时效页面
        3. Click other service button - 点击其他服务按钮
        4. Navigate to corresponding page - 跳转到对应页面
        5. Take screenshot - 截图保存页面结果
        """
        self.waiting_for_page_load(driver)
        self.agree_cookie_policy(driver)

        # XPath dictionary for element locators - XPath 元素定位器字典
        # 复用已有的 XPATH - Reuse existing XPATHs
        XPATHS = {
            "service_support_button": '//a[text()="服务支持"]',
            "freight_timeliness_menu": '//li[contains(text(), "运费时效")]',
            "service_insured": '//*[@id="chn"]/div/div[2]/div/div[2]/div[3]/div/a[1]',  # 保价按钮
            "service_cod": '//*[@id="chn"]/div/div[2]/div/div[2]/div[3]/div/a[2]',  # 代收贷款按钮
            "service_sign_return": '//*[@id="chn"]/div/div[2]/div/div[2]/div[3]/div/a[3]',  # 签单返还按钮
            "service_packaging": '//*[@id="chn"]/div/div[2]/div/div[2]/div[3]/div/a[4]',  # 包装服务按钮
        }

        wait_time = 2

        try:
            logger.info(f"开始执行测试用例: {case_id}")
            logger.info(f"测试参数 - 其他服务: {service_name}")

            # Step 1: Click service support button - 点击【服务支持】按钮
            logger.info("Step 1: 点击【服务支持】按钮")
            service_support_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["service_support_button"]))
            )
            service_support_btn.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 2: Click freight timeliness menu - 点击【运费时效】菜单
            logger.info("Step 2: 点击左侧菜单栏的【运费时效】")
            freight_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, XPATHS["freight_timeliness_menu"])
                )
            )
            freight_menu.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 3: Click other service button - 点击其他服务按钮
            logger.info(f"Step 3: 点击【{service_name}】按钮")

            # Map service name to XPATH key - 将服务名称映射到XPATH键
            service_xpath_map = {
                "保价": "service_insured",
                "代收贷款": "service_cod",
                "签单返还": "service_sign_return",
                "包装服务": "service_packaging",
            }

            xpath_key = service_xpath_map.get(service_name)
            if xpath_key and XPATHS[xpath_key]:
                service_btn = driver.find_element(By.XPATH, XPATHS[xpath_key])
                service_btn.click()
                time.sleep(wait_time)
                self.waiting_for_page_load(driver)
            else:
                logger.warning(f"⚠️ {service_name}按钮的XPATH未填充，跳过点击操作")

            # Step 4: Take screenshot - 截图保存页面结果
            logger.info(f"Step 4: 截图保存【{service_name}】页面结果 - {case_id}")
            time.sleep(wait_time)
            self.take_screenshot(driver, f"{case_id}.png")

            logger.info(f"✅ 测试用例 {case_id} 执行完成")

        except selenium_exceptions.TimeoutException as e:
            logger.error(f"❌ 超时异常: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise
        except Exception as e:
            logger.error(f"❌ 测试执行失败: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise

    def test_SF_R006(self, driver):
        """Test SF R006: Service network query function
        测试顺丰 R006：服务网点查询功能

        Test steps - 测试步骤:
        1. Click service support button - 点击服务支持按钮
        2. Navigate to service network page - 进入服务网点页面
        3. Select Shanghai - Huangpu District - 选择上海市-黄浦区
        4. Input keyword "兴业太古汇" - 输入关键词"兴业太古汇"
        5. Click query button - 点击查询按钮
        6. Find and click "国泰君安快递服务中心" on map - 在地图中查找并点击"国泰君安快递服务中心"
        7. Click city zoom level on map - 点击地图缩放控制条的【市】
        8. Take screenshot including map, service details and zoom info - 截图保存结果
        """
        self.waiting_for_page_load(driver)
        self.agree_cookie_policy(driver)

        # XPath dictionary for element locators - XPath 元素定位器字典
        # 等待人工填充 - Waiting for manual filling
        XPATHS = {
            "service_support_button": '//a[text()="服务支持"]',  # 服务支持按钮
            "service_network_menu": '//li[contains(text(), "服务网点")]',  # 服务网点菜单
            "area_select_box": '//*[@id="range-query-citypicker"]/input',  # 选择收寄件区域选择框
            # 热门城市按钮
            "hot_city": '//*[@id="range-query-citypicker"]/div/div[3]/div[1]/ul/li[1]',
            "hot_city_shanghai": '//*[@id="range-query-citypicker"]/div/div[3]/div[2]/ul/li[2]',  # 热门城市上海选项
            "huangpu_district": '//*[@id="range-query-citypicker"]/div/div[3]/div[2]/ul/li[1]',  # 黄浦区选项
            "keyword_input": '//*[@id="range-key-word"]',  # 输入关键词输入框
            "query_button": '//*[@id="chn"]/div/div[2]/div/div[2]/div[1]/div[3]/button',  # 查询按钮
            "service_center_marker": '//*[@id="chn"]/div/div[2]/div/div[2]/div[2]/div/div[1]/div[1]/div[2]/div[2]/span[131]',  # 国泰君安快递服务中心标记
            "zoom_city_button": '//*[@id="chn"]/div/div[2]/div/div[2]/div[2]/div/div[1]/div[13]/div[2]/div[4]/div[2]',  # 地图缩放控制条【市】按钮
        }

        wait_time = 2
        case_id = "SF_R006_001"

        try:
            logger.info(f"开始执行测试用例: {case_id}")
            logger.info("测试参数 - 区域: 上海市 黄浦区, 关键词: 兴业太古汇")

            # Step 1: Click service support button - 点击【服务支持】按钮
            logger.info("Step 1: 点击【服务支持】按钮")
            service_support_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XPATHS["service_support_button"]))
            )
            service_support_btn.click()
            time.sleep(wait_time)
            self.waiting_for_page_load(driver)

            # Step 2: Click service network menu - 点击【服务网点】菜单
            logger.info("Step 2: 点击左侧菜单栏的【服务网点】")
            if XPATHS["service_network_menu"]:
                network_menu = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, XPATHS["service_network_menu"])
                    )
                )
                network_menu.click()
                time.sleep(wait_time)
                self.waiting_for_page_load(driver)
            else:
                logger.warning("⚠️ 服务网点菜单的XPATH未填充，跳过点击操作")

            # Step 3: Select area - Shanghai, Huangpu District - 选择区域：上海市-黄浦区
            logger.info("Step 3: 选择收寄件区域 - 上海市 黄浦区")
            if XPATHS["area_select_box"]:
                area_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, XPATHS["area_select_box"]))
                )
                area_box.click()
                time.sleep(wait_time)

                # Click hot city Shanghai - 点击热门城市的上海市
                logger.info("点击热门城市的【上海市】")
                if XPATHS["hot_city_shanghai"]:
                    shanghai = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, XPATHS["hot_city_shanghai"])
                        )
                    )
                    shanghai.click()
                    time.sleep(wait_time)
                else:
                    logger.warning("⚠️ 上海市选项的XPATH未填充，跳过点击操作")

                # Click Huangpu District - 点击黄浦区
                logger.info("点击黄浦区")
                if XPATHS["huangpu_district"]:
                    huangpu = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, XPATHS["huangpu_district"])
                        )
                    )
                    huangpu.click()
                    time.sleep(wait_time)
                else:
                    logger.warning("⚠️ 黄浦区选项的XPATH未填充，跳过点击操作")
            else:
                logger.warning("⚠️ 选择收寄件区域选择框的XPATH未填充，跳过选择操作")

            # Step 4: Input keyword - 输入关键词
            logger.info("Step 4: 在【输入关键词】输入框中输入'兴业太古汇'")
            if XPATHS["keyword_input"]:
                keyword_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, XPATHS["keyword_input"]))
                )
                keyword_input.clear()
                keyword_input.send_keys("兴业太古汇")
                time.sleep(wait_time)
                keyword_input.click()
                time.sleep(wait_time)
            else:
                logger.warning("⚠️ 关键词输入框的XPATH未填充，跳过输入操作")

            # Step 5: Click query button - 点击查询按钮
            logger.info("Step 5: 点击【查询】按钮")
            if XPATHS["query_button"]:
                query_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, XPATHS["query_button"]))
                )
                query_btn.click()
                time.sleep(wait_time)
                time.sleep(2)
            else:
                logger.warning("⚠️ 查询按钮的XPATH未填充，跳过点击操作")

            # Step 6: Find and click service center on map - 在地图中查找并点击服务中心
            logger.info("Step 6: 在地图中查找并点击'国泰君安快递服务中心'")
            if XPATHS["service_center_marker"]:
                service_center = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, XPATHS["service_center_marker"])
                    )
                )
                service_center.click()
                time.sleep(wait_time)
                time.sleep(2)
            else:
                logger.warning("⚠️ 国泰君安快递服务中心标记的XPATH未填充，跳过点击操作")

            # Step 7: Click city zoom level button - 点击地图缩放控制条的【市】按钮
            logger.info("Step 7: 点击地图右下角缩放控制条的【市】按钮")
            if XPATHS["zoom_city_button"]:
                zoom_city_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, XPATHS["zoom_city_button"]))
                )
                zoom_city_btn.click()
                time.sleep(wait_time)
                time.sleep(2)
            else:
                logger.warning("⚠️ 地图缩放【市】按钮的XPATH未填充，跳过点击操作")

            # Step 8: Take screenshot - 截图保存查询结果
            logger.info(
                f"Step 8: 截图保存查询结果（包含整个地图、服务网点详细信息和缩放后的地图信息） - {case_id}"
            )
            self.take_screenshot(driver, f"{case_id}.png")

            logger.info(f"✅ 测试用例 {case_id} 执行完成")

        except selenium_exceptions.TimeoutException as e:
            logger.error(f"❌ 超时异常: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise
        except Exception as e:
            logger.error(f"❌ 测试执行失败: {str(e)}")
            self.take_screenshot(driver, f"{case_id}_error.png")
            raise

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
