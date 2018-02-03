# from time import time
from bs4 import BeautifulSoup
import requests
import pypyodbc
import os
import re


def get_external_ip4():
    url = 'https://www.google.ca/search?q=whats+my+ip+address&rlz=1C1CHBF_enCA748CA748&oq=whats+&aqs=chrome.0' \
          '.69i59j69i60l2j69i57j69i60j35i39.1311j0j1&sourceid=chrome&ie=UTF-8 '
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # print(soup.prettify())  # use for DEBUGGING
    name_box = soup.find('div', attrs={'class': '_h4c _rGd vk_h'})
    # print(name_box)
    name = name_box.text.strip()
    print(f' External ip: http://{name}:99/')
    return name


def get_external_ip3():
    url = 'https://www.privateinternetaccess.com/pages/whats-my-ip/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    name_box = soup.find('li', {'class': 'topbar__item topbar__item-ip'})
    name = name_box.text.strip()[17:]
    # name = name[17:]
    print(f' External ip: http://{name}:99/')
    return


def get_external_ip2():
    url = 'http://whatismyip.org/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    name = soup.find('span', style="color: blue; font-size: 36px; font-weight: 600;").text
    print(f' External ip: http://{name}:99/')
    return


# def database():
#     cwd = os.getcwd()
#     print(cwd)
#     file = cwd + r'\Information.accdb'
#     print(file)
#     pypyodbc.lowercase = False
#     conn = pypyodbc.connect(
#         r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" +
#         r"Dbq=C:\Users\maste\Documents\Python Projects\Website\Information.accdb;")
#     cur = conn.cursor()
#     cur.execute("SELECT ID, First_Name, Last_Name, Pw, Date_of_Birth FROM Information")
#     while True:
#         row = cur.fetchone()
#         if row[1] is None: break
#         birth_date = row.get('Date_of_Birth').date()  # get date from datetime.datetime
#         print(f"User {row.get('ID')} is {row.get('First_Name')} {row.get('Last_Name')}")
#         print(f"User {row.get('ID')} has password {row.get('pw')}")
#         print(f"User {row.get('ID')} was born on {birth_date}")
#     cur.close()
#     conn.close()


def get_external_ip():
    try:
        res = requests.get("http://whatismyip.org")
        ip = re.compile('(\d{1,3}\.){3}\d{1,3}').search(res.text).group()
        if ip != "":
            print(f' External ip: http://{ip}:99/')
            return ip
    except: pass
    return print('ERROR occured while getting ip adress')

