import logging
import time
import os
from functions.database import Database
import random
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)
userTable = Database()


class MALFriendClient:
    def __init__(self, headless: bool = True):
        self.driver = self.createclient(headless)
        self.globalstart = time.time()

    @staticmethod
    def createclient(headless):
        # Set up Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--log-level=3")

        # Set up Chrome driver
        os.environ['WDM_LOCAL'] = '1'
        driver_service = webdriver.ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=driver_service, options=chrome_options)
        return driver

    def closeclient(self):
        self.driver.quit()

    def mallogin(self, username: str, password: str):
        self.driver.get("https://myanimelist.net/login.php")
        self.driver.find_element(By.ID, "loginUserName").send_keys(username)
        self.driver.find_element(By.ID, "login-password").send_keys(password + Keys.ENTER)
        time.sleep(1)
        login = len(self.driver.find_elements(By.CLASS_NAME, "badresult"))
        self.driver.switch_to.new_window('tab')
        return login

    def getusers(self):
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[1])
        self.driver.get("https://myanimelist.net/users.php")
        time.sleep(2)

        element_list = self.driver.find_elements(By.XPATH, "//*[@class='borderClass']/div[1]/a")
        friends = list()
        for element in element_list:
            friends.append(element.text)
        return friends

    def adduser(self, username, message):
        start = time.time()
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[1])
        self.driver.get("https://myanimelist.net/profile" + "/" + username)
        time.sleep(2)

        # Check if user exists
        is404 = len(self.driver.find_elements(By.CLASS_NAME, "error404"))

        # Check if request is available
        is_request = len(self.driver.find_elements(By.CSS_SELECTOR,
                                                   ".user-profile .user-function .icon-user-function.icon-request.disabled i.fas"))

        # Check if already a friend
        is_friend = len(self.driver.find_elements(By.CSS_SELECTOR,
                                                  ".user-profile .user-function .icon-user-function.icon-remove i.fas"))

        # Check if comments are available
        is_comment = len(self.driver.find_elements(By.CLASS_NAME, "textarea"))
        if is404 > 0:
            return False

        if is_request > 0:
            return False

        if is_friend > 0:
            print(username + " is already a friend")
            userTable.add_user(username)
            return False

        if is_comment > 0 and message is not None:
            # Add Some Comments
            comments = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.CLASS_NAME, "textarea")))
            comments.send_keys(message)

            submit_button = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, "//*[@id='lastcomment']/div/form/div/input")))
            submit_button.click()

            time.sleep(2)
        elif is_comment == 0 and message is not None:
            print("User Doesn't have Comments Turned On")

        try:

            end = time.time()
            sleeptime = random.randint(26, 35) - (end - start)
            time.sleep(sleeptime)

            request = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, "//*[@id='request']")))
            request.click()

            request_submit = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, "//*[@id='dialog']/tbody/tr/td/form/div[3]/input[1]")))
            request_submit.click()

            if len(self.driver.find_elements(By.CLASS_NAME, "badresult")) > 0:
                print(f"Adding {username} failed. Retrying...")
                self.driver.back()
                time.sleep(10)
                request_submit = WebDriverWait(self.driver, 10).until(
                    ec.visibility_of_element_located((By.XPATH, "//*[@id='dialog']/tbody/tr/td/form/div[3]/input[1]")))
                request_submit.click()
                if len(self.driver.find_elements(By.CLASS_NAME, "badresult")) > 0:
                    print(f"Retry Failed.")
                    return False

            realend = time.time()
            print(f"{username} Added after {realend - self.globalstart} seconds")
            self.globalstart = time.time()
            userTable.add_user(username)

            return True
        except Exception as e:
            print(e)
            return False
