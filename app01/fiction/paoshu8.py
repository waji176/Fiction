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

Fiction_url = ["http://www.paoshu8.com/0_" + str(page) for page in range(1, 14624)]


def get_chapter(fiction_url):
    '''
    获取小说的章节列表
    :param fiction_url:
    :return:
    '''
    chapter_url = []
    try:
        ret = requests.get(url=fiction_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=fiction_url, headers=headers)
    ret.encoding = "gbk"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    dl = soup.find('dl', )
    for url in dl.find_all("a"):
        # print(url.attrs.get("href"))
        chapter_url.append("http://www.paoshu8.com" + url.attrs.get("href"))
    div = soup.find('div', attrs={"id": "maininfo"})
    author = div.find("p").text.split("：")[1]

    return {"chapter_url": chapter_url, "author": author}


def get_chapter_content(fiction_content_url, author):
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
    div1 = soup.find("div", attrs={"class": "con_top"})
    text = div1.text.split(">")
    Classification = text[1].strip()
    fiction_name = text[2].strip()
    chapter_name = text[3].strip()
    chapter_content = ''
    div2 = soup.find("div", attrs={"id": "content"})
    for j in div2:
        chapter_content += str(j)
    # print("分类：{} , 书名：{} , 作者：{} , 章节：{} ".format(Classification, fiction_name, author, chapter_name))
    return {"chapter_content": chapter_content, "chapter_name": chapter_name, "fiction_name": fiction_name,
            "author": author, "cassificationc": Classification}



def ruku(fiction_url):
    '''
    入库
    :param fiction_url:
    :return:
    '''
    chapter_list = get_chapter(fiction_url)
    for v2 in chapter_list['chapter_url']:
        chapter_content = get_chapter_content(v2, chapter_list['author'])
        # print(chapter_content)
        if not models.Classification.objects.filter(name=chapter_content.get("cassificationc"), source="笔趣阁").exists():
            Classification = models.Classification(name=chapter_content.get("cassificationc"), source="笔趣阁")
            try:
                Classification.save()
            except Exception:
                pass
        else:
            Classification = models.Classification.objects.get(name=chapter_content.get("cassificationc"))

        if not models.Fiction_list.objects.filter(fiction_name=chapter_content.get("fiction_name"),
                                                  author=chapter_content.get("author")):
            Fiction_list = models.Fiction_list(cassificationc=Classification,
                                               fiction_name=chapter_content.get("fiction_name"),
                                               author=chapter_content.get("author"))
            Fiction_list.save()
        else:
            Fiction_list = models.Fiction_list.objects.get(fiction_name=chapter_content.get("fiction_name"),
                                                           author=chapter_content.get("author"))
        if not models.Fiction_chapter.objects.filter(chapter_name=chapter_content.get("chapter_name"),
                                                     fiction_name=Fiction_list):
            Fiction_chapter = models.Fiction_chapter(chapter_name=chapter_content.get("chapter_name"),
                                                     fiction_name=Fiction_list,
                                                     chapter_content=chapter_content.get("chapter_content"))
            Fiction_chapter.save()
        else:
            if chapter_content:
                models.Fiction_list.objects.filter(fiction_name=chapter_content.get("fiction_name"),
                                                   author=chapter_content.get("author")).update(
                    chapter_name=chapter_content.get("chapter_name"),
                    fiction_name=Fiction_list,
                    chapter_content=chapter_content.get("chapter_content"))
        print("分类：{} , 书名：{} , 作者：{} , 章节：{} ".format(chapter_content.get("cassificationc"),
                                                      chapter_content.get("fiction_name"),
                                                      chapter_content.get("author"),
                                                      chapter_content.get("chapter_name")))


if __name__ == "__main__":
    # print(get_chapter("http://www.paoshu8.com/0_1"))
    # print(get_chapter_content("http://www.paoshu8.com/0_1/291.html","author"))
    def done(request, *args, **kwargs):  #
        result = request.result()
        print(result, args, kwargs)


    pool = ThreadPoolExecutor(100)
    for i in Fiction_url:
        chapter = get_chapter(i)
        author = chapter['author']
        chapter_url_li = chapter['chapter_url']
        v_ = pool.submit(ruku, i)
        v_.add_done_callback(done)

    pool.shutdown(wait=True)
