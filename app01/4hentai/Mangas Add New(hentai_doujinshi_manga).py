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

    name_li = []
    for j in models.Hentai_flag.objects.all().values('name'):
        name_li.append(j['name'])
    li = read_sql('''select t1.id from app01_hentai t1, (select count(name_id) as img_num,name_id from app01_hentai_img group by name_id) t2 where replace(t1.length,' pages','')=t2.img_num and t1.id=t2.name_id;''')
    id_in = []
    for i in li:
        id_in.append(i[0])
    Hentai = models.Hentai.objects.exclude(name__in=name_li).filter( id__in=id_in)

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
    if models.Hentai_flag.objects.filter(name=i.name).exists():
        print(i.name, "已经存在")
        return
    while 1:
        try:
            js = 'window.location.href="{}";'.format(url)
            driver.execute_script(js)
            driver.find_element_by_xpath('''//a[@id="set-post-thumbnail"]''').click()
        except Exception:
            print("------------------------弹出框点取消----------------------------------")
            time.sleep(2)
            dig_confirm = driver.switch_to.alert  # 获取confirm对话框
            time.sleep(1)
            dig_confirm.dismiss()  # 点击“取消”按钮
            time.sleep(10)
            driver.find_element_by_xpath('''//input[@id="publish"]''').click()
            time.sleep(6)
        else:
            break

    While_cmd(driver, """driver.find_element_by_xpath('''//button[@id="__wp-uploader-id-1"]''').click()""")
    cover_image = models.Hentai_img.objects.filter(name_id=i.id).order_by('sort')[0].image
    req = requests.get(url=cover_image)
    print(cover_image)
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

    name = re.sub("\W", ' ', i.name)
    driver.find_element_by_xpath('''//input[@name="post_title"]''').send_keys(name)
    # driver.find_element_by_xpath('''//input[@name="post_title"]''').send_keys(i.name.replace("-", ' ').replace("{", ' ').replace("}", ' ').replace("[", ' ').replace("]", ' '))
    driver.find_element_by_xpath('''//textarea[@name="acf[field_59ff44bdc167a]"]''').send_keys(i.name)
    driver.find_element_by_xpath('''//input[@name="acf[field_59ff4518c167b]"]''').send_keys("2018")
    driver.find_element_by_xpath('''//textarea[@name="acf[field_5a03bbccbd712]"]''').send_keys(i.name)
    driver.find_element_by_xpath('''//input[@name="ping_status"]''').click()
    categorychecklist = driver.find_element_by_xpath('''//ul[@id="categorychecklist"]''').get_attribute('innerHTML')
    soup = BeautifulSoup(categorychecklist, 'html.parser')
    for j in soup.find_all("li"):
        if i.classification.strip() == j.text.strip():
            driver.find_element_by_xpath('''//li[@id="{}"]/label/input'''.format(j.attrs.get("id"))).click()
    driver.find_element_by_xpath('''//a[@id="category-add-toggle"]''').click()
    driver.find_element_by_xpath('''//input[@name="newcategory"]''').send_keys(i.classification)
    driver.find_element_by_xpath('''//input[@id="category-add-submit"]''').click()

    # WebDriverWait(driver, 30, poll_frequency=0.5, ignored_exceptions=None).until(lambda x: driver.find_element_by_xpath('''//button[@calss="button media-button button-primary button-large media-button-select"]''').click())
    js = """var q=document.documentElement.scrollTop=0;"""
    driver.execute_script(js)
    driver.find_element_by_xpath('''//input[@id="publish"]''').click()

    print(i.name, "提交成功")
    driver.find_element_by_xpath('''//input[@id="publish"]''').click()
    models.Hentai_flag.objects.create(name=i.name)
    Add_New_Post_chapter(data)


def Add_New_Post_chapter(data):
    driver = data[0]
    url = "https://4hentai.net/wp-admin/post-new.php?post_type=chapters"
    i = data[2]
    while 1:
        try:
            js = 'window.location.href="{}";'.format(url)
            driver.execute_script(js)
            driver.find_element_by_xpath('''//input[@name="post_title"]''').send_keys("1" + " - " + str(i.name))
        except Exception:
            print("------------------------弹出框点取消----------------------------------")
            time.sleep(2)
            dig_confirm = driver.switch_to.alert  # 获取confirm对话框
            time.sleep(1)
            dig_confirm.dismiss()  # 点击“取消”按钮
            time.sleep(10)
            driver.find_element_by_xpath('''//input[@id="publish"]''').click()
            time.sleep(6)
        else:
            break

    # driver.find_element_by_xpath('''//input[@name="acf[field_5a1123bb8350a]"]''').send_keys("1" + " - " + str(i.name))
    time.sleep(1)
    name = re.sub("\W", ' ', i.name)
    driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(name)
    # driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(str(i.name).replace("-", ' ').replace("{", ' ').replace("}", ' ').replace("[", ' ').replace("]", ' '))
    time.sleep(1)

    def is_element_exist(driver, xpath):
        s = driver.find_elements_by_xpath(xpath)
        if len(s) == 0:
            print("元素未找到:%s" % xpath)
            return 0
        else:
            print("找到%s个元素：%s" % (len(s), xpath))
            return len(s)

    flag = False
    while True:
        # if flag: break
        if is_element_exist(driver, '''//ul[@class="acf-bl list values-list ui-sortable"]/li/span[@class="acf-rel-item"]'''):
            break
        if is_element_exist(driver, '''//ul[@class="acf-bl list choices-list"]/li/span''') == 1:
            driver.find_element_by_xpath('''//ul[@class="acf-bl list choices-list"]/li''').click()
            break
        elif is_element_exist(driver, '''//ul[@class="acf-bl list choices-list"]/li/span'''):
            num = 0
            for x in driver.find_elements_by_xpath('''//ul[@class="acf-bl list choices-list"]/li'''):
                num += 1
                if len(str(x.text).strip()) - len(name) < 3:
                    driver.find_element_by_xpath('''//ul[@class="acf-bl list choices-list"]/li[{}]'''.format(num)).click()
                    # flag = True
                    break
        else:
            driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').clear()
            driver.find_element_by_xpath('''//input[@placeholder="Search..."]''').send_keys(name)
        js = 'document.getElementsByClassName("acf-bl list choices-list")[0].scrollTop=10000'
        driver.execute_script(js)
        time.sleep(1)
    driver.find_element_by_xpath('''//input[@id="acf-field_5a21994feb83e-External"]''').click()
    url_li = ''
    for j in models.Hentai_img.objects.filter(name_id=i.id).order_by("sort"):
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
    print(i.name, "提交成功")
    driver.find_element_by_xpath('''//input[@id="publish"]''').click()
    models.Hentai_chapter_flag.objects.create(chapter_name=i.name)


if __name__ == "__main__":
    Login("https://4hentai.net/wp-admin/post-new.php?post_type=mangas")
