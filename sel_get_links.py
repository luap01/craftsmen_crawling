
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from python3_anticaptcha import ImageToTextTask
import time
import os
import random
import json
# import google.cloud.logging
import sys

from datetime import datetime

from selenium.webdriver.common.action_chains import ActionChains
import math


from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

def get_links(pattern, plz, num_pages):
    captcha = "3enY3"
    url = f"https://www.handwerker-radar.de/5100,111,hwrsearch.html?page=1plz={plz}&radius=250&text=&captchaAnswer={captcha}&op=search"

    firefox_options = Options()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/100.0'
    firefox_options.add_argument(f'user-agent={user_agent}')
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")

    # Provide the path to the geckodriver executable
    gecko_path = "geckodriver_dir/geckodriver"
    driver = webdriver.Firefox(service=Service(gecko_path), options=firefox_options)

    driver.get(url)
    time.sleep(4)

    css_selector_cookie = "button.cm-btn:nth-child(1)"
    driver.find_element(By.CSS_SELECTOR, css_selector_cookie).click()

    css_selector_plz = '#plz'
    driver.find_element(By.CSS_SELECTOR, css_selector_plz).send_keys(plz)


    captcha = driver.find_element(By.CSS_SELECTOR, '.margin-top-xs > div:nth-child(1) > img:nth-child(1)')
    captcha_image = captcha.screenshot_as_png

    with open('image.png', 'wb') as f:
        f.write(captcha_image)

    ANTICAPTCHA_KEY = ''
    captcha_file = "image.png"
    result = ImageToTextTask.ImageToTextTask(
        anticaptcha_key=ANTICAPTCHA_KEY).captcha_handler(captcha_file=captcha_file)
    captcha.send_keys(result['solution']['text'])

    driver.find_element(By.CSS_SELECTOR, '#submit').click()

    df = pd.DataFrame(columns=['name', 'link'])
    df_links = pd.DataFrame(columns=['link'])


    i = 1
    while i < num_pages:
        # Extract the names
        item_headings = driver.find_elements(By.CLASS_NAME, 'list-group-item-heading')
        h4s = [name.text for name in item_headings]
        
        # Extract hrefs that are not Google Maps
        a_elements = driver.find_elements(By.CSS_SELECTOR, '[id^="detail_"] div.row a')
        
        hrefs = [a.get_attribute('href') for a in a_elements if re.search(pattern, a.get_attribute('href'))]
        
        df_tmp_links = pd.DataFrame(data={'link': hrefs})
        if len(h4s) == len(hrefs):
            df_temp = pd.DataFrame(data={'name': h4s, 'link': hrefs})
            df = pd.concat([df, df_temp], ignore_index=True)

        df_links = pd.concat([df_links, df_tmp_links], ignore_index=True)
        driver.find_element(By.CSS_SELECTOR, 'div.col-sm-4:nth-child(3) > a:nth-child(1)').click()

        time.sleep(0.5)
        i +=1

    driver.quit()

    return df_links


pattern = '^https?://.*(?:hwk|hk-ulm|handwerkskammer-koeln|handwerkskammer-ff|handwerk-owl)(?:.*id=|.*/handwerkersuche/\d{5}$|.*betrnr=)'

df_87719 = get_links(pattern, 87719, 6601)
df_10969 = get_links(pattern, 10969, 3874)
df_27305 = get_links(pattern, 27305, 5798)
df_57080 = get_links(pattern, 57080, 11611)
df_96487 = get_links(pattern, 96487, 10325)

df = pd.concat([df_87719, df_10969], ignore_index=True)
df_tmp = pd.concat([df_27305, df_57080], ignore_index=True)
df = pd.concat([df, df_tmp], ignore_index=True)
df = pd.concat([df, df_96487], ignore_index=True)

df_excel = pd.DataFrame(data={'link': df['link'].unique()})
df_excel.to_excel("all_urls.xlsx")