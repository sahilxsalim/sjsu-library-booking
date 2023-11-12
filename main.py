from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import time
import os
from util import get_today_date, increment_date, create_titles, send_email

# ROOM NUMBER 864
ROOM_ID = 9766


def get_available_slots(room_id=ROOM_ID, date=increment_date(get_today_date(), 4)):
    """
    Get available slots for the King Library.
    """
    headers = {
        'authority': 'booking.sjlibrary.org',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://booking.sjlibrary.org',
        'referer': 'https://booking.sjlibrary.org/reserve/king',
        'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'lid': '1164',
        'gid': '0',
        'eid': '-1',
        'seat': '0',
        'seatId': '0',
        'zone': '0',
        'start': date,
        'end': increment_date(date, 1),
        'pageIndex': '0',
        'pageSize': '18',
    }

    response = requests.post(
        'https://booking.sjlibrary.org/spaces/availability/grid', headers=headers, data=data)

    return [slot for slot in response.json()['slots'] if slot['itemId'] == room_id and "className" not in slot]


def book_slots(slots, username, password):
    """
    Book the given slots.
    """
    success = False
    try:
        service = Service()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument("--disable-gpu")
        # options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.99 Safari/537.36")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        driver.get("https://booking.sjlibrary.org/reserve/king")
        wait = WebDriverWait(driver, 5)
        next_date_btn = driver.find_element(
            By.XPATH, '//*[@id="eq-time-grid"]/div[1]/div[1]/div/button[2]')

        for _ in range(4):
            next_date_btn.click()

        for slot in slots:
            # Click on the slot
            slot_btn = driver.find_element(
                By.XPATH, f"//a[@title='{slot}']")
            slot_btn.click()
            time.sleep(0.5)
        
        submit_times_btn = driver.find_element(By.XPATH, '//*[@id="submit_times"]')
        submit_times_btn.click()

        username_field = driver.find_element(By.XPATH, '//*[@id="username"]')
        username_field.send_keys(username)
        password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
        password_field.send_keys(password)
        login_btn = driver.find_element(By.XPATH, '//*[@id="s-libapps-login-button"]')
        login_btn.click()

        continue_btn = driver.find_element(By.XPATH, '//*[@id="terms_accept"]')
        continue_btn.click()

        submit_slots_btn = driver.find_element(By.XPATH, '//*[@id="btn-form-submit"]')
        submit_slots_btn.click()
        time.sleep(2)
        success = True
    except Exception as e:
        print(e)
        success = False
    finally:
        driver.close()
        return success


if __name__ == "__main__":

    users = json.loads(os.environ["USER_DETAILS"])
    slots_booked = []

    for username,password in users:
        # Get the slots
        time.sleep(3)
        slots = get_available_slots(ROOM_ID, increment_date(get_today_date(), 4))
        # Create the titles
        titles = create_titles(slots[:4])
        slot_times = [title.split(' ')[0] for title in titles]

        if len(titles) > 0:
            if book_slots(titles, username, password) == True:
                slots_booked.extend(slot_times)
    
    if len(slots_booked) > 0:
        send_email(",".join([titles[0].split(',')[1]] + slots_booked))
    
