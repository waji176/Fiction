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
    driver.find_element_by_xpath('''//*[@id="sign-in"]''').click()
    driver.find_element_by_xpath('''//input[@id="user_session_login"]''').send_keys('邮箱@qq.com')
    driver.find_element_by_xpath('''//input[@id="user_session_password"]''').send_keys('密码')
    driver.find_element_by_xpath('''//input[@id="user_session_submit"]''').click()
    time.sleep(5)
    js = 'window.location.href="https://tastebuds.fm/search";'
    driver.execute_script(js)
    driver.find_element_by_xpath('''//*[@id="peopleWrapper"]/div[1]/ul/li[4]''').click()
    time.sleep(5)
    driver.find_element_by_xpath('''//*[@id="country"]''').click()
    s1 = Select(driver.find_element_by_id('country'))  # 实例化Select
    s1.select_by_value("us")  # 选择value="us"的项

    url_li = set()
    # for num in range(1, 55):
    for num in range(1, 55):
        li = driver.find_elements_by_xpath(
            '''//ul[@class="userGrid js_append_people"]/li/a''')
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
        name_info = driver.find_element_by_xpath('''//h2[@class="js_meta_outer offline"]''').text
    except Exception:
        time.sleep(30)
        name_info = driver.find_element_by_xpath('''//h2[@class="js_meta_outer offline"]''').text
    name = name_info.split()[0]
    age = name_info.split(',')[0].split()[1]
    sex = name_info.split(',')[1]
    try:
        country_address = driver.find_element_by_xpath('''//p[@class="userFact factNationality"]/span''').text
    except Exception:
        country_address = ''
    if len(name_info.split(',')) > 3:
        country_address += name_info.split(',')[2] + name_info.split(',')[3]
    elif len(name_info.split(',')) > 2:
        country_address += name_info.split(',')[2]
    elif len(name_info.split(',')) < 2:
        country_address += ''

    try:
        photo = driver.find_element_by_xpath('''//div[@class="profileImg"]/a/img''')  # 头像
        photo = photo.get_attribute('src')
    except Exception:
        photo = ''
    try:
        height = driver.find_element_by_xpath('''//p[@class="userFact factHeight"]/span''').text  # 身高
    except Exception:
        height = ''
    try:
        more = driver.find_element_by_xpath('''//div[@class="js_facts_display_outer"]''').text  # 更多信息
    except Exception:
        more = ''
    try:
        ethnicity = driver.find_element_by_xpath('''//p[@class="userFact factEthnicity"]/span''').text  # 种族
    except Exception:
        ethnicity = ''
    try:
        relationship = driver.find_element_by_xpath('''//p[@class="userFact factStatus"]/span''').text  # status:是否单身
    except Exception:
        relationship = ''
    try:
        body_type = driver.find_element_by_xpath('''//p[@class="userFact factBodyType"]/span''').text  # 体型
    except Exception:
        body_type = ''
    try:
        instructions = driver.find_element_by_xpath('''//div[@class="profileContentBoxInner"]''').text  # 交友说明
    except Exception:
        instructions = ''
    try:
        faith = driver.find_element_by_xpath('''//p[@class="userFact factReligion"]/span''').text  # 宗教
    except Exception:
        faith = ''
    # print("name:", name, "age:", age, "sex:", sex, "country_address:", country_address, "photo:", photo, "height:", height, "more:", more, "ethnicity:", ethnicity)
    photo_gallery = []  # 照片库
    photo_gallery.append(photo)
    try:
        photo_gallery1 = driver.find_elements_by_xpath('''//div[@class="userPhotos sideBox"]/a/img''')
        for i in photo_gallery1:
            photo_gallery1 = i.get_attribute("src")
            # print(photo_gallery1)
            photo_gallery.append(photo_gallery1)
    except Exception:
        pass
    photo_gallery = json.dumps(photo_gallery)

    source = 'tastebuds.fm'

    education = ''
    have_kids = ''
    smoke = ''
    want_kids = ''
    drink = ''
    INTERESTS_and_PORTS = ''
    ruku.ruhu(source, name, age, photo, country_address, instructions, relationship, education, faith, have_kids, body_type, smoke, want_kids, height, drink, ethnicity, more, photo_gallery, sex, INTERESTS_and_PORTS)


if __name__ == "__main__":
    get_url("https://tastebuds.fm/search")
