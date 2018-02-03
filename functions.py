import requests
from bs4 import BeautifulSoup


def get_external_ip():
    url = 'https://www.google.ca/search?q=whats+my+ip+address&rlz=1C1CHBF_enCA748CA748&oq=whats+&aqs=chrome.0' \
          '.69i59j69i60l2j69i57j69i60j35i39.1311j0j1&sourceid=chrome&ie=UTF-8 '
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # print(soup.prettify())  # use for DEBUGGING
    # print(list(soup.children))  # use for DEBUGGING
    name_box = soup.find('div', attrs={'class': '_h4c _rGd vk_h'})
    # print(name_box)
    name = name_box.text.strip()
    print(name)


get_external_ip()
