from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as exceptions

import bs4

import asyncio
import logging
from typing import List
from .Monitor import Monitor


class DanmakuSpider:
    # driver_path = "lib/chromedriver.exe"
    log_path = "log/danmaku_spider.log"
    danmaku_list_xpath = "//*[@id=\"chat-items\"]"
    _url: str
    _driver: webdriver.Chrome
    _subscribers: List[Monitor]   # objects should have update method
    _current_danmaku_list_text: str

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

        # set log path
        service = webdriver.ChromeService(log_output=DanmakuSpider.log_path)
        # add driver path if version of selenium < 4.6

        self._driver = webdriver.Chrome(service=service, options=options)

    def __init__(self, room_id: str):
        self._url = "https://live.bilibili.com/" + room_id
        self._init()
        self._subscribers = []
        self._current_danmaku_list_text = ""

    def register(self, subscriber: object):
        self._subscribers.append(subscriber)

    def unregister(self, subscriber: object):
        self._subscribers.remove(subscriber)

    @property
    def subscribers(self):
        return self._subscribers

    async def start(self):
        self._driver.get(self._url)
        while True:
            tasks = []
            try:
                danmaku_list = WebDriverWait(self._driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, DanmakuSpider.danmaku_list_xpath))
                )
                danmaku_list_text = danmaku_list.text
                if danmaku_list_text != self._current_danmaku_list_text:
                    self._current_danmaku_list_text = danmaku_list_text
                    html_code = danmaku_list.get_attribute("outerHTML")
                    soup = bs4.BeautifulSoup(html_code, "html.parser")
                    tasks = [subscriber.update(soup) for subscriber in self._subscribers]
            except Exception as e:
                print(e)
            tasks.append(asyncio.sleep(2))
            await asyncio.gather(*tasks)

    def stop(self):
        if self._driver is not None:
            self._driver.quit()

    def __del__(self):
        self.stop()