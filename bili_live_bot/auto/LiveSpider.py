from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as exceptions

import bs4

import asyncio
import logging
from typing import List


class LiveSpider:
    driver_path = "lib/chromedriver.exe"
    log_path = "log/live_spider.log"
    danmaku_input_xpath = "//*[@id=\"control-panel-ctnr-box\"]/div[2]/div[2]/textarea"
    _url: str
    _driver: webdriver.Chrome
    _bili_cookies: List[dict]

    def _init(self):
        # set options
        options = webdriver.ChromeOptions()
        # headless mode
        options.add_argument("--headless")
        # fake user agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")
        # disable images and css
        prefs = {
            "profile.default_content_setting_values": {
                "images": 2,  # disable images
                "css": 2  # disable css
            }
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("detach", True)

        # set log path
        service = webdriver.ChromeService(executable_path=LiveSpider.driver_path, log_output=LiveSpider.log_path)

        self._driver = webdriver.Chrome(service=service, options=options)

    def __init__(self, bili_cookies: List[dict], room_id: str):
        self._url = "https://live.bilibili.com/" + room_id
        self._init()
        self._bili_cookies = bili_cookies

    def start(self):
        # self._driver.maximize_window()
        self._driver.get(self._url)
        [self._driver.add_cookie(cookie) for cookie in self._bili_cookies]
        self._driver.refresh()
        self._driver.get(self._url)

    async def send_short_danmaku(self, text: str):
        try:
            input_box = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.XPATH, LiveSpider.danmaku_input_xpath))
            )
            input_box.send_keys(text[:20])  # 20 characters limited
            input_box.send_keys(u"\ue007")  # press enter
        except exceptions.TimeoutException as toe:
            print(toe)

    async def send_long_danmaku(self, text: str):
        # bilibili has a 20 characters limit for each danmaku
        # so we split the long danmaku into multiple short ones
        try:
            input_box = WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.XPATH, LiveSpider.danmaku_input_xpath))
            )
            for i in range(0, len(text), 20):
                input_box.send_keys(text[i:i+20])
                input_box.send_keys(u"\ue007")  # press enter
                await asyncio.sleep(1)
        except exceptions.TimeoutException as toe:
            print(toe)

    def stop(self):
        if self._driver is not None:
            self._driver.quit()

    def __del__(self):
        self.stop()


if __name__ == "__main__":
    import json
    with open("./config.json", "r") as f:
        config = json.load(f)
    spider = LiveSpider(config["bili_cookies"], config["room_id"])
    spider.start()
    asyncio.run(spider.send_danmaku("hello world!"))