from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time, re, os, sys, json, requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

with open("1.html", encoding="utf-8") as f:
    html = f.read()
What_She_is_Looking_For = ''
soup = BeautifulSoup(html, 'html.parser')

li = soup.find_all("tr", )
for td in li:
    try:
        What_She_is_Looking_For += td.find("div", attrs={"class": "_2U2nqx7 _2RKQ9JC"}).text.strip() + " ： " + td.find("div", attrs={"class": "_3qQbn1K"}).text + " 。 ：" + td.find_all("td")[-1].text + "\n"
    except:
        pass
print(What_She_is_Looking_For)
