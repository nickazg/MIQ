
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time



################


MONTH_TO_GET = 'March'
DAYS_TO_GET = ['10', '11'] # etc



################

portal_url = 'https://allocation.miq.govt.nz/portal/login'
chrome_path = '/Users/nicholasgrobler/Downloads/chromedriver'

rr = webdriver.Chrome(chrome_path)
rr.get('https://shorturl.at/coxSX')
rr.get('https://shorturl.at/coxSX')

driver = webdriver.Chrome(chrome_path)
driver.get(portal_url)
print(driver.session_id)

url = 'http://localhost:52341'
session_id = driver.session_id   # 4a9d8404e5606b62a311f5fb8e462fa4
input("Press Enter to continue...")

def attach_to_session(executor_url, session_id):
    original_execute = WebDriver.execute
    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return original_execute(self, command, params)
    # Patch the function before creating the driver object
    WebDriver.execute = new_command_execute
    driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    driver.session_id = session_id
    # Replace the patched function with original function
    WebDriver.execute = original_execute
    return driver


# driver = attach_to_session('http://localhost:52341', '4a9d8404e5606b62a311f5fb8e462fa4')

def set_month(month):
    next_month = driver.find_element(By.CLASS_NAME, 'flatpickr-next-month')
    cur_month = driver.find_element(By.CLASS_NAME, 'cur-month')

    if month not in cur_month.text:
        # ActionChains(driver).move_to_element(next_month).click(next_month).perform()
        ActionChains(driver).click(next_month).perform()
        set_month(month)


def get_date(month_str, day_strs):
    scroll_to = driver.find_element(By.XPATH,'//*[@id="step-3"]/div[1]/h2/span')
    time.sleep(0.5)
    ActionChains(driver).move_to_element(scroll_to).perform()

    set_month(month_str)
    calender = driver.find_element(By.CLASS_NAME, 'dayContainer')
    days = calender.find_elements(By.XPATH, ".//*")

    days_avaliable = []
    days_unavaliable = []

    for day in days:
        if 'flatpickr-disabled' in day.get_attribute('class'):
            days_unavaliable.append([day.get_attribute('aria-label'), day])

        else:
            days_avaliable.append([day.get_attribute('aria-label'), day])

    day_selected = False
    date_selected = 99

    print('Days Avaliable:')
    for da, da_ele in days_avaliable:
        print(da)
        m, d, y = da.split(' ')
        d = d.split(',')[0]

        if month_str == m and d in day_strs:
            if  int(d) < date_selected:
                print('found best date', da)
                date_selected = int(d)
                da_ele.click()
                day_selected = da

    print('\n')

    # print('Days Unavaliable:')
    # for du, du_ele in days_unavaliable:
    #     print(du)


    submit_button = driver.find_element(By.ID, 'form_next')

    if day_selected:
        print('Yay we got the date!')
        print(day_selected)
        no_disablity = driver.find_element(By.ID, 'form_rooms_0_accessibilityRequirement_1')
        driver.execute_script("arguments[0].click();", no_disablity)
        driver.execute_script("arguments[0].click();", submit_button)

        time.sleep(60)
        verify = driver.find_element(By.XPATH, '//*[@id="accommodation"]/div/h3')
        if 'allocation is held' in verify.text:
            print('verified')
        else:
            print('Verification Failed, start again')
            driver.refresh()
            get_date(month_str, day_strs)
        



        return

    else:
        print('refreshing page:', datetime.now())      
        time.sleep(1)  
        driver.refresh()
        time.sleep(1)  
        get_date(month_str, day_strs)

# get_date('March', ['2', '4'])
# get_date('February', ['8','3'])

def always_get_date(month, days):
    try:
        get_date(month, days)
    except:
        always_get_date(month, days)

always_get_date('March', ['2', '4'])


