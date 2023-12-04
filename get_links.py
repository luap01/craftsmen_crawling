import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup
import re

def write_number_to_file(filename, number):
    with open(filename, 'a') as f: 
        f.write(str(number) + '\n')


def get_links(pattern, zip, num_pages, cookie_string):

    cookies_dict = {cookie.split('=')[0]: "=".join(cookie.split('=')[1:]) for cookie in cookie_string.split('; ')}
    df = pd.DataFrame(columns=['link'])

    i = 1
    running = True
    retry_counter = 0
    file_name = f"missing_pages_{zip}.txt"

    while running:
        while i < num_pages:
            url = f"https://www.handwerker-radar.de/5100,111,hwrsearch.html?page={i}&plz={zip}&radius=250&text=&captchaAnswer=HEHmf&op=search"
            response = requests.get(url, cookies=cookies_dict)
            print(i)

            if response.status_code != 200:
                retry_counter += 1
                break
            
            soup = BeautifulSoup(response.content, 'html.parser')
            a_elements = soup.select('[id^="detail_"] div.row a')

            hrefs = [a['href'] for a in a_elements if re.search(pattern, a['href'])]

            if len(hrefs) < 15:
                running = False
                break

            df_tmp = pd.DataFrame(data={'link': hrefs})
            i += 1
            df = pd.concat([df, df_tmp], ignore_index=True)

        if response.status_code != 500:
            running = False
            print(response.status_code)
        
        if retry_counter == 10:
            retry_counter = 0
            write_number_to_file(filename=file_name, number=i)
            i += 1

    return df

pattern = '^https?://.*(?:hwk|hk-ulm|handwerkskammer-koeln|handwerkskammer-ff|handwerk-owl)(?:.*id=|.*/handwerkersuche/\d{5}$|.*betrnr=)'
cookie_string = 'odav-cookie-consent={"consents":{"technical":true,"analytics":true,"extmedia":true},"uuid":"70a6b4f7-1631-46af-8167-873a12bb2fc1","version":1}; _pk_id.yw7K2D8zoNOL43jo.dd10=9058a3f5d70a13be.1695229879.; ROUTEID=.node8; JSESSIONID=AEE1947A286F1A6BB11FE23728C1CCD1.webview-8967795f-gmnd6; _pk_ses.yw7K2D8zoNOL43jo.dd10=1'

df_87719 = get_links(pattern, 87719, 6601, cookie_string)
df_10969 = get_links(pattern, 10969, 3874, cookie_string)
df_27305 = get_links(pattern, 27305, 5798, cookie_string)
df_57080 = get_links(pattern, 57080, 11611, cookie_string)
df_96487 = get_links(pattern, 96487, 10325, cookie_string)

df = pd.concat([df_87719, df_10969], ignore_index=True)
df_tmp = pd.concat([df_27305, df_57080], ignore_index=True)
df = pd.concat([df, df_tmp], ignore_index=True)
df = pd.concat([df, df_96487], ignore_index=True)

df_excel = pd.DataFrame(data={'link': df['link'].unique()})
df_excel.to_excel("all_urls.xlsx")