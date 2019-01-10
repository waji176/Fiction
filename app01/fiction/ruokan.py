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

source = "若看小说网"

classification_url = [
    "http://www.ruokan.net/book/lastupdate_0_0_0_0_0_0_0_0_" +
    str(page) for page in range(1, 10218)
]


def get_Fiction(classification_url):
    '''
    获取分类里面的小说列表
    :param classification_url:
    :return:
    '''
    Fiction = []
    try:
        ret = requests.get(url=classification_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=classification_url, headers=headers)
    ret.encoding = 'gbk'
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    ul = soup.find('ul', attrs={"class": "list-filter clearfix"})
    for i in ul.find_all("li"):
        span = i.find_all("span")
        classification = span[0].text
        fiction_name = span[1].a.text
        fiction_url = "http://www.ruokan.net" + span[1].a.attrs.get("href")
        author = span[2].text
        fiction_update_time = span[3].text
        # print(classification, fiction_name, fiction_url, author, fiction_update_time)
        Fiction.append({
            "classification": classification,
            "fiction_name": fiction_name,
            "fiction_url": fiction_url,
            "fiction_update_time": fiction_update_time,
            "author": author,
        })
    return Fiction


def get_chapter(fiction_url):
    '''
    获取小说的章节列表
    :param fiction_url:
    :return:
    '''
    chapter = []
    try:
        ret = requests.get(url=fiction_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=fiction_url, headers=headers)
    ret.encoding = "gbk"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    fiction_img = soup.find('a', attrs={"class": "img"}).img.attrs.get("src")
    status = soup.find('a', attrs={"class": "img"}).span.text
    li = soup.find_all("li", attrs={"class": "odd"})
    author = li[0].p.text
    viewing_count = li[1].p.text
    fiction_update_time = li[2].p.text
    # print(author, viewing_count, fiction_update_time,fiction_img)
    fiction_url = soup.find("div", attrs={"class": "handle"}).a.attrs.get("href")
    try:
        ret = requests.get(url=fiction_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=fiction_url, headers=headers)
    ret.encoding = "gbk"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    for li in soup.find("ul", attrs={"class": "clearfix"}).find_all("li"):
        chapter_name = li.text
        chapter_url = "http://www.ruokan.net" + li.a.attrs.get("href")
        # print(chapter_name, chapter_url)
        chapter.append({
            "chapter_name": chapter_name,
            "chapter_url": chapter_url,
            "fiction_img": fiction_img,
            "author": author,
            "viewing_count": viewing_count,
            "fiction_update_time": fiction_update_time,
            "status": status,
        })
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
    ret.encoding = "gbk"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    try:
        chapter_update_time = soup.find("span", attrs={"class": "time"}).text
        chapter_update_time = chapter_update_time.replace("更新时间：", '')
        chapter_content = soup.find("div", attrs={"class": "content clearfix"})
        chapter_content = str(chapter_content)

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
            # print(classification, source)
            Classification.save()
        except Exception as e:
            # print(e)
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


def done(request, *args, **kwargs):
    result = request.result()
    print(result, args, kwargs)


def func(c_url):
    c_url = c_url + ".html"
    # print(c_url)
    for fiction in get_Fiction(c_url):
        classification = fiction['classification']
        fiction_name = fiction['fiction_name']
        fiction_url = fiction['fiction_url']
        fiction_update_time = fiction['fiction_update_time']
        author = fiction['author']
        for chapter in get_chapter(fiction_url):
            is_vip = False
            chapter_name = chapter['chapter_name']
            chapter_url = chapter['chapter_url']
            fiction_img = chapter['fiction_img']
            status = chapter['status']
            viewing_count = chapter['viewing_count']
            content = get_chapter_content(chapter_url)
            chapter_content = content['chapter_content']
            chapter_update_time = content['chapter_update_time']
            ruku(source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status,
                 is_vip, chapter_name, chapter_content, chapter_update_time)


if __name__ == "__main__":
    # print(get_Fiction("http://www.ruokan.net/book/lastupdate_0_0_0_0_0_0_0_0_1.html"))
    # print(get_chapter("http://www.ruokan.net/book/457671/"))
    # print(get_chapter_content("http://www.ruokan.net/book/457671/30249721.html"))
    pool = ThreadPoolExecutor(5)
    for c_url in classification_url:
        v_ = pool.submit(func, c_url)
        v_.add_done_callback(done)
    pool.shutdown(wait=True)
