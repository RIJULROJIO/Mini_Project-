


# # import time
# # import unittest
# # from selenium import webdriver
# # from selenium.webdriver.common.by import By

# # class LoginTest(unittest.TestCase):

# #     def setUp(self):
# #         self.driver = webdriver.Chrome()

# #     def test_successful_login(self):
# #         self.driver.get('http://127.0.0.1:8000/login')
# #         username_input = self.driver.find_element(By.ID, 'username')
# #         password_input = self.driver.find_element(By.ID, 'password')

# #         # Replace 'valid_username' and 'valid_password' with actual credentials
# #         username_input.send_keys('rijulrojio')
# #         password_input.send_keys('rR@12345')

# #         login_button = self.driver.find_element(By.ID, 'login')
# #         login_button.click()

# #         time.sleep(2)  # Adjust the time as needed

# #         # ... (Your existing login code)

# #         # Check if redirected to the home page
# #         self.assertIn('http://127.0.0.1:8000/ownerpage', self.driver.current_url.lower())

# #         # Click on the "Dashboard" link
# #         dashboard_link = self.driver.find_element(By.LINK_TEXT, 'Dashboard')
# #         dashboard_link.click()

# #         # Check if redirected to the owner's dashboard
# #         self.assertIn('http://127.0.0.1:8000/ownerpg', self.driver.current_url.lower())

# #         # Click on the "Add Properties" link
# #         add_properties_link = self.driver.find_element(By.LINK_TEXT, 'Add Properties')
# #         add_properties_link.click()

# #         # Fill the property details in the form
# #         property_type_dropdown = self.driver.find_element(By.ID, 'property_type')
# #         address_input = self.driver.find_element(By.ID, 'address')
# #         monthly_rent_input = self.driver.find_element(By.ID, 'monthly_rent')
# #         security_deposit_input = self.driver.find_element(By.ID, 'security_deposit')
# #         lease_duration_dropdown = self.driver.find_element(By.ID, 'lease_duration')
# #         availability_date_input = self.driver.find_element(By.ID, 'availability_date')

# #         # Replace these values with actual property details
# #         property_type_dropdown.send_keys('Apartment')
# #         address_input.send_keys('123 Main St')
# #         monthly_rent_input.send_keys('1500')
# #         security_deposit_input.send_keys('2000')
# #         lease_duration_dropdown.send_keys('1 year')
# #         availability_date_input.send_keys('01-02-2022')

# #         # Submit the form
# #         submit_button = self.driver.find_element(By.CSS_SELECTOR, '#add-property-form button[type="submit"]')
# #         submit_button.click()

# #         time.sleep(2)  # Adjust the time as needed

# #         # Now you can add assertions to check if the property was added successfully
# #         # For example, check for success messages or check if the property appears in the list

# #     def tearDown(self):
# #         self.driver.quit()

# # if __name__ == "__main__":
# #     unittest.main()


# import time
# import unittest
# from selenium import webdriver
# from selenium.webdriver.common.by import By

# class LoginTest(unittest.TestCase):

#     def setUp(self):
#         self.driver = webdriver.Chrome()

#     def test_successful_login(self):
#         self.driver.get('http://127.0.0.1:8000/login')
#         username_input = self.driver.find_element(By.ID, 'username')
#         password_input = self.driver.find_element(By.ID, 'password')

#         # Replace 'valid_username' and 'valid_password' with actual credentials
#         username_input.send_keys('jubil')
#         password_input.send_keys('jJ@12345')

#         login_button = self.driver.find_element(By.ID, 'login')
#         login_button.click()

#         time.sleep(2)  # Adjust the time as needed


#         # Check if redirected to the tenantpage
#         self.assertIn('http://127.0.0.1:8000/tenantpage', self.driver.current_url.lower())

#         # Click on the "Dashboard" link
#         dashboard_link = self.driver.find_element(By.LINK_TEXT, 'Dashboard')
#         dashboard_link.click()

#         time.sleep(2)  # Adjust the time as needed

#         self.assertIn('http://127.0.0.1:8000/tenantpg', self.driver.current_url.lower())
#         property_type_dropdown = self.driver.find_element(By.ID, 'property_type')
#         min_rent_input = self.driver.find_element(By.NAME, 'min_rent')
#         max_rent_input = self.driver.find_element(By.NAME, 'max_rent')
#         search_button = self.driver.find_element(By.CSS_SELECTOR, '#property-search-form button[type="submit"]')

#         # Replace these values with the desired search criteria
#         property_type_dropdown.send_keys('Apartment')
#         min_rent_input.send_keys('1000')
#         max_rent_input.send_keys('2000')
#         search_button.click()

#         time.sleep(2)  # Adjust the time as needed


#     def tearDown(self):
#         self.driver.quit()

# if __name__ == "__main__":
#     unittest.main()

# import time
# import unittest
# from selenium import webdriver
# from selenium.webdriver.common.by import By

# class LoginTest(unittest.TestCase):

#     def setUp(self):
#         self.driver = webdriver.Chrome()

#     def test_successful_login(self):
#         self.driver.get('http://127.0.0.1:8000/login')
#         username_input = self.driver.find_element(By.ID, 'username')
#         password_input = self.driver.find_element(By.ID, 'password')

#         # Replace 'valid_username' and 'valid_password' with actual credentials
#         username_input.send_keys('rijulrojio')
#         password_input.send_keys('rR@12345')

#         login_button = self.driver.find_element(By.ID, 'login')
#         login_button.click()

#         time.sleep(2)  # Adjust the time as needed

#         # Check if redirected to the ownerpage
#         self.assertIn('http://127.0.0.1:8000/ownerpage', self.driver.current_url.lower())

#         # Click on the "Dashboard" link
#         dashboard_link = self.driver.find_element(By.LINK_TEXT, 'Dashboard')
#         dashboard_link.click()

#         time.sleep(2)  # Adjust the time as needed

#         # Check if redirected to the ownerpg
#         self.assertIn('http://127.0.0.1:8000/ownerpg', self.driver.current_url.lower())

#         # Click on the "Manage Properties" link
#         manage_properties_link = self.driver.find_element(By.LINK_TEXT, 'Manage Properties')
#         manage_properties_link.click()

#         time.sleep(2)  # Adjust the time as needed

#         # Check if redirected to the manageprop
#         self.assertIn('http://127.0.0.1:8000/manageprop', self.driver.current_url.lower())

#         # Click on the "Accept Request" button
#         accept_request_button = self.driver.find_element(By.CSS_SELECTOR, 'form button.btn-primary')
#         accept_request_button.click()

#         time.sleep(2)  # Adjust the time as needed

#         # Now you can add assertions to check if the acceptance was successful
#         # For example, check for success messages or changes in the UI

#     def tearDown(self):
#         self.driver.quit()

# if __name__ == "__main__":
#     unittest.main()


#mainproject 
    
#1
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class LoginTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_successful_login(self):
        self.driver.get('http://127.0.0.1:8000/login')
        username_input = self.driver.find_element(By.ID, 'username')
        password_input = self.driver.find_element(By.ID, 'password')

        # Replace 'valid_username' and 'valid_password' with actual credentials
        username_input.send_keys('george')
        password_input.send_keys('gG@12345')

        login_button = self.driver.find_element(By.ID, 'login')
        login_button.click()

        time.sleep(2)  # Adjust the time as needed

        # Check if redirected to the ownerpage
        self.assertIn('http://127.0.0.1:8000/serproviderpage', self.driver.current_url.lower())

        # Click on the dashboard link
        dashboard_button = self.driver.find_element(By.CLASS_NAME, 'dashboard-btn')
        dashboard_button.click()

        time.sleep(2)  # Adjust the time as needed

        # Check if redirected to the serproviderdash page
        self.assertIn('http://127.0.0.1:8000/serproviderdash/', self.driver.current_url.lower())

        # Find and click on the "Service Requests" link
        service_requests_link = self.driver.find_element(By.ID, 'serviceRequestsLink')
        service_requests_link.click()

        time.sleep(2)  # Adjust the time as needed

        # Scroll to the "Schedule Service" button
        schedule_service_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Schedule Service')]")
        self.driver.execute_script("arguments[0].scrollIntoView();", schedule_service_button)

        time.sleep(2)  # Adjust the time as needed

        # Click the "Schedule Service" button
        schedule_service_button.click()

        time.sleep(2)  # Adjust the time as needed

        # Fill the scheduled date
        scheduled_date_input = self.driver.find_element(By.ID, 'scheduled_date')
        scheduled_date_input.send_keys('20-03-2024')

        # Fill the scheduled time
        scheduled_time_input = self.driver.find_element(By.ID, 'scheduled_time')
        scheduled_time_input.send_keys('10:00')

        # Click the "Schedule Service" button within the form
        schedule_service_button_in_form = self.driver.find_element(By.XPATH, "//form//button[contains(text(), 'Schedule Service')]")
        schedule_service_button_in_form.click()

        time.sleep(2)  # Adjust the time as needed

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()

#2