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

classification_url = ["http://all.17k.com/lib/book/2_0_0_0_0_0_0_0_1.html",
                      "http://all.17k.com/lib/book/3_0_0_0_0_0_0_0_1.html",
                      "http://all.17k.com/lib/book/4_0_0_0_0_0_0_0_1.html"]


def done(request, *args, **kwargs):  #
    result = request.result()
    print(result, args, kwargs)


def get_Fiction(classification_url):
    '''
    获取分类里面的小说列表
    :param classification_url:
    :return:
    '''
    Fiction_url = []
    try:
        ret = requests.get(url=classification_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=classification_url, headers=headers)
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    div1 = soup.find('div', attrs={"class": "page"})
    max_page = int(div1.text.split("共")[-1].split("页")[0])
    all_page_url = [
        "http://all.17k.com/lib/book/4_0_0_0_0_0_0_0_" + str(page) for page in range(1, max_page + 1)]

    pool = ThreadPoolExecutor(100)

    def func(url):
        url = url + ".html"
        # print(url)
        try:
            ret = requests.get(url=url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=url, headers=headers)
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', )

        for tr in table.find_all("tr"):
            try:
                Fiction = tr.find("td", attrs={"class": "td3"}).a.attrs.get("href")
                if Fiction == "#":
                    continue
                Fiction_url.append(Fiction)
            except Exception:
                pass

    for url in all_page_url:
        v_ = pool.submit(func, url)
        v_.add_done_callback(done)
    pool.shutdown(wait=True)
    return Fiction_url


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
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    dl = soup.find('dl', attrs={"class": "Bar"})
    url = dl.dt.a.attrs.get("href")
    try:
        ret = requests.get(url=url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=url, headers=headers)
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    author = soup.find('div', attrs={"class": "Author"}).a.text
    dl1 = soup.find('dl', attrs={"class": "Volume"}).dd
    for url in dl1.find_all("a"):
        chapter_url.append("http://www.17k.com" + url.attrs.get("href"))

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
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    div1 = soup.find("div", attrs={"class": "infoPath"}).text.split(">>")
    Classification = div1[2].strip()
    fiction_name = div1[3].strip().split("\n")[0]
    chapter_name = soup.find("h1", ).text.strip()
    buyaode = '''<div class="author-say"></div>
<!--二维码广告 Start-->
<div class="qrcode">
<img alt="wap_17K" height="118" src="http://img.17k.com/images/ad/qrcode.jpg" width="96"/>
<ul>
<li>[^<]*</li>
<li>17K客户端专享，签到即送VIP，免费读全站。</li>
</ul>
</div>
<!--二维码广告 End-->
<div class="chapter_text_ad" id="BAIDU_933954"></div>'''

    chapter_content = str(soup.find("div", attrs={"class": "p"}))
    chapter_content = re.sub(buyaode, "", chapter_content)
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
        if not models.Classification.objects.filter(name=chapter_content.get("cassificationc"), source="17k").exists():
            Classification = models.Classification(name=chapter_content.get("cassificationc"), source="17k")
            Classification.save()

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
            print("分类：{} , 书名：{} , 作者：{} , 章节：{} ".format(chapter_content.get("cassificationc"),
                                                          chapter_content.get("fiction_name"),
                                                          chapter_content.get("author"),
                                                          chapter_content.get("chapter_name")))


if __name__ == "__main__":
    # get_Fiction("http://all.17k.com/lib/book/2_0_0_0_0_0_0_0_1.html")
    # get_chapter("http://www.17k.com/book/2832175.html")
    # get_chapter_content("http://www.17k.com/chapter/2838235/35201081.html", "author")
    def done(request, *args, **kwargs):  #
        result = request.result()
        print(result, args, kwargs)


    for i in classification_url:
        pool = ThreadPoolExecutor(100)
        for j in get_Fiction(i):
            v_ = pool.submit(ruku, j)
            v_.add_done_callback(done)

        pool.shutdown(wait=True)
