import scrapy, re, os, requests, json, sys, time, boto3, hashlib
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from fiction_scrapy.items import FictionScrapyItem
from bs4 import BeautifulSoup
from django.core.wsgi import get_wsgi_application
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # 定位到你的django根目录
# print(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fiction.settings")  # 你的django的settings文件
application = get_wsgi_application()
from app01 import models

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}


class XiaoHuar_Spider(scrapy.spiders.Spider):
    name = "test1"
    allowed_domains = ["test.com"]
    start_urls = [
        "https://e-hentai.org/g/1284534/2448151ee4/",

    ]
    source = "test"

    def parse(self, response):
        name = response.xpath('''string(//h1[@id="gn"])''').extract_first().replace("\xa0", "")
        classification = response.xpath('''string(//div[@id="gdc"]/a/img/@src)''').extract_first().split("/")[-1].replace(".png", '')
        author = response.xpath('''string(//div[@id="gdn"])''').extract_first().replace("\xa0", "")
        posted = response.xpath('''string(//div[@id="gdd"]/table/tr[1]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        parent = response.xpath('''string(//div[@id="gdd"]/table/tr[2]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        language = response.xpath('''string(//div[@id="gdd"]/table/tr[4]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        file_size = response.xpath('''string(//div[@id="gdd"]/table/tr[5]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        length = response.xpath('''string(//div[@id="gdd"]/table/tr[6]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        url = response.xpath('''//div[@id="gdt"]/div[@class="gdtm"]/div/a/@href''').extract_first()
        print(name, "-", classification, "-", author, "-", posted, "-", parent, "-", language, "-", file_size, "-", length, "-", url)


class Test2(scrapy.spiders.Spider):
    name = "test2"
    allowed_domains = ["test.com"]
    start_urls = [
        "http://www.qwsy.com/read.aspx?cid=731543",
    ]
    source = "test"

    def parse(self, response):
        url = response.url
        # driver = webdriver.Chrome()
        # driver = webdriver.PhantomJS(executable_path='/opt/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')  # 这里的executable_path填你phantomJS的路径
        driver = webdriver.PhantomJS(executable_path='C:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')  # 这里的executable_path填你phantomJS的路径
        driver.get(url)
        chapter_name = driver.find_element_by_xpath('''//h2[@class="dirbt"]''').text
        chapter_con = driver.find_element_by_xpath('''//div[@id="div_readContent"]''').text
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False
        chapter_update_time = driver.find_element_by_xpath('''//div[@class="readbtsmall borbutton"]''').text
        chapter_update_time = chapter_update_time.split("[")[1].replace("更新时间]", "")
        print(chapter_content, chapter_name, chapter_update_time)
        driver.close()
        # chapter_con = response.xpath('''string(//div[@id="content"])''').extract()
        # chapter_content = ''
        # for i in chapter_con:
        #     chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        # if len(chapter_content.strip()) == 0:
        #     is_vip = True
        # else:
        #     is_vip = False
        # print(chapter_content)


class Test3(scrapy.spiders.Spider):
    name = "test3"
    allowed_domains = ["test.com"]
    start_urls = [
        "https://www.zfbook.net/book/24384/chapter.html",
    ]
    source = "test"

    def parse(self, response):
        print(len(response.text))
        # hxs = HtmlXPathSelector(response)
        # fiction_name = hxs.select('''/html/body/div[3]/div[2]/p[1]/span/text()''').extract_first()
        # fiction_update_time = hxs.select('''/html/body/div[3]/div[2]/p[2]/span[2]/text()''').extract_first()
        # author = hxs.select('''/html/body/div[3]/div[2]/p[2]/span[1]/a/text()''').extract_first()
        # li = hxs.select('''//ul[@class="chapter-list clear"]/li''')
        # index = 0
        # for i in li:
        #     url = i.select('''.//a/@href''').extract_first()
        #     chapter_name = i.select('''.//a/text()''').extract_first()
        #     if i.select('''.//em[@class="vipico"]'''):
        #         is_vip = True
        #     else:
        #         is_vip = False
        #     index += 1
        #     print(url, is_vip, chapter_name)
        # print(fiction_name, fiction_update_time, author)


class Test4(scrapy.spiders.Spider):
    name = "test4"
    allowed_domains = ["test.com"]
    start_urls = [
        "https://e-hentai.org/s/d8b67abf1f/1292198-16",
    ]
    source = "test"

    def parse(self, response):
        sort = response.url.split("-")[-1]
        url = response.xpath('''//a[@id="next"]/@href''').extract_first()
        image = response.xpath('''//img[@id="img"]/@src''').extract_first()
        print(url, sort, image)


class Test5(scrapy.spiders.Spider):
    name = "test5"
    allowed_domains = ["test.com"]
    start_urls = [
        "https://e-hentai.org/?f_doujinshi=on&f_manga=on&f_apply=Apply+Filter&page=1",
    ]
    source = "test"

    def parse(self, response):
        li = response.xpath('''//tr/td[3]/div/div[@class="it5"]/a''')
        for i in li:
            url = i.xpath('''.//@href''').extract_first()
            name = i.xpath('''.//text()''').extract_first()
            print(url, name)


class Test6(scrapy.spiders.Spider):
    name = "test6"
    allowed_domains = ["test.com"]
    start_urls = [
        "http://www.comics-porn.com/gals/kaoscomics/69f7e7/big-bum-golden-haired-woman-explores-significant-dark-prick-inside-her-throat-and-mouth-located-in-exclusive-comic-porn-pix.php",
    ]
    source = "test"

    def parse(self, response):
        li = response.xpath('''//a/@href''').extract()
        for i in li:
            if str(i).endswith(".jpg") and str(i).startswith("http://page-x.com"):
                print(i)


class Test7(scrapy.spiders.Spider):
    name = "test7"
    allowed_domains = ["test.com"]
    start_urls = [
        "https://hentai2read.com/puru_puri_panic/1/",
    ]
    source = "hentai2read.com"

    def parse(self, response):
        page = response.xpath('''//div[@class="controls-block dropdown"]/ul[@class="dropdown-menu scrollable-dropdown dropdown-menu-center"]''')[0]
        page = page.xpath('''.//li/a/text()''').extract()
        print(len(page))
