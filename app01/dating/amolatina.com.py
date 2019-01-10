from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time, re, os, sys, json
from concurrent.futures import ThreadPoolExecutor
import ruku


def done(request, *args, **kwargs):  #
    result = request.result()
    # print(result, args, kwargs)


def get_info(data):
    url = data[0]
    driver = data[1]
    index = data[2]
    print(url)
    # js = 'window.open("{}");'.format(url)
    js = 'window.location.href="{}";'.format(url)
    driver.execute_script(js)
    # handles = driver.window_handles
    # driver.switch_to.window(handles[index])
    time.sleep(10)
    try:
        name = driver.find_element_by_xpath('''//p[@class="text phrase-name"]/txt/span[@class="name-age-container"]/span[@class="name"]''').text
    except Exception:
        time.sleep(30)
        try:
            name = driver.find_element_by_xpath('''//p[@class="text phrase-name"]/txt/span[@class="name-age-container"]/span[@class="name"]''').text
        except Exception:
            name = ''
            names = driver.find_elements_by_xpath('''//span[@class="name-container"]''')
            for i in names:
                name += str(i.text).strip()

    try:
        photo = driver.find_element_by_xpath('''//img[@class="thumbnail photo existing "]''')  # 头像
        photo = photo.get_attribute('src')
    except Exception:
        photo = ''
    try:
        age = driver.find_element_by_xpath('''//p[@class="text phrase-name"]/txt/span[@class="name-age-container"]/span[@class="age"]''').text
    except Exception:
        age = ''
    try:
        country_address = driver.find_element_by_xpath('''//div[@class="location"]/span''').text  # 国家地址地区
    except Exception:
        country_address = ''
    try:
        instructions = driver.find_element_by_xpath('''//div[@class="phrase-container"]''').text  # 交友说明
    except Exception:
        instructions = ''
    try:
        relationship = driver.find_element_by_xpath('''//div[@class="relationship"]/span''').text  # status:是否单身
    except Exception:
        relationship = ''
    try:
        education = driver.find_element_by_xpath('''//div[@class="education"]/span''').text  # 教育程度
    except Exception:
        education = ''
    faith = ''  # 宗教信仰
    try:
        have_kids = driver.find_element_by_xpath('''//div[@class="kids"]/span''').text  # 是否有小孩
    except Exception:
        have_kids = ''
    try:
        body_type = driver.find_element_by_xpath('''//div[@class="bodytype"]/span''').text  # 体型
    except Exception:
        body_type = ''
    try:
        smoke = driver.find_element_by_xpath('''//div[@class="smoke"]/span''').text  # 是否抽烟
    except Exception:
        smoke = ''
    want_kids = ''  # 打不打算要小孩
    try:
        height = driver.find_element_by_xpath('''//div[@class="height"]/span''').text  # 身高
    except Exception:
        height = ''
    try:
        drink = driver.find_element_by_xpath('''//div[@class="drink"]/span''').text  # 喝不喝酒
    except Exception:
        drink = ''
    try:
        more = driver.find_element_by_xpath('''//div[@class="column preferences"]''').text  # 更多信息
    except Exception:
        more = ''
    try:
        INTERESTS_and_PORTS = driver.find_element_by_xpath('''//div[@class="selected-interests icons"]''').text  # 兴趣爱好
    except Exception:
        INTERESTS_and_PORTS = ''

    photo_gallery = []  # 照片库

    try:
        photo_gallery1 = driver.find_elements_by_xpath('''//img''')
        for i in photo_gallery1:
            photo_gallery1 = i.get_attribute("src")
            # print(photo_gallery1)
            photo_gallery.append(photo_gallery1)
    except Exception:
        pass

    photo_gallery = json.dumps(photo_gallery)

    # print("photo:", photo, "name:", name, 'age:', age, 'country_address:', country_address,
    #       'instructions:', instructions, "relationship:", relationship, "education:", education,
    #       "have_kids:{}".format(have_kids), "body_type:{}".format(body_type), "smoke:{}".format(smoke)
    #       , "height:{}".format(height), "drink:{}".format(drink), "more:{}".format(more),
    #       "INTERESTS_and_PORTS{}".format(INTERESTS_and_PORTS)
    #       )
    # print(photo_gallery)
    ethnicity = ''
    sex = 'Female'
    source = 'www.amolatina.com'
    ruku.ruhu(source, name, age, photo, country_address, instructions, relationship, education, faith, have_kids, body_type, smoke, want_kids, height, drink, ethnicity, more, photo_gallery, sex,
              INTERESTS_and_PORTS)

    # ActionChains(driver).key_down(Keys.ALT).send_keys("w").key_up(Keys.ALT).perform()  # 关闭标签页


def get_url(url):
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        time.sleep(5)
        driver.find_element_by_xpath('''//*[@id="fellow-to"]/div[2]/div/div/div/div/div/div[2]/form/div/l10n-attribute/div/input''').send_keys('邮箱@poling.hk')
        driver.find_element_by_xpath('''//*[@id="fellow-to"]/div[2]/div/div/div/div/div/div[2]/form/p/label/l10n-attribute/div/input''').send_keys('hua123456')
        driver.find_element_by_xpath('''//*[@id="fellow-to"]/div[2]/div/div/div/div/div/div[2]/form/button''').click()
    except Exception:
        pass
    time.sleep(5)

    url_li = set()
    # for num in range(1, 85):
    for num in range(1, 85):
        li = driver.find_elements_by_xpath('''//a[@class="profile-card"]''')
        for i in li:
            url_li.add(i.get_attribute("href"))
        driver.execute_script("window.scrollBy(0,{})".format(700))
        print("下拉了{}次".format(num))
        time.sleep(2)
        try:
            driver.find_element_by_xpath('''//div[@class="more-results"]/button[@class="small approve button"]''').click()
        except Exception:
            pass
    print(len(url_li))
    pool = ThreadPoolExecutor(1)
    index = 0
    for i in url_li:
        index += 1
        v_ = pool.submit(get_info, [i, driver, index])
        v_.add_done_callback(done)

    pool.shutdown(wait=True)

    driver.quit()


if __name__ == "__main__":
    get_url("https://www.amolatina.com/people/#")
