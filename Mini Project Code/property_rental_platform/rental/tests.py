from datetime import datetime
from django.test import TestCase
from selenium import webdriver

from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Hosttest(TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.live_server_url = 'http://127.0.0.1:8000/'

    def tearDown(self):
        self.driver.quit()

    def test_01_login_page(self):
        driver = self.driver
        driver.get(self.live_server_url)
        driver.maximize_window()
        time.sleep(1)

        # Click on the login icon
        logd = driver.find_element(By.CSS_SELECTOR, "i#log-drop.bi.bi-person-gear.customSize.mr-3")
        logd.click()
        time.sleep(1)

        # Click on the login link
        login = driver.find_element(By.CSS_SELECTOR, "a[href='/login/']")
        login.click()
        time.sleep(1)

        # Enter a valid username and password
        username = driver.find_element(By.CSS_SELECTOR, "input#username[name='username']")
        username.send_keys("rijulrojio")  # Replace with a valid username

        password = driver.find_element(By.CSS_SELECTOR, "input#password[name='password']")
        password.send_keys("rR@12345")  # Replace with a valid password

        print('Typed username and password')
        time.sleep(1)

        # Click on the login button
        login_button = driver.find_element(By.CSS_SELECTOR, "button.btn[type='submit']")
        login_button.click()
        print('Logged in')
        time.sleep(2)

if __name__ == '__main__':
    import unittest
    unittest.main()
