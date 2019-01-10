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


def get_classification():
    '''
    获取所有分类
    :return:
    '''
    classification = {}
    url = "http://www.inbook.net/ycsk.asp"
    ret = requests.get(url=url, headers=headers)
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    span = soup.find('span', attrs={'class': 'links'})
    for house in span.find_all('a', ):
        # if "全部" == house.text:
        #     break
        # print(house.text, house.attrs['href'])
        classification[house.text] = "http://www.inbook.net/" + house.attrs['href']
    return classification


def get_Fiction(classification_url):
    '''
    获取分类里面的小说列表
    :param classification_url:
    :return:
    '''
    Fiction = {}
    try:
        ret = requests.get(url=classification_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=classification_url, headers=headers)
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    select = soup.find('select', attrs={"name": "page"})

    all_fiction_url = []
    for house in select.find_all('option', ):
        all_fiction_url.append("http://www.inbook.net/" + house.attrs['value'])

    for fiction_url_list in all_fiction_url:
        try:
            ret = requests.get(url=fiction_url_list, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=fiction_url_list, headers=headers)
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', attrs={"align": "center"})
        for tr in table.find_all('tr', attrs={"bgcolor": ""}):
            for td in tr.find_all("td", attrs={"align": "left"}):
                if td.attrs.get("title"):
                    for a in td.find_all("a", attrs={"class": "link"}):
                        # print(a.text, a.attrs.get("href"))
                        Fiction[str(a.text).strip()] = "http://www.inbook.net/" + a.attrs.get("href")

    return Fiction


def get_chapter(fiction_url):
    '''
    获取小说的章节列表
    :param fiction_url:
    :return:
    '''
    chapter = {}
    # fiction_url = "http://www.inbook.net/Manuscriptdetail_88487.html"
    try:
        ret = requests.get(url=fiction_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=fiction_url, headers=headers)
    html = ret.text
    # print(html)
    if "该作品未能提供授权书，暂时不能阅读" in html:
        return chapter
    soup = BeautifulSoup(html, 'html.parser')
    a = soup.find("div", attrs={"class": "Div1_L_2_B_1"}).find('a', )
    chapter_url = "http://www.inbook.net/" + a.attrs.get("href")
    # print(chapter_url)
    try:
        ret = requests.get(url=chapter_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=chapter_url, headers=headers)
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    # print(chapter_url,soup)
    div = soup.find('div', attrs={'class': 'Div3_3'})
    # print(div)
    for a in div.find_all('a', ):
        # print(a)
        chapter[a.text] = "http://www.inbook.net/" + a.attrs.get("href")

    return chapter


def get_chapter_content(fiction_content_url):
    '''
    获取章节内容
    :param fiction_content_url:
    :return:
    '''
    # fiction_content_url = "http://www.inbook.net/zuopin2_503413_1.html"
    try:
        ret = requests.get(url=fiction_content_url, headers=headers)
    except Exception:
        time.sleep(5)
        ret = requests.get(url=fiction_content_url, headers=headers)
    ret.encoding = "gbk"
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', attrs={'class': 'Div3_3'})
    chapter_content = str(div)
    chapter_name = str(div.find_all("center")[1].text)
    div2 = soup.find('div', attrs={'class': 'Div3_2'})
    fiction_name = div2.find("span").text
    author = div2.find("a").text
    div3 = soup.find('div', attrs={'class': 'Div2_1'})
    cassificationc = div3.text.split(">")[1].strip()
    return {"chapter_content": chapter_content, "chapter_name": chapter_name, "fiction_name": fiction_name,
            "author": author, "cassificationc": cassificationc}


if __name__ == "__main__":
    # all = models.Fiction_list.objects.all()
    # print(all)
    # get_chapter_content()
    def func(fiction_url):
        for k2, v2 in get_chapter(fiction_url).items():
            chapter_content = get_chapter_content(v2)
            # print(chapter_content)
            if not models.Classification.objects.filter(name=chapter_content.get("cassificationc"),
                                                        source="inbook").exists():
                Classification = models.Classification(name=chapter_content.get("cassificationc"), source="inbook")
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
            else:
                if chapter_content:
                    models.Fiction_list.objects.filter(fiction_name=chapter_content.get("fiction_name"),
                                                       author=chapter_content.get("author")).update(
                        chapter_content.get("cassificationc"),
                        chapter_content.get("fiction_name"),
                        chapter_content.get("author"),
                        chapter_content.get("chapter_name"))


    def done(request, *args, **kwargs):  #
        result = request.result()
        print(result, args, kwargs)


    for k, v in get_classification().items():
        # if k == "青春校园":
        #     continue
        Fiction = get_Fiction(v)
        pool = ThreadPoolExecutor(100)
        for k1, v1 in Fiction.items():
            v_ = pool.submit(func, v1)
            v_.add_done_callback(done)

        pool.shutdown(wait=True)
