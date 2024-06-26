import logging
import time
import os
from MALFriendBot.database import Database
import random
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(logging.WARNING)

os.environ['WDM_LOCAL'] = '1'

class MALFriendClient:
    def __init__(self, headless: bool = True):
        self.driver = self.createclient(headless)
        self.userTable = Database()
        self.globalstart = time.time()

    @staticmethod
    def createclient(headless):
        # Set up Chrome driver
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--log-level=3")
        driver_service = webdriver.ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=driver_service, options=chrome_options)
        return driver

    def closeclient(self):
        self.driver.quit()
        self.userTable.close()

    def mallogin(self, username: str, password: str):
        #Navigate to Login page and enter login
        self.driver.get("https://myanimelist.net/login.php")
        self.driver.find_element(By.ID, "loginUserName").send_keys(username)
        self.driver.find_element(By.ID, "login-password").send_keys(password + Keys.ENTER)
        time.sleep(1)
        login = len(self.driver.find_elements(By.CLASS_NAME, "badresult"))
        self.driver.switch_to.new_window('tab')
        return login

    def getusers(self):
        #Navigate to Users Page
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[1])
        self.driver.get("https://myanimelist.net/users.php")
        time.sleep(2)

        #Create a list of the user elements
        element_list = self.driver.find_elements(By.XPATH, "//*[@class='borderClass']/div[1]/a")
        friends = list()
        for element in element_list:
            friends.append(element.text)
        return friends

    def adduser(self, username, message):
        start = time.time()

        #Navigate to User Profile
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[1])
        self.driver.get("https://myanimelist.net/profile" + "/" + username)
        time.sleep(2)

        # Check if user exists
        is404 = len(self.driver.find_elements(By.CLASS_NAME, "error404"))

        # Check if request is available (Disabled Friend Requests)
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
            self.userTable.add_user(username)
            return False

        if is_comment > 0 and message is not None:
            # Navigate to Comment Box
            comments = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.CLASS_NAME, "textarea")))
            comments.send_keys(message)

            #Send Profile Comment
            submit_button = WebDriverWait(self.driver, 10).until(
                ec.visibility_of_element_located((By.XPATH, "//*[@id='lastcomment']/div/form/div/input")))
            submit_button.click()
            time.sleep(2)

        try:

            end = time.time()
            sleeptime = random.randint(26, 35) - (end - start)
            time.sleep(sleeptime)

            #Click Request Button on user profile
            request = WebDriverWait(self.driver, 10).until(
                ec.element_to_be_clickable((By.XPATH, "//*[@id='request']")))
            self.driver.execute_script("arguments[0].click();", request)

            #First Friend request attempt
            request_submit = WebDriverWait(self.driver, 10).until(
                ec.element_to_be_clickable((By.XPATH, "//*[@id='dialog']/tbody/tr/td/form/div[3]/input[1]")))
            self.driver.execute_script("arguments[0].click();", request_submit)

            #Redundant Friend request attempt
            if len(self.driver.find_elements(By.CLASS_NAME, "badresult")) > 0:
                self.driver.back()
                time.sleep(10)
                request_submit = WebDriverWait(self.driver, 10).until(
                    ec.element_to_be_clickable((By.XPATH, "//*[@id='dialog']/tbody/tr/td/form/div[3]/input[1]")))
                self.driver.execute_script("arguments[0].click();", request_submit)
                if len(self.driver.find_elements(By.CLASS_NAME, "badresult")) > 0:
                    return False

            realend = time.time()
            print(f"[{round(realend - self.globalstart,1)}s] {username} added")
            self.globalstart = time.time()
            self.userTable.add_user(username)

            return True
        except Exception as e:
            print(e)
            return False
