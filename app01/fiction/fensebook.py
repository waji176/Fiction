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

source = "粉色书城"
classification_url = [
    "http://www.fensebook.com/index.php/Book/Booklist/catId/0/vips/0/words/0/progress/0/order/0/time/0/p/" +
    str(page) for page in range(1, 364)
]


def done(request, *args, **kwargs):
    result = request.result()
    print(result, args, kwargs)


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
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', attrs={"class": "booklist"}).table.tbody
    for tr in div.find_all("tr"):
        fiction_name = tr.find_all("td")[1].find("a", attrs={"class": "title"}).text
        fiction_url = tr.find_all("td")[1].find("a", attrs={"class": "title"}).attrs.get("href")
        author = tr.find_all("td")[2].text
        viewing_count = tr.find_all("td")[4].text
        fiction_update_time = tr.find_all("td")[5].text
        # print(fiction_name,fiction_url,author,viewing_count,fiction_update_time)
        Fiction.append({
            "fiction_name": fiction_name,
            "fiction_url": "http://www.fensebook.com" + fiction_url,
            "author": author,
            "viewing_count": viewing_count,
            "fiction_update_time": fiction_update_time,
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
    ret.encoding = "utf-8"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find("div", attrs={"class": "one1-left clearfix"})
    fiction_img = div.find_all("img")[1].attrs.get("src")
    status = soup.find("p", attrs={"class": "book-index-lable"}).span.text
    fiction_url = "http://www.fensebook.com" + soup.find("div", attrs={"class": "one2"}).ul.li.div.a.attrs.get("href")
    try:
        ret = requests.get(url=fiction_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=fiction_url, headers=headers)
    ret.encoding = "utf-8"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    classification = soup.find("p", attrs={"class": "fl book-label"}).span.text
    ul = soup.find("ul", attrs={"class": "directory-list clearfix"})
    for li in ul.find_all("li"):
        chapter_name = li.a.p.text
        chapter_url = "http://www.fensebook.com" + li.a.attrs.get("href")
        if li.a.p.img:
            is_vip = True
        else:
            is_vip = False
        # print(chapter_name, chapter_url, is_vip)
        chapter.append({
            "classification": classification,
            "chapter_name": chapter_name,
            "chapter_url": chapter_url,
            "is_vip": is_vip,
            "fiction_img": fiction_img,
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
    ret.encoding = "utf-8"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    try:
        chapter_update_time = soup.find("div", attrs={"class": "til"}).p.find_all("span")[1].text
        chapter_update_time = chapter_update_time.replace("发布时间：", '')
        chapter_content = soup.find("div", attrs={"class": "main_read read-con"})
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


def func(Fiction):
    fiction_name = Fiction['fiction_name']
    fiction_url = Fiction['fiction_url']
    author = Fiction['author']
    viewing_count = Fiction['viewing_count']
    fiction_update_time = Fiction['fiction_update_time']
    for chapter in get_chapter(fiction_url):
        classification = chapter['classification']
        fiction_img = chapter['fiction_img']
        status = chapter['status']
        chapter_name = chapter['chapter_name']
        chapter_url = chapter['chapter_url']
        is_vip = chapter['is_vip']
        content = get_chapter_content(chapter_url)
        chapter_content = content['chapter_content']
        chapter_update_time = content['chapter_update_time']
        fiction_update_time = chapter_update_time
        ruku(source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status,
             is_vip, chapter_name, chapter_content, chapter_update_time)


if __name__ == "__main__":
    # print(get_Fiction(
    #     "http://www.fensebook.com/index.php/Book/Booklist/catId/0/vips/0/words/0/progress/0/order/0/time/0/p/1"))
    # print(get_chapter("http://www.fensebook.com/index.php/Book/Index/id/2117542"))
    # get_chapter_content("http://www.fensebook.com/index.php/Book/Read/bid/2117542/cid/36214136")
    for c_url in classification_url:
        pool = ThreadPoolExecutor(100)
        for Fiction in get_Fiction(c_url):
            v_ = pool.submit(func, Fiction)
            v_.add_done_callback(done)

        pool.shutdown(wait=True)
