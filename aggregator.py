import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

df_new = pd.read_excel("all_urls.xlsx")
urls = df_new['link'].tolist()

df = pd.DataFrame(columns=['business_name', 'business_type', 'owner_name','street', 'zip', 'city', 'district', 'work_description', 'registered_trade', 'contact_name', 'telephone_number', 'cellphone_number', 'fax', 'email', 'website', "hwk_url", 'complete_address', 'complete_contact_info'])
df_unreachable = pd.DataFrame(columns=['hwk-url', 'status_code'])

pattern_website = re.compile(r'.*(http://|https://|www\.).*')
pattern_href = re.compile(r'href="([^"]*)"')
pattern_contact_name = re.compile("^[A-Za-z]+$")

k = 0
# 318516
while k < 318516:

    url = urls[k]
    print(f"{k} - {url}")

    if url.startswith("http://hwk-heilbronn"):
        response.status_code = 500
    else:
        response = requests.get(url)
    
    business_name = "" 
    business_type = ""
    owner_name = ""
    street = "" 
    zip = "" 
    city = ""
    district = ""
    work_description = ""
    registered_trade = ""
    contact_name = "" 
    telephone = "" 
    cellphone = "" 
    fax = "" 
    email = "" 
    website = "" 
    complete_address = ""
    complete_contact_info = ""

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        container = soup.find("div", class_="container content")

        if url.startswith("http://www.hwk-ff"):              
            owner_name = container.h1.text
            business_name = owner_name
            
            list_group = container.find_all("div", class_="list-group-item inline")
            cellphone = ""
            for item in list_group:
                if "Anschrift" in item.find("div", class_="col-sm-3").text:
                    complete_address = item.find("div", class_="col-sm-9").text
                    street = complete_address.split(",")[0]
                    place_address = complete_address.split(",")[1]
                    zip = place_address.split()[0]
                    city = place_address.split()[1]
                if "Telefon" in item.find("div", class_="col-sm-3").text:
                    telephone = item.find("div", class_="col-sm-9").text
                if "Webseite" in item.find("div", class_="col-sm-3").text:
                    website = item.find("div", class_="col-sm-9").text
                if "E-Mail" in item.find("div", class_="col-sm-3").text:
                    email = item.find("div", class_="col-sm-9").text
                if "Beruf" in item.find("div", class_="col-sm-3").text:
                    trade = item.find("div", class_="col-sm-9").text
                if "Fax" in item.find("div", class_="col-sm-3").text:
                    fax = item.find("div", class_="col-sm-9").text

        elif url.startswith("https://service.hwk-reutlingen"):
            page = soup.find(id="page")

            container = page.find("div", class_="container")

            section_element = soup.find('section', {'id': 'section-1'})

            information_type = section_element.find_all("div", class_="col-12 col-xs-12 col-sm-6 col-md-5")
            information = section_element.find_all("div", class_="col-12 col-xs-12 col-sm-6 col-md-7")
            
            i = 0
            while i < len(information):
                if "Name" in information_type[i].label.text:
                    owner_name = information[i].p.text.strip()
                    business_name = owner_name
                if "Straße" in information_type[i].label.text:
                    street = information[i].p.text.strip()
                if "Postleitzahl" in information_type[i].label.text:
                    zip = information[i].p.text.strip()
                if "Stadt" in information_type[i].label.text:
                    city = information[i].p.text.strip()
                if "Telefon:" in information_type[i].label.text:
                    telephone = information[i].p.text.strip()
                if "Telefon (Mobil):" in information_type[i].label.text:
                    cellphone = information[i].p.text.strip()
                if "Fax" in information_type[i].label.text:
                    fax = information[i].p.text.strip()
                if "Gewerk(e)" in information_type[i].label.text:
                    trade = information[i].p.text.strip()
                if "E-Mail" in information_type[i].label.text:
                    email = information[i].p.text.strip()
                if "Internet" in information_type[i].label.text:
                    website = information[i].p.text.strip()
                  
                i += 1
        else:            
            rows = container.find_all("div", class_="row")

            row_margin = container.find_all("div", class_="row margin-top-s")

            work_description = ""

            i = 0
            while i < (len(row_margin) - 1): 
                if row_margin[i].h5.text in "Leistungsbeschreibung":
                    work_description = row_margin[i].p.text
                if row_margin[i].h5.text in "Eingetragene Berufe":
                    trade = str(row_margin[i].p).replace("<p>", "").replace("</p>", "").replace("<br/>", ", ")
                i += 1
                
            if len(rows) > 0:
                business_name = rows[0].text.strip()

                content = rows[1].find_all("div", class_="col-md-3")

                business_type = content[0].h5.text

                info = str(content[0].p)

                address_info = info.replace("<p>", "").replace("</p>", "").split("<br/>")
                
                complete_address = " ".join(address_info)

                index = len(address_info) - 2
                owner_name = address_info[0]
                street = address_info[1]
                place_address = address_info[2]
                zip = place_address.split()[0]
                city = place_address.split()[1]
                district = address_info[index]

                if len(content) > 1:
                    contact_info = str(content[1].p)
                    contact_info = contact_info.replace("<p>", "").replace("</p>", "").split("<br/>")

                    complete_contact = " ".join(contact_info)

                    if re.search(pattern_contact_name, contact_info[0]):
                        contact_name = contact_info[0]

                    for info in contact_info:
                        if "Telefon" in info:
                            telephone = info.split()[1:]
                            telephone = " ".join(telephone)
                        if "Handy" in info:
                            cellphone = info.split()[1:]
                            cellphone = " ".join(cellphone)
                        if "Fax" in info:
                            fax = info.split()[1:]
                            fax = " ".join(fax)
                        if "mail" in info:
                            match = pattern_href.search(info)
                            if match:
                                email = match.group(1)
                                email = email.replace("--at--", "@")
                        if pattern_website.match(info):
                            match = pattern_href.search(info)
                            if match:
                                website = match.group(1)

        df_tmp = pd.DataFrame(data={'business_name': [business_name], 'business_type': [business_type], 'owner_name': [owner_name], 'street': [street], 'zip': [zip], 'city': [city], 'district': [district], 'work_description': [work_description], 'registered_trade': [trade], 'contact_name': [contact_name], 'telephone_number': [telephone], 'cellphone_number': [cellphone], 'fax': [fax], 'email': [email], 'website': [website], 'hwk_url' : [url], 'complete_address': [complete_address], 'complete_contact_info': [complete_contact]})
        df = pd.concat([df, df_tmp], ignore_index=True)
    else:
        df_tmp = pd.DataFrame(data={'hwk-url': [url], 'status_code': [response.status_code]})   
        df_unreachable = pd.concat([df_unreachable, df_tmp], ignore_index=True)        

    k += 1


df.to_excel("all_craftsmen.xlsx")
df_unreachable.to_excel("hwk_links_not_working.xlsx")