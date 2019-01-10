from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time, re, os, sys, json, requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup


def done(request, *args, **kwargs):  #
    result = request.result()


def get_url(url):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.find_element_by_xpath('''//input[@name="nick"]''').send_keys('hestiaob')
    driver.find_element_by_xpath('''//input[@name="password"]''').send_keys('zyy2826')
    verifycode = input("输入数字验证码:")
    driver.find_element_by_xpath('''//input[@name="verifycode"]''').send_keys(verifycode)
    driver.find_element_by_xpath('''//input[@name="B1"]''').click()
    urlli = []
    for i in range(1, 38):  # 38
        url = "https://ebook.longmabook.com/myfunction/outputhtml/ebook_new_proxy_newbooklist_all_page{}.html".format(i)
        urlli.append(url)
    pool = ThreadPoolExecutor(1)
    for url in urlli:
        v_ = pool.submit(get_fiction_list, [url, driver])
        v_.add_done_callback(done)
    pool.shutdown(wait=True)


def get_fiction_list(data):
    url = data[0]
    driver = data[1]
    print(url)
    js = 'window.location.href="{}";'.format(url)
    driver.execute_script(js)
    li = driver.find_elements_by_xpath('''//tr/td/a[2]''')
    urlli = []
    for i in li:
        url = i.get_attribute("href")
        urlli.append(url)
    pool = ThreadPoolExecutor(1)
    for url in urlli:
        v_ = pool.submit(get_fiction_info, [url, driver])
        v_.add_done_callback(done)
    pool.shutdown(wait=True)


def get_fiction_info(data):
    url = data[0]
    driver = data[1]
    print(url)
    js = 'window.location.href="{}";'.format(url)
    driver.execute_script(js)
    classification = driver.find_element_by_xpath('''//div[@id="css_table2"]/div[@class="css_tr"]/div[@class="css_td"]/a/b''').text.split("/")[0]
    fiction_name = driver.find_element_by_xpath('''//div[@class="css_td"]/b/a''').text
    fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
    status = driver.find_element_by_xpath('''//div[@class="css_td"]/font''').text
    # print(classification, fiction_name, status, )
    li = driver.find_elements_by_xpath('''//tr/td[@align="left"]/a[2]''')
    urlli = []
    for i in li:
        url = i.get_attribute("href")
        urlli.append(url)
    pool = ThreadPoolExecutor(1)
    index = 0
    for url in urlli:
        index += 1
        v_ = pool.submit(get_chapter_content, [url, driver, index, classification, fiction_name, fiction_img, status])
        v_.add_done_callback(done)
    pool.shutdown(wait=True)


def get_chapter_content(data):
    url = data[0]
    driver = data[1]
    index = data[2]
    classification = data[3]
    fiction_name = data[4]
    fiction_img = data[5]
    status = data[6]
    author = '未知'
    viewing_count = ''
    chapter_update_time = ''
    print(url)
    js = 'window.location.href="{}";'.format(url)
    driver.execute_script(js)
    try:
        driver.find_element_by_xpath('''//*[@id="fastloaders"]/b/a''').click()
    except Exception:
        pass
    chapter_name = driver.find_element_by_xpath('''//td[@class="styleshowbook210"]''').text
    chapter_content = driver.find_element_by_xpath('''//*[@id="mypaper"]''').text
    if chapter_content:
        is_vip = False
    else:
        is_vip = True
    ruku.ruku("海棠文化", classification, fiction_name, fiction_img, author, viewing_count, chapter_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


if __name__ == "__main__":
    import ruku

    get_url("https://ebook.longmabook.com/login")
