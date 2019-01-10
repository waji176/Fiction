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


def main(url):
    driver = webdriver.Chrome("D:\\chromedriver.exe")
    driver.get(url)
    # fiction_img = driver.find_element_by_xpath('''//div[@class="page_container"]/img''').get_attribute("src")
    fiction_img = "https://img30.360buyimg.com/ebookadmin/jfs/t5098/313/1865794756/161412/7eccda48/591512c6Na0e6247c.jpg"
    author = "郝景芳"
    for i in range(10):
        js = '''window.scrollBy(0,{});'''.format(i * 1000)
        driver.execute_script(js)
        time.sleep(1)
    content = driver.find_element_by_xpath('''//div[@id="JD_content"]''').text

    Classification = models.Classification(source="京东", name="其他")
    Classification.save()
    fiction = models.Fiction_list(cassificationc=Classification, fiction_name="北京折叠", author=author, status="完成", image=fiction_img)
    fiction.save()
    chapter = models.Fiction_chapter(fiction_name=fiction, chapter_name="北京折叠", chapter_content=content)
    chapter.save()


if __name__ == '__main__':
    main("https://cread.jd.com/read/startRead.action?bookId=30341192&readType=1")
