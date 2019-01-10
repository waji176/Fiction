from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time, re, os, sys, json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import ruku


def done(request, *args, **kwargs):  #
    result = request.result()
    # print(result, args, kwargs)


def get_info(dat):
    url = dat[0]
    driver = dat[1]
    index = dat[2]

    print(url)
    # js = 'window.open("{}");'.format(url)
    js = 'window.location.href="{}";'.format(url)
    driver.execute_script(js)
    # handles = driver.window_handles
    # driver.switch_to.window(handles[index])
    # driver = webdriver.Chrome()
    # driver.get(url)
    # driver.find_element_by_xpath('''//*[@id="nav_LR"]/a[1]''').click()
    # driver.find_element_by_xpath('''/html/body/div[2]/div[1]/div/div/div[6]/div[2]/p/span/a[1]''').click()
    # driver.find_element_by_xpath('''//*[@id="email"]''').send_keys('brian@poling.hk')
    # driver.find_element_by_xpath('''//*[@id="password"]''').send_keys('5618477')
    # driver.find_element_by_xpath(
    #     '''//*[@id="app"]/div/div[1]/div[1]/div/div/section/div/div/form/fieldset[2]/button''').click()
    time.sleep(2)
    try:
        name = driver.find_element_by_xpath('''//text[@class="_2Q6_JZN"]''').text
    except Exception:
        time.sleep(10)
        name = driver.find_element_by_xpath('''//text[@class="_2Q6_JZN"]''').text

    try:
        photo = driver.find_element_by_xpath('''//figure[@class="_1Ai3K7V _1g_rgDt"]/img''')  # 头像
        photo = photo.get_attribute('src')
    except Exception:
        photo = ''

    try:
        age = driver.find_element_by_xpath('''//ul[@class="_2u0Uxak"]/li[1]''').text
    except Exception:
        age = ''

    try:
        country_address = driver.find_element_by_xpath('''//ul[@class="_2u0Uxak"]/li[2]''').text  # 国家 地区
    except Exception:
        country_address = ''
    try:
        instructions = driver.find_element_by_xpath('''//div[@class="_2ErlQcq"]''').text  # 交友说明
    except Exception:
        instructions = ''

    try:
        relationship = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[5]/div[1]/div/ul/li[1]/div[2]''').text  # status:是否单身
        education = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[5]/div[2]/div/ul/li[1]/div[2]''').text  # 教育程度
        faith = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[5]/div[3]/div/ul/li[1]/div[2]''').text  # 宗教信仰
        have_kids = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[5]/div[1]/div/ul/li[2]/div[2]''').text  # 是否有小孩
        body_type = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[5]/div[2]/div/ul/li[2]/div[2]''').text  # 体型
        smoke = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[5]/div[3]/div/ul/li[2]/div[2]''').text  # 是否抽烟
        want_kids = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[5]/div[1]/div/ul/li[3]/div[2]''').text  # 有没有小孩
        height = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[5]/div[2]/div/ul/li[3]/div[2]''').text  # 身高
        drink = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[5]/div[3]/div/ul/li[3]/div[2]''').text  # 喝不喝酒
    except Exception:
        relationship = ''
        education = ''
        faith = ''
        have_kids = ''
        body_type = ''
        want_kids = ''
        height = ''
        drink = ''
        smoke = ''
    try:
        # ethnicity = driver.find_element_by_xpath('''//*[@id="mainContent"]/section/div/div[7]/div[2]/div/ul/li/div[2]/text/text''').text  # 种族
        # more = driver.find_element_by_xpath('''//div[@class="_1s7p-lA Csq5B6q _16Gji06"]''').text  # 更多信息
        ethnicity = ''
        more = ''
        info = driver.find_element_by_xpath('''//div[@class="_1s7p-lA Csq5B6q _16Gji06"]''').get_attribute('innerHTML')  # 更多信息
        soup = BeautifulSoup(info, 'html.parser')
        li = soup.find_all("li")
        for i in li:
            if "Ethnicity" in i.text:
                ethnicity = i.find('div', attrs={"class": "_3qQbn1K"}).text
            more += i.find('div', attrs={"class": "_2U2nqx7 _2RKQ9JC"}).text + " ： " + i.find('div', attrs={"class": "_3qQbn1K"}).text + "\n"
    except Exception:
        ethnicity = ''
        more = ''
    photo_gallery = []  # 照片库
    try:
        photo_gallerys = driver.find_elements_by_xpath('''//*[@id="mainContent"]/section/div/div[6]/section/div[1]/div/div[1]/div''')
        for i in photo_gallerys:
            photo_gallery1 = re.findall('''background-image\: url\("(.*?)"\)''', i.get_attribute("style"))[0]
            photo_gallery.append(photo_gallery1)
    except Exception:
        pass

    photo_gallery = json.dumps(photo_gallery)
    try:
        #                                                                   _2U-oEx2 _1aP6Y2w _31Q4Lr_ _1T4lQe4 _1qsxzum
        INTERESTS_and_PORTS = driver.find_element_by_xpath('''//div[@class="_2U-oEx2 _1aP6Y2w _31Q4Lr_ _1T4lQe4 _1qsxzum"]''').text  # 兴趣与体育
    except Exception:
        INTERESTS_and_PORTS = ''
    # //*[@id="mainContent"]/section/div/div[10]/div[2]/div[@class="_3wkoHVP"]/span
    # time.sleep(5)
    What_She_is_Looking_For = ''
    try:
        driver.execute_script("window.scrollBy(0,{})".format(1000))
        driver.find_element_by_xpath('''//button[@class="_3mMeNZw b_ccDtK"]''').click()
    except Exception:
        pass

    try:
        try:
            driver.find_element_by_xpath('''//div[@class="_3Wxr0_U _1XfdK-h _1r4VfO3"]/div/span''').click()
        except Exception:
            time.sleep(5)
            try:
                driver.execute_script("window.scrollBy(0,{})".format(1000))
                driver.find_element_by_xpath('''//button[@class="_3mMeNZw b_ccDtK"]''').click()
            except Exception:
                pass
            driver.find_element_by_xpath('''//div[@class="_3Wxr0_U _1XfdK-h _1r4VfO3"]/div[2]/span''').click()
        # time.sleep(5)
        info = driver.find_elements_by_xpath('''//table[@class="vdSo-eb"]''')
        infohtml = ''
        for i in info:
            infohtml += i.get_attribute('innerHTML')
        # print(infohtml)
        soup = BeautifulSoup(infohtml, 'html.parser')
        li = soup.find_all("tr", )
        for td in li:
            try:
                What_She_is_Looking_For += td.find("div", attrs={"class": "_2U2nqx7 _2RKQ9JC"}).text.strip() + " ： " + td.find("div", attrs={"class": "_3qQbn1K"}).text + " 。 ：" + td.find_all("td")[-1].text + "\n"
            except:
                pass
    except Exception as e:
        print(e)
    source = "cn.match.com"
    sex = age
    ruku.ruhu(source, name, age, photo, country_address, instructions, relationship, education, faith, have_kids, body_type, smoke, want_kids, height, drink, ethnicity, more,
              photo_gallery, sex, INTERESTS_and_PORTS, What_She_is_Looking_For)

    # ActionChains(driver).key_down(Keys.ALT).send_keys("w").key_up(Keys.ALT).perform()  # 关闭标签页


def get_all_url(url):
    # driver = webdriver.Firefox()
    driver = webdriver.Chrome()
    # driver.set_window_size(1000, 300000)
    driver.get(url)
    # driver.find_element_by_xpath('''//*[@id="nav_LR"]/a[1]''').click()
    # driver.find_element_by_xpath('''/html/body/div[2]/div[1]/div/div/div[6]/div[2]/p/span/a[1]''').click()
    # driver.find_element_by_xpath('''//*[@id="email"]''').send_keys('brainyliu@gmail.com')
    driver.find_element_by_xpath('''//*[@id="email"]''').send_keys('邮箱@poling.hk')
    # driver.find_element_by_xpath('''//*[@id="password"]''').send_keys('19734628')
    driver.find_element_by_xpath('''//*[@id="password"]''').send_keys('5618477')
    driver.find_element_by_xpath('''//*[@id="app"]/div/div[1]/div[1]/div/div/section/div/div/form/fieldset[2]/button''').click()
    url_li = set()
    time.sleep(10)
    for num in range(1, 50):
        # for num in range(1, 25):
        li = driver.find_elements_by_xpath('''//a[@class="_22cLnhm"]''')
        for i in li:
            url_li.add(i.get_attribute("href"))
        driver.execute_script("window.scrollBy(0,{})".format(700))
        print("下拉了{}次".format(num))
        time.sleep(2)

    # driver.close()

    pool = ThreadPoolExecutor(1)
    index = 0
    for i in url_li:
        index += 1
        v_ = pool.submit(get_info, [i, driver, index])
        v_.add_done_callback(done)

    pool.shutdown(wait=True)

    driver.quit()


if __name__ == "__main__":
    # get_info("http://cn.match.com/profile/Jdy-TEdZs8NyNbAiqef0Hw2?page=1&searchType=oneWaySearch&sortBy=1")
    # get_info("http://cn.match.com/profile/n8akvW7CO6gyWkxBajT18Q2?page=1&searchType=oneWaySearch&sortBy=1")
    # get_all_url("http://cn.match.com/search")
    get_all_url("http://cn.match.com/search?EXEC=GO&SB=radius&by=region&lid=226&region&st=Q&ua=120")
