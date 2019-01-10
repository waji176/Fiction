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
    driver.get("https://wordpress.com/log-in")
    While_cmd(driver, """driver.find_element_by_xpath('''//input[@name="usernameOrEmail"]''').send_keys('邮箱@vangox.com')""")
    driver.find_element_by_xpath('''//button[@class="button form-button is-primary"]''').click()

    While_cmd(driver, """driver.find_element_by_xpath('''//input[@name="password"]''').send_keys('vangox123')""")
    driver.find_element_by_xpath('''//button[@class="button form-button is-primary"]''').click()

    li = read_sql('''select name_id from app01_hentai2read_chapter where id in ( select chapter_name_id from app01_hentai2read_img group by chapter_name_id having count(chapter_name_id)<3)''')
    id_in = []
    for i in li:
        id_in.append(i[0])
    li1 = read_sql('''select name_id from app01_hentai2read_chapter where id in ( select chapter_name_id from app01_hentai2read_img where img_index=1  )''')
    id_in1 = []
    for i in li1:
        id_in1.append(i[0])
    name_li = []
    for j in models.Hentai2read_flag.objects.all().values('name'):
        name_li.append(j['name'])
    Hentai = models.Hentai2read.objects.exclude(name__in=name_li).filter(id__in=id_in1).exclude(id__in=id_in)

    for i in Hentai:
        try:
            Add_New_Post([driver, url, i])
        except Exception as e:
            print(e)
            Login("https://4hentai.net/wp-admin/post-new.php?post_type=mangas")


def Add_New_Post(data):
    driver = data[0]
    url = data[1]
    i = data[2]
    if models.Hentai2read_flag.objects.filter(name=i.name).exists():
        print(i.name, "已经存在")
        return

    try:
        js = 'window.location.href="{}";'.format(url)
        driver.execute_script(js)
        driver.find_element_by_xpath('''//a[@id="set-post-thumbnail"]''').click()
    except Exception as e:
        print("------------------------弹出框点取消----------------------------------", e)
        time.sleep(5)
        dig_confirm = driver.switch_to.alert  # 获取confirm对话框
        time.sleep(1)
        dig_confirm.dismiss()  # 点击“取消”按钮
        time.sleep(10)
        driver.find_element_by_xpath('''//input[@id="publish"]''').click()
        time.sleep(10)
        driver.close()
        return

    While_cmd(driver, """driver.find_element_by_xpath('''//button[@id="__wp-uploader-id-1"]''').click()""")
    req = requests.get(url=i.cover_image)
    print(i.cover_image)
    with open("D:\\1.jpg", "wb") as f:
        f.write(req.content)
    os.system("upfile.exe")
    while True:
        if is_element_exist(driver, '''//div[@class="centered"]/img'''):  # 当图片没有上传完成一直循环
            if is_element_exist(driver, '''//li[@aria-checked="false"]'''):
                driver.find_element_by_xpath('''//div[@class="centered"]/img''').click()
            if is_element_exist(driver, '''//li[@aria-checked="true"]'''):
                driver.find_element_by_xpath('''//button[@class="button media-button button-primary button-large media-button-select"]''').click()
                break
        time.sleep(3)

    driver.find_element_by_xpath('''//input[@name="post_title"]''').send_keys(i.name.replace("-", ' '))
    driver.find_element_by_xpath('''//textarea[@name="acf[field_59ff44bdc167a]"]''').send_keys(i.name + i.Parody)
    driver.find_element_by_xpath('''//input[@name="acf[field_59ff4518c167b]"]''').send_keys("2018")
    driver.find_element_by_xpath('''//textarea[@name="acf[field_5a03bbccbd712]"]''').send_keys(i.name + i.Parody)
    driver.find_element_by_xpath('''//input[@name="ping_status"]''').click()
    categorychecklist = driver.find_element_by_xpath('''//ul[@id="categorychecklist"]''').get_attribute('innerHTML')
    soup = BeautifulSoup(categorychecklist, 'html.parser')
    for j in soup.find_all("li"):
        if i.Content.strip() == j.text.strip():
            driver.find_element_by_xpath('''//li[@id="{}"]/label/input'''.format(j.attrs.get("id"))).click()
    driver.find_element_by_xpath('''//a[@id="category-add-toggle"]''').click()
    driver.find_element_by_xpath('''//input[@name="newcategory"]''').send_keys(i.Content)
    driver.find_element_by_xpath('''//input[@id="category-add-submit"]''').click()

    # WebDriverWait(driver, 30, poll_frequency=0.5, ignored_exceptions=None).until(lambda x: driver.find_element_by_xpath('''//button[@calss="button media-button button-primary button-large media-button-select"]''').click())
    js = """var q=document.documentElement.scrollTop=0;"""
    driver.execute_script(js)
    driver.find_element_by_xpath('''//input[@id="publish"]''').click()

    print(i.name, "提交成功")
    driver.find_element_by_xpath('''//input[@id="publish"]''').click()
    models.Hentai2read_flag.objects.create(name=i.name)

    Hentai = models.Hentai2read_chapter.objects.filter(name=i)
    for j in Hentai:
        Add_New_Post_chapter([driver, url, j])


def Add_New_Post_chapter(data):
    def is_element_exist(driver, xpath):
        s = driver.find_elements_by_xpath(xpath)
        if len(s) == 0:
            print("元素未找到:%s" % xpath)
            return 0
        else:
            print("找到%s个元素：%s" % (len(s), xpath))
            return len(s)

    driver = data[0]
    url = "https://4hentai.net/wp-admin/post-new.php?post_type=chapters"
    i = data[2]
    if models.Hentai2read_chapter_flag.objects.filter(chapter_name=i.chapter_name).exists():
        print(i.chapter_name, "已经存在")
        return
    try:
        js = 'window.location.href="{}";'.format(url)
        driver.execute_script(js)
        driver.find_element_by_xpath('''//input[@name="post_title"]''').send_keys(i.chapter_name.split()[0] + " - " + str(i.name))
    except Exception as e:
        print("------------------------弹出框点取消----------------------------------", e)
        time.sleep(5)
        dig_confirm = driver.switch_to.alert  # 获取confirm对话框
        time.sleep(1)
        dig_confirm.dismiss()  # 点击“取消”按钮
        time.sleep(10)
        driver.find_element_by_xpath('''//input[@id="publish"]''').click()
        time.sleep(10)
        driver.close()
        return

    # driver.find_element_by_xpath('''//input[@name="acf[field_5a1123bb8350a]"]''').send_keys(i.chapter_name[0] + " - " + str(i.name))
    time.sleep(1)
    driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(str(i.name).replace("-", ' '))
    time.sleep(1)

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

    driver.find_element_by_xpath('''//input[@id="publish"]''').click()
    print(i.chapter_name, "提交成功")
    time.sleep(5)
    models.Hentai2read_chapter_flag.objects.create(chapter_name=i.chapter_name)


if __name__ == "__main__":
    Login("https://4hentai.net/wp-admin/post-new.php?post_type=mangas")
    print("已经完成")
