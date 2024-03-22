from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import logging

class ChatGPTDriver:
    def __init__(self, url, cookie):
        self.url = url
        self.cookie = cookie
        self.browser = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)  # Adjust the logging level as needed

    def start(self):
        self.logger.info("Starting the browser...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome(options=options)
        stealth(
            self.browser,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        self.browser.maximize_window()
        self.browser.get(self.url)
        self.browser.add_cookie(self.cookie)
        self.browser.refresh()
        self.browser.get(self.url)
        input("Call me if you have passed the verification (type in any key to continue): ")  # manually pass cloudflare
        self.browser.minimize_window()
        self.logger.info("Browser started successfully.")

    def wait_until_complete(self, waiting_seconds=10):
        self.logger.info(f"Waiting for page to load. Timeout set to {waiting_seconds} seconds.")
        WebDriverWait(self.browser, waiting_seconds).until(lambda x: x.execute_script("return document.readyState == \"complete\""))
        self.logger.info("Page loaded successfully.")

    def prompt(self, input_str):
        self.logger.info(f"Sending prompt: {input_str}")
        if self.browser is None:
            raise Exception("Browser not started. Call start() first.")

        prompt_input_area = self.browser.find_element(By.ID, "prompt-textarea")
        prompt_input_area.send_keys(input_str + Keys.RETURN)
        wait = WebDriverWait(self.browser, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid=\"send-button\"]")))
        chat_area = self.browser.find_element(By.XPATH, "/html/body/div[1]/div[1]/div/main/div[1]/div[1]/div/div/div")
        response_areas = chat_area.find_elements(By.CLASS_NAME, "text-token-text-primary")
        response_content = response_areas[-1].find_element(By.CLASS_NAME, "markdown")
        self.logger.info("Received response successfully.")
        return response_content.text

    def new_chat(self):
        self.logger.info("Starting a new chat...")
        if self.browser is None:
            raise Exception("Browser not started. Call start() first.")

        button = self.browser.find_element(By.XPATH, "//*[contains(text(), \"New Chat\")]")
        button.click()
        self.wait_until_complete()
        self.logger.info("New chat started successfully.")

    def switch_chat(self, index):
        self.logger.info(f"Switching to chat at index {index}...")
        if self.browser is None:
            raise Exception("Browser not started. Call start() first.")
        today_chats = self.browser.find_elements(By.XPATH, "/html/body/div[1]/div[1]/div[1]/div/div/div/div/nav/div[3]/div/div/span[1]/div[1]/ol/*")
        today_chats[index].click()
        self.wait_until_complete()
        self.logger.info("Switched to the specified chat successfully.")

    def close(self):
        if self.browser:
            self.logger.info("Closing the browser...")
            self.browser.quit()
            self.logger.info("Browser closed.")


if __name__ == "__main__":
    # Example usage
    url = "https://chat.openai.com/"
    cookie = {
        "name": "cookie_name",
        "value": "cookie_value"
    }
    driver = ChatGPTDriver(url, cookie)
    driver.start()
    driver.new_chat()
    response = driver.prompt("Hello, how are you?")
    print(response)
    driver.close()