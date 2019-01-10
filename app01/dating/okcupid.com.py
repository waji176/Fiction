from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import time, re, os, sys, json
from concurrent.futures import ThreadPoolExecutor
import ruku


def done(request, *args, **kwargs):  #
    result = request.result()
    # print(result, args, kwargs)


def get_url(url):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.find_element_by_xpath('''//input[@name="username"]''').send_keys('邮箱@qq.com')
    driver.find_element_by_xpath('''//input[@name="password"]''').send_keys('密码')
    driver.find_element_by_xpath('''//input[@type="submit"]''').click()
    time.sleep(5)
    js = 'window.location.href="{}";'.format("https://www.okcupid.com/match")
    driver.execute_script(js)
    url_li = set()
    # for num in range(1, 80):
    for num in range(1, 100):
        li = driver.find_elements_by_xpath(
            '''//a[@class="image_link"]''')
        for i in li:
            url_li.add(i.get_attribute("href"))
        driver.execute_script("window.scrollBy(0,{})".format(700))
        print("下拉了{}次".format(num))
        time.sleep(2)
    print(len(url_li))
    pool = ThreadPoolExecutor(1)
    for i in url_li:
        v_ = pool.submit(get_info, [i, driver, ])
        v_.add_done_callback(done)
    pool.shutdown(wait=True)

    driver.quit()


def get_info(data):
    url = data[0]
    driver = data[1]
    print(url)
    js = 'window.location.href="{}";'.format(url)
    driver.execute_script(js)
    time.sleep(10)
    try:
        name = driver.find_element_by_xpath('''//div[@class="userinfo2015-basics-username"]''').text
    except Exception:
        time.sleep(30)
        name = driver.find_element_by_xpath('''//div[@class="userinfo2015-basics-username"]''').text

    try:
        age = driver.find_element_by_xpath('''//*[@id="profile2015"]/div[1]/div/div[1]/div[2]/div[2]/span[1]''').text
    except Exception:
        age = ''
    try:
        country_address = driver.find_element_by_xpath('''//*[@id="profile2015"]/div[1]/div/div[1]/div[2]/div[2]/span[3]''').text  # 国家 地区
    except Exception:
        country_address = ''
    try:
        instructions = driver.find_element_by_xpath('''//*[@id="react-profile-essays"]/div/div[1]/p''').text  # 交友说明
    except Exception:
        instructions = ''
    try:
        relationship = driver.find_element_by_xpath('''//*[@id="react-profile-details"]/div/div/div[1]/div[2]''').text  # status:是否单身
    except Exception:
        relationship = ''
    sex = relationship

    try:
        more = driver.find_element_by_xpath('''//*[@id="react-profile-details"]/div/div/div[2]/div[2]''').text  # 更多信息
    except Exception:
        more = ''
    education = more
    have_kids = more
    smoke = more
    drink = more
    # print("name:", name, "age:", age, "country_address:", country_address, "instructions:", instructions, "relationship:", relationship, "more:", more)
    photo_gallery = []  # 照片库

    try:
        photo = driver.find_elements_by_xpath(
            '''//div[@class="userinfo2015-thumb"]/img''')  # 头像
        for i in photo:
            photo = i.get_attribute('src')
            photo_gallery.append(i.get_attribute('src'))
    except Exception:
        photo = ''
    try:
        photo_gallery1 = driver.find_elements_by_xpath('''//div[@class="morePhotos2015-photos-photo"]/img''')
        for i in photo_gallery1:
            photo_gallery1 = i.get_attribute("src")
            photo_gallery.append(photo_gallery1)
    except Exception:
        pass
    photo_gallery = json.dumps(photo_gallery)
    # print(photo_gallery)

    source = 'www.okcupid.com'
    faith = ''
    body_type = ''
    want_kids = ''
    height = ''
    ethnicity = ''
    INTERESTS_and_PORTS = ''
    ruku.ruhu(source, name, age, photo, country_address, instructions, relationship, education, faith, have_kids,
              body_type, smoke, want_kids, height, drink, ethnicity, more, photo_gallery, sex, INTERESTS_and_PORTS)


if __name__ == "__main__":
    get_url("https://www.okcupid.com/login")
