from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
import time, re, os, sys, json, requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from django.core.wsgi import get_wsgi_application

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 定位到你的django根目录
print(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fiction.settings")  # 你的django的settings文件
application = get_wsgi_application()
from app01 import models
from django.db import connection


def read_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    nRet = cursor.fetchall()
    return nRet


def done(request, *args, **kwargs):  #
    result = request.result()
    print(result)


def While_cmd(driver, cmd):
    while True:
        try:
            exec(cmd)
        except Exception as e:
            # print(e)
            time.sleep(0.5)
        else:
            break


def is_element_exist(driver, xpath):
    s = driver.find_elements_by_xpath(xpath)
    if len(s) == 0:
        print("元素未找到:%s" % xpath)
        return False
    elif len(s) == 1:
        return True
    else:
        print("找到%s个元素：%s" % (len(s), xpath))
        return False


def Login(url):
    driver = webdriver.Chrome()
    driver.get(url)
    # try:
    #     with open("cookies.txt", "r") as fp:
    #         cookies = json.load(fp)
    #         for cookie in cookies:
    #             driver.add_cookie(cookie)
    #     js = 'window.location.href="{}";'.format(url)
    #     driver.execute_script(js)
    # except Exception as e:
    #     print(e)
    While_cmd(driver, """driver.find_element_by_xpath('''//input[@name="usernameOrEmail"]''').send_keys('邮箱@vangox.com')""")
    driver.find_element_by_xpath('''//button[@class="button form-button is-primary"]''').click()
    While_cmd(driver, """driver.find_element_by_xpath('''//input[@name="password"]''').send_keys('vangox123')""")
    driver.find_element_by_xpath('''//button[@class="button form-button is-primary"]''').click()
    # print(driver.get_cookies())
    # cookies = driver.get_cookies()
    # with open("cookies.txt", "w") as fp:
    #     json.dump(cookies, fp)
    while True:
        Del(driver)


def Del(driver):
    While_cmd(driver, """driver.find_element_by_xpath('''//input[@id="cb-select-all-1"]''').click()""")
    s1 = Select(driver.find_element_by_xpath('''//select[@id="bulk-action-selector-top"]'''))  # 实例化Select
    s1.select_by_value("delete")  # 选择value="xxx    "的项
    driver.find_element_by_xpath('''//input[@id="doaction"]''').click()


if __name__ == "__main__":
    # Login("https://4hentai.net/wp-admin/edit.php?post_type=chapters")
    # Login("https://4hentai.net/wp-admin/edit.php?post_status=trash&post_type=mangas&paged=1")
    Login("https://4hentai.net/wp-admin/edit.php?post_status=trash&post_type=chapters")
