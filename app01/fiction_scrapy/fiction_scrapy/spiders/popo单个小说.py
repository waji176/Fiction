from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time, re, os, sys, json, requests
from concurrent.futures import ThreadPoolExecutor


def done(request, *args, **kwargs):  #
    result = request.result()


def get_url(url):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.find_element_by_xpath('''//input[@name="account"]''').send_keys('jiang290070744')
    driver.find_element_by_xpath('''//input[@name="pwd"]''').send_keys('jiang290070744')
    driver.find_element_by_xpath('''//input[@type="submit"]''').click()
    urlli = [
        "https://www.popo.tw/books/641150",
        "https://www.popo.tw/books/650499",
        "https://www.popo.tw/books/654071",
        "https://www.popo.tw/books/653534",
        "https://www.popo.tw/books/571561",
    ]

    pool = ThreadPoolExecutor(1)
    for i in urlli:
        v_ = pool.submit(get_info, [i, driver, ])
        v_.add_done_callback(done)
        # break
    pool.shutdown(wait=True)

    # driver.quit()


def get_info(data):
    url = data[0]
    if url[-1] == '/':
        url = url + "articles"
    else:
        url = url + "/articles"
    driver = data[1]
    # print(url)
    js = 'window.location.href="{}";'.format(url)
    driver.execute_script(js)
    try:
        driver.find_element_by_xpath('''//*[@id="books-form"]/div[2]/div/a[2]''').click()
    except Exception:
        pass
    time.sleep(5)
    fiction_name = driver.find_element_by_xpath('''//h3[@class="title"]''').text
    try:
        fiction_img = driver.find_element_by_xpath('''//img[@id="rs"]''').get_attribute("src")
    except Exception:
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
    author = driver.find_element_by_xpath('''//a[@class="blue"]''').text
    classification = driver.find_element_by_xpath('''//dd[@class="b_cate"]/span''').text
    try:
        status = driver.find_element_by_xpath('''//dd[@class="b_statu"]''').text
    except Exception:
        status = ''

    try:
        viewing_count = driver.find_element_by_xpath('''/html/body/div[4]/div[2]/div[1]/div[1]/div[3]/div[2]/table[3]/tbody/tr[3]/td''').text
    except Exception:
        viewing_count = ''

    li = driver.find_elements_by_xpath('''//div[@class="clist"]''')
    index = 0
    chapter_urlli = []
    for i in li:
        index += 1
        print(index)

        chapter_name = i.find_element_by_xpath('''.//div[@class="c2"]''').text
        try:
            chapter_url = i.find_element_by_xpath('''.//div[@class="c2"]/a''').get_attribute("href")
            is_vip = False
        except Exception:
            chapter_url = ''
            is_vip = True
        chapter_update_time = i.find_element_by_xpath('''.//div[@class="c3"]''').text
        chapter_urlli.append({"chapter_name": chapter_name, "chapter_url": chapter_url, "is_vip": is_vip, "chapter_update_time": chapter_update_time, "index": index})

    for i in chapter_urlli:
        chapter_name = i['chapter_name']
        is_vip = i['is_vip']
        chapter_url = i['chapter_url']
        chapter_update_time = i['chapter_update_time']
        index = i['index']
        if not is_vip:
            js = 'window.location.href="{}";'.format(chapter_url)
            driver.execute_script(js)
            chapter_content = driver.find_element_by_xpath('''//div[@id="readmask"]''').text
        else:
            chapter_content = ''
        ruku.ruku("popo", classification, fiction_name, fiction_img, author, viewing_count, chapter_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


if __name__ == "__main__":
    import ruku

    get_url("https://members.popo.tw/apps/login.php")
