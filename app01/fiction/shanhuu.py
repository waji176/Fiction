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
classification_url = ["http://www.shanhuu.com/modules/article/toplist.php?order=allvisit&page=" + str(page) for page in
                      range(1, 4)]


def done(request, *args, **kwargs):  #
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
    ret.encoding = "gbk"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    tr = soup.find_all('tr', )
    pool = ThreadPoolExecutor(100)

    def func(i):
        td = i.find_all("td")
        if not td: return
        fiction_name = td[0].find_all("a")[1].text
        fiction_url = td[0].find_all("a")[1].attrs.get("href")
        try:
            ret = requests.get(url=fiction_url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=fiction_url, headers=headers)
        ret.encoding = "gbk"
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        # fiction_img = soup.find('div', attrs={"class": "divbox"}).img.attrs.get("src")
        fiction_img = soup.find('div', attrs={"class": "divbox"}).a.attrs.get("href")
        # print(fiction_img)
        fiction_url = td[0].find_all("a")[0].attrs.get("href")
        author = td[2].text
        viewing_count = td[3].text
        update_time = td[4].text
        status = td[5].text
        Fiction.append({
            "fiction_name": fiction_name,
            "fiction_img": fiction_img,
            "fiction_url": fiction_url,
            "author": author,
            "viewing_count": viewing_count,
            "fiction_update_time": update_time,
            "status": status,
        })

    for i in tr:
        v_ = pool.submit(func, i)
        v_.add_done_callback(done)
    pool.shutdown(wait=True)
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
    div = soup.find("div", attrs={"class": "linkleft"})
    classification = div.find_all("a")[1].text
    dl = soup.find("dl", attrs={"class": "index"})
    for i in dl.find_all("dd"):
        if i.em:
            is_vip = True
        else:
            is_vip = False
        chapter.append({
            "is_vip": is_vip,
            "chapter_name": i.a.text,
            "chapter_url": i.a.attrs.get("href"),
            "classification": classification,
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
    div1 = soup.find("div", attrs={"id": "acontent"})
    chapter_content = str(div1).replace("display:none;", "")
    chapter_update_time = soup.find("div", attrs={"class": "ainfo"}).text.split("：")[2].split("\xa0\xa0\xa0\xa0")[0]
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
    # Fiction=get_Fiction("http://www.shanhuu.com/modules/article/toplist.php?order=allvisit&page=1")
    # print(Fiction)
    # chapter = get_chapter("http://www.shanhuu.com/html/60/60557/index.html")
    # print(chapter)
    # get_chapter_content("http://www.shanhuu.com/html/60/60557/114161.html")
    source = "珊瑚文学"


    def func(fiction):
        fiction_url = fiction["fiction_url"]
        fiction_name = fiction["fiction_name"]
        fiction_img = fiction["fiction_img"]
        author = fiction["author"]
        viewing_count = fiction["viewing_count"]
        fiction_update_time = fiction["fiction_update_time"]
        status = fiction["status"]

        chapter_list = get_chapter(fiction_url)
        for chapter in chapter_list:
            is_vip = chapter['is_vip']
            classification = chapter['classification']
            chapter_name = chapter['chapter_name']
            chapter_url = chapter['chapter_url']
            get_chapter_contents = get_chapter_content(chapter_url)
            chapter_content = get_chapter_contents['chapter_content']
            chapter_update_time = get_chapter_contents['chapter_update_time']
            ruku(source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status,
                 is_vip, chapter_name, chapter_content, chapter_update_time)


    for c_url in classification_url:
        Fiction = get_Fiction(c_url)

        pool = ThreadPoolExecutor(100)
        for fiction in Fiction:
            v_ = pool.submit(func, fiction)
            v_.add_done_callback(done)

        pool.shutdown(wait=True)
