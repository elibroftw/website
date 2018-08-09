from bs4 import BeautifulSoup
import requests
import re
import datetime
import markdown


class SchoolDay:
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'October', 'November',
              'December']

    def __init__(self, month: int, day: int, year=2018):
        self.day = day
        self.month = month
        self.year = year
        self.weekday = datetime.datetime(year, self.month, self.day).weekday()

    def __str__(self):
        return f'SchoolDay {self.get_weekday_name()} {self.month} {self.day} {self.year}'

    def get_weekday_name(self):
        return self.weekdays[self.weekday]

    def get_month_name(self):
        return self.months[self.month-1]


def get_data():
    url = 'https://sites.google.com/a/hdsb.ca/business-at-bateman---mrs-daly/home/6-grade-11-ib-economics'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    el = soup('table')[1]
    l2 = el.find_all('table')  # l2[1]  # first table
    l22 = l2[1].find_all('td')
    data = {}
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'October', 'November', 'December']
    days = re.compile('[1-9][0-9]|[1-9]')
    m = ''
    last = 0
    for i in range(len(l22) - 1):
        t: str = l22[i].text
        t = t.replace('\xa0', '')
        info = t[t.index('.')+1:]
        info = info.replace('  ', '')
        links = l22[i].find_all('a')  # use format [text goes here](link goes here)
        for link in links:
            info = info.replace(link.text, f"[{link.text}]({link['href']})")  # l22[i].a['href'] is a link
        day = days.search(t).group()[0:]
        if int(day) < last: m += 1
        last = int(day)
        if i == 0:
            for month in months:
                if month in t: m = months.index(month)+1
        if m == 2 and 25 > last > 20: last -= 1  # TODO: THIS IS A BUG FIX FOR HER WEBSITE
        data[SchoolDay(m, last)] = info
    l22 = l2[2].find_all('td')  # l2[2]  # second table
    last = 0
    for i in range(4, len(l22)):
        t: str = l22[i].text
        t = t.replace('\xa0', '')
        day = days.search(t).group()[0:]
        if int(day) < last: m += 1
        last = int(day)
        if i == 0:
            for month in months:
                if month in t: m = months.index(month) + 1
        info = t[t.index('.') + 1:]
        info = info.replace('  ', '')
        links = l22[i].find_all('a')
        for link in links:
            if link.text != '':
                info = info.replace(link.text, f"[{link.text}]({link['href']})")
        data[SchoolDay(m, last)] = info
    l22 = l2[3].find_all('td')
    for i in range(len(l22)-3):
        t: str = l22[i].text
        t = t.replace('\xa0', '')
        day = days.search(t).group()[0:]
        if int(day) < last: m += 1
        last = int(day)
        if i == 0:
            for month in months:
                if month in t: m = months.index(month) + 1
        info = t[t.index('.') + 1:]
        info = info.replace('  ', '')
        links = l22[i].find_all('a')
        for link in links:
            if link.text != '':
                info = info.replace(link.text, f"[{link.text}]({link['href']})")
        # if m == 5 and last > 14: last -= 1  # TODO: THIS IS A BUG FIX FOR HER WEBSITE
        # elif m == 6:
        #     last -= 1  # TODO: THIS IS A BUG FIX FOR HER WEBSITE
        #     if last == 0: m, last = 5, 31
        data[SchoolDay(m, last)] = info
    return data


def make_html_friendly(text):
    return markdown.markdown(text).replace('<p>', '').replace('</p>', '')


def info_to_html(month_name, day, info):
    return f'\n<td id={month_name}{day}><i>{month_name} {day}</i><br/>{info}</td>'


def get_template_data():
    schedule_data = get_data()
    template = ''
    last_weekday = 0
    for k, v in schedule_data.items():
        if k.get_weekday_name() == 'Monday':
            if not template.endswith('</tr>'): template += '</tr>'
            template += '\n<tr>'
            template += info_to_html(k.get_month_name(), k.day, make_html_friendly(v))
        else:
            # if template.endswith('</tr>'):
            #     template += '\n<tr>'
            #     for i in range(k.weekday - 1):
            #         template += '\n<td></td>'
            #     template += info_to_html(k.get_month_name(), k.day, make_html_friendly(v))
            if k.weekday < last_weekday:
                template += '\n</tr>'
                for i in range(k.weekday):
                    template += '\n<td></td>'
                template += info_to_html(k.get_month_name(), k.day, make_html_friendly(v))
            else:
                template += info_to_html(k.get_month_name(), k.day, make_html_friendly(v))
            # if k.weekday == 6: template += '\n</tr>'  # also maybe use 4
        last_weekday = k.weekday
    if not template.endswith('</tr>'): template += '\n</tr>'
    return template


if __name__ == '__main__':
    print(get_data())
