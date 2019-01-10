import requests, re, threading, os, sys, time
from bs4 import BeautifulSoup
from django.core.wsgi import get_wsgi_application
from concurrent.futures import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 定位到你的django根目录
print(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fiction.settings")  # 你的django的settings文件
application = get_wsgi_application()
from app01 import models

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}

source = "花溪小说"


def done(request, *args, **kwargs):  #
    result = request.result()
    print(result, args, kwargs)


def get_Fiction():
    '''
    获取分类里面的小说列表
    :param classification_url:
    :return:
    '''
    classification_url = "https://w.huaxi.net/"
    Fiction = []
    try:
        ret = requests.get(url=classification_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=classification_url, headers=headers)
    ret.encoding = "utf-8"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', attrs={"id": "jsTab2"})
    for i in div.find_all("li"):
        fiction_name = i.find("div", attrs={"class": "book-title"}).text
        fiction_url = i.find("a", attrs={"class": "book-link"}).attrs.get("href")
        fiction_image = i.find("div", attrs={"class": "book-cover"}).img.attrs.get("src")
        author = i.find("div", attrs={"class": "book-author"}).text
        viewing_count = i.find("b", attrs={"class": "font-orenge"}).text
        # print(i)
        Fiction.append({
            "fiction_name": fiction_name,
            "fiction_url": "https:" + fiction_url,
            "fiction_image": fiction_image,
            "author": author,
            "viewing_count": viewing_count,
            "classification": "热销排行",
            "status": "",
        })
    div1 = soup.find('div', attrs={"id": "jsTab4"})
    for i in div1.find_all("li"):
        fiction_name = i.find("div", attrs={"class": "book-title"}).text
        fiction_url = i.find("a", attrs={"class": "book-link"}).attrs.get("href")
        fiction_image = i.find("div", attrs={"class": "book-cover"}).img.attrs.get("src")
        author = i.find("div", attrs={"class": "book-author"}).text
        viewing_count = i.find("b", attrs={"class": "font-orenge"}).text
        # print(i)
        Fiction.append({
            "fiction_name": fiction_name,
            "fiction_url": "https:" + fiction_url,
            "fiction_image": fiction_image,
            "author": author,
            "viewing_count": viewing_count,
            "classification": "编辑推荐",
            "status": "",
        })

    classification_url2 = ["https://w.huaxi.net/action/aspxnovellist/ajax/store?order=2",
                           "https://w.huaxi.net/action/aspxnovellist/ajax/store?vip=2&order=28"]
    for classification_url in classification_url2:
        try:
            ret = requests.get(url=classification_url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=classification_url, headers=headers)
        ret.encoding = "utf-8"
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        li = soup.find_all('li', )
        for i in li:
            fiction_name = i.find("div", attrs={"class": "book-title"}).text
            fiction_url = i.find("a", attrs={"class": "book-link"}).attrs.get("href")
            fiction_image = i.find("div", attrs={"class": "book-cover"}).img.attrs.get("src")
            author = i.find("div", attrs={"class": "book-author"}).text
            viewing_count = i.find("b", attrs={"class": "font-orenge"}).text
            status = i.find("div", attrs={"class": "book-title"}).span.text
            # print(i)
            Fiction.append({
                "fiction_name": fiction_name,
                "fiction_url": "https://w.huaxi.net" + fiction_url,
                "fiction_image": fiction_image,
                "author": author,
                "viewing_count": viewing_count,
                "classification": "最新更新",
                "status": status,
            })

    return Fiction


def get_chapter(fiction_url):
    '''
    获取小说的章节列表
    :param fiction_url:
    :return:
    '''
    fiction_url = fiction_url + "/list"
    chapter = []
    try:
        ret = requests.get(url=fiction_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=fiction_url, headers=headers)
    ret.encoding = "utf-8"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    li = soup.find_all("li", )
    for i in li:
        # print(i.a.attrs.get("href"))
        chapter_name = i.text
        chapter_url = "https:" + i.a.attrs.get("href")
        if i.img:
            is_vip = True
        else:
            is_vip = False
        chapter.append({
            "chapter_name": chapter_name,
            "chapter_url": chapter_url,
            "is_vip": is_vip,
        })
    # print(chapter)
    return chapter


def get_chapter_content(fiction_content_url, ):
    '''
    获取章节内容
    :param fiction_content_url:
    :return:
    '''
    try:
        ret = requests.get(url=fiction_content_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=fiction_content_url, headers=headers)
    ret.encoding = "utf-1"
    html = ret.text
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    try:
        chapter_update_time = soup.find("p", attrs={"class": "time-txt"}).text.strip()
        chapter_content_obj = soup.find("div", attrs={"id": "htmlContent"})
        chapter_content = '''<div id="htmlContent" class="article-text">''' + str(
            chapter_content_obj.text) + '''</div>'''
    except Exception:
        chapter_content = ''
        chapter_update_time = ''
    return {"chapter_content": chapter_content, "chapter_update_time": chapter_update_time}



def ruku(source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip,
         chapter_name, chapter_content, chapter_update_time):
    '''
    入库
    :return:
    '''
    if not models.Classification.objects.filter(name=classification, source=source).exists():
        Classification = models.Classification(name=classification, source=source)
        try:
            Classification.save()
        except Exception:
            Classification = models.Classification.objects.get(name=classification, source=source)
    else:
        Classification = models.Classification.objects.get(name=classification, source=source)

    if not models.Fiction_list.objects.filter(fiction_name=fiction_name, author=author):
        Fiction_list = models.Fiction_list(cassificationc=Classification, fiction_name=fiction_name,
                                           viewing_count=viewing_count, author=author, update_time=fiction_update_time,
                                           status=status, image=fiction_img)
        Fiction_list.save()
    else:
        models.Fiction_list.objects.filter(fiction_name=fiction_name, author=author).update(viewing_count=viewing_count,
                                                                                            update_time=fiction_update_time,
                                                                                            status=status, )
        Fiction_list = models.Fiction_list.objects.get(fiction_name=fiction_name, author=author)

    if not models.Fiction_chapter.objects.filter(chapter_name=chapter_name, fiction_name=Fiction_list):
        Fiction_chapter = models.Fiction_chapter(chapter_name=chapter_name, fiction_name=Fiction_list, is_vip=is_vip,
                                                 chapter_content=chapter_content, update_time=chapter_update_time)
        Fiction_chapter.save()
    else:
        if chapter_content:
            models.Fiction_chapter.objects.filter(chapter_name=chapter_name, fiction_name=Fiction_list).update(
                chapter_name=chapter_name, fiction_name=Fiction_list, is_vip=is_vip,
                chapter_content=chapter_content, update_time=chapter_update_time)
    print(
        "来源：{} , 分类：{} , 书名：{} , 作者：{} , 章节：{} ".format(source, classification, fiction_name, author, chapter_name)
    )


if __name__ == "__main__":
    def func(i):
        fiction_name = i['fiction_name']
        fiction_url = i['fiction_url']
        fiction_image = i['fiction_image']
        author = i['author']
        viewing_count = i['viewing_count']
        classification = i['classification']
        status = i['status']
        for chapter in get_chapter(fiction_url):
            chapter_name = chapter['chapter_name']
            chapter_url = chapter['chapter_url']
            is_vip = chapter['is_vip']
            content = get_chapter_content(chapter_url)
            chapter_content = content['chapter_content']
            chapter_update_time = content['chapter_update_time']
            fiction_update_time = chapter_update_time
            ruku(source, classification, fiction_name, fiction_image, author, viewing_count, fiction_update_time,
                 status, is_vip, chapter_name, chapter_content, chapter_update_time)


    pool = ThreadPoolExecutor(100)
    for i in get_Fiction():
        v_ = pool.submit(func, i)
        v_.add_done_callback(done)

    pool.shutdown(wait=True)
