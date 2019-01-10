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
        return len(s)
    else:
        print("找到%s个元素：%s" % (len(s), xpath))
        return len(s)


def Login(url):
    driver = webdriver.Chrome()
    driver.get("https://wordpress.com/log-in")
    While_cmd(driver, """driver.find_element_by_xpath('''//input[@name="usernameOrEmail"]''').send_keys('yaox@vangox.com')""")
    driver.find_element_by_xpath('''//button[@class="button form-button is-primary"]''').click()
    While_cmd(driver, """driver.find_element_by_xpath('''//input[@name="password"]''').send_keys('vangox123')""")
    driver.find_element_by_xpath('''//button[@class="button form-button is-primary"]''').click()
    time.sleep(1)
    js = 'window.location.href="{}";'.format(url)
    driver.execute_script(js)
    Test(driver)


def Test(driver):
    name = "OK"
    driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(name)
    time.sleep(5)
    # li_num = 0
    # while True:
    #     if is_element_exist(driver, '''//ul[@class="acf-bl list values-list ui-sortable"]/li/span[@class="acf-rel-item"]'''):
    #         break
    #     try:
    #         total = is_element_exist(driver, '''//ul[@class="acf-bl list choices-list"]/li/span''')
    #         if total:
    #             for x in range(li_num, total + 1):
    #                 li_num += 1
    #                 print(li_num, )
    #                 print(driver.find_elements_by_xpath('''//ul[@class="acf-bl list choices-list"]/li''')[x].text)
    #                 if len(str(driver.find_elements_by_xpath('''//ul[@class="acf-bl list choices-list"]/li''')[x].text).strip()) - len(name) < 3:
    #                     driver.find_element_by_xpath('''//ul[@class="acf-bl list choices-list"]/li[{}]'''.format(x + 1)).click()
    #                     break
    #         else:
    #             li_num = 0
    #             driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').clear()
    #             driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(name)
    #             time.sleep(1)
    #     except Exception as e:
    #         print(e)
    #     js = '''var div=document.getElementsByClassName("acf-bl list choices-list")[0];div.scrollTop = div.scrollHeight;'''
    #     driver.execute_script(js)


    while True:
        if is_element_exist(driver, '''//ul[@class="acf-bl list values-list ui-sortable"]/li/span[@class="acf-rel-item"]'''):
            break
        try:
            if is_element_exist(driver, '''//ul[@class="acf-bl list choices-list"]/li/span'''):
                num = 0
                for x in driver.find_elements_by_xpath('''//ul[@class="acf-bl list choices-list"]/li'''):
                    num += 1
                    if len(str(x.text).strip()) - len(str(name).replace("-", ' ').strip()) < 3 and str(x.text).strip().startswith(str(name)[0]):
                        driver.find_element_by_xpath('''//ul[@class="acf-bl list choices-list"]/li[{}]'''.format(num)).click()
                        break
                else:
                    for item in range(len(driver.find_elements_by_xpath('''//ul[@class="acf-bl list choices-list"]/li'''))):
                        js = '''var parent = document.getElementsByClassName("acf-bl list choices-list")[0];var child = parent.getElementsByTagName("li")[{}];parent.removeChild(child);'''.format(item)
                        try:
                            driver.execute_script(js)
                            print("删除成功", end=' ')
                        except Exception:
                            pass
            else:
                driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').clear()
                driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(str(name).replace("-", ' '))
                time.sleep(1)

        except Exception as e:
            print(e)
        js = '''var div=document.getElementsByClassName("acf-bl list choices-list")[0];div.scrollTop = div.scrollHeight;'''
        driver.execute_script(js)
        time.sleep(1)
    time.sleep(60)


if __name__ == "__main__":
    Login("https://4hentai.net/wp-admin/post-new.php?post_type=chapters")
