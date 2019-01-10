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
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Host": "book.qidian.com",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}
proxies = {
  "http": "http://223.241.119.2:18118",
  "https": "http://182.114.84.102:48860",
}


start_urls = [
    "https://www.qidian.com/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page=" + str(page) for
    page in range(1, 10)
]


def get_Fiction(classification_url):
    '''
        获取小说url列表
        :param classification_url:
        :return:
        '''
    Fiction_url = []
    ret = requests.get(url=classification_url, headers=headers)
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    h4 = soup.find_all('h4', )
    for a in h4:
        if not a.a:
            continue
        # print(a.a.attrs['href'])
        Fiction_url.append("https:" + a.a.attrs['href'] + "#Catalog")

    return Fiction_url


def get_chapter(fiction_url):
    '''
        获取小说的章节列表
        :param fiction_url:
        :return:
        '''
    Fiction = []
    try:
        ret = requests.get(url=fiction_url, headers=headers, )
    except Exception:
        time.sleep(5)
        ret = requests.get(url=fiction_url, headers=headers, )
    html = ret.text
    soup = BeautifulSoup(html, 'html.parser')
    print(soup)


if __name__ == "__main__":
    # Fiction_url = get_Fiction(
    #     "https://www.qidian.com/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page=1")
    # print(Fiction_url)

    get_chapter('https://book.qidian.com/info/1003517327#Catalog')
