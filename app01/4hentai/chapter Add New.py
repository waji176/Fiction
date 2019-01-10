from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
import time, re, os, sys, json, requests, threading
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
        return 0
    else:
        print("找到%s个元素：%s" % (len(s), xpath))
        return len(s)


def Login(url):
    driver = webdriver.Chrome()
    driver.get("https://wordpress.com/log-in")
    While_cmd(driver, """driver.find_element_by_xpath('''//input[@name="usernameOrEmail"]''').send_keys('邮箱@vangox.com')""")
    driver.find_element_by_xpath('''//button[@class="button form-button is-primary"]''').click()

    While_cmd(driver, """driver.find_element_by_xpath('''//input[@name="password"]''').send_keys('vangox123')""")
    driver.find_element_by_xpath('''//button[@class="button form-button is-primary"]''').click()
    name_li = []
    for j in models.Hentai2read_flag.objects.all().values('name'):
        name_li.append(j['name'])
    chapter_name_li = []
    for x in models.Hentai2read_chapter_flag.objects.all().values('chapter_name'):
        chapter_name_li.append(x['chapter_name'])
    Hentai = models.Hentai2read_chapter.objects.filter(name__name__in=name_li).exclude(chapter_name__in=chapter_name_li)

    for i in Hentai:
        try:
            Add_New_Post([driver, url, i])
        except Exception as e:
            print(e)
            Login("https://4hentai.net/wp-admin/post-new.php?post_type=chapters")


def Add_New_Post(data):
    driver = data[0]
    url = data[1]
    i = data[2]
    if models.Hentai2read_chapter_flag.objects.filter(chapter_name=i.chapter_name).exists():
        print(i.chapter_name, "已经存在")
        return
    js = 'window.location.href="{}";'.format(url)
    driver.execute_script(js)
    driver.find_element_by_xpath('''//input[@name="post_title"]''').send_keys(i.chapter_name.split()[0] + " - " + str(i.name))
    # driver.find_element_by_xpath('''//input[@name="acf[field_5a1123bb8350a]"]''').send_keys(i.chapter_name[0] + " - " + str(i.name))
    time.sleep(1)
    driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(str(i.name).replace("-", ' '))
    time.sleep(1)
    # flag = False
    # scrollTop = 10000
    # li_num = 0
    # while True:
    #     # if flag: break
    #     if is_element_exist(driver, '''//ul[@class="acf-bl list values-list ui-sortable"]/li/span[@class="acf-rel-item"]'''):
    #         break
    #     try:
    #         if is_element_exist(driver, '''//ul[@class="acf-bl list choices-list"]/li/span'''):
    #             num = 0
    #             for x in driver.find_elements_by_xpath('''//ul[@class="acf-bl list choices-list"]/li'''):
    #                 num += 1
    #                 if num <= li_num: continue
    #                 li_num += 1
    #                 # print(li_num, "----------", num)
    #                 if len(str(x.text).strip()) - len(str(i.name).replace("-", ' ').strip()) < 3 and str(x.text).strip().startswith(str(i.name)[0]):
    #                     driver.find_element_by_xpath('''//ul[@class="acf-bl list choices-list"]/li[{}]'''.format(num)).click()
    #                     # flag = True
    #                     break
    #         else:
    #             driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').clear()
    #             driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(str(i.name).replace("-", ' '))
    #             time.sleep(1)
    #
    #         # js = 'document.getElementsByClassName("acf-bl list choices-list")[0].scrollTop={}'.format(scrollTop)
    #         # driver.execute_script(js)
    #         # js = '''var div=document.getElementsByClassName("acf-bl list choices-list")[0];div.scrollTop = div.scrollHeight;'''
    #         # driver.execute_script(js)
    #     except Exception as e:
    #         print(e)
    #     # scrollTop += 10000
    #     js = '''var div=document.getElementsByClassName("acf-bl list choices-list")[0];div.scrollTop = div.scrollHeight;'''
    #     driver.execute_script(js)
    #     time.sleep(0.5)
    while True:
        if is_element_exist(driver, '''//ul[@class="acf-bl list values-list ui-sortable"]/li/span[@class="acf-rel-item"]'''):
            break
        try:
            if is_element_exist(driver, '''//ul[@class="acf-bl list choices-list"]/li/span''') == 1:
                driver.find_element_by_xpath('''//ul[@class="acf-bl list choices-list"]/li''').click()
                break
            if is_element_exist(driver, '''//ul[@class="acf-bl list choices-list"]/li/span'''):
                num = 0
                for x in driver.find_elements_by_xpath('''//ul[@class="acf-bl list choices-list"]/li'''):
                    num += 1
                    if len(str(x.text).strip()) - len(str(i.name).replace("-", ' ').strip()) < 3 and str(x.text).strip().startswith(str(i.name)[0]):
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
                driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(str(i.name).replace("-", ' '))
                time.sleep(1)

        except Exception as e:
            print(e)
        js = '''var div=document.getElementsByClassName("acf-bl list choices-list")[0];div.scrollTop = div.scrollHeight;'''
        driver.execute_script(js)
        time.sleep(1)

    driver.find_element_by_xpath('''//input[@id="acf-field_5a21994feb83e-External"]''').click()
    url_li = ''
    for j in models.Hentai2read_img.objects.filter(chapter_name__chapter_name=i.chapter_name).order_by("img_index"):
        url_li += j.image + "\n"
    driver.find_element_by_xpath('''//textarea[@name="acf[field_5a21989692339]"]''').send_keys(url_li.strip())

    driver.find_element_by_xpath('''//input[@id="pms-content-restrict-user-status"]''').click()
    time.sleep(1)
    try:
        driver.find_element_by_xpath('''//input[@id="pms-content-restrict-subscription-plan-8665"]''').click()
        driver.find_element_by_xpath('''//input[@id="pms-content-restrict-subscription-plan-8676"]''').click()
    except Exception as e:
        print(e)

    js = """var q=document.documentElement.scrollTop=0;"""
    driver.execute_script(js)

    # driver.find_element_by_xpath('''//a[@class="edit-visibility hide-if-no-js"]''').click()
    # While_cmd(driver, """driver.find_element_by_xpath('''//input[@id="visibility-radio-private"]''').click()""")
    # While_cmd(driver, """driver.find_element_by_xpath('''//a[@class="save-post-visibility hide-if-no-js button"]''').click()""")
    # time.sleep(5)

    driver.find_element_by_xpath('''//input[@id="publish"]''').click()
    print(i.chapter_name, "提交成功")
    time.sleep(5)
    models.Hentai2read_chapter_flag.objects.create(chapter_name=i.chapter_name)


if __name__ == "__main__":
    while 1:
        Login("https://4hentai.net/wp-admin/post-new.php?post_type=chapters")
        time.sleep(300)
