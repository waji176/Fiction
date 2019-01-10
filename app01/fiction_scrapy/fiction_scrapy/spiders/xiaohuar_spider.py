import scrapy, re, os, requests, json, sys, time, boto3, hashlib
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from fiction_scrapy.items import FictionScrapyItem
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from django.core.wsgi import get_wsgi_application

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # 定位到你的django根目录
print(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fiction.settings")  # 你的django的settings文件
application = get_wsgi_application()
from app01 import models

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
}


class Gungunbook(scrapy.spiders.Spider):
    name = "gungunbook"
    allowed_domains = ["gungunbook.com"]
    start_urls = [
        "https://m.gungunbook.com/index.php/Book/Classify",
    ]
    source = "滚滚小说网"

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        if response.url == "https://m.gungunbook.com/index.php/Book/Classify":
            div = hxs.select('//div[@class="classify-main"]/div[@class="classify"]/ul[@class="classify-list clearfix"]/li')
            for i in div:
                # print(i.extract())
                classification = i.select('''.//a/text()''').extract_first()
                classification_url = "https://m.gungunbook.com" + i.select('''.//a/@href''').extract_first()
                # print(classification, classification_url, response.url)
                yield Request(classification_url, callback=lambda response, classification=classification: self.get_Fiction(response, classification))

    def get_Fiction(self, response, classification):
        '''
    获取分类里面的小说列表
    :param classification_url:
    :return:
    '''
        if re.match('https://m.gungunbook.com/index.php/Book/Booklist/catId/\d+', response.url):
            hxs = HtmlXPathSelector(response)
            ul = hxs.select('''//ul[@class="saleBook-list"]/li''')
            for i in ul:
                author = i.select('''.//div[@class="fl saleBook-list-right"]/p/text()''').extract_first()
                fiction_name = i.select('''.//div[@class="fl saleBook-list-right"]/h3/text()''').extract_first()
                fiction_url = "https://m.gungunbook.com/index.php/Book/Directory/id/" + i.select('''.//a[@class="saleBook-list-left"]/@href''').extract_first().split("/")[-1]
                fiction_img = i.select('''.//img/@src''').extract_first()
                # print(author, fiction_name, fiction_url, fiction_img)
                yield Request(fiction_url, callback=lambda response, classification=classification, author=author,
                                                           fiction_name=fiction_name, fiction_img=fiction_img:
                self.get_chapter(response, classification, author, fiction_img, fiction_name)
                              )

    def get_chapter(self, response, classification, author, fiction_img, fiction_name):
        '''
            获取小说的章节列表
            :param fiction_url:
            :return:
            '''
        # print(classification, author, fiction_img, fiction_name)
        if not re.match("https://m.gungunbook.com/index.php/Book/Directory/id/\d+/page/\d+/desc/1", response.url):
            fiction_id = response.url.split("/")[-1]
            hxs = HtmlXPathSelector(response)
            select = hxs.select('''//select[@id="listPage"]/option/@value''')[-1].extract()
            chapter_url_list = ["https://m.gungunbook.com/index.php/Book/Directory/id/%s/page/" + str(page) for page in range(1, int(select) + 1)]
            for chapter_url in chapter_url_list:
                chapter_url = chapter_url + "/desc/1"
                chapter_url = chapter_url % fiction_id
                ret = requests.get(url=chapter_url)
                html = ret.text
                soup = BeautifulSoup(html, 'html.parser')
                ul = soup.find("ul", attrs={"class": "lists"})
                for li in ul.find_all("li", attrs={"class": "list-lis"}):
                    chapter_name = li.text
                    chapter_url = "https://m.gungunbook.com" + li.a.attrs.get("href")
                    if li.img:
                        is_vip = True
                    else:
                        is_vip = False
                    # print(classification, author, fiction_img, fiction_name, chapter_name, chapter_url, is_vip)
                    try:
                        ret = requests.get(url=chapter_url)
                        html = ret.text
                        soup = BeautifulSoup(html, 'html.parser')
                        chapter_content = str(soup.find("div", attrs={"class": "chapter-con"}))
                    except Exception:
                        chapter_content = ''
                    viewing_count = ''
                    fiction_update_time = ''
                    status = ''
                    chapter_update_time = ''
                    ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time)


class Jiu_kus(scrapy.spiders.Spider):
    source = "九库"
    name = "9kus"
    allowed_domains = ["9kus.com"]
    start_urls = [
        "http://www.9kus.com/Rank/book_list/attr/2/type_id/26/order/1/pn/" + str(page) for page in range(1, 84)
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        fiction_id_obj = hxs.select('''//div[@class="booklists clearfix"]/ul/li/span/a/@href''')
        for i in fiction_id_obj:
            yield Request("http://www.9kus.com/Book/directory/book_id/" +
                          i.extract().split("/")[-1],
                          callback=self.get_chapter
                          )

    def get_chapter(self, response, ):
        '''
                    获取小说的章节列表
                    :param fiction_url:
                    :return:
                    '''
        print(response.url)
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//div[@class="totals"]/a/text()''').extract_first()
        viewing_count = hxs.select('''//div[@class="totals"]/text()''').extract()[0].strip()
        fiction_update_time = hxs.select('''//div[@class="totals"]/text()''').extract()[-1].strip()
        fiction_name = hxs.select('''//h1/a[@class="bookname_ch"]/text()''').extract_first()
        status = hxs.select('''//h1/span/text()''').extract_first()
        fiction_img = hxs.select('''//div[@class="leftimg"]/a/img/@src''').extract_first()
        # print(cassificationc, viewing_count, fiction_update_time, fiction_name, status)
        chapter = hxs.select('''//div[@class="book_catalogue"]/ul/li''')
        for i in chapter:
            chapter_url = i.select('''.//span[@class="sp2 word-wrap"]/a/@href''').extract_first()
            if i.select('''.//span[@class="sp3"]/img'''):
                is_vip = True
            else:
                is_vip = False
            ret = requests.get(url=chapter_url)
            html = ret.text
            soup = BeautifulSoup(html, 'html.parser')
            chapter_name = soup.find("div", attrs={"class": "contents"}).h2.text
            p = soup.find("p", attrs={"class": "otinfo"}).text.split("|")
            author = p[0]
            chapter_update_time = p[1]
            chapter_content = str(soup.find("div", attrs={"class": "allfonts"}))
            # print(chapter_name, author, chapter_update_time, fiction_img, is_vip)
            ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time)


class Zhuishushenqi(scrapy.spiders.Spider):
    source = "追书神器"
    name = "zhuishushenqi"
    allowed_domains = ["zhuishushenqi.com"]
    start_urls = [
        "http://www.zhuishushenqi.com/selection/vsjx?page=" + str(page) for page in range(1, 21)
        # "http://www.zhuishushenqi.com/selection/vsjx?page=1"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_obj = hxs.select('''//div[@class="books-list"]/a[@class="book"]''')
        for i in fiction_obj:
            fiction_url = "http://www.zhuishushenqi.com" + i.select('''.//@href''').extract_first()
            status = i.select('''.//div[@class="right"]/h4[@class="name"]/span[@class="tag"]/text()''').extract_first()
            # print(fiction_url, status)
            yield Request(fiction_url,
                          callback=lambda response, status=status:
                          self.get_chapter(response, status)
                          )

    def get_chapter(self, response, status):
        '''
        获取小说的章节
        :param response:
        :param status:
        :return:
        '''
        hxs = HtmlXPathSelector(response)
        ul = hxs.select('''//ul[@class="page-route"]/li''')
        # print(ul)
        fiction_name = ul[-1].select('''.//text()''').extract_first()
        cassificationc = ul[1].select('''.//a/text()''').extract_first()
        author = hxs.select('''//p[@class="sup"]/a/text()''').extract_first()
        fiction_img = hxs.select('''//div[@class="book-info"]/img/@src''').extract_first()
        fiction_update_time = hxs.select('''//p[@class="sup"]/text()''').extract()[-1]
        viewing_count = hxs.select('''//i[@class="value"]/text()''').extract_first()
        ul1 = hxs.select('''//ul[@id="J_chapterList"]/li/a/@href''')
        for i in ul1:
            chapter_url = "http://www.zhuishushenqi.com" + i.extract()
            ret = requests.get(url=chapter_url)
            html = ret.text
            soup = BeautifulSoup(html, 'html.parser')
            chapter_name = soup.find("span", attrs={"class": "current-chapter"}).text
            chapter_content = str(soup.find("div", attrs={"class": "inner-text"}))

            is_vip = False
            # print(chapter_name, chapter_content)
            chapter_update_time = ''
            ruku(self.source, cassificationc, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time)


class Y7sw(scrapy.spiders.Spider):
    source = "17书屋"
    name = "17sw"
    allowed_domains = ["17sw.cc"]
    start_urls_ = [
        "http://www.17sw.cc/list/1/" + str(page) for page in range(1, 99)
        # "http://www.17sw.cc/list/1/" + str(page) for page in range(1, 2)

    ]
    start_urls = []
    for i in start_urls_:
        start_urls.append(i + ".html")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        for i in hxs.select('''//ul[@class="item-con"]/li'''):
            pass
        url = i.select('''.//span[@class="s2"]/a/@href''').extract_first()
        yield Request(url,
                      self.get_chapter,
                      )

    def get_chapter(self, response, ):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//div[@class="book-title"]/h1/text()''').extract_first()
        fiction_img = hxs.select('''//*[@id="content"]/div[1]/div/div[1]/img/@src''').extract_first()
        author = hxs.select('''//div[@class="book-title"]/em/text()''').extract_first()
        status = hxs.select('''//p[@class="book-stats"]/text()''').extract()[1].strip()
        fiction_update_time = hxs.select('''//p[@class="book-stats"]/text()''').extract()[3]
        cassificationc = hxs.select('''//html/body/div[2]/a[2]/text()''').extract_first()
        url = hxs.select('''//*[@id="content"]/div[1]/div/div[2]/div[2]/a[2]/@href''').extract_first()

        # url_li = [
        #     "http://www.17sw.cc/txt/5/5070/",
        #     "http://www.17sw.cc/txt/8/8437/",
        #     "http://www.17sw.cc/txt/59/59883/",
        #     "http://www.17sw.cc/txt/35/35215/",
        #     "http://www.17sw.cc/txt/63/63888/",
        #     "http://www.17sw.cc/txt/65/65306/",
        #     "http://www.17sw.cc/txt/65/65289/",
        #     "http://www.17sw.cc/txt/65/65345/",
        #     "http://www.17sw.cc/txt/65/65347/",
        #     "http://www.17sw.cc/txt/63/63862/",
        #     "http://www.17sw.cc/txt/63/63884/",
        #     "http://www.17sw.cc/txt/65/65153/",
        #     "http://www.17sw.cc/txt/64/64178/",
        #     "http://www.17sw.cc/txt/63/63887/",
        #     "http://www.17sw.cc/txt/48/48228/",
        #     "http://www.17sw.cc/txt/63/63936/",
        #     "http://www.17sw.cc/txt/48/48230/",
        #     "http://www.17sw.cc/txt/63/63872/",
        #     "http://www.17sw.cc/txt/32/32278/",
        #     "http://www.17sw.cc/txt/25/25513/",
        #     "http://www.17sw.cc/txt/14/14483/",
        #     "http://www.17sw.cc/txt/63/63930/",
        #     "http://www.17sw.cc/txt/64/64152/",
        #     "http://www.17sw.cc/txt/63/63314/",
        #     "http://www.17sw.cc/txt/64/64248/",
        #     "http://www.17sw.cc/txt/64/64246/",
        #     "http://www.17sw.cc/txt/64/64313/",
        #     "http://www.17sw.cc/txt/64/64354/",
        #     "http://www.17sw.cc/txt/64/64373/",
        #     "http://www.17sw.cc/txt/64/64416/",
        #     "http://www.17sw.cc/txt/63/63825/",
        #     "http://www.17sw.cc/txt/63/63823/",
        #     "http://www.17sw.cc/txt/63/63824/",
        #     "http://www.17sw.cc/txt/62/62605/",
        #     "http://www.17sw.cc/txt/62/62776/",
        #     "http://www.17sw.cc/txt/62/62775/",
        #     "http://www.17sw.cc/txt/62/62774/",
        #     "http://www.17sw.cc/txt/63/63323/",
        #     "http://www.17sw.cc/txt/58/58356/",
        #     "http://www.17sw.cc/txt/14/14566/",
        #     "http://www.17sw.cc/txt/59/59033/",
        #     "http://www.17sw.cc/txt/59/59836/",
        #     "http://www.17sw.cc/txt/59/59930/",
        #     "http://www.17sw.cc/txt/59/59976/",
        #     "http://www.17sw.cc/txt/11/11961/",
        # ]
        # fiction_name = ''
        # fiction_img = ''
        # author = ''
        # status = ''
        # fiction_update_time = ''
        # cassificationc = ''

        # for url in url_li:
        yield Request(url,
                      callback=lambda response, cassificationc=cassificationc, fiction_name=fiction_name, author=author,
                                      status=status, fiction_update_time=fiction_update_time, fiction_img=fiction_img:
                      self.get_chapter1(response, cassificationc, fiction_name, author, status, fiction_update_time, fiction_img)
                      )

    def get_chapter1(self, response, cassificationc, fiction_name, author, status, fiction_update_time, fiction_img):
        hxs = HtmlXPathSelector(response)
        chapter_url = hxs.select('''//dl[@class="chapterlist"]/dd/a/@href''').extract()
        for url in chapter_url:
            url = "http://www.17sw.cc" + url
            # self.down_txt(url)
            yield Request(url,
                          callback=lambda response, cassificationc=cassificationc, fiction_name=fiction_name,
                                          author=author, status=status, fiction_update_time=fiction_update_time, fiction_img=fiction_img:
                          self.get_chapter_content(response, cassificationc, fiction_name, author, status, fiction_update_time, fiction_img)
                          )

    def down_txt(self, url):

        try:
            ret = requests.get(url=url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=url, headers=headers)
        ret.encoding = "gbk"
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        fiction_name = soup.find('div', attrs={"class": "fl"}).find_all("a")[-1].text
        chapter_name = soup.find('div', attrs={"id": "BookCon"}).h1.text.strip()
        chapter_content = soup.find('div', attrs={"id": "BookText"}).text.replace("    ", "    ").replace("\r", '').strip()

        with open("{}.txt".format(fiction_name), "a", encoding="utf-8") as f:
            f.write("\n\n{}\n\n    {}\n".format(chapter_name, chapter_content))
            print(fiction_name, chapter_name, "写入成功")

    def get_chapter_content(self, response, cassificationc, fiction_name, author, status, fiction_update_time, fiction_img):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//*[@id="BookCon"]/h1/text()''').extract_first()
        chapter_content = hxs.select('''//*[@id="BookText"]/text()''').extract()
        chapter_content_info = ""
        for i in chapter_content:
            chapter_content_info += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        chapter_content = chapter_content_info
        viewing_count = ''
        is_vip = False
        chapter_update_time = ''
        ruku(self.source, cassificationc, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time)


class Xinshubao3(scrapy.spiders.Spider):
    source = "新第二书包网"
    name = "xinshubao3"
    allowed_domains = ["xinshubao3.com"]
    start_urls = [

        "http://www.xinshubao3.com/xs/8_0_0_0_1.html",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        div = hxs.select('''//*[@id="main"]/*[@class="sb"]/*[@class="pic"]''')
        # print(div)
        for i in div:
            url = i.select('''.//a/@href''').extract_first()

            yield Request(url, callback=self.get_fiction_info)

    def get_fiction_info(self, response):
        # print(response.url)
        hxs = HtmlXPathSelector(response)
        img = hxs.select('''//img/@src''').extract()[-1]
        img = "http://www.xinshubao3.com" + img
        classification = hxs.select('''//h2[@class="BookAuthor"]/text()''').extract()[1].split("：")[1]
        author = hxs.select('''//h2[@class="BookAuthor"]/a/text()''').extract_first()
        status = hxs.select('''/html/head/meta[15]/@content''').extract_first()
        div = hxs.select('''//li/a/@href''')
        index = 0
        for i in div:
            url = response.url + i.extract()
            # print(url)
            yield Request(url,
                          callback=lambda response, classification=classification, author=author, status=status, fiction_img=img, index=index:
                          self.get_chapter_content(response, classification, author, status, fiction_img, index)
                          )
        # print(img, classification, author, status)

    def get_chapter_content(self, response, classification, author, status, fiction_img, index):
        # print(response.url)
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//*[@id="srcbox"]/div[1]/a[3]/text()''').extract_first()
        chapter_name = hxs.select('''//*[@id="title"]/text()''').extract_first()
        chapter_content = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_content_info = ''
        for i in chapter_content:
            chapter_content_info += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        chapter_content = chapter_content_info

        viewing_count = ''
        fiction_update_time = ''
        is_vip = False
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Bsl8(scrapy.spiders.Spider):
    source = "百书楼"
    name = "bsl8"
    allowed_domains = ["bsl8.la"]
    start_urls1 = [
        "http://www.bsl8.la/page_lastupdate/" + str(page) for page in range(1, 1636)

    ]
    start_urls2 = [
        "http://www.bsl8.la/page_allvisit/" + str(page) for page in range(1, 1636)
    ]
    start_urls = [
        # "http://www.bsl8.la"
    ]
    for i in start_urls1:
        start_urls.append(i + ".html")
    for i in start_urls2:
        start_urls.append(i + ".html")

    # start_urls = ["http://www.bsl8.la/page_lastupdate/1.html"]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        # print(response.url)
        table = hxs.select('''//table[@class="grid"]/tr/td[@class="odd"]/a/@href''')

        for i in table:
            fiction_url = i.extract()
            # print(fiction_url)
            yield Request(fiction_url,
                          callback=self.get_chapter
                          )
        # yield Request("http://www.bsl8.la/books_57695.html",
        #               callback=self.get_chapter
        #               )

    def get_chapter(self, response, ):
        '''
                    获取小说的章节列表
                    :param fiction_url:
                    :return:
                    '''
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//div[@class="btitle clear"]/text()''').extract_first().strip()
        author = hxs.select('''//div[@class="btitle clear"]/em/a/text()''').extract_first().strip()
        cassificationc = hxs.select('''//div[@class="binfo clear"]/span/a/text()''').extract_first().strip()
        status = hxs.select('''//div[@class="binfo clear"]/span/text()''').extract()[1].strip()
        fiction_updatetime = hxs.select('''//div[@class="binfo clear"]/span/text()''').extract()[2].strip()
        viewing_count = hxs.select('''//div[@id="tp_Content0"]/table/tr''')[1].select('''.//td/text()''')[2].extract().strip()
        img = hxs.select('''//div[@class="bimg"]/a/img/@src''').extract_first()
        chapter_li_url = hxs.select('''//div[@class="bstart clear"]/ul/li/a/@href''').extract_first()
        # print(cassificationc, fiction_name, author, status, fiction_updatetime, viewing_count, img, chapter_li_url)
        yield Request(chapter_li_url, callback=lambda
            response, cassificationc=cassificationc, status=status, fiction_name=fiction_name, author=author, fiction_updatetime=fiction_updatetime, viewing_count=viewing_count, img=img:
        self.get_chapter_content(response, cassificationc, fiction_name, author, fiction_updatetime, viewing_count, img, status)
                      )

    def get_chapter_content(self, response, cassificationc, fiction_name, author, fiction_updatetime, viewing_count, img, status):
        hxs = HtmlXPathSelector(response)
        index = 0
        for i in hxs.select('''//div[@id="defaulthtml4"]/table/tr/td/a/@href'''):
            index += 1
            url = response.url + i.extract()
            yield Request(url,
                          callback=lambda
                              response, cassificationc=cassificationc, status=status, fiction_name=fiction_name, author=author, fiction_updatetime=fiction_updatetime, viewing_count=viewing_count, img=img, index=index:
                          self.get_chapter_content_info(response, cassificationc, fiction_name, author, fiction_updatetime, viewing_count, img, status, index)
                          )

    def get_chapter_content_info(self, response, cassificationc, fiction_name, author, fiction_update_time, viewing_count, fiction_img, status, index):
        hxs = HtmlXPathSelector(response)
        chapter_content = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_content_info = ""
        for i in chapter_content:
            chapter_content_info += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        chapter_content = chapter_content_info
        chapter_name = hxs.select('''//*[@class="bname_content"]/text()''').extract_first()
        chapter_update_time = ''
        is_vip = False
        ruku(self.source, cassificationc, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Hebaomi(scrapy.spiders.Spider):
    source = "荷包网"
    name = "hebaomi"
    allowed_domains = ["hebaomi.com"]
    start_urls = [
        "http://www.hebaomi.com/lawen/",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_url_list = ["http://www.hebaomi.com/0_696/"]
        div = hxs.select('''//ul/li/span[@class="s2"]/a/@href''').extract()
        for i in div:
            fiction_url_list.append(i)
        for url in fiction_url_list:
            yield Request(url, callback=self.get_fiction_info)

    def get_fiction_info(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//*[@id="info"]/h1/text()''').extract_first().strip()
        classification = hxs.select('''//div[@class="con_top"]/a[2]/text()''').extract_first().strip()
        author = hxs.select('''//*[@id="info"]/p[1]/text()''').extract_first().split("：")[1]
        fiction_update_time = hxs.select('''//*[@id="info"]/p[3]/text()''').extract_first().split("：")[1]
        fiction_img = "http://www.hebaomi.com" + hxs.select('''//*[@id="fmimg"]/script/@src''').extract_first()
        status = "连载"
        dl = hxs.select('''//*[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for url in dl:
            index += 1
            url = "http://www.hebaomi.com" + url
            yield Request(url, callback=lambda response, classification=classification, status=status, fiction_name=fiction_name, author=author, fiction_update_time=fiction_update_time,
                                               fiction_img=fiction_img, index=index:
            self.get_chapter(response, classification, fiction_name, author, fiction_update_time, fiction_img, status, index))

    def get_chapter(self, response, classification, fiction_name, author, fiction_update_time, fiction_img, status, index):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_content = hxs.select('''//div[@id="content"]/text()''').extract()
        chapter_content_info = ''
        for i in chapter_content:
            chapter_content_info += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        chapter_content = chapter_content_info
        viewing_count = ''
        is_vip = False
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Ba0txt(scrapy.spiders.Spider):
    source = "[爆文]80电子书"
    name = "80txt"
    allowed_domains = ["80txt.com"]
    start_urls = [
        "http://www.80txt.com/txtxz/43140.html",
        "http://www.80txt.com/txtxz/44308.html",
        "http://www.80txt.com/txtxz/13168.html",
        "http://www.80txt.com/txtxz/8597.html",
        "http://www.80txt.com/txtxz/8373.html",
        "http://www.80txt.com/txtml_7438.html",
        "http://www.80txt.com/txtxz/12968.html",
        "http://www.80txt.com/txtxz/43059.html",

    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        viewing_count = hxs.select('''//*[@id="soft_info_para"]/div[2]/li[6]/text()''').extract_first().replace("次", '')
        status = hxs.select('''//*[@id="soft_info_para"]/div[2]/li[7]/strong/text()''').extract_first()
        img = hxs.select('''//*[@id="soft_info_para"]/div[2]/img/@src''').extract_first()
        url = hxs.select('''//*[@id="soft_info_para"]/div[2]/li[12]/b[2]/a/@href''').extract_first()
        yield Request(url, callback=lambda response, status=status, viewing_count=viewing_count, fiction_img=img:
        self.get_chapter(response, viewing_count, fiction_img, status, ))

    def get_chapter(self, response, viewing_count, fiction_img, status, ):
        hxs = HtmlXPathSelector(response)
        fiction_update_time = hxs.select('''//*[@id="titlename"]/div/span[4]/text()''').extract_first()
        cassificationc = hxs.select('''//*[@id="titlename"]/div/span[2]/a/text()''').extract_first()
        author = hxs.select('''//*[@id="titlename"]/div/span[1]/a/text()''').extract_first()
        div = hxs.select('''//*[@id="yulan"]/li/a/@href''').extract()
        index = 0
        for url in div:
            index += 1
            # self.down_txt(url)
            yield Request(url, callback=lambda
                response, status=status, viewing_count=viewing_count, fiction_img=fiction_img, cassificationc=cassificationc, author=author, fiction_update_time=fiction_update_time, index=index:
            self.get_chapter_content(response, viewing_count, fiction_img, status, cassificationc, author, fiction_update_time, index), dont_filter=True)

    def down_txt(self, url):
        try:
            ret = requests.get(url=url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=url, headers=headers)
        ret.encoding = "gbk"
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        fiction_name = soup.find('p', attrs={"class": "text"}).find_all("a")[1].text
        chapter_name = soup.find('div', attrs={"class": "date"}).h1.text.strip()
        chapter_content = soup.find('div', attrs={"id": "content"}).text.strip().replace("    ", "    \n    \n    ").replace('''read_di();''', '  ')
        chapter_content = re.sub('''txt下载地址：.*?手机阅读：.*?为了方便下次阅读，你可以在顶部"加入书签"记录本次.*?的阅读记录，下次打开书架即可看到！请向你的朋友（QQ、博客、微信等方式）推荐本书，兰岚谢谢您的支持！！''', '', chapter_content)
        with open("{}.txt".format(fiction_name), "a", encoding="utf-8") as f:
            f.write("\n{}\n\n    {}".format(chapter_name, chapter_content))
            print(fiction_name, chapter_name, "写入成功")

    def get_chapter_content(self, response, viewing_count, fiction_img, status, cassificationc, author,
                            fiction_update_time, index):

        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//*[@id="main"]/div[4]/div[1]/div/h1/text()''').extract_first()
        fiction_name = hxs.select('''//*[@id="main"]/div[2]/p/a[2]/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_update_time = ''
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        is_vip = False

        ruku(self.source, cassificationc, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Keanshu(scrapy.spiders.Spider):
    source = "[爆文]女儿的奶水小说网"
    name = "keanshu"
    allowed_domains = ["keanshu.com"]
    start_urls = [
        "http://www.keanshu.com/html/0/26/",
        "http://www.keanshu.com/html/0/28/",
        "http://www.keanshu.com/html/0/3/",
        "http://www.keanshu.com/html/0/8/",
        "http://www.keanshu.com/html/0/7/",
        "http://www.keanshu.com/html/0/9/",
        "http://www.keanshu.com/html/0/15/",
        "http://www.keanshu.com/html/0/20/",
        "http://www.keanshu.com/html/0/19/",
        "http://www.keanshu.com/html/0/39/",
        "http://www.keanshu.com/html/0/133/",
        "http://www.keanshu.com/html/0/132/",
        "http://www.keanshu.com/html/0/131/",
        "http://www.keanshu.com/html/0/129/",
        "http://www.keanshu.com/html/0/110/",
        "http://www.keanshu.com/html/0/93/",
        "http://www.keanshu.com/html/0/60/",
        "http://www.keanshu.com/html/0/121/",

    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        tr = hxs.select('''//*[@id="at"]/tr/td/a/@href''').extract()
        author = hxs.select('''//*[@id="a_main"]/div[2]/dl/dd[2]/h3/text()''').extract_first()
        index = 0
        for i in tr:
            url = response.url + i
            index += 1
            # self.down_txt(url)
            yield Request(url, callback=lambda response, index=index, author=author: self.get_chapter(response, index, author)
                          )

    def down_txt(self, url):
        try:
            ret = requests.get(url=url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=url, headers=headers)
        ret.encoding = "gbk"
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        fiction_name = soup.find('div', attrs={"id": "amain"}).dl.dt.find_all("a")[-1].text
        chapter_name = soup.find('div', attrs={"id": "amain"}).dl.dd.h1.text.strip()
        chapter_content = soup.find('dd', attrs={"id": "contents"}).text.strip().replace("    ", "    ")

        with open("{}.txt".format(fiction_name), "a", encoding="utf-8") as f:
            f.write("\n{}\n\n    {}\n".format(chapter_name, chapter_content))
            print(fiction_name, chapter_name, "写入成功")

    def get_chapter(self, response, index, author):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//*[@id="amain"]/dl/dt/a[2]/text()''').extract_first()
        chapter_name = hxs.select('''//*[@id="amain"]/dl/dd[1]/h1/text()''').extract_first()
        fiction_name = hxs.select('''//*[@id="amain"]/dl/dt/a[3]/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="contents"]/text()''').extract()
        chapter_update_time = ''
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"

        fiction_img = ''
        viewing_count = ''
        fiction_update_time = ''
        status = ''
        is_vip = False
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Lanrou(scrapy.spiders.Spider):
    source = "[爆文]蓝柔小说网"
    name = "lanrou"
    allowed_domains = ["lanrou.com"]
    start_urls = [
        # "http://www.lanrou.net/11/11049/",
        "http://www.lanrou.net/0/89/",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//ul[@class="bread-crumbs"]/li[2]/a/text()''').extract_first()
        fiction_name = hxs.select('''//div[@class="infot"]/h1/text()''').extract_first()
        author = hxs.select('''//div[@class="infot"]/span/text()''').extract_first()
        li = hxs.select('''//div[@class="liebiao"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.lanrou.net" + i
            index += 1
            # self.down_txt(url)
            yield Request(url,
                          callback=lambda response, index=index, author=author, classification=classification, fiction_name=fiction_name:
                          self.get_chapter(response, index, author, classification, fiction_name), dont_filter=True
                          )

    def down_txt(self, url):
        try:
            ret = requests.get(url=url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=url, headers=headers)
        ret.encoding = "gbk"
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        fiction_name = soup.find('div', attrs={"align": "center"}).h1.text
        chapter_name = soup.find('div', attrs={"align": "center"}).h2.text.strip()
        chapter_content = soup.find('div', attrs={"id": "content"}).text.replace("    ", "    ")

        with open("{}.txt".format(fiction_name), "a", encoding="utf-8") as f:
            with open("{}.txt".format(fiction_name), "r", encoding="utf-8") as f_r:
                if chapter_name in f_r.read():
                    print("重复")
                else:
                    f.write("\n\n{}\n\n{}".format(chapter_name, chapter_content))
                    print(fiction_name, chapter_name, "写入成功")

    def get_chapter(self, response, index, author, classification, fiction_name):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//*[@id="bgdiv"]/table/tbody/tr[1]/td/div/h2/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="content"]/p/text()''').extract()
        chapter_update_time = ''
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"

        fiction_img = ''
        viewing_count = ''
        fiction_update_time = ''
        status = ''
        is_vip = False
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Xxsy(scrapy.spiders.Spider):
    source = "潇湘书院"
    name = "xxsy"
    allowed_domains = ["xxsy.com"]
    # start_urls = [
    #     "http://www.xxsy.net/info/943497.html",
    #     "http://www.xxsy.net/info/438872.html",
    #     "http://www.xxsy.net/info/864354.html",
    #     "http://www.xxsy.net/info/932543.html",
    #     "http://www.xxsy.net/info/845988.html",
    #     "http://www.xxsy.net/info/926205.html",
    #     "http://www.xxsy.net/info/924578.html",
    #     "http://www.xxsy.net/info/921936.html",
    #     "http://www.xxsy.net/info/943611.html",
    #     "http://www.xxsy.net/info/938571.html",
    #
    # ]
    start_urls = ["http://www.xxsy.net/search?s_wd=&sort=9&pn=" + str(page) for page in range(1, 5369)]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@class="result-list"]/ul/li/a/@href''').extract()
        for i in li:
            url = "http://www.xxsy.net" + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response):
        bookid = response.url.split("/")[-1].split(".")[0]
        hxs = HtmlXPathSelector(response)
        fiction_img = "https:" + hxs.select('''/html/body/div[3]/div/div[1]/dl/dt/img/@src''').extract_first()
        fiction_update_time = hxs.select('''/html/body/div[3]/div/div[1]/dl/dd/div[2]/p[2]/span/text()''').extract_first()
        viewing_count = hxs.select('''/html/body/div[3]/div/div[1]/dl/dd/p[2]/span[2]/*/text()''').extract_first()
        status = hxs.select('''/html/body/div[3]/div/div[1]/dl/dd/p[1]/span[2]/text()''').extract_first()
        # print(fiction_img, viewing_count, fiction_update_time)
        url = "http://www.xxsy.net/partview/GetChapterList?bookid={}&noNeedBuy=0&special=0".format(bookid)
        yield Request(url,
                      callback=lambda response, fiction_img=fiction_img, fiction_update_time=fiction_update_time,
                                      viewing_count=viewing_count, status=status:
                      self.get_chapter(response, fiction_img, fiction_update_time, viewing_count, status),
                      dont_filter=True
                      )

    def get_chapter(self, response, fiction_img, fiction_update_time, viewing_count, status):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//*[@id="chapter"]/dd[1]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.xxsy.net" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_img=fiction_img, fiction_update_time=fiction_update_time, viewing_count=viewing_count, index=index, status=status:
                          self.get_chapter_content(response, fiction_img, fiction_update_time, viewing_count, index, status),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, fiction_img, fiction_update_time, viewing_count, index, status):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//*[@id="auto-container"]/p/a[2]/text()''').extract_first()
        fiction_name = hxs.select('''//*[@id="auto-container"]/p/a[3]/text()''').extract_first()
        chapter_name = hxs.select('''//*[@id="auto-container"]/div[1]/h1/text()''').extract_first()
        chapter_con = hxs.select('''//*[@class="chapter-main"]/p/text()''').extract()
        chapter_update_time = hxs.select('''//*[@id="auto-container"]/div[1]/p/text()[4]''').extract_first()
        author = hxs.select('''//*[@id="auto-container"]/div[1]/p/a[2]/text()''').extract_first()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Ybdu(scrapy.spiders.Spider):
    source = "全本小说网"
    name = "ybdu"
    allowed_domains = ["ybdu.com"]
    start_urls = [
        "https://www.ybdu.com/xiazai/23/23228/",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        url = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/div[1]/span[2]/a/@href''').extract_first()
        author = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[1]/td/div[1]/p[1]/text()''').extract_first().replace("\xa0", '').replace("最新章节：", '')
        cassificationc = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[1]/td/div[1]/p[2]/a/text()''').extract_first()
        viewing_count = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[1]/div[1]/text()''').extract_first()
        fiction_update_time = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[3]/td/div[1]/text()''').extract_first()
        status = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[1]/td/div[1]/p[2]/text()[2]''').extract_first()
        fiction_img = "https://www.ybdu.com" + hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[1]/img/@src''').extract_first()
        # print(cassificationc, url, author, viewing_count, fiction_update_time, status, fiction_img)
        yield Request(url,
                      callback=lambda response, cassificationc=cassificationc, author=author, status=status, viewing_count=viewing_count, fiction_update_time=fiction_update_time,
                                      fiction_img=fiction_img:
                      self.get_fiction_info(response, cassificationc, author, viewing_count, fiction_update_time, status, fiction_img),
                      dont_filter=True
                      )

    def get_fiction_info(self, response, cassificationc, author, viewing_count, fiction_update_time, status, fiction_img):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//*[@id="header"]/div[3]/div[3]/div[1]/h1/text()''').extract_first()
        li = hxs.select('''//*[@id="header"]/div[3]/div[3]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            yield Request(url,
                          callback=lambda response, index=index, fiction_name=fiction_name, cassificationc=cassificationc, author=author, viewing_count=viewing_count,
                                          fiction_update_time=fiction_update_time, status=status, fiction_img=fiction_img:
                          self.get_chapter(response, index, fiction_name, cassificationc, author, viewing_count, fiction_update_time, status, fiction_img), dont_filter=True
                          )

    def get_chapter(self, response, index, fiction_name, cassificationc, author, viewing_count, fiction_update_time, status, fiction_img):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//*[@id="content"]/div/div[1]/h1/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="htmlContent"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True
        chapter_update_time = ''
        ruku(self.source, cassificationc, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Shubao99(scrapy.spiders.Spider):
    source = "九九小说网"
    name = "shubao99"
    allowed_domains = ["shubao99.cc"]
    start_urls = [
        "http://www.shubao99.cc/xiaoshuo_6/",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//ul/li/span[@class="s2"]/a/@href''').extract()
        for i in li:
            yield Request(i, callback=lambda response,: self.get_fiction(response, ), dont_filter=True)

    def get_fiction(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = "http://www.shubao99.cc" + hxs.select('''//*[@id="fmimg"]/script/@src''').extract_first()
        ret = requests.get(url=fiction_img)
        fiction_img = re.findall("src='(.*?)'", ret.text)[0]
        author = hxs.select('''//*[@id="info"]/p[1]/text()''').extract_first().replace("\xa0", '')
        fiction_update_time = "http://www.shubao99.cc" + hxs.select('''//*[@id="info"]/p[3]/script/@src''').extract_first()
        ret = requests.get(url=fiction_update_time)
        fiction_update_time = ret.text
        fiction_update_time = re.findall("(\d+-\d+-\d+)", fiction_update_time)[0]
        li = hxs.select('''//*[@id="list"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            yield Request(url,
                          callback=lambda response, index=index, author=author, fiction_update_time=fiction_update_time, fiction_img=fiction_img:
                          self.get_chapter(response, index, author, fiction_update_time, fiction_img), dont_filter=True
                          )

    def get_chapter(self, response, index, author, fiction_update_time, fiction_img):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//div[@class="con_top"]/text()[3]''').extract_first().replace(">", '').strip()
        fiction_name = hxs.select('''//div[@class="con_top"]/a[2]/text()''').extract_first()
        chapter_name = hxs.select('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True
        viewing_count = ''
        status = '连载'
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Yyxs555(scrapy.spiders.Spider):
    source = "YY小说网"
    name = "yyxs555"
    allowed_domains = ["yyxs555.com"]
    start_urls = [
        "http://www.yyxs555.com/1_1/",
        "http://www.yyxs555.com/2_1/",
        "http://www.yyxs555.com/3_1/",
        "http://www.yyxs555.com/4_1/",
        "http://www.yyxs555.com/5_1/",
        "http://www.yyxs555.com/6_1/",
        "http://www.yyxs555.com/7_1/",
        "http://www.yyxs555.com/8_1/",
        "http://www.yyxs555.com/9_1/",
        "http://www.yyxs555.com/10_1/",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        zuihou = hxs.select('''//a[@class="last"]/text()''').extract_first()
        index = response.url.split("/")[-2].split("_")[0]
        urlli = ["http://www.yyxs555.com/" + index + "_" + str(page) for page in range(1, int(zuihou) + 1)]
        for i in urlli:
            url = i + "/"
            yield Request(url, callback=self.get_fiction_url)

    def get_fiction_url(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@id="alistbox"]/div[@class="pic"]/a/@href''').extract()
        for i in li:
            url = i
            yield Request(url, callback=self.get_fiction_info)

    def get_fiction_info(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = hxs.select('''//img[@class="BookImg"]/@src''').extract_first()
        status = hxs.select('''//*[@id="adbanner_1"]/text()''').extract_first()
        li = hxs.select('''//ul[@class="ListRow"]/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.yyxs555.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, index=index, status=status, fiction_img=fiction_img:
                          self.get_chapter(response, index, status, fiction_img), dont_filter=True
                          )

    def get_chapter(self, response, index, status, fiction_img):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//*[@id="srcbox"]/div[1]/a[2]/text()''').extract_first().replace(">", '').strip()
        fiction_name = hxs.select('''//*[@id="srcbox"]/div[1]/a[3]/text()''').extract_first()
        chapter_name = hxs.select('''//*[@id="title"]/text()''').extract_first()
        author = hxs.select('''//*[@id="main"]/h2/text()''').extract_first().split("/")[-1]
        chapter_con = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        viewing_count = ''
        fiction_update_time = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Keai1(scrapy.spiders.Spider):
    source = "可爱小说网"
    name = "keai1"
    allowed_domains = ["keai1.com"]
    start_urls = [
        "http://www.keai1.com/fl/7/1.html",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//ul/li/span[@class="s2"]/a/@href''').extract()
        for i in li:
            url = "http://www.keai1.com" + i
            yield Request(url, callback=lambda response,: self.get_fiction(response, ), dont_filter=True)

    def get_fiction(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = "http://www.keai1.com" + hxs.select('''//*[@id="fmimg"]/script/@src''').extract_first()
        ret = requests.get(url=fiction_img)
        fiction_img = re.findall("src='(.*?)'", ret.text)[0]
        author = hxs.select('''//*[@id="info"]/p[1]/text()''').extract_first().replace("\xa0", '')
        fiction_update_time = "http://www.keai1.com" + hxs.select('''//*[@id="info"]/p[3]/script/@src''').extract_first()
        ret = requests.get(url=fiction_update_time)
        fiction_update_time = ret.text
        fiction_update_time = re.findall("(\d+-\d+-\d+)", fiction_update_time)[0]
        li = hxs.select('''//*[@id="list"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            yield Request(url,
                          callback=lambda response, index=index, author=author, fiction_update_time=fiction_update_time, fiction_img=fiction_img:
                          self.get_chapter(response, index, author, fiction_update_time, fiction_img), dont_filter=True
                          )

    def get_chapter(self, response, index, author, fiction_update_time, fiction_img
                    ):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//div[@class="con_top"]/text()[3]''').extract_first().replace(">", '').strip()
        fiction_name = hxs.select('''//div[@class="con_top"]/a[2]/text()''').extract_first()
        chapter_name = hxs.select('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True
        viewing_count = ''
        status = '连载'
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Yishuge(scrapy.spiders.Spider):
    source = "一书阁"
    name = "yishuge"
    allowed_domains = ["yishuge.cc"]
    start_urls = [
        "http://www.yishuge.cc/fenlei/7_1.html",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@id="alistbox"]/div[@class="pic"]/a/@href''').extract()
        for i in li:
            url = i
            print(url)
            yield Request(url, callback=self.get_fiction_info)

    def get_fiction_info(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = hxs.select('''//div[@class="pic"]/img/@src''').extract_first()
        viewing_count = hxs.select('''//div[@class="tLJ"]/text()''').extract_first()
        url = "http://www.yishuge.cc" + hxs.select('''//span[@class="btopt"]/a/@href''').extract_first()
        fiction_update_time = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[6]/td[4]/text()''').extract_first()
        status = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[5]/td[3]/text()''').extract_first()

        yield Request(url,
                      callback=lambda response, status=status, viewing_count=viewing_count, fiction_update_time=fiction_update_time, fiction_img=fiction_img:
                      self.get_chapter(response, status, fiction_img, viewing_count, fiction_update_time),
                      dont_filter=True
                      )

    def get_chapter(self, response, status, fiction_img, viewing_count, fiction_update_time):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@class="liebiao"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.yishuge.cc" + i
            index += 1
            yield Request(url,
                          callback=lambda response, status=status, viewing_count=viewing_count, fiction_update_time=fiction_update_time, fiction_img=fiction_img, index=index:
                          self.get_chapter_content(response, status, fiction_img, viewing_count, fiction_update_time, index),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, status, fiction_img, viewing_count, fiction_update_time, index):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''/html/body/div[2]/div/ul/li[2]/a/text()''').extract_first().strip()
        fiction_name = hxs.select('''//*[@id="bgdiv"]/table/tbody/tr[1]/td/div/h1/text()''').extract_first()
        chapter_name = hxs.select('''//*[@id="bgdiv"]/table/tbody/tr[1]/td/div/h2/text()''').extract_first()
        author = hxs.select('''//*[@id="bgdiv"]/table/tbody/tr[1]/td/div/div[1]/text()''').extract_first().split("作者：")[-1].split("本章：")[0]
        chapter_con = hxs.select('''//*[@id="content"]/p[2]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Bookbao8(scrapy.spiders.Spider):
    source = "书包网"
    name = "bookbao8"
    allowed_domains = ["bookbao8.com"]
    start_urls = [
        "https://www.bookbao8.com/Topten.html",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@class="topten_box"]/ul/li/a/@href''').extract()
        for i in li:
            url = "https://www.bookbao8.com" + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = hxs.select('''//*[@id="fmimg"]/img/@src''').extract_first()
        fiction_name = hxs.select('''//*[@id="info"]/h1/text()''').extract_first()
        author = hxs.select('''//*[@id="info"]/p[1]/a/text()''').extract_first()
        classification = hxs.select('''//*[@id="info"]/p[2]/a/text()''').extract_first()
        status = hxs.select('''//*[@id="info"]/p[4]/text()''').extract_first()
        fiction_update_time = hxs.select('''//*[@id="info"]/p[5]/text()''').extract_first()
        viewing_count = hxs.select('''//*[@id="hits"]/text()''').extract_first()
        li = hxs.select('''//div[@class="wp b2 info_chapterlist"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://www.bookbao8.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_img=fiction_img, fiction_name=fiction_name, author=author, classification=classification, status=status, index=index,
                                          fiction_update_time=fiction_update_time, viewing_count=viewing_count:
                          self.get_chapter(response, fiction_img, fiction_name, author, classification, status, fiction_update_time, viewing_count, index),
                          dont_filter=True
                          )

    def get_chapter(self, response, fiction_img, fiction_name, author, classification, status, fiction_update_time, viewing_count, index):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//*[@id="amain"]/dl/dd[1]/h1/text()''').extract_first()
        chapter_update_time = hxs.select('''//*[@id="amain"]/dl/dd[2]/h3/text()[3]''').extract_first().split("\xa0")[2]
        chapter_con = hxs.select('''//*[@id="contents"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Yi5doc(scrapy.spiders.Spider):
    source = "嘀嗒小说网"
    name = "15doc"
    allowed_domains = ["15doc.com"]
    start_urls = [
        "http://www.15doc.com/xiaoshuo/9/1.htm",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        url_li = []
        li = hxs.select('''//ul[@class="item-con"]/li/span[@class="s2"]/a/@href''').extract()
        for i in li:
            url_li.append(i)
        li1 = hxs.select('''//ul[@class="item-list"]/li/a/@href''').extract()
        for i in li1:
            url_li.append(i)
        for url in url_li:
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = hxs.select('''//div[@class="book-img"]/img/@src''').extract_first()
        status = hxs.select('''//p[@class="book-stats"]/text()''').extract()[1].replace("\xa0", '')
        fiction_update_time = hxs.select('''//p[@class="book-stats"]/text()''').extract()[-1].replace("\xa0", '')
        url = hxs.select('''//div[@class="book-link"]/a[2]/@href''').extract_first()
        yield Request(url,
                      callback=lambda response, fiction_img=fiction_img, status=status, fiction_update_time=fiction_update_time:
                      self.get_chapter(response, fiction_img, status, fiction_update_time),
                      dont_filter=True
                      )

    def get_chapter(self, response, fiction_img, status, fiction_update_time):
        hxs = HtmlXPathSelector(response)
        author = hxs.select('''//div[@class="btitle"]/em/a/text()''').extract_first()
        li = hxs.select('''//dl[@class="chapterlist"]/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url.replace("index.html", '') + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_img=fiction_img, status=status, author=author, index=index, fiction_update_time=fiction_update_time:
                          self.get_chapter_content(response, fiction_img, status, fiction_update_time, author, index),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, fiction_img, status, fiction_update_time, author, index):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//*[@id="wrapper"]/div[2]/div[1]/a[2]/text()''').extract_first()
        fiction_name = hxs.select('''//*[@id="wrapper"]/div[2]/div[1]/text()[2]''').extract_first().replace(">", '').strip()
        chapter_name = hxs.select('''//*[@id="BookCon"]/h1/text()''').extract_first()
        chapter_update_time = ''
        chapter_con = hxs.select('''//*[@id="BookText"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        viewing_count = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class S55555(scrapy.spiders.Spider):
    source = "五五小说网"
    name = "s55555"
    allowed_domains = ["s55555.cc"]
    start_urls = [
        "http://www.s55555.cc/fenlei/7_1.html",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@id="alistbox"]/div[@class="pic"]/a/@href''').extract()
        for i in li:
            url = i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction(response, ),
                          dont_filter=True
                          )

    def get_fiction(self, response):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//*[@id="content"]/div[2]/ul/li[2]/a/text()''').extract_first()
        fiction_name = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[1]/td/div[1]/h1/text()''').extract_first()
        author = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[1]/td/div[1]/h1/em/text()''').extract_first()
        fiction_img = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[1]/img/@src''').extract_first()
        viewing_count = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[1]/div[1]/text()''').extract_first()
        fiction_update_time = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[6]/td[4]/text()''').extract_first()
        url = "http://www.s55555.cc" + hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/div/span[2]/a/@href''').extract_first()
        status = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[5]/td[3]/text()''').extract_first()
        yield Request(url,
                      callback=lambda response, fiction_img=fiction_img, status=status, classification=classification, fiction_name=fiction_name, author=author, viewing_count=viewing_count,
                                      fiction_update_time=fiction_update_time:
                      self.get_chapter(response, fiction_img, status, fiction_update_time, classification, fiction_name, author, viewing_count),
                      dont_filter=True
                      )

    def get_chapter(self, response, fiction_img, status, fiction_update_time, classification, fiction_name, author, viewing_count):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@class="liebiao"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.s55555.cc" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_img=fiction_img, status=status, classification=classification,
                                          fiction_name=fiction_name, author=author, viewing_count=viewing_count, index=index, fiction_update_time=fiction_update_time:
                          self.get_chapter_content(response, fiction_img, status, fiction_update_time, classification, fiction_name, author, viewing_count, index),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, fiction_img, status, fiction_update_time, classification, fiction_name, author, viewing_count, index):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//div[@align="center"]/h2/text()''').extract_first()
        chapter_update_time = ''
        chapter_con = hxs.select('''//*[@id="content"]/p[2]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Lawen33(scrapy.spiders.Spider):
    source = "辣文小说网"
    name = "lawen33"
    allowed_domains = ["lawen33.com"]
    start_urls = []
    for i in range(1, 1123):  start_urls.append("http://www.lawen33.com/hwen/" + str(i) + ".html")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//table/tr/td/a/@href''').extract()
        for i in li:
            url = "http://www.lawen33.com" + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response):
        hxs = HtmlXPathSelector(response)
        Classification = hxs.select('''//td[@class="td1"]/a/text()''').extract_first()
        fiction_name = hxs.select('''//div[@class="ilbox"]/h1/text()''').extract_first()
        fiction_img = "http://www.lawen33.com" + hxs.select('''//td[@class="icover"]/img/@src''').extract_first()
        status = hxs.select('''//tr/td/b/text()''').extract_first()
        author = hxs.select('''//div[@class="infotable"]/table/tr[2]/td[4]/text()''').extract_first()
        viewing_count = hxs.select('''//div[@class="infotable"]/table/tr[3]/td[4]/text()''').extract_first()
        fiction_update_time = hxs.select('''//div[@class="infotable"]/table/tr[4]/td[4]/text()''').extract_first()
        li = hxs.select('''//div[@class="mulu"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.lawen33.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_img=fiction_img, status=status, author=author, index=index, fiction_update_time=fiction_update_time, Classification=Classification,
                                          fiction_name=fiction_name, viewing_count=viewing_count:
                          self.get_chapter_content(response, fiction_img, status, fiction_update_time, author, index, fiction_name, viewing_count, Classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, fiction_img, status, fiction_update_time, author, index, fiction_name, viewing_count, Classification):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//div[@class="mc"]/h1/text()''').extract_first()
        chapter_update_time = ''
        chapter_con = hxs.select('''//div[@class="mcc"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        ruku(self.source, Classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Shubao95(scrapy.spiders.Spider):
    source = "第九书包网"
    name = "shubao95"
    allowed_domains = ["shubao95.com"]
    start_urls = []
    for i in range(1, 291):  start_urls.append("http://www.shubao95.com/hxiaoshuo/" + str(i) + ".html")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//table/tr/td/a/@href''').extract()
        for i in li:
            url = "http://www.lawen33.com" + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response):
        hxs = HtmlXPathSelector(response)
        Classification = hxs.select('''//td[@class="td1"]/a/text()''').extract_first()
        fiction_name = hxs.select('''//div[@class="ilbox"]/h1/text()''').extract_first()
        fiction_img = "http://www.lawen33.com" + hxs.select('''//td[@class="icover"]/img/@src''').extract_first()
        status = hxs.select('''//tr/td/b/text()''').extract_first()
        author = hxs.select('''//div[@class="infotable"]/table/tr[2]/td[4]/text()''').extract_first()
        viewing_count = hxs.select('''//div[@class="infotable"]/table/tr[3]/td[4]/text()''').extract_first()
        fiction_update_time = hxs.select('''//div[@class="infotable"]/table/tr[4]/td[4]/text()''').extract_first()
        li = hxs.select('''//div[@class="mulu"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.lawen33.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_img=fiction_img, status=status, author=author, index=index, fiction_update_time=fiction_update_time, Classification=Classification,
                                          fiction_name=fiction_name, viewing_count=viewing_count:
                          self.get_chapter_content(response, fiction_img, status, fiction_update_time, author, index, fiction_name, viewing_count, Classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, fiction_img, status, fiction_update_time, author, index, fiction_name, viewing_count, Classification):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//div[@class="mc"]/h1/text()''').extract_first()
        chapter_update_time = ''
        chapter_con = hxs.select('''//div[@class="mcc"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        ruku(self.source, Classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class S4444(scrapy.spiders.Spider):
    source = "四四小说网"
    name = "s4444"
    allowed_domains = ["s4444.com"]
    start_urls = [
        # "http://s4444.cc/fenlei/7_1.html"
    ]

    for i in range(1, 2491): start_urls.append("http://s4444.cc/fenlei/7_" + str(i) + ".html")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@id="alistbox"]/div[@class="pic"]/a/@href''').extract()
        for i in li:
            url = i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response):
        hxs = HtmlXPathSelector(response)
        Classification = hxs.select('''//ul[@class="bread-crumbs"]/li[2]/a/text()''').extract_first()
        fiction_name = hxs.select('''//h1[@class="f20h"]/text()''').extract_first()
        fiction_img = hxs.select('''//div[@class="pic"]/img/@src''').extract_first()
        author = hxs.select('''//h1[@class="f20h"]/em/text()''').extract_first()
        viewing_count = hxs.select('''//div[@class="tLJ"]/text()''').extract_first()
        fiction_update_time = hxs.select('''//p[@class="ti"]/em/text()''').extract_first().replace("网友上传时间：", '')
        status = hxs.select('''//*[@id="detail-box"]/div/div[1]/div[1]/div[2]/table/tbody/tr[5]/td[3]/text()''').extract_first()
        url = "http://s4444.cc" + hxs.select('''//span[@class="btopt"]/a/@href''').extract_first()
        yield Request(url,
                      callback=lambda response, fiction_img=fiction_img, status=status, classification=Classification, fiction_name=fiction_name, author=author, viewing_count=viewing_count,
                                      fiction_update_time=fiction_update_time:
                      self.get_chapter(response, fiction_img, status, fiction_update_time, classification, fiction_name, author, viewing_count),
                      dont_filter=True
                      )

    def get_chapter(self, response, fiction_img, status, fiction_update_time, classification, fiction_name,
                    author, viewing_count):
        # print(response.url)
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@class="liebiao"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://s4444.cc" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_img=fiction_img, status=status, classification=classification,
                                          fiction_name=fiction_name, author=author, viewing_count=viewing_count, index=index, fiction_update_time=fiction_update_time:
                          self.get_chapter_content(response, fiction_img, status, fiction_update_time, classification, fiction_name, author, viewing_count, index),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, fiction_img, status, fiction_update_time, classification, fiction_name, author, viewing_count, index):
        # print(response.url)
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//div[@align="center"]/h2/text()''').extract_first()
        chapter_update_time = ''
        chapter_con = hxs.select('''//*[@id="content"]/p[2]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Ashubao(scrapy.spiders.Spider):
    source = "啊书包网"
    name = "ashubao"
    allowed_domains = ["ashubao.com"]
    start_urls = [
        "http://www.ashubao.vip/0_267/",
        "http://www.ashubao.vip/0_223/",
        "http://www.ashubao.vip/0_641/",
        "http://www.ashubao.vip/0_559/",
        "http://www.ashubao.vip/1_1554/",
        "http://www.ashubao.vip/7_7563/",
        "http://www.ashubao.vip/23_23932/",
        "http://www.ashubao.vip/12_12261/",
        "http://www.ashubao.vip/0_222/",
        "http://www.ashubao.vip/0_252/",
        "http://www.ashubao.vip/0_260/",
        "http://www.ashubao.vip/0_265/",

    ]

    # for i in range(1, 24619):
    #     start_urls.append("http://www.ashubao.vip/0_" + str(i) + "/")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = "http://www.ashubao.vip" + hxs.select('''//*[@id="fmimg"]/script/@src''').extract_first()
        ret = requests.get(url=fiction_img)
        fiction_img = re.findall("src='(.*?)'", ret.text)[0]
        author = hxs.select('''//*[@id="info"]/p[1]/text()''').extract_first().replace("\xa0", '')
        fiction_update_time = hxs.select('''//*[@id="info"]/p[3]/text()''').extract_first()
        fiction_name = hxs.select('''//*[@id="info"]/h1/text()''').extract_first()
        li = hxs.select('''//*[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.ashubao.vip" + i
            index += 1
            # self.down_txt(url)
            yield Request(url,
                          callback=lambda response, index=index, author=author, fiction_update_time=fiction_update_time, fiction_img=fiction_img:
                          self.get_chapter(response, index, author, fiction_update_time, fiction_img), dont_filter=True
                          )

    def down_txt(self, url):

        try:
            ret = requests.get(url=url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=url, headers=headers)
        ret.encoding = "gbk"
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        fiction_name = soup.find('div', attrs={"class": "con_top"}).find_all("a")[-1].text
        chapter_name = soup.find('div', attrs={"class": "bookname"}).h1.text.strip()
        chapter_content = soup.find('div', attrs={"id": "content"}).text.strip().replace("请记住本站域名 www.ashubao.vip 防止丢失", '').replace("</div>", '').strip().replace("    ", '    ').replace('''\r''', '')

        with open("{}.txt".format(fiction_name), "a", encoding="utf-8") as f:
            f.write("{}\n\n    {}\n\n".format(chapter_name, chapter_content))
            print(fiction_name, chapter_name, "写入成功")

    def get_chapter(self, response, index, author, fiction_update_time, fiction_img):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//div[@class="con_top"]/text()[3]''').extract_first().replace(">", '').strip()
        fiction_name = hxs.select('''//div[@class="con_top"]/a[2]/text()''').extract_first()
        chapter_name = hxs.select('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True
        viewing_count = ''
        status = '连载'
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Ldw(scrapy.spiders.Spider):
    source = "努努书坊"
    name = "ldw"
    allowed_domains = ["ldw.la"]
    start_urls = [
    ]
    for i in range(1, 293):
        # for i in range(1, 2):
        start_urls.append("http://www.ldw.la/ldw_sort23/" + str(i) + ".htm")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//table/tr''')
        for i in li:
            Classification = i.select('''.//td[@class="odd"]/text()''').extract_first()
            if not Classification:
                continue
            fiction_name = i.select('''.//td[@class="odd"]/text()''').extract()[1]
            fiction_url = i.select('''.//td[@class="odd"]/a/@href''').extract_first()
            author = i.select('''.//td[@class="odd"]/text()''').extract()[-2]
            status = i.select('''.//td[@class="odd"]/text()''').extract()[-1]

            yield Request(fiction_url,
                          callback=lambda response, classification=Classification, author=author, status=status, fiction_name=fiction_name:
                          self.get_fiction_info(response, classification, status, author, fiction_name)
                          )

    def get_fiction_info(self, response, classification, status, author, fiction_name):
        hxs = HtmlXPathSelector(response)
        fiction_img = hxs.select('''//*[@id="bigImg"]/div/img/@src''').extract_first()
        fiction_update_time = hxs.select('''//*[@id="tab1_tool"]/small/text()''').extract_first()
        viewing_count = hxs.select('''//*[@id="fragment-0"]/table/tbody/tr[3]/td[2]/text()''').extract_first()
        url = hxs.select('''//*[@id="bt_1"]/a/@href''').extract_first()
        yield Request(url,
                      callback=lambda response, classification=classification, author=author, status=status, fiction_name=fiction_name, fiction_img=fiction_img,
                                      fiction_update_time=fiction_update_time, viewing_count=viewing_count:
                      self.get_chapter_url(response, classification, status, author, fiction_name, fiction_img, fiction_update_time, viewing_count)
                      )

    def get_chapter_url(self, response, classification, status, author, fiction_name, fiction_img, fiction_update_time, viewing_count):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//table[@class="acss"]/tr/td/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            yield Request(url,
                          callback=lambda response, classification=classification, author=author, status=status, fiction_name=fiction_name, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, viewing_count=viewing_count, index=index:
                          self.get_chapter_content(response, classification, status, author, fiction_name, fiction_img, fiction_update_time, viewing_count, index)
                          )

    def get_chapter_content(self, response, classification, status, author, fiction_name, fiction_img, fiction_update_time, viewing_count, index):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//div[@id="box"]/h1/text()''').extract_first()
        chapter_con = hxs.select('''//div[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Fushuwang(scrapy.spiders.Spider):
    source = "腐书网"
    name = "fushuwang"
    allowed_domains = ["fushuwang.com"]
    start_urls = [
        "https://www.fushuwang.net/bookall/gcls/index.html"
    ]

    for i in range(2, 36):
        start_urls.append("https://www.fushuwang.net/bookall/gcls/index_" + str(i) + ".html")

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//*[@id="article"]/div[@class="breadcrumb"]/a[3]/text()''').extract_first()
        li = hxs.select('''//div[@class="loop"]''')
        for i in li:
            fiction_name = i.select('''.//div[@class="content_body"]/h2/a/text()''').extract_first()
            fiction_url = i.select('''.//div[@class="content_body"]/h2/a/@href''').extract_first()
            fiction_update_time = i.select('''.//div[@class="content_infor"]/span[@class="more2"]/span/text()''').extract_first()
            viewing_count = i.select('''.//div[@class="content_infor"]/span[@class="more2"]/strong/text()''').extract_first()
            try:
                author = fiction_name.split("：")[-1]
            except Exception:
                author = ''
            status = ''
            fiction_img = ''
            # print(classification, fiction_name, fiction_url, fiction_update_time, viewing_count,author)
            yield Request(fiction_url,
                          callback=lambda response, classification=classification, author=author, status=status, fiction_name=fiction_name, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, viewing_count=viewing_count:
                          self.get_chapter_url(response, classification, status, author, fiction_name, fiction_img, fiction_update_time, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_url(self, response, classification, status, author, fiction_name, fiction_img, fiction_update_time, viewing_count):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//select[@name="titleselect"]/option/@value''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, classification=classification, author=author, status=status, fiction_name=fiction_name, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, viewing_count=viewing_count, index=index:
                          self.get_chapter_content(response, classification, status, author, fiction_name, fiction_img, fiction_update_time, viewing_count, index),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, classification, status, author, fiction_name, fiction_img, fiction_update_time, viewing_count, index):
        hxs = HtmlXPathSelector(response)
        chapter_con = hxs.select('''//div[@class="post"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True
        chapter_update_time = ''
        chapter_name = index
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Ayaxs888(scrapy.spiders.Spider):
    source = "阿雅小说网"
    name = "ayaxs888"
    allowed_domains = ["ayaxs888.com"]
    start_urls = [
    ]
    for i in range(1, 122):
        start_urls.append("http://www.ayaxs888.com/1_{}/".format(i))
    for i in range(1, 14):
        start_urls.append("http://www.ayaxs888.com/2_{}/".format(i))
    for i in range(1, 158):
        start_urls.append("http://www.ayaxs888.com/3_{}/".format(i))
    for i in range(1, 2):
        start_urls.append("http://www.ayaxs888.com/4_{}/".format(i))
    for i in range(1, 3):
        start_urls.append("http://www.ayaxs888.com/5_{}/".format(i))
    for i in range(1, 14):
        start_urls.append("http://www.ayaxs888.com/6_{}/".format(i))
    for i in range(1, 25):
        start_urls.append("http://www.ayaxs888.com/7_{}/".format(i))
    for i in range(1, 4):
        start_urls.append("http://www.ayaxs888.com/8_{}/".format(i))
    for i in range(1, 45):
        start_urls.append("http://www.ayaxs888.com/9_{}/".format(i))
    for i in range(1, 22):
        start_urls.append("http://www.ayaxs888.com/10_{}/".format(i))

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@id="alistbox"]''')
        for i in li:
            fiction_img = i.select('''.//div[@class="pic"]/a/img/@src''').extract_first()
            fiction_url = i.select('''.//div[@class="pic"]/a/@href''').extract_first()
            yield Request(fiction_url,
                          callback=lambda response, fiction_img=fiction_img:
                          self.get_fiction_info(response, fiction_img),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, fiction_img):
        hxs = HtmlXPathSelector(response)
        index = 0
        li = hxs.select('''//*[@id="defaulthtml4"]/table/tbody/tr/td/div/a/@href''').extract()
        author = hxs.select('''/html/body/div[3]/div[1]/span/text()''').extract_first()
        for i in li:
            url = "http://www.ayaxs888.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, index=index, fiction_img=fiction_img, author=author:
                          self.get_chaper_content(response, index, fiction_img, author),
                          dont_filter=True
                          )

    def get_chaper_content(self, response, index, fiction_img, author):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''/html/body/div[2]/div/ul/li[2]/a/text()''').extract_first()
        fiction_name = hxs.select('''////*[@id="bgdiv"]/table/tbody/tr[1]/td/div/h1/text()''').extract_first()
        chapter_name = hxs.select('''//*[@id="bgdiv"]/table/tbody/tr[1]/td/div/h2/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="content"]/p/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        viewing_count = ''
        status = ''
        chapter_update_time = ''
        fiction_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Xianwangs(scrapy.spiders.Spider):
    source = "鲜网文学"
    name = "xianwangs"
    allowed_domains = ["xianwangs.com"]
    start_urls = [
    ]
    for i in range(1, 20):
        start_urls.append("http://www.xianwangs.cc/gaolawen/shuku_925_{}.html".format(i))

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//ul[@class="ul_m_list"]/li/div[@class="title"]/div[@class="t"]/a/@href''').extract()
        for i in li:
            url = "http://www.xianwangs.cc" + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//div[@class="title"]/h2/text()''').extract_first()
        fiction_img = "http://www.xianwangs.cc" + hxs.select('''/html/body/div[6]/div/div[1]/div[1]/div[1]/a/img/@src''').extract_first().strip()
        author = hxs.select('''//div[@class="info"]/ul/li/a/text()''').extract_first()
        status = hxs.select('''/html/body/div[6]/div/div[1]/div[2]/div[2]/ul/li[8]/text()''').extract_first()
        viewing_count = hxs.select('''//div[@class="info"]/ul/li/font[@id="cms_clicks"]/text()''').extract_first()
        Classification = hxs.select('''//div[@class="info"]/ul/li/a/text()''').extract()[-1]
        fiction_update_time = hxs.select('''/html/body/div[6]/div/div[1]/div[2]/div[3]/text()[2]''').extract_first().replace("）", '').replace("（", '')
        li = hxs.select('''//div[@class="list_box"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.xianwangs.cc" + i
            index += 1
            yield Request(url,
                          callback=lambda response, index=index, fiction_img=fiction_img, author=author, fiction_name=fiction_name, status=status, viewing_count=viewing_count,
                                          Classification=Classification, fiction_update_time=fiction_update_time:
                          self.get_chaper_content(response, index, fiction_img, author, fiction_name, status, viewing_count, Classification, fiction_update_time),
                          dont_filter=True
                          )

    def get_chaper_content(self, response, index, fiction_img, author, fiction_name, status,
                           viewing_count, classification, fiction_update_time):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//div[@class="Con box_con"]/h2/text()''').extract_first()
        chapter_update_time = hxs.select('''//div[@class="info"]/text()''').extract_first().split("更新时间：")[-1]
        chapter_con = hxs.select('''//div[@class="box_box"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Yanshuwu(scrapy.spiders.Spider):
    source = "艳书屋"
    name = "yanshuwu"
    allowed_domains = ["yanshuwu.com"]
    start_urls = [
        "http://www.yanshuwu.com/book/0/81/",
        "http://www.yanshuwu.com/book/0/6/",
        "http://www.yanshuwu.com/book/0/81/",
        "http://www.yanshuwu.com/book/0/424/",
        "http://www.yanshuwu.com/book/0/222/",
        "http://www.yanshuwu.com/book/0/656/",

    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = hxs.select('''//div[@class="pic"]/img/@src''').extract_first()
        fiction_name = hxs.select('''//*[@id="info"]/h1/text()''').extract_first()
        fiction_update_time = hxs.select('''//div[@class="update"]/text()[2]''').extract_first().replace("）", '').replace("（", '')
        Classification = hxs.select('''//div[@class="title"]/b/a[2]/text()''').extract_first()
        author = hxs.select('''//*[@id="info"]/div[1]/span[1]/text()''').extract_first()
        # print(fiction_img, Classification, fiction_name, author, fiction_update_time)
        li = hxs.select('''//div[@class="book_list"]/ul/li/a/@href''').extract()
        urlli = {}
        index_li = []
        for i in li:
            url = "http://www.yanshuwu.com" + i
            index = int(i.split("/")[-1].split(".")[0])
            index_li.append(index)
            urlli[index] = url
        index_li.sort()
        for i in index_li:
            url = urlli[i]
            # self.down_txt(url)
            yield Request(url,
                          callback=lambda response, index=i, fiction_img=fiction_img, author=author, fiction_name=fiction_name,
                                          Classification=Classification, fiction_update_time=fiction_update_time:
                          self.get_chaper_content(response, index, fiction_img, author, fiction_name, Classification, fiction_update_time),
                          dont_filter=True
                          )

    def get_chaper_content(self, response, index, fiction_img, author, fiction_name, classification, fiction_update_time):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//div[@class="h1title"]/h1/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="htmlContent"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        viewing_count = ''
        status = '连载'
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)

    def down_txt(self, url):
        try:
            ret = requests.get(url=url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=url, headers=headers)
        ret.encoding = "gbk"
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        fiction_name = soup.find('div', attrs={"class": "title"}).b.find_all("a")[2].text
        chapter_name = soup.find('div', attrs={"class": "h1title"}).h1.text.strip()
        chapter_content = soup.find('div', attrs={"id": "htmlContent"}).text \
            .strip().replace("    ", "    ").replace("\r", '')

        with open("{}.txt".format(fiction_name), "a", encoding="utf-8") as f:
            with open("{}.txt".format(fiction_name), "r", encoding="utf-8") as f_r:
                f.write("{}\n\n    {}\n\n".format(chapter_name, chapter_content))
                print(fiction_name, chapter_name, "写入成功")


class Eryq(scrapy.spiders.Spider):
    source = "爱言情"
    name = "2yq"
    allowed_domains = ["2yq.com"]
    start_urls = [

    ]
    for i in range(1, 586):
        # for i in range(1, 586):
        url = "http://www.2yq.com/gengxin/gengxin1_{}.html".format(i)
        start_urls.append(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''/html/body/table[7]/tr/td/table[1]/tr''')

        for i in li:
            fiction_name = i.select('''.//td[3]/a/text()''').extract_first()
            author = i.select('''.//td[2]/a/text()''').extract_first()
            fiction_update_time = i.select('''.//td[1]/text()''').extract_first()
            url = i.select('''.//td[3]/a/@href''').extract_first()
            if not url:
                continue
            # print(fiction_name, url, author, fiction_update_time)
            yield Request(url,
                          callback=lambda response, author=author, fiction_name=fiction_name, fiction_update_time=fiction_update_time:
                          self.get_fiction_info(response, author, fiction_name, fiction_update_time),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, author, fiction_name, fiction_update_time):
        hxs = HtmlXPathSelector(response)
        fiction_img = hxs.select('''/html/body/table[7]/tr[2]/td/table[2]/tr[1]/td[1]/img[1]/@src''').extract_first()
        li = hxs.select('''/html/body/table[7]/tr[2]/td/table[2]/tr[4]/td/table/tr/td/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            # print(url, fiction_update_time)
            yield Request(url,
                          callback=lambda response, index=index, fiction_img=fiction_img, author=author, fiction_name=fiction_name, fiction_update_time=fiction_update_time:
                          self.get_chaper_content(response, index, fiction_img, author, fiction_name, fiction_update_time),
                          dont_filter=True
                          )

    def get_chaper_content(self, response, index, fiction_img, author, fiction_name, fiction_update_time):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''/html/body/table[3]/tr/td[1]/h1/text()''').extract_first().replace("\xa0", '').strip()
        chapter_con = hxs.select('''//*[@id="zoom"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        viewing_count = ''
        status = ''
        chapter_update_time = ''
        classification = '爱情言情'
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Yi2kanshu(scrapy.spiders.Spider):
    source = "12看书"
    name = "12kanshu"
    allowed_domains = ["12kanshu.com"]
    start_urls = [
        # "http://www.12kanshu.com/book/7094/"
    ]

    for i in range(1000, 30000):
        url = "http://www.12kanshu.com/book/{}/".format(i)
        start_urls.append(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = "http://www.12kanshu.com" + hxs.select('''//div[@class="book_cover fl"]/p/a/img/@src''').extract_first()
        fiction_name = hxs.select('''//div[@class="status fl"]/h1/text()''').extract_first()
        author = hxs.select('''//div[@class="booksub"]/a[1]/text()''').extract_first()
        classification = hxs.select('''//div[@class="booksub"]/a[2]/text()''').extract_first()
        viewing_count = hxs.select('''//p[@class="fb"]/text()''').extract_first()
        fiction_update_time = hxs.select('''//div[@class="keyword"]/text()''').extract_first().replace("）", "").replace("（", "")
        # print(fiction_img, fiction_name, author, Classification, viewing_count, fiction_update_time)
        status = ''
        li = hxs.select('''//td[@class="chapterBean"]/a/@href''').extract()

        index = 0
        for i in li:
            url = response.url + i
            index += 1
            # self.down_txt(url, index)
            yield Request(url,
                          callback=lambda response, index=index, fiction_img=fiction_img, author=author, fiction_name=fiction_name, status=status, viewing_count=viewing_count
                                          , fiction_update_time=fiction_update_time, classification=classification:
                          self.get_chaper_content(response, index, fiction_img, author, fiction_name, fiction_update_time, status, viewing_count, classification),
                          dont_filter=True
                          )

    def get_chaper_content(self, response, index, fiction_img, author, fiction_name, fiction_update_time, status, viewing_count, classification):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//div[@class="tc txt"]/h1/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="chapterContent"]/p/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)

    def down_txt(self, url, index):
        try:
            ret = requests.get(url=url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=url, headers=headers)
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        fiction_name = soup.find('span', attrs={"class": "nav"}).find_all("a")[1].text.strip()
        chapter_name = soup.find('div', attrs={"class": "tc txt"}).h1.text.strip()
        chapter_name = re.sub("第.*?章", "", chapter_name)
        chapter_name = "第" + str(index) + "章 " + chapter_name
        chapter_content = soup.find('div', attrs={"id": "chapterContent"}).p.text.strip() \
            .replace("　　", "    \n    \n    ").replace("\t", '').replace("<", '')

        with open("{}.txt".format(fiction_name), "a", encoding="utf-8") as f:
            with open("{}.txt".format(fiction_name), "r", encoding="utf-8") as f_r:
                f.write("{}\n\n    {}\n\n".format(chapter_name, chapter_content))
                try:
                    print(fiction_name, chapter_name, "写入成功")
                except Exception:
                    pass


class Biqugeso(scrapy.spiders.Spider):
    source = "笔趣阁"
    name = "biqugeso"
    allowed_domains = ["biqugeso.com"]
    start_urls = [
        # "http://www.biqugeso.com/book/22088/",
        # "http://www.biqugeso.com/book/50382/",
        # "http://www.biqugeso.com/book/39328/",
        # "http://www.biqugeso.com/book/26348/",
        "http://www.biqugeso.com/book/7679/",
    ]

    # for i in range(1, 50383):
    #     url = "http://www.biqugeso.com/book/{}/".format(i)
    #     start_urls.append(url)

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_img = hxs.select('''//img[@class="img-thumbnail"]/@src''').extract_first()
        fiction_name = hxs.select('''//h1[@class="bookTitle"]/text()''').extract_first()
        fiction_update_time = hxs.select('''//span[@class="hidden-xs"]/text()''').extract_first().replace("）", '').replace("（", '')
        status = hxs.select('''//span[@class="blue"]/text()''').extract()[-1]
        viewing_count = hxs.select('''//span[@class="blue"]/text()''').extract()[-2]
        classification = hxs.select('''/html/body/div[2]/ol/li[2]/a/text()''').extract_first()
        author = hxs.select('''/html/body/div[2]/div[1]/div/div/div[2]/p[1]/a[1]/text()''').extract_first()
        # print(fiction_img, fiction_name, status, viewing_count, classification, fiction_update_time, author)
        li = hxs.select('''//dd[@class="col-md-3"]/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            # if index < 110:
            #     continue
            # self.down_txt(url, index)
            yield Request(url,
                          callback=lambda response, index=index, fiction_img=fiction_img, author=author, fiction_name=fiction_name, status=status, viewing_count=viewing_count
                                          , fiction_update_time=fiction_update_time, classification=classification:
                          self.get_chaper_content(response, index, fiction_img, author, fiction_name, fiction_update_time, status, viewing_count, classification),
                          dont_filter=True
                          )

    def get_chaper_content(self, response, index, fiction_img, author, fiction_name, fiction_update_time, status, viewing_count, classification):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//*[@id="content"]/div[1]/h1/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="htmlContent"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)

    def down_txt(self, url, index):
        try:
            ret = requests.get(url=url, headers=headers)
        except Exception:
            time.sleep(5)
            ret = requests.get(url=url, headers=headers)
        ret.encoding = "gbk"
        html = ret.text
        soup = BeautifulSoup(html, 'html.parser')
        fiction_name = soup.find('ol', attrs={"class": "breadcrumb hidden-xs"}).find_all("li")[2].a.text.strip()
        chapter_name = soup.find('h1', attrs={"class": "readTitle"}).text.strip()
        chapter_name = re.sub("第.*?章", "", chapter_name)
        chapter_name = "第" + str(index) + "章 " + chapter_name
        chapter_content = soup.find('div', attrs={"id": "htmlContent"}).text \
            .replace("\xa0", ' ').replace("\t", '').strip()
        # print(fiction_name, chapter_name, chapter_content)
        with open("{}.txt".format(fiction_name), "a", encoding="utf-8") as f:
            with open("{}.txt".format(fiction_name), "r", encoding="utf-8") as f_r:
                f.write("{}\n\n    {}\n\n".format(chapter_name, chapter_content))
                print(fiction_name, chapter_name, "写入成功")


class Xs8(scrapy.spiders.Spider):
    source = "言情小说吧"
    name = "xs8"
    allowed_domains = ["xs8.cn"]
    start_urls = [
        "https://www.xs8.cn/finish?pageSize=10&gender=2&catId=-1&isFinish=1&isVip=-1&size=-1&updT=-1&orderBy=0&pageNum=" + str(page) for page in range(1, 4729)
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@class="right-book-list"]/ul/li''')
        for i in li:
            fiction_url = "https://www.xs8.cn" + i.select('''.//div[@class="book-img"]/a/@href''').extract_first() + "#Catalog"
            fiction_name = i.select('''.//div[@class="book-info"]/h3/a/text()''').extract_first()
            author = i.select('''.//div[@class="book-info"]/h4/a/text()''').extract_first()
            classification = i.select('''.//div[@class="book-info"]/p[@class="tag"]/span[@class="org"]/text()''').extract_first()
            status = i.select('''.//div[@class="book-info"]/p[@class="tag"]/span[@class="green"]/text()''').extract_first()
            viewing_count = i.select('''.//div[@class="book-info"]/p[@class="tag"]/span[@class="blue"]/text()''').extract_first()
            # print(classification, fiction_url, fiction_name, author, status, viewing_count)
            yield Request(fiction_url,
                          callback=lambda response, author=author, fiction_name=fiction_name, status=status, viewing_count=viewing_count, classification=classification:
                          self.get_fiction_info(response, author, fiction_name, status, viewing_count, classification),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, author, fiction_name,
                         status, viewing_count, classification):
        hxs = HtmlXPathSelector(response)
        fiction_img = "https:" + hxs.select('''//*[@id="bookImg"]/img/@src''').extract_first()
        li = hxs.select('''//div[@class="volume-wrap"]/div[@class="volume"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "https:" + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, status=status, viewing_count=viewing_count
                                          , classification=classification, index=index:
                          self.get_chapter_content(response, author, fiction_name, status, viewing_count, classification, fiction_img, index),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name,
                            status, viewing_count, classification, fiction_img, index):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//h3[@class="j_chapterName"]/text()''').extract_first()
        chapter_update_time = hxs.select('''//span[@class="j_updateTime"]/text()''').extract_first()
        chapter_con = hxs.select('''//div[@class="read-content j_readContent"]/p/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        if hxs.select('''//h3[@class="lang"]'''):
            is_vip = True
        else:
            is_vip = False
        fiction_update_time = chapter_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Ymlt(scrapy.spiders.Spider):
    source = "印摩罗天言情小说"
    name = "ymlt"
    allowed_domains = ["ymlt.com"]
    start_urls = [

    ]
    for i in range(1, 16):
        start_urls.append("http://www.ymlt.net/list_{}.html".format(i))
    for i in range(1, 21):
        start_urls.append("http://www.ymlt.net/good_{}.html".format(i))

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//div[@class="block"]/ul/li''')
        for i in li:
            url = "http://www.ymlt.net" + i.select('''.//a[1]/@href''').extract_first()
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        hxs = HtmlXPathSelector(response)
        fiction_img = "http://www.ymlt.net" + hxs.select('''//div[@class="block_img2"]/img/@src''').extract_first()
        fiction_name = hxs.select('''//div[@class="block_txt2"]/h2/text()''').extract_first()
        fiction_update_time = hxs.select('''//div[@class="block_txt2"]/p/text()''').extract()[-1].split()[-1]
        author = hxs.select('''//div[@class="block_txt2"]/p/a/text()''').extract_first()

        li = hxs.select('''//ul[@class="chapter"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, fiction_update_time=fiction_update_time, index=index:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//*[@id="nr_title"]/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="nr1"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"

        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        status = ''
        chapter_update_time = ''
        viewing_count = ''
        classification = '言情小说'
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Msxf(scrapy.spiders.Spider):
    source = "陌上香坊"
    name = "msxf"
    allowed_domains = ["msxf.cn"]
    start_urls = [

    ]
    # for i in range(0, 1):
    for i in range(0, 74):
        start_urls.append("http://www.msxf.cn/shuku/0-0-0-0-0-1-0-{}.html".format(i))

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//ul[@class="clear"]/li/p[@class="screenshot"]/a/@href''').extract()
        for i in li:
            yield Request(i,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//p[@class="title"]/a/text()''').extract_first()
        fiction_img = hxs.select('''//dd[@class="pic"]/a/img[1]/@src''').extract_first()
        status = hxs.select('''//p[@class="info"]/span/em/text()''').extract_first()
        viewing_count = hxs.select('''//p[@class="info"]/span/em/text()''').extract()[3]
        url = "http://www.msxf.cn" + hxs.select('''//a[@class="moreList"]/@href''').extract_first()
        yield Request(url,
                      callback=lambda response, fiction_name=fiction_name, fiction_img=fiction_img, status=status, viewing_count=viewing_count:
                      self.get_fiction_info1(response, fiction_name, fiction_img, status, viewing_count),
                      dont_filter=True
                      )

    def get_fiction_info1(self, response, fiction_name, fiction_img, status, viewing_count):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''//div[@class="chapter-path"]/span/a[2]/text()''').extract_first()
        fiction_update_time = hxs.select('''//p[@class="book-mes"]/span/text()''').extract()[1].replace("更新时间：", '')
        author = hxs.select('''//p[@class="book-mes"]/span/a/text()''').extract_first()
        li = hxs.select('''//ul[@class="chapter-list clear"]/li''')
        index = 0
        for i in li:
            url = i.select('''.//a/@href''').extract_first()
            chapter_name = i.select('''.//a/text()''').extract_first()
            if i.select('''.//em[@class="vipico"]'''):
                is_vip = True
            else:
                is_vip = False
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, status=status, fiction_name=fiction_name, fiction_update_time=fiction_update_time
                                          , index=index, viewing_count=viewing_count, is_vip=is_vip, chapter_name=chapter_name, classification=classification:
                          self.get_chapter_content(response, author, fiction_name, status, viewing_count, fiction_img, index, fiction_update_time, is_vip, chapter_name, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, status, viewing_count, fiction_img, index, fiction_update_time, is_vip, chapter_name, classification):
        hxs = HtmlXPathSelector(response)
        try:
            chapter_update_time = hxs.select('''//div[@class="article-info"]/text()''').extract()[2].replace("发布时间：", '')
            chapter_con = hxs.select('''//*[@id="article-content"]/p/text()''').extract()
            chapter_content = ''
            for i in chapter_con:
                chapter_content += i.replace("\xa0", '&nbsp;').strip() + "<br>"
        except Exception:
            chapter_update_time = ''
            chapter_content = ''

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Quanben(scrapy.spiders.Spider):
    source = "全本小说网"
    name = "quanben"
    allowed_domains = ["quanben.io"]
    start_urls = [
        "http://www.quanben.io/n/gaoguandexinchong/list.html"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//h1[@itemprop="name headline"]/text()''').extract_first()
        author = hxs.select('''//span[@itemprop="author"]/text()''').extract_first()
        classification = hxs.select('''//span[@itemprop="category"]/text()''').extract_first()
        status = hxs.select('''//div[@class="list2"]/p[3]/span/text()''').extract_first()
        fiction_img = hxs.select('''//div[@class="list2"]/img/@src''').extract_first()
        li = hxs.select('''//li[@itemprop="itemListElement"]/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.quanben.io" + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, status=status, fiction_name=fiction_name, index=index, classification=classification:
                          self.get_chapter_content(response, author, fiction_name, status, fiction_img, index, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, status,
                            fiction_img, index, classification):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//h1[@class="headline"]/text()''').extract_first()
        info = hxs.select('''/html/body/div[3]/div[1]/script[3]/text()''').extract_first()
        info = re.findall("""'book','ajax','pinyin','(.*?)','id','(\d+)','sky','(.*?)','t','(\d+)'""", info)[0]
        pinyin = info[0]
        id = int(info[1])
        sky = info[2]
        t = int(info[3])
        ret = requests.post(
            url="http://www.quanben.io/index.php?c=book&a=ajax",
            headers=headers,
            data={
                "pinyin": pinyin,
                "id": id,
                "sky": sky,
                "t": t,
                "_type": "ajax",
            }
        )
        chapter_content = str(ret.text)
        if len(chapter_content.strip()) > 0:
            is_vip = False
        else:
            is_vip = True

        viewing_count = ''
        fiction_update_time = ''
        chapter_update_time = ''

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Zfbook(scrapy.spiders.Spider):
    source = "逐风中文网"
    name = "zfbook"
    allowed_domains = ["zfbook.net"]
    start_urls = [
        # "https://www.zfbook.net/shuku/0-0-0-0-0-1-0-46.html"
    ]

    for i in range(0, 46):
        start_urls.append("https://www.zfbook.net/shuku/0-0-0-0-0-1-0-{}.html".format(i))

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//ul[@class="clear"]/li/p/a/@href''').extract()
        for i in li:
            url = i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        hxs = HtmlXPathSelector(response)
        fiction_img = hxs.select('''/html/body/div[3]/div/div/div[1]/dl/dd/a/img/@src''').extract_first()
        status = hxs.select('''/html/body/div[3]/div/div/div[1]/dl/dt/p[2]/span[1]/em/text()''').extract_first()
        classification = hxs.select('''/html/body/div[2]/div/div/a[2]/text()''').extract_first()
        viewing_count = hxs.select('''/html/body/div[3]/div/div/div[1]/dl/dt/p[2]/span[4]/em/text()''').extract_first()
        url = "https://www.zfbook.net" + hxs.select('''/html/body/div[3]/div/div/div[1]/dl/dt/p[7]/a[1]/@href''').extract_first()
        yield Request(url,
                      callback=lambda response, fiction_img=fiction_img, status=status, classification=classification, viewing_count=viewing_count:
                      self.get_fiction_info1(response, fiction_img, status, classification, viewing_count),
                      dont_filter=True
                      )

    def get_fiction_info1(self, response, fiction_img, status, classification, viewing_count):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''/html/body/div[3]/div[2]/p[1]/span/text()''').extract_first()
        fiction_update_time = hxs.select('''/html/body/div[3]/div[2]/p[2]/span[2]/text()''').extract_first()
        author = hxs.select('''/html/body/div[3]/div[2]/p[2]/span[1]/a/text()''').extract_first()
        li = hxs.select('''//ul[@class="chapter-list clear"]/li''')
        index = 0
        for i in li:
            url = i.select('''.//a/@href''').extract_first()
            if i.select('''.//em[@class="vipico"]'''):
                is_vip = True
            else:
                is_vip = False
            index += 1
            chapter_name = i.select('''.//a/text()''').extract_first()
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, status=status, fiction_name=fiction_name, fiction_update_time=fiction_update_time
                                          , index=index, viewing_count=viewing_count, is_vip=is_vip, chapter_name=chapter_name, classification=classification:
                          self.get_chapter_content(response, author, fiction_name, status, viewing_count, fiction_img, index, fiction_update_time, is_vip, chapter_name, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, status, viewing_count, fiction_img, index, fiction_update_time, is_vip, chapter_name, classification):
        hxs = HtmlXPathSelector(response)
        try:
            chapter_update_time = hxs.select('''//div[@class="article-info"]/text()''').extract()[-2]
            chapter_con = hxs.select('''//*[@id="article-content"]/p/text()''').extract()
            chapter_content = ''
            for i in chapter_con:
                chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        except Exception:
            chapter_update_time = ''
            chapter_content = ''

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Slzww(scrapy.spiders.Spider):
    source = "思路中文网"
    name = "slzww"
    allowed_domains = ["slzww.com"]
    start_urls = [
        # "http://www.slzww.com/slzwwtoplastupdate/0/468.html"
    ]

    for i in range(1, 2):
        start_urls.append("http://www.slzww.com/slzwwtoplastupdate/0/{}.html".format(i))

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//*[@id="content"]/table/tr/td[1]/a/@href''').extract()
        for i in li:
            url = i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//td[@valign="middle"]/h1/text()''').extract_first()
        fiction_img = hxs.select('''//td[@valign="top"]/a/img/@src''').extract_first()
        classification = hxs.select('''//*[@id="content"]/table/tr[1]/td/table/tr[2]/td[1]/text()''').extract_first().split("：")[1]
        author = hxs.select('''//*[@id="content"]/table/tr[1]/td/table/tr[2]/td[2]/text()''').extract_first().split("：")[1]
        fiction_update_time = hxs.select('''//*[@id="content"]/table/tr[1]/td/table/tr[3]/td[1]/text()''').extract_first().split("：")[1]
        status = hxs.select('''//*[@id="content"]/table/tr[1]/td/table/tr[3]/td[2]/text()''').extract_first().split("：")[1]
        viewing_count = hxs.select('''//*[@id="content"]/table/tr[1]/td/table/tr[4]/td[1]/text()''').extract_first().split("：")[1]
        url = hxs.select('''//*[@id="content"]/table/tr[4]/td/table/tr/td[1]/ul/li[1]/a/@href''').extract_first()
        yield Request(url,
                      callback=lambda response, fiction_img=fiction_img, status=status, classification=classification,
                                      viewing_count=viewing_count, fiction_update_time=fiction_update_time, fiction_name=fiction_name, author=author:
                      self.get_fiction_info1(response, fiction_img, status, classification, viewing_count, fiction_name, author, fiction_update_time),
                      dont_filter=True
                      )

    def get_fiction_info1(self, response, fiction_img, status, classification, viewing_count, fiction_name, author, fiction_update_time):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//*[@id="Content_list"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, status=status, fiction_name=fiction_name, fiction_update_time=fiction_update_time
                                          , index=index, viewing_count=viewing_count, classification=classification:
                          self.get_chapter_content(response, author, fiction_name, status, viewing_count, fiction_img, index, fiction_update_time, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, status, viewing_count, fiction_img, index, fiction_update_time, classification):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''/html/body/h1/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Fmxxs(scrapy.spiders.Spider):
    source = "言情小说书库"
    name = "fmxxs"
    allowed_domains = ["fmxxs.com"]
    start_urls = [

    ]

    for i in range(1, 6):
        start_urls.append("http://www.fmxxs.com/data/xz/list1_{}.html".format(i))

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select(
            '''/html/body/table[7]/tr/td[3]/table/tr[2]/td[2]/table/tr/td/table[1]/tr/td[3]/a/@href''').extract()
        for i in li:
            url = i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//td[@class="p6"]/text()''').extract_first()
        fiction_img = hxs.select('''//td[@class="pic01"]/img/@src''').extract_first()
        author = hxs.select('''//td[@class="p88"]/a/text()''').extract_first()
        fiction_update_time = hxs.select('''//span[@class="p5"]/text()''').extract_first()
        url = response.url + hxs.select('''//td[@class="p88"][@align="right"]/a/@href''').extract_first()
        yield Request(url,
                      callback=lambda response, fiction_img=fiction_img, fiction_name=fiction_name, author=author, fiction_update_time=fiction_update_time:
                      self.get_fiction_info1(response, fiction_img, fiction_name, author, fiction_update_time),
                      dont_filter=True
                      )

    def get_fiction_info1(self, response, fiction_img, fiction_name, author, fiction_update_time):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//td[@align="center"]/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url.split("/")[-1]
            url = response.url.replace(url, '') + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, fiction_update_time=fiction_update_time, index=index,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, ):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//*[@id="title"]/text()''').extract_first().replace("\xa0", "")
        chapter_con = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        classification = '言情小说'
        viewing_count = ''
        status = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Qidian(scrapy.Spider):
    source = "起点中文网"
    name = 'qidian'
    allowed_domains = ['qidian.com']
    start_urls = [
        "https://www.qidian.com/all?orderId=&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page=" + str(page) for page in range(1, 47530)
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        li = hxs.select('''//ul[@class="all-img-list cf"]/li/div[@class="book-img-box"]/a/@href''').extract()
        for i in li:
            url = "https:" + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//div[@class="book-info "]/h1/em/text()''').extract_first()
        fiction_img = "https:" + hxs.select('''//a[@id="bookImg"]/img/@src''').extract_first()
        author = hxs.select('''//a[@class="writer"]/text()''').extract_first()
        status = hxs.select('''//p[@class="tag"]/span[@class="blue"]/text()''').extract_first()
        ret = requests.get(url="https://book.qidian.com/")
        csrfToken = ret.cookies['_csrfToken']
        ret = requests.get(url="https://book.qidian.com/ajax/book/category?_csrfToken={}&bookId={}".format(csrfToken, response.url.split("/")[-1]))
        ret.encoding = "utf-8"
        data = ret.json()['data']['vs'][0]['cs']

        li = []
        for i in data:
            url = "https://read.qidian.com/chapter/" + i['cU']
            chapter_update_time = i['uT']
            chapter_name = i['cN']
            is_vip = False
            li.append({
                "url": url, "chapter_name": chapter_name, "chapter_update_time": chapter_update_time, "is_vip": is_vip
            })
        data = ret.json()['data']['vs'][1]['cs']
        for i in data:
            url = "https://read.qidian.com/chapter/" + i['cU']
            chapter_update_time = i['uT']
            chapter_name = i['cN']
            is_vip = False
            li.append({
                "url": url, "chapter_name": chapter_name, "chapter_update_time": chapter_update_time, "is_vip": is_vip
            })
        index = 0
        for i in li:
            url = i['url']
            chapter_name = i['chapter_name']
            chapter_update_time = i['chapter_update_time']
            is_vip = i['is_vip']
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, fiction_update_time=chapter_update_time, index=index, status=status,
                                          chapter_name=chapter_name:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, chapter_name, is_vip),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status,
                            chapter_name, is_vip):
        hxs = HtmlXPathSelector(response)
        classification = hxs.select('''/html/body/div[2]/div[3]/a[3]/text()''').extract_first()
        chapter_con = hxs.select('''//div[@class="read-content j_readContent"]/p/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", " ") + "<br>"

        chapter_update_time = fiction_update_time
        viewing_count = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Xklxsw(scrapy.Spider):
    source = "可乐小说网"
    name = 'xklxsw'
    allowed_domains = ['xklxsw.com']
    start_urls = [
        # "https://www.xklxsw.com/book/38972/",
        "https://www.xklxsw.com/book/39552/",
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        fiction_name = hxs.select('''//h1[@class="article-title"]/text()''').extract_first()
        author = hxs.select('''/html/body/div[2]/div[2]/text()''').extract()[2].replace("\xa0", '').split("：")[1].split("\n")[0]
        status = hxs.select('''/html/body/div[2]/div[2]/text()''').extract()[2].replace("\xa0", '').split("：")[-1]
        fiction_img = "https://www.xklxsw.com" + hxs.select('''//div[@class="bookimg"]/img/@data-original''').extract_first()
        classification = hxs.select('''//div[@class="dh"]/a[2]/text()''').extract_first()
        li = hxs.select('''/html/body/div[2]/div[5]/span[@class="item chapter"]/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, status=status, index=index, classification=classification:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, status, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, status, classification):
        hxs = HtmlXPathSelector(response)
        chapter_name = hxs.select('''//h1[@class="title"]/text()''').extract_first()
        chapter_con = hxs.select('''//*[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        fiction_update_time = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Zhuishubang(scrapy.Spider):
    source = "追书帮"
    name = 'zhuishubang'
    allowed_domains = ['zhuishubang.com']
    start_urls = [
        # "https://www.zhuishubang.com/48204/"
    ]

    for i in range(1, 1798):
        start_urls.append("https://www.zhuishubang.com/all/0_lastupdate_0_0_0_0_0_0_{}.html".format(i))

    def parse(self, response):
        li = response.xpath('''//div[@class="listRightBottom"]/ul/li''')
        for i in li:
            fiction_name = i.xpath('''.//h2/a/text()''').extract_first()
            fiction_img = i.xpath('''.//a/img/@src''').extract_first()
            url = i.xpath('''.//h2/a/@href''').extract_first()
            author = i.xpath('''.//p[@class="bookPhrTop"]/span[@class="writer"]/text()''').extract_first()
            status = i.xpath('''.//p[@class="bookPhrTop"]/span[@class="state"]/text()''').extract_first()
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, fiction_img=fiction_img, author=author, status=status:
                          self.get_fiction_info(response, fiction_name, fiction_img, author, status),
                          dont_filter=True
                          )
        # li = [
        #     # {"url": "https://www.zhuishubang.com/45964/", "name": "极品好儿媳", "author": "毒刺", "fiction_img": "https://www.zhuishubang.com/files/article/image/45/45964/45964l.jpg"},
        #     # {"url": "https://www.zhuishubang.com/47500/", "name": "乡野风月", "author": "鸿运当头", "fiction_img": "https://www.zhuishubang.com/files/article/image/47/47500/47500l.jpg"},
        #     # {"url": "https://www.zhuishubang.com/48919/", "name": "爱上你，我有罪", "author": "追书帮", "fiction_img": "https://www.zhuishubang.com/modules/article/images/nocover.jpg"},
        #     # {"url": "https://www.zhuishubang.com/47561/", "name": "家有美媳", "author": "乔静陆明华陆平", "fiction_img": "https://www.zhuishubang.com/files/article/image/47/47561/47561l.jpg"},
        #     # {"url": "https://www.zhuishubang.com/3911/", "name": "青春无期", "author": "浪里小白龙", "fiction_img": "https://www.zhuishubang.com/files/article/image/3/3911/3911l.jpg"},
        #     # {"url": "https://www.zhuishubang.com/43845/", "name": "沉沦：女主播的秘密", "author": "谢晚风", "fiction_img": "https://www.zhuishubang.com/modules/article/images/nocover.jpg"},
        #
        # ]
        #
        # for i in li:
        #     fiction_name = i['name']
        #     fiction_img = i['fiction_img']
        #     url = i['url']
        #     author = i['author']
        #     status = ''
        #     yield Request(url,
        #                   callback=lambda response, fiction_name=fiction_name, fiction_img=fiction_img, author=author,
        #                                   status=status:
        #                   self.get_fiction_info(response, fiction_name, fiction_img, author, status),
        #                   dont_filter=True
        #                   )

    def get_fiction_info(self, response, fiction_name, fiction_img, author, status):
        classification = response.xpath('''/html/body/div[3]/div/div[2]/div[1]/div[3]/dl/dd[2]/text()''').extract_first().replace("类型：", '')
        viewing_count = response.xpath('''/html/body/div[3]/div/div[2]/div[1]/div[3]/dl/dd[5]/text()''').extract_first().replace("收藏：", '')
        fiction_update_time = response.xpath('''/html/body/div[3]/div/div[2]/div[1]/div[3]/div[1]/span/text()''').extract_first()
        li = response.xpath('''//div[@class="chapterCon"]/ul/li/a/@href''').extract()
        urlli = []
        for i in li:
            urlli.append("https://www.zhuishubang.com" + i)
        urlli.reverse()
        index = 0
        for url in urlli:
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, classification=classification, index=index, status=status,
                                          viewing_count=viewing_count:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count):
        chapter_name = response.xpath('''//div[@class="articleTitle"]/h2/text()''').extract_first() + str(index)
        chapter_con = response.xpath('''string(//div[@class="articleCon"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Wodeshucheng(scrapy.Spider):
    source = "我的书城网"
    name = 'wodeshucheng'
    allowed_domains = ['wodeshucheng.com']
    start_urls = [
        # "http://wodeshucheng.com/7_1/"
    ]

    for i in range(1, 289):
        start_urls.append("http://wodeshucheng.com/7_{}/".format(i))

    def parse(self, response):
        li = response.xpath('''//div[@class="bk"]''')
        for i in li:
            url = i.xpath('''.//div[@class="pic"]/a/@href''').extract_first()
            fiction_img = i.xpath('''.//div[@class="pic"]/a/img/@src''').extract_first()
            fiction_update_time = i.xpath('''.//div[@class="bnew"]/span/text()''').extract_first().replace("最后更新：", '')
            fiction_name = i.xpath('''.//h3/a/text()''').extract_first()
            author = i.xpath('''.//h4/text()''').extract_first().replace("作者：", '')
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, fiction_img=fiction_img, author=author, fiction_update_time=fiction_update_time:
                          self.get_fiction_info(response, fiction_name, fiction_img, author, fiction_update_time),
                          dont_filter=True
                          )
        # li = [
        #     {"url": "http://wodeshucheng.com/book_21124/", "fiction_name": "爱似毒药恨似糖", "author": "月茶"}
        # ]
        #
        # for i in li:
        #     url = i['url']
        #     fiction_img = ''
        #     fiction_update_time = ''
        #     fiction_name = i['fiction_name']
        #     author = i['author']
        #     yield Request(url,
        #                   callback=lambda response, fiction_name=fiction_name, fiction_img=fiction_img, author=author,
        #                                   fiction_update_time=fiction_update_time:
        #                   self.get_fiction_info(response, fiction_name, fiction_img, author, fiction_update_time),
        #                   dont_filter=True
        #                   )

    def get_fiction_info(self, response, fiction_name, fiction_img, author, fiction_update_time):
        classification = response.xpath('''//div[@class="infos"]/span/a/text()''').extract_first()
        status = response.xpath('''//font[@color="red"]/text()''').extract_first()
        li = response.xpath('''//div[@class="book_list boxm"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, classification=classification, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification):
        chapter_name = response.xpath('''//div[@class="h1title"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''//div[@id="htmlContent"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class cuisiliu(scrapy.Spider):
    source = "垂丝柳"
    name = 'cuisiliu'
    allowed_domains = ['cuisiliu.com']
    start_urls = [
        # "http://www.cuisiliu.com/book/11370.html",
        # "http://www.cuisiliu.com/book/11042.html",
    ]
    for i in range(1, 19725):
        start_urls.append("http://www.cuisiliu.com/book/{}.html".format(i))

    def parse(self, response):
        fiction_img = "http://www.cuisiliu.com" + response.xpath('''//div[@class="bookcover col-lg-3 col-md-3 col-sm-3 col-xs-4"]/img/@src''').extract_first()
        fiction_name = response.xpath('''//h1[@class="col-xs-12"]/text()''').extract_first()
        classification = response.xpath('''//td[@class="col-xs-4"]/text()''').extract_first().replace("分类：", '')
        author = response.xpath('''//td[@class="col-xs-4"][2]/text()''').extract_first().replace("作者：", '')
        status = response.xpath('''//td[@class="col-xs-4"]/text()''').extract()[2].replace("状态：", '')
        viewing_count = response.xpath('''//td[@class="hidden-xs"]/text()''').extract()[-1].replace("月点击：", '')
        fiction_update_time = response.xpath('''//p[@class="pull-right"]/text()''').extract_first().replace(")", '').replace("(", '')
        li = response.xpath('''//li[@class="list-group-item col-lg-3 col-md-3 col-sm-4 col-xs-6 book"]/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.cuisiliu.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, classification=classification, index=index, status=status,
                                          viewing_count=viewing_count:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count):
        chapter_name = response.xpath('''//*[@id="content"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''//div[@class="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Er9shu(scrapy.Spider):
    source = "29书吧"
    name = '29shu'
    allowed_domains = ['29shu.com']
    start_urls = [
        "https://www.29shu.com/xs/19/19101/",
        "https://www.29shu.com/xs/4/4758/",
    ]

    # for i in range(1, 1666):
    #     start_urls.append("https://www.29shu.com/xs/quanbu-default-0-0-0-0-0-0-{}.html".format(i))

    def parse(self, response):
        classification = response.xpath('''//*[@id="main"]/div[1]/div[1]/a[2]/text()''').extract_first()
        fiction_img = "https://www.29shu.com" + response.xpath('''//div[@class="pic"]/img/@src''').extract_first()
        fiction_name = response.xpath('''//*[@id="info"]/h1/text()''').extract_first()
        fiction_update_time = response.xpath('''//*[@id="info"]/div[2]/text()[2]''').extract_first().replace(")", '').replace("(", '')
        author = response.xpath('''//*[@id="info"]/div[1]/span/a/text()''').extract_first()
        li = response.xpath('''//*[@id="main"]/div[4]/div[1]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://www.29shu.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, index=index, classification=classification:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index,
                            fiction_update_time, classification):
        chapter_name = response.xpath('''//*[@id="jsnc_l"]/div/div[1]/h1/text()''').extract_first()
        chapter_con = response.xpath('''//div[@id="htmlContent"]/text()''').extract()
        chapter_con_ = response.xpath('''//*[@id="jsnc_l"]/div/p[2]/text()''').extract_first()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        chapter_content += chapter_con_
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        status = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class W21danmei(scrapy.Spider):
    source = "就要耽美网"
    name = '521danmei'
    allowed_domains = ['521danmei.com']
    start_urls = [
        "http://www.521danmei.com/read/26023/",
    ]

    def parse(self, response):
        fiction_name = response.xpath('''//div[@class="infotitle"]/h1/text()''').extract_first()
        classification = response.xpath('''//a[@class="typename"]/text()''').extract_first()
        author = response.xpath('''//*[@id="info"]/div[1]/span/a/text()''').extract_first()
        fiction_update_time = "http://www.521danmei.com" + response.xpath('''//*[@id="info"]/div[1]/span/span/script/@src''').extract_first()
        ret = requests.get(url=fiction_update_time, headers=headers)
        fiction_update_time = ret.text.replace('''document.write''', '').replace('("', '').replace('")', '')
        fiction_img = "http://www.521danmei.com" + response.xpath('''//div[@class="img_in"]/img/@src''').extract_first()
        # print(classification, fiction_name, author, fiction_update_time, fiction_img)
        li = response.xpath('''//*[@id="box"]/div/dl/dd''')
        index = 0
        for i in li:
            url = "http://www.521danmei.com" + i.xpath('''.//a/@href''').extract_first()
            index += 1
            # if "医生" not in i.xpath('''.//a/text()''').extract_first():
            #     continue
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_name=fiction_name, index=index, classification=classification:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index,
                            fiction_update_time, classification):
        chapter_name = response.xpath('''//*[@id="main"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''//*[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + '<br>'
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        status = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Haxds(scrapy.Spider):
    source = "海岸线文学网"
    name = 'haxds'
    allowed_domains = ['haxds.com']
    start_urls = [
        "https://www.haxds.com/files/article/html/38/38186/index.html",
    ]

    def parse(self, response):
        fiction_name = response.xpath('''//div[@class="btitle"]/h1/text()''').extract_first()
        author = response.xpath('''//div[@class="btitle"]/em/a/text()''').extract_first()
        classification = response.xpath('''//*[@id="wrapper"]/div[2]/a[2]/text()''').extract_first()
        # print(fiction_name, author, classification)
        li = response.xpath('''//dl[@class="chapterlist"]/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://www.haxds.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_name=fiction_name, index=index, classification=classification:
                          self.get_chapter_content(response, author, fiction_name, index, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, index, classification):
        chapter_name = index
        chapter_con = response.xpath('''//*[@id="BookText"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + '<br>'
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False
        fiction_img = ''
        viewing_count = ''
        fiction_update_time = ''
        status = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Lewendu8(scrapy.Spider):
    source = "乐文小说网"
    name = 'lewendu8'
    allowed_domains = ['lewendu8.com']
    start_urls = [
        "https://www.lewendu8.com/books/55/55733/",
    ]

    def parse(self, response):
        fiction_name = response.xpath('''//div[@class="infot"]/h1/text()''').extract_first()
        # classification = response.xpath('''//div[@class="infot"]/h1/text()''').extract_first()
        author = response.xpath('''//div[@class="infot"]/span/text()''').extract_first().replace("作者：", '')
        # print(fiction_name, author)
        li = response.xpath('''//div[@class="dccss"]/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://www.lewendu8.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_name=fiction_name, index=index,:
                          self.get_chapter_content(response, author, fiction_name, index, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, index, ):
        classification = response.xpath('''//div[@class="border_b"]/text()''').extract_first().split()[0].replace("类别：", '')
        chapter_name = response.xpath('''//div[@align="center"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''//*[@id="content"]/p/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + '<br>'
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        fiction_img = ''
        viewing_count = ''
        fiction_update_time = ''
        status = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Lewenxiaoshuo(scrapy.Spider):
    source = "乐文小说网"
    name = 'lewenxiaoshuo'
    allowed_domains = ['lewenxiaoshuo.com']
    start_urls = [
        "https://www.lewenxiaoshuo.com/books/sifangcuirushi/",
    ]

    def parse(self, response):
        fiction_name = response.xpath('''//div[@id="info"]/h1/text()''').extract_first()
        # classification = response.xpath('''//div[@class="infot"]/h1/text()''').extract_first()
        author = response.xpath('''//div[@id="info"]/p/text()''').extract_first().replace("\xa0", "").replace("作者：", '')
        # print(fiction_name, author)
        li = response.xpath('''//div[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author,
                                          fiction_name=fiction_name, index=index,:
                          self.get_chapter_content(response, author, fiction_name, index, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, index, ):
        classification = response.xpath('''//div[@class="con_top"]/a[2]/text()''').extract_first()
        chapter_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + '<br>'
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        fiction_img = ''
        viewing_count = ''
        fiction_update_time = ''
        status = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Banfusheng(scrapy.Spider):
    source = "半浮生"
    name = 'banfusheng'
    allowed_domains = ['banfusheng.com']
    start_urls = [
        "http://www.banfusheng.com/chapter/1006911669/5332585.html",
        # "http://www.banfusheng.com/chapter/1006911669/5332508.html",
    ]

    def parse(self, response):

        classification = response.xpath('''//*[@id="header"]/div[2]/span/a[2]/text()''').extract_first()
        fiction_name = response.xpath('''//*[@id="header"]/div[2]/span/a[3]/text()''').extract_first()
        author = response.xpath('''//*[@id="center"]/div[1]/span[1]/a/text()''').extract_first()
        chapter_name = response.xpath('''//div[@class="title"]/h1/text()''').extract_first()
        chapter_update_time = response.xpath('''//div[@class="title"]/span/text()''').extract()[-1]
        chapter_con = response.xpath('''//div[@id="content"]/p/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += '    ' + i.replace("\xa0", "&nbsp;") + '<br>'
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False
        buyaod = response.url.split("/")[-1]
        url = response.url.replace(buyaod, '') + \
              response.xpath('''//div[@class="jump jumptop"]/a/@href''').extract()[-1]

        fiction_img = ''
        fiction_update_time = chapter_update_time
        status = ''
        viewing_count = ''
        index = chapter_update_time
        timeArray = time.strptime(index, "%Y-%m-%d %H:%M:%S")
        index = int(time.mktime(timeArray))
        # print(chapter_content, classification, fiction_name, chapter_name, chapter_update_time, author, url, index)
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)

        yield Request(url,
                      callback=lambda response,:
                      self.get_chapter_content(response, ),
                      dont_filter=True
                      )

    def get_chapter_content(self, response, ):
        classification = response.xpath('''//*[@id="header"]/div[2]/span/a[2]/text()''').extract_first()
        fiction_name = response.xpath('''//*[@id="header"]/div[2]/span/a[3]/text()''').extract_first()
        author = response.xpath('''//*[@id="center"]/div[1]/span[1]/a/text()''').extract_first()
        chapter_name = response.xpath('''//div[@class="title"]/h1/text()''').extract_first()
        chapter_update_time = response.xpath('''//div[@class="title"]/span/text()''').extract()[-1]

        chapter_con = response.xpath('''//div[@id="content"]/p/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += '    ' + i.replace("\xa0", "&nbsp;") + '<br>'
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False
        buyaod = response.url.split("/")[-1]
        url = response.url.replace(buyaod, '') + \
              response.xpath('''//div[@class="jump jumptop"]/a/@href''').extract()[-1]

        fiction_img = ''
        fiction_update_time = chapter_update_time
        status = ''
        viewing_count = ''
        index = chapter_update_time
        timeArray = time.strptime(index, "%Y-%m-%d %H:%M:%S")
        index = int(time.mktime(timeArray))
        # print(chapter_content, classification, fiction_name, chapter_name, chapter_update_time, author, url,index)
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)

        yield Request(url,
                      callback=lambda response,:
                      self.get_chapter_content(response, ),
                      dont_filter=True
                      )


class Yueduyue(scrapy.Spider):
    source = "阅读悦"
    name = 'yueduyue'
    allowed_domains = ['yueduyue.com']
    start_urls = [
        "http://www.yueduyue.com/354_354953/"
    ]

    def parse(self, response):
        classification = response.xpath(
            '''//*[@id="content"]/div/div[2]/div[1]/div[1]/div/a[2]/text()''').extract_first()
        fiction_name = response.xpath('''//div[@class="chapter_head"]/h3/text()''').extract_first()
        author = response.xpath('''//*[@id="content"]/div/div[2]/div[1]/div[2]/p/span[1]/text()''').extract_first()
        status = response.xpath('''//*[@id="content"]/div/div[2]/div[1]/div[2]/p/span[2]/text()''').extract_first()
        fiction_update_time = response.xpath('''//*[@id="content"]/div/div[2]/div[1]/div[2]/p/span[4]/text()''').extract_first()
        # print(classification, fiction_name, author, fiction_update_time, status)
        li = response.xpath('''//ul[@class="f-gray3"]/li/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, classification=classification, fiction_name=fiction_name, author=author, status=status, index=index:
                          self.get_chapter_content(response, classification, fiction_name, author, status, fiction_update_time, index),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, classification, fiction_name, author, status, fiction_update_time, index):
        chapter_name = response.xpath('''//div[@class="read_top"]/h1/text()''').extract_first()
        chapter_update_time = response.xpath('''//p[@class="info"]/span[1]/text()''').extract_first()
        chapter_con = response.xpath('''//div[@id="readcon"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + '<br>'
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        fiction_img = ''
        viewing_count = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Huaxiangju(scrapy.Spider):
    source = "花香居"
    name = 'huaxiangju'
    allowed_domains = ['huaxiangju.com']
    start_urls = [
        "https://www.huaxiangju.com/28059/"
    ]

    def parse(self, response, ):
        classification = response.xpath('''//div[@class="routeLeft"]/a[3]/text()''').extract_first()
        viewing_count = response.xpath('''//div[@class="bookPhr"]/dl/dd[4]/text()''').extract_first().replace("总点击：", '')
        fiction_update_time = response.xpath('''//div[@class="renew"]/span/text()''').extract_first()
        author = response.xpath('''//div[@class="bookPhr"]/dl/dd[1]/text()''').extract_first().replace("作者：", '')
        fiction_img = "https://www.huaxiangju.com" + response.xpath('''//div[@class="bookImg"]/img/@src''').extract_first()
        fiction_name = response.xpath('''//div[@class="bookPhr"]/h2/text()''').extract_first()
        status = ''
        # print(classification, viewing_count, fiction_update_time, author, fiction_img, fiction_name)
        li = response.xpath('''//div[@class="chapterCon"]/ul/li/a/@href''').extract()
        urlli = []
        for i in li:
            urlli.append("https://www.huaxiangju.com" + i)
        urlli.reverse()
        index = 0
        for url in urlli:
            index += 1
            # print(url)
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, fiction_name=fiction_name, classification=classification,
                                          index=index, status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count):
        chapter_name = response.xpath('''//div[@class="articleTitle"]/h2/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="articleCon"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Bichi(scrapy.Spider):
    source = "笔痴中文"
    name = 'bichi'
    allowed_domains = ['bichi.com']
    start_urls = [
        "https://www.bichi.me/read/488946.html"
    ]

    def parse(self, response, ):
        classification = response.xpath('''//div[@class="bookinfo"]/ul/li[1]/span/a/text()''').extract_first()
        fiction_name = response.xpath('''//div[@class="bookinfo"]/h2/em/@title''').extract_first()
        author = response.xpath('''//div[@class="bookinfo"]/ul/li[1]/span/span[1]/span/text()''').extract_first()
        fiction_img = response.xpath('''//div[@class="fleft"]/img/@src''').extract_first()
        # print(classification, fiction_name, fiction_img, author)
        li = response.xpath('''//div[@class="TabCss"]/dl/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = "https://www.bichi.me" + i
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time='', fiction_name=fiction_name, classification=classification, index=index, status='', viewing_count='':
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count):
        chapter_name = response.xpath('''//div[@class="ydleft"]/h2/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="yd_text2"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Kuaiyankanshu(scrapy.Spider):
    source = "快眼看书"
    name = 'kuaiyankanshu'
    allowed_domains = ['kuaiyankanshu.com']
    start_urls = [
        # "https://www.bichi.me/read/488946.html"
    ]
    # for i in range(1, 754400):
    for i in range(1, 754400):
        start_urls.append("https://www.kuaiyankanshu.net/{}/dir.html".format(i))

    def parse(self, response, ):
        classification = response.xpath('''/html/body/section/nav/ul/li[2]/a/text()''').extract_first()
        fiction_name = response.xpath('''//div[@class="header line"]/h1/text()''').extract_first().replace("最佳来源", '')
        author = response.xpath('''/html/body/section/div[1]/div[1]/div/div[2]/div[1]/div[1]/ul/li[1]/a/text()''').extract_first()
        viewing_count = response.xpath('''/html/body/section/div[1]/div[1]/div/div[2]/div[1]/div[1]/ul/li[3]/text()''').extract_first().replace("点击：", '')
        fiction_update_time = response.xpath('''/html/body/section/div[1]/div[1]/div/div[2]/div[1]/div[1]/ul/li[7]/text()''').extract_first().replace("更新：", '')
        fiction_img = "https:" + response.xpath('''/html/body/section/div[1]/div[1]/div/div[2]/div[1]/div[2]/img/@src''').extract_first()
        # print(classification, fiction_name, author, viewing_count, fiction_update_time, fiction_img)
        if models.Fiction_list.objects.filter(fiction_name=fiction_name, update_time=fiction_update_time).exists():
            return
        li = response.xpath('''//ul[@class="dirlist clearfix"]/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://www.kuaiyankanshu.net" + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, fiction_name=fiction_name, classification=classification
                                          , index=index, status='', viewing_count=viewing_count:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count):
        chapter_name = response.xpath('''//div[@class="title"]/h1/a/text()''').extract_first()
        chapter_update_time = response.xpath('''//div[@class="info"]/span[3]/text()''').extract_first().replace("更新时间：", '')
        chapter_con = response.xpath('''//div[@id="chaptercontent"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Szyangxiao(scrapy.Spider):
    source = "南山书院"
    name = 'szyangxiao'
    allowed_domains = ['szyangxiao.com']
    start_urls = [
    ]
    # for i in range(1, 5424):
    for i in range(1, 2):
        start_urls.append("https://www.szyangxiao.com/top/allvisit/{}.shtml".format(i))

    def parse(self, response, ):
        li = response.xpath('''//ul[@class="nav clearfix"]/span/a[2]/@href''').extract()
        for i in li:
            url = "https:" + i
            yield Request(url, callback=lambda response,: self.get_fiction_info(response, ), dont_filter=True)

    def get_fiction_info(self, response):
        classification = response.xpath('''/html/body/div[1]/p/a[2]/text()''').extract_first()
        fiction_name = response.xpath('''//div[@class="wrapper"]/h1/a/text()''').extract_first()
        fiction_img = response.xpath('''/html/body/div[1]/p/img/@src''').extract_first()
        url = "https:" + response.xpath('''/html/body/div[1]/p/a[4]/@href''').extract_first()

        yield Request(url, callback=lambda response, classification=classification, fiction_name=fiction_name, fiction_img=fiction_img:
        self.get_fiction_info1(response, classification, fiction_name, fiction_img), dont_filter=True)

    def get_fiction_info1(self, response, classification, fiction_name, fiction_img):
        fiction_update_time = response.xpath('''/html/body/div[1]/p/text()[1]''').extract_first().replace("更新时间：", '').replace("小说作者：", '').strip()
        author = response.xpath('''/html/body/div[1]/p/a[1]/text()''').extract_first()
        # print(classification, fiction_name, fiction_img, fiction_update_time, author)
        if models.Fiction_list.objects.filter(fiction_name=fiction_name, update_time=fiction_update_time).exists():
            return
        li = response.xpath('''//ul[@class="nav clearfix"]/span/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://www.szyangxiao.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, fiction_name=fiction_name, classification=classification, index=index, status='',:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, ):
        chapter_name = response.xpath('''//div[@class="title"]/text()''').extract_first()
        chapter_update_time = response.xpath('''/html/body/div[5]/text()[2]''').extract_first().replace("更新：", '').strip()
        chapter_con = response.xpath('''//div[@id="content"]/p/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Tqshuyuan(scrapy.Spider):
    source = "天晴书院"
    name = 'tqshuyuan'
    allowed_domains = ['tqshuyuan.com']
    start_urls = [
        "http://m.tqshuyuan.com/8_8695/"
    ]

    def parse(self, response, ):
        fiction_img = "http://m.tqshuyuan.com" + re.findall('''this\.src=\'(.*?)\'''', response.xpath('''//div[@class="synopsisArea_detail"]/img/@onerror''').extract_first())[0]
        fiction_name = response.xpath('''//span[@class="title"]/text()''').extract_first().strip()
        author = response.xpath('''//p[@class="author"]/text()''').extract_first().replace("作者：", '').strip()
        classification = response.xpath('''//p[@class="sort"]/text()''').extract_first().replace("类别：", '').strip()
        status = response.xpath('''/html/body/div[2]/div/p[2]/text()''').extract_first().replace("状态：", '').strip()
        aid = response.url.split("/")[-2].split("_")[-1]
        ret = requests.get(url="http://m.tqshuyuan.com/ajax.php?ac=allvisit&aid={}".format(aid))
        viewing_count = re.findall('''document.write\(\"(\d+)\"\)''', ret.text)[0]
        fiction_update_time = response.xpath('''/html/body/div[2]/div/p[4]/text()''').extract_first().replace("更新：", '').strip()
        url = "http://m.tqshuyuan.com" + response.xpath('''//p[@class="btn"]/a/@href''').extract_first()
        # print(fiction_img, fiction_name, author, classification, status, viewing_count, fiction_update_time, url)
        yield Request(url, callback=lambda response, fiction_img=fiction_img, fiction_name=fiction_name, author=author, classification=classification, status=status, viewing_count=viewing_count,
                                           fiction_update_time=fiction_update_time:
        self.get_fiction_info(response, fiction_img, fiction_name, author, classification, status, viewing_count, fiction_update_time), dont_filter=True)

    def get_fiction_info(self, response, fiction_img, fiction_name, author, classification, status, viewing_count, fiction_update_time):
        li = response.xpath('''//div[@id="chapterlist"]/p/a''')
        index = 0
        for i in li:
            url = "http://m.tqshuyuan.com" + i.xpath('''.//@href''').extract_first()
            chapter_name = i.xpath('''.//text()''').extract_first()
            index += 1
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, fiction_name=fiction_name, classification=classification, index=index, status=status,
                                          viewing_count=viewing_count, chapter_name=chapter_name:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count, chapter_name),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count, chapter_name):
        chapter_con = response.xpath('''//div[@id="chaptercontent"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Plxsw(scrapy.Spider):
    source = "盘龙小说网"
    name = 'plxsw'
    allowed_domains = ['plxsw.com']
    start_urls = [
        "http://www.plxsw.com/27650/"
    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@id="info"]/h1/text()''').extract_first()
        author = response.xpath('''//div[@id="info"]/p/text()''').extract_first().replace("\xa0", '').replace("作者：", '')
        status = response.xpath('''//*[@id="info"]/p[2]/text()[1]''').extract_first().replace("\xa0", '').replace("状态：", '')
        fiction_update_time = response.xpath('''//*[@id="info"]/p[3]/text()''').extract_first().replace("最后更新：", '')
        fiction_img = response.xpath('''//div[@id="fmimg"]/img/@src''').extract_first()
        classification = response.xpath('''//*[@id="wrapper"]/div[5]/div[1]/a[2]/text()''').extract_first()
        # print(fiction_name, author, status, fiction_update_time, fiction_img, classification)
        li = response.xpath('''//div[@id="list"]/dl/dd/li/a''')
        index = 0
        for i in li:
            index += 1
            chapter_name = i.xpath('''.//text()''').extract_first()
            url = i.xpath('''.//@href''').extract_first()
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, fiction_name=fiction_name, classification=classification, index=index, status=status,
                                          viewing_count='', chapter_name=chapter_name:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count, chapter_name),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification, viewing_count, chapter_name):
        chapter_con = response.xpath('''//div[@id="content"]/text()''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Nongcunxsw(scrapy.Spider):
    source = "农村小说网"
    name = 'nongcunxsw'
    allowed_domains = ['nongcunxsw.com']
    start_urls = [
        "http://www.nongcunxsw.com/"
    ]

    def parse(self, response, ):
        li = response.xpath('''//a/@href''').extract()
        for i in li:
            url = i
            yield Request(url, callback=lambda response,:
            self.get_fiction_info(response, ), dont_filter=True)

    def get_fiction_info(self, response, ):
        fiction_name = response.xpath('''//div[@class="book-describe"]/h1/text()''').extract_first()
        fiction_img = response.xpath('''//div[@class="book-img"]/img/@src''').extract_first()
        author = response.xpath('''//div[@class="book-describe"]/p/text()''').extract_first().replace("作者：", '')
        status = response.xpath('''//div[@class="book-describe"]/p[2]/text()''').extract_first().replace("状态：", '')
        fiction_update_time = response.xpath('''//div[@class="book-describe"]/p[3]/text()''').extract_first().replace("最近更新：", '')
        li = response.xpath('''//div[@class="book-list f-cb"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = i
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, fiction_name=fiction_name, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, ):
        chapter_name = response.xpath('''//div[@class="m-article-title"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="m-article-text"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        classification = "农村言情小说"
        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class vodtw(scrapy.Spider):
    source = "品书网"
    name = 'vodtw'
    allowed_domains = ['vodtw.com']
    start_urls = [
        "https://www.vodtw.com/html/book/48/48204/"
    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        classification = response.xpath('''/html/body/div[6]/div/a[2]/text()''').extract_first()
        fiction_img = response.xpath('''//div[@class="bookpic"]/img/@src''').extract_first()
        author = response.xpath('''//ul[@class="bookdata clearfix"]/li/h2/text()''').extract_first().replace("作    者：", '').replace("作者：", '')
        status = response.xpath('''//ul[@class="bookdata clearfix"]/li[2]/text()''').extract_first().replace("状    态：", '').replace("状态：", '')
        fiction_update_time = response.xpath('''//ul[@class="bookdata clearfix"]/li[4]/text()''').extract_first().replace("更新时间：", '')
        # print(fiction_name, fiction_img, author, status, fiction_update_time, classification)
        li = response.xpath('''//div[@class="insert_list"]/dl/dd/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = response.url + i
            # print(url)
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, classification=classification, fiction_name=fiction_name, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification):
        chapter_name = response.xpath('''//span[@id="htmltimu"]/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@id="BookText"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Jiu0xss(scrapy.Spider):
    source = "九零小说网"
    name = '90xss'
    allowed_domains = ['90xss.com']
    start_urls = [
        "http://www.90xss.com/chuanyuezhiwanqitianxia/"
    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@id="info"]/h1/text()''').extract_first()
        classification = response.xpath('''/html/body/div[6]/div[1]/a[2]/text()''').extract_first()
        fiction_img = "http://www.90xss.com" + response.xpath('''//div[@id="fmimg"]/a/img/@src''').extract_first()
        author = response.xpath('''//*[@id="info"]/p[1]/a/text()''').extract_first()
        status = '连载'
        fiction_update_time = response.xpath('''//*[@id="info"]/p[3]/text()''').extract_first().replace("最后更新：", '')
        # print(fiction_name, fiction_img, author, status, fiction_update_time, classification)
        li = response.xpath('''//div[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = "http://www.90xss.com" + i
            # print(url)
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, classification=classification, fiction_name=fiction_name, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification):
        chapter_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Biqudu(scrapy.Spider):
    source = "笔趣读"
    name = 'biqudu'
    allowed_domains = ['biqudu.tv']
    start_urls = [
        "https://www.biqudu.tv/3_3475/"
    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@id="info"]/h1/text()''').extract_first()
        classification = response.xpath('''//div[@class="con_top"]/a[2]/text()''').extract_first()
        fiction_img = "https://www.biqudu.tv" + response.xpath('''//div[@id="fmimg"]/img/@src''').extract_first()
        author = response.xpath('''//*[@id="info"]/p[1]/text()''').extract_first().replace("\xa0", '').replace("作者：", '')
        status = '连载'
        fiction_update_time = response.xpath('''//*[@id="info"]/p[3]/text()''').extract_first().replace("最后更新：", '')

        print(fiction_name, classification, fiction_img, author, fiction_update_time)
        li = response.xpath('''//div[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = "https://www.biqudu.tv" + i
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, classification=classification, fiction_name=fiction_name, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification):
        chapter_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Sibqg(scrapy.Spider):
    source = "笔趣阁"
    name = '4bqg'
    allowed_domains = ['4bqg.com']
    start_urls = [
        "http://www.4bqg.com/4bqg/23_23211/"
    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@id="info"]/h1/text()''').extract_first()
        classification = response.xpath('''//div[@class="con_top"]/a[2]/text()''').extract_first()
        fiction_img = response.xpath('''//div[@id="bdshare"]/img/@src''').extract_first()
        author = response.xpath('''//*[@id="info"]/p/text()''').extract_first().replace("\xa0", '').replace("作者：", '')
        status = '连载'
        fiction_update_time = response.xpath('''//*[@id="info"]/p[3]/text()''').extract_first().replace("最后更新：", '')
        print(fiction_name, classification, fiction_img, author, fiction_update_time)
        li = response.xpath('''//div[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = response.url + i
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, classification=classification, fiction_name=fiction_name, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification):
        chapter_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Qianqianxs(scrapy.Spider):
    source = "千千小说"
    name = 'qianqianxs'
    allowed_domains = ['qianqianxs.com']
    start_urls = [
        # "http://www.qianqianxs.com/18/18729/",
        # "http://www.qianqianxs.com/62/62941/",
        "http://www.qianqianxs.com/11/11453/",
        "http://www.qianqianxs.com/6/6525/",
        "http://www.qianqianxs.com/8/8205/",
    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@class="info2"]/h1/text()''').extract_first()
        classification = response.xpath('''//div[@class="panel-body text-center info3"]/p/text()''').extract_first().split('/')[0].replace("小说类别：", '')
        fiction_img = "http://www.qianqianxs.com" + response.xpath('''//div[@class="info1"]/img/@src''').extract_first()
        author = response.xpath('''//h3[@class="text-center"]/a/text()''').extract_first()
        status = response.xpath('''//div[@class="panel-body text-center info3"]/p/text()''').extract_first().split('/')[1].replace("写作状态：", '')
        fiction_update_time = response.xpath('''//div[@class="panel-body text-center info3"]/p/font/text()''').extract_first()
        print(fiction_name, classification, fiction_img, author, fiction_update_time, status)
        li = response.xpath('''//ul[@class="list-group list-charts"]/li/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = "http://www.qianqianxs.com" + i
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, classification=classification, fiction_name=fiction_name, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification):
        chapter_name = response.xpath('''//div[@class="panel-heading"]/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="panel-body content-body content-ext"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Biqudan(scrapy.Spider):
    source = "笔趣蛋"
    name = 'biqudan'
    allowed_domains = ['biqudan.com']
    start_urls = [
        "http://www.biqudan.com/txt/3/",
        "http://www.biqudan.com/txt/32371/",
    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@id="info"]/h1/text()''').extract_first()
        classification = response.xpath('''//div[@class="con_top"]/a[2]/text()''').extract_first()
        fiction_img = "http://www.biqudan.com" + response.xpath('''//div[@id="fmimg"]/img/@src''').extract_first()
        author = response.xpath('''//*[@id="info"]/p[1]/text()''').extract_first().replace("\xa0", '').replace("作者：", '')
        status = '连载'
        fiction_update_time = response.xpath('''//*[@id="info"]/p[3]/text()''').extract_first().replace("最后更新：", '')

        print(fiction_name, classification, fiction_img, author, fiction_update_time)
        li = response.xpath('''//div[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = response.url + i
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, classification=classification, fiction_name=fiction_name, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification):
        chapter_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Er3wxw(scrapy.Spider):
    source = "顶点小说网"
    name = '23wxw'
    allowed_domains = ['23wxw.cc']
    start_urls = [
        "https://www.23wxw.cc/html/52367/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@id="info"]/h1/text()''').extract_first()
        classification = '顶点小说网'
        fiction_img = "https://www.23wxw.cc" + response.xpath('''//div[@id="fmimg"]/img/@src''').extract_first()
        author = response.xpath('''//*[@id="info"]/p[1]/text()''').extract_first().replace("\xa0", '').replace("作者：", '')
        status = '连载'
        fiction_update_time = response.xpath('''//*[@id="info"]/p[3]/text()''').extract_first().replace("最后更新：", '')

        print(fiction_name, classification, fiction_img, author, fiction_update_time)
        li = response.xpath('''//div[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = "https://www.23wxw.cc" + i
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, classification=classification, fiction_name=fiction_name, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification):
        chapter_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Yangguiweihuo(scrapy.Spider):
    source = "养鬼为祸"
    name = 'yangguiweihuo'
    allowed_domains = ['yangguiweihuo.com']
    start_urls = [
        "https://www.yangguiweihuo.com/9/9682/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@class="info"]/h2/text()''').extract_first()
        classification = response.xpath('''//div[@class="small"]/span[2]/text()''').extract_first().replace("分类：", '')
        fiction_img = "https://www.yangguiweihuo.com" + response.xpath('''//div[@class="cover"]/img/@src''').extract_first()
        author = response.xpath('''//div[@class="small"]/span[1]/text()''').extract_first().replace("\xa0", '').replace("作者：", '')
        status = response.xpath('''//div[@class="small"]/span[3]/text()''').extract_first().replace("状态：", '')
        fiction_update_time = response.xpath('''//div[@class="small"]/span[5]/text()''').extract_first().replace("更新时间：", '')

        print(fiction_name, classification, fiction_img, author, fiction_update_time)
        li = response.xpath('''//div[@class="listmain"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = "https://www.yangguiweihuo.com" + i
            yield Request(url,
                          callback=lambda response, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, classification=classification, fiction_name=fiction_name, index=index, status=status,:
                          self.get_chapter_content(response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, author, fiction_name, fiction_img, index, fiction_update_time, status, classification):
        chapter_name = response.xpath('''//div[@class="content"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Baoliny(scrapy.Spider):
    source = "风云小说"
    name = 'baoliny'
    allowed_domains = ['baoliny.com']
    start_urls = [
        "http://www.baoliny.com/117899/index.html?qqdrsign=0286c",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//h1/text()''').extract_first().replace("\xa0", "")
        li = response.xpath('''/html/body/div[2]/div[4]/table/tr/td/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index,:
                          self.get_chapter_content(response, index, fiction_name),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name):
        classification = response.xpath('''//*[@id="yueduye"]/text()''').extract_first().split("\xa0")[0].replace("类别：", "")
        author = response.xpath('''//*[@id="yueduye"]/a[1]/text()''').extract_first()
        chapter_name = response.xpath('''//*[@id="h1"]/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        fiction_img = ''
        viewing_count = ''
        fiction_update_time = ''
        status = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Feiyanqing(scrapy.Spider):
    source = "飞言情"
    name = 'feiyanqing'
    allowed_domains = ['feiyanqing.com']
    start_urls = [
        "https://www.feiyanqing.com/danmei/22176/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//h1[@class="sjbt"]/text()''').extract_first()
        fiction_img = "https://www.feiyanqing.com" + response.xpath('''//div[@id="intro"]/img/@src''').extract_first()
        classification = response.xpath('''//div[@class="weizhi"]/a[2]/text()''').extract_first()
        print(fiction_name, fiction_img, classification)
        li = response.xpath('''//div[@id="list"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://www.feiyanqing.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, fiction_img=fiction_img, classification=classification:
                          self.get_chapter_content(response, index, fiction_name, fiction_img, classification),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, fiction_img, classification):
        author = response.xpath('''//div[@class="wzxx"]/a[2]/text()''').extract_first()
        chapter_name = response.xpath('''//h1[@class="wzbt"]/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="zw"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        fiction_update_time = ''
        status = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Luoxia(scrapy.Spider):
    source = "落霞小说网"
    name = 'luoxia'
    allowed_domains = ['luoxia.com']
    start_urls = [
        "http://www.luoxia.com/meizhewujiang/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@class="book-describe"]/h1/text()''').extract_first()
        author = response.xpath('''//div[@class="book-describe"]/p[1]/text()''').extract_first().replace("作者：", "")
        classification = response.xpath('''//div[@class="book-describe"]/p[2]/text()''').extract_first().replace("类型：", "")
        status = response.xpath('''//div[@class="book-describe"]/p[3]/text()''').extract_first().replace("状态：", "")
        fiction_update_time = response.xpath('''//div[@class="book-describe"]/p[4]/text()''').extract_first().replace("最近更新：", "")
        fiction_img = response.xpath('''//div[@class="book-img"]/img/@src''').extract_first()
        print(fiction_img, fiction_name, author, status, fiction_update_time, classification)

        li = response.xpath('''//div[@class="book-list clearfix"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, fiction_img=fiction_img, classification=classification, fiction_update_time=fiction_update_time,
                                          author=author, status=status:
                          self.get_chapter_content(response, index, fiction_name, fiction_img, classification, author, status, fiction_update_time),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, fiction_img, classification, author, status, fiction_update_time):

        chapter_name = response.xpath('''//h1[@id="nr_title"]/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@id="nr1"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Xiangcunxs2(scrapy.Spider):
    source = "乡村小说网"
    name = 'xiangcunxs2'
    allowed_domains = ['xiangcunxs2.com']
    start_urls = [
        "http://xiangcunxs2.com/shaofubaijie/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//p[@class="lead hidden-phone"]/a/@title''').extract_first()
        fiction_img = 'http://xiangcunxs2.com' + response.xpath('''//p[@class="lead hidden-phone"]/a/img/@src''').extract_first()
        author = response.xpath('''//p[@class="lead hidden-phone"]/strong[2]/text()''').extract_first().replace("作者:", '')
        print(fiction_name, author, fiction_img)

        li = response.xpath('''//div[@class="span4 item"]/a/@href''').extract()
        index = 0
        for i in li:
            url = 'http://xiangcunxs2.com' + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, fiction_img=fiction_img, classification='乡村小说', author=author,:
                          self.get_chapter_content(response, index, fiction_name, fiction_img, classification, author, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, fiction_img, classification, author, ):

        chapter_name = response.xpath('''//h2[@class="text-center red"]/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        fiction_update_time = ''
        status = ''
        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Yubook(scrapy.Spider):
    source = "御宅屋"
    name = 'yubook'
    allowed_domains = ['yubook.com']
    start_urls = [
        # "https://www.yubook.net/read/30578/",
        "https://www.yubook.net/read/30559/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@class="infotitle"]/h1/text()''').extract_first()
        author = response.xpath('''//div[@class="infotitle"]/span/a/text()''').extract_first()
        fiction_update_time = response.xpath('''//div[@class="infotitle"]/span/span/time/text()''').extract_first()
        classification = response.xpath('''//*[@id="srcbox"]/a[2]/text()''').extract_first()
        print(fiction_name, author, fiction_update_time)
        li = response.xpath('''//*[@id="box"]/div/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = 'https://www.yubook.net' + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_update_time=fiction_update_time:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time):

        chapter_name = response.xpath('''///*[@id="main"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="_chapter"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        fiction_img = ''
        viewing_count = ''
        status = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Bl5xs(scrapy.Spider):
    source = "BL小说网"
    name = 'bl5xs'
    allowed_domains = ['bl5xs.net']
    start_urls = [
        "http://www.bl5xs.net/read/28052/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//*[@id="info"]/h1/text()''').extract_first()
        author = response.xpath('''//*[@id="info"]/p[1]/text()''').extract_first().replace("作者：", '')
        status = response.xpath('''//*[@id="info"]/p[2]/text()''').extract_first().replace("状态：", '')
        classification = response.xpath('''//*[@id="info"]/p[3]/text()''').extract_first().replace("类型：", '')
        fiction_update_time = response.xpath('''//*[@id="info"]/p[5]/text()''').extract_first().replace("最后更新：", '')
        fiction_img = response.xpath('''//*[@id="fmimg"]/img/@src''').extract_first()
        print(fiction_name, author, status, classification, fiction_update_time, fiction_img)
        li = response.xpath('''//*[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = 'http://www.bl5xs.net' + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time, status=status:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img):

        chapter_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        viewing_count = ''
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Bamxs(scrapy.Spider):
    source = "8mxs"
    name = '8mxs'
    allowed_domains = ['8mxs.cc']
    start_urls = [
        # "http://www.8mxs.cc/read.asp?id=14300",
        "http://www.8mxs.cc/read.asp?id=12341",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''/html/body/table[3]/tr[2]/td/strong/text()''').extract_first()
        fiction_img = "http://www.8mxs.cc" + str(response.xpath('''/html/body/table[3]/tr[5]/td[1]/img/@src''').extract_first())
        classification = response.xpath('''/html/body/table[3]/tr[3]/td[1]/a/text()''').extract_first()
        author = response.xpath('''/html/body/table[3]/tr[3]/td[2]/a/text()''').extract_first()
        status = response.xpath('''/html/body/table[3]/tr[3]/td[3]/a/text()''').extract_first()
        viewing_count = response.xpath('''/html/body/table[3]/tr[3]/td[5]/text()''').extract_first().replace("\xa0", "").replace("浏览:", "")
        fiction_update_time = response.xpath('''/html/body/table[3]/tr[3]/td[6]/text()''').extract_first().replace("\xa0", "").replace("更新:", "")
        print(fiction_name, fiction_img, classification, author, status, viewing_count, fiction_update_time)
        li = response.xpath('''/html/body/table[4]/tr/td/div/a/@href''').extract()
        for i in li:
            url = i
            index = i.split("=")[-1]
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''/html/body/table[3]/tr[2]/td/font/strong/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@class="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Mozhua(scrapy.Spider):
    source = "爪资源"
    name = 'mozhua'
    allowed_domains = ['mozhua.net']
    start_urls = [
        "http://www.mozhua.net/forum.php?mod=viewthread&tid=252491",

    ]

    def parse(self, response, ):
        classification = response.xpath('''//h1[@class="ts"]/a/text()''').extract_first()
        fiction_name = response.xpath('''//*[@id="thread_subject"]/text()''').extract_first()
        author = response.xpath('''//*[@id="thread_subject"]/text()''').extract_first()
        status = response.xpath('''//*[@id="thread_subject"]/text()''').extract_first()
        fiction_img = response.xpath('''//*[@id="favatar3678272"]/div[3]/div/a/img/@src''').extract_first()
        fiction_update_time = response.xpath('''//*[@id="authorposton3678272"]/text()''').extract_first().replace("发表于", '')
        print(classification, fiction_name, author, status, fiction_update_time, fiction_img)
        li = response.xpath('''//*[@id="pid3678272"]/tr[1]/td[2]/div[2]/div/table/tr/td/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status,:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, ):
        driver = webdriver.Chrome()
        driver.get(response.url)
        try:
            chapter_name = driver.find_element_by_xpath('''//h1[@class="flb hm txt_title"]''').text
            chapter_con = driver.find_element_by_xpath('''//div[@id="txt_content"]''').text
            driver.close()
            chapter_content = ''
            for i in chapter_con:
                chapter_content += i.replace("\xa0", "&nbsp;")
            if len(chapter_content.strip()) == 0:
                is_vip = True
            else:
                is_vip = False

            viewing_count = ''
            chapter_update_time = fiction_update_time
            ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)
        finally:
            driver.close()


class Yushuwu(scrapy.Spider):
    source = "御宅屋"
    name = 'yushuwu'
    allowed_domains = ['yushuwu.com']
    start_urls = [
        # "https://m.yushuwu.com/novel/31215.html",
        "https://m.yushuwu.com/novel/21183.html",

    ]

    def parse(self, response, ):
        classification = response.xpath('''//*[@id="nr_body"]/nav/ul/li[1]/a/text()''').extract_first()
        fiction_name = response.xpath('''//*[@id="nr_body"]/nav/ul/li[2]/text()''').extract_first()
        author = response.xpath('''//*[@id="novelMain"]/div[1]/table/tr/td[1]/div[1]/h2/text()''').extract_first()
        fiction_update_time = response.xpath('''//*[@id="novelMain"]/div[1]/table/tr/td[1]/div[4]/time/text()''').extract_first()
        print(classification, fiction_name, author, fiction_update_time, )
        li = response.xpath('''//div[@class="lb_mulu chapterList"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img='',
                                          fiction_update_time=fiction_update_time, status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''//*[@id="nr_title"]/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="nr1"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Tiefu(scrapy.Spider):
    source = "贴夫网"
    name = '8tiefu'
    allowed_domains = ['8tiefu.com']
    start_urls = [
        "https://www.8tiefu.com/1/",
        "https://www.8tiefu.com/5/",
    ]

    def parse(self, response, ):
        li = response.xpath('''//div[@class="col xs-4 text-right"]/a/@href''').extract()
        for i in li:
            url = "https://www.8tiefu.com" + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        classification = response.xpath('''//div[@class="nav-body"]/a[2]/text()''').extract_first()
        fiction_name = response.xpath('''//h1[@class="book-title"]/text()''').extract_first()
        author = response.xpath('''//a[@class="book-author"]/text()''').extract_first()
        status = response.xpath('''//div[@class="row text-center"]/text()''').extract_first().split()[2]
        viewing_count = response.xpath('''//div[@class="row text-center"]/text()''').extract_first().split()[-1]
        print(classification, fiction_name, author, status, viewing_count)
        li = response.xpath('''//div[@class="row text-hide"]/a/@href''').extract()
        for i in li:
            url = "https://www.8tiefu.com" + i
            index = i.split("/")[-1].split('.')[0]
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img='https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg',
                                          fiction_update_time='', status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        driver = webdriver.Chrome()
        driver.get(response.url)

        chapter_name = driver.find_element_by_xpath('''//div[@class="box-border"]/h1''').text
        chapter_con = driver.find_element_by_xpath('''//*[@id="chapter-content"]''').text
        driver.close()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;").replace("。", "。<br>")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Ifuwen(scrapy.Spider):
    source = "腐国度"
    name = 'ifuwen'
    allowed_domains = ['ifuwen.com']
    start_urls = [
        # "https://www.ifuwen.com/read/1736/",
        "https://www.ifuwen.com/read/30360/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@class="infotitle"]/h1/text()''').extract_first()
        fiction_img = response.xpath('''//div[@class="img_in"]/img/@src''').extract_first()
        author = response.xpath('''//div[@class="infotitle"]/span/a/text()''').extract_first()
        fiction_update_time_url = "https://www.ifuwen.com" + response.xpath('''//*[@id="info"]/div[1]/span/span/script/@src''').extract_first()
        ret = requests.get(url=fiction_update_time_url)
        fiction_update_time = re.findall('''document.write\("(.*?)"\)''', ret.text)[0]
        print(fiction_name, author, fiction_update_time, fiction_img)
        li = response.xpath('''//*[@id="box"]/div/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://www.ifuwen.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification='', author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        classification = response.xpath('''//*[@id="srcbox"]/a[2]/text()''').extract_first()
        chapter_name = response.xpath('''//*[@id="main"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Dzxs(scrapy.Spider):
    source = "大众小说网"
    name = 'dzxs'
    allowed_domains = ['dzxs.cc']
    start_urls = [
        "http://www.dzxs.cc/read/3639.html",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//div[@class="book-title"]/h1/text()''').extract_first()
        classification = response.xpath('''//div[@class="fl"]/a[2]/text()''').extract_first()
        fiction_img = "http://www.dzxs.cc" + response.xpath('''//*[@id="content1"]/div[1]/div/div[1]/img/@src''').extract_first()
        author = response.xpath('''//div[@class="book-title"]/p/text()''').extract_first().replace("\xa0", '').replace("作者：", '')
        print(fiction_name, classification, fiction_img, author)
        li = response.xpath('''//dl[@class="chapterlist"]/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.dzxs.cc" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time='', status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''//*[@id="BookCon"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="BookText"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Shubao888(scrapy.Spider):
    source = "第二书包网"
    name = 'shubao888'
    allowed_domains = ['shubao888.com']
    start_urls = [
        "https://www.shubao888.com/book/1/1159/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''//*[@id="info"]/h1/text()''').extract_first()
        fiction_img = 'https://www.shubao888.com' + response.xpath('''//*[@id="fmimg"]/img/@onerror''').extract_first().replace("src=", '').replace("'", '')
        classification = response.xpath('''//*[@id="wrapper"]/div[2]/div[4]/div[1]/a[2]/text()''').extract_first()
        author = response.xpath('''//*[@id="info"]/p[1]/text()''').extract_first().replace("\xa0", '').replace("作者：", '')
        print(fiction_name, fiction_img, classification, author)
        li = response.xpath('''//*[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time='', status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Novel101(scrapy.Spider):
    source = "101 小说典藏网"
    name = 'novel101'
    allowed_domains = ['novel101.com']
    start_urls = [
        "https://novel101.com/novels/4e5f4de2-6c63-423e-9135-058bbe5f1654",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="col-md-12"]/h1)''').extract_first()
        author = response.xpath('''string(//div[@class="col-md-12"]/div)''').extract_first().replace("作者：", '')

        print(fiction_name, author)
        li = response.xpath('''//li[@class="list-group-item"]/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://novel101.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification='', author=author, fiction_img='',
                                          fiction_update_time='', status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''string(//h2)''').extract_first().replace("\xa0", "")
        chapter_con = response.xpath('''string(//div[@class="body"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Jingxuanxiaoshuo(scrapy.Spider):
    source = "精选小说网"
    name = 'jingxuanxiaoshuo'
    allowed_domains = ['jingxuanxiaoshuo.com']
    start_urls = [
        "http://www.jingxuanxiaoshuo.com/read/7153.html",
        "http://www.jingxuanxiaoshuo.com/read/7131.html",
    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="info2"]/h1)''').extract_first()
        fiction_img = 'http://www.jingxuanxiaoshuo.com' + response.xpath('''//div[@class="info1"]/img/@src''').extract_first()
        author = response.xpath('''string(//h3[@class="text-center"]/a)''').extract_first()
        classification = response.xpath('''string(//div[@class="panel-body text-center info3"]/p)''').extract_first().split("/")[0].replace("小说类别：", '')
        status = response.xpath('''string(//div[@class="panel-body text-center info3"]/p)''').extract_first().split("/")[1].replace("写作状态：", '')
        fiction_update_time = response.xpath('''string(/html/body/div[2]/div[1]/div[1]/div/div[3]/p[2]/font)''').extract_first()
        print(fiction_name, author, classification, status, fiction_update_time, fiction_img, )
        li = response.xpath('''//li[@class="chapter"]/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''string(//div[@class="panel-heading"])''').extract_first().replace("\xa0", "")
        chapter_con = response.xpath('''string(//div[@class="panel-body content-body content-ext"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Piaotian(scrapy.Spider):
    source = "飘天文学"
    name = 'piaotian'
    allowed_domains = ['piaotian.cc']
    start_urls = [
        "https://tw.piaotian.cc/read/102073/index.html",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//h1[@class="novel_name"])''').extract_first()
        author = response.xpath('''string(//*[@id="wp"]/div/div[2]/p/a)''').extract_first()
        classification = response.xpath('''string(//*[@id="wp"]/div/div[1]/h2/a[3])''').extract_first()
        print(fiction_name, author, classification)
        li = response.xpath('''//div[@class="novel_list"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "https://tw.piaotian.cc" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img='',
                                          fiction_update_time='', status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''string(//h1[@class="novel_title"])''').extract_first().replace("\xa0", "")
        chapter_con = response.xpath('''string(//div[@class="novel_content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Xbiquge(scrapy.Spider):
    source = "笔趣阁"
    name = 'xbiquge'
    allowed_domains = ['xbiquge.cc']
    start_urls = [
        "http://www.xbiquge.cc/book/18646/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//*[@id="info"]/h1)''').extract_first()
        author = response.xpath('''string(//*[@id="info"]/p[1]/a)''').extract_first()
        fiction_update_time = response.xpath('''string(//*[@id="info"]/p[3])''').extract_first().replace("\xa0", "").replace("更新时间：", "").split("[")[0]
        fiction_img = response.xpath('''//*[@id="fmimg"]/img/@src''').extract_first()
        classification = response.xpath('''string(//div[@class="con_top"])''').extract_first().split(">")[-2].strip()

        print(fiction_name, author, fiction_update_time, fiction_img, classification)
        li = response.xpath('''//*[@id="list"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = response.url + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''//div[@class="bookname"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Mlxiaoshuo(scrapy.Spider):
    source = "魔龙小说网"
    name = 'mlxiaoshuo'
    allowed_domains = ['mlxiaoshuo.com']
    start_urls = [
        "http://www.mlxiaoshuo.com/book/1eed88ea9f0d209a22ac81416c6541f1.html",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="autoCenter contentDiv colorStyleBg changeStyle2"]/div[@class="colorStyleTitle"])''').extract_first()
        author = response.xpath('''string(//a[@class="colorStyleLink"])''').extract_first()
        fiction_img = response.xpath('''//a[@class="textImage"]/img/@src''').extract_first()
        classification = response.xpath('''string(//div[@class="autoCenter navSub"]/a[2])''').extract_first()
        print(fiction_name, author, fiction_img, classification)
        li = response.xpath('''//ul[@class="row zhangjieUl"]/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.mlxiaoshuo.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time='', status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''//div[@class="juanRow navText colorStyleTitle2"]/span/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="textP fontStyle2 colorStyleText"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0", "&nbsp;") + "<br>"
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Shubao4(scrapy.Spider):
    source = "第二书包网"
    name = 'shubao4'
    allowed_domains = ['shubao4.com']
    start_urls = [
        "http://www.shubao4.com/read/431.html",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="book-title"]/h1)''').extract_first()
        author = response.xpath('''string(//div[@class="book-title"]/p)''').extract_first().replace("\xa0", "").replace("作者：", "")
        fiction_img = 'http://www.shubao4.com' + re.findall('''this.onerror=null;this.src=\'(.*?)\'''', response.xpath('''//div[@class="book-img"]/img/@onerror''').extract_first())[0]
        classification = response.xpath('''string(//div[@class="fl"]/a[2])''').extract_first()
        print(fiction_name, author, fiction_img, classification)
        li = response.xpath('''//*[@id="main"]/div/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = 'http://www.shubao4.com' + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time='', status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''//*[@id="BookCon"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="BookText"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0\xa0\xa0\xa0", "。<br>&nbsp;&nbsp;&nbsp;&nbsp;")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Yqxs123(scrapy.Spider):
    source = "言情小说网"
    name = 'yqxs123'
    allowed_domains = ['yqxs123.com']
    start_urls = [
        "http://www.yqxs123.com/c12/rwlw_182/1154595.html",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="title"]/h1)''').extract_first()
        author = response.xpath('''string(/html/body/section[1]/div[3]/div[2]/p[1]/a)''').extract_first()
        fiction_img = response.xpath('''/html/body/section[1]/div[3]/div[1]/img/@src''').extract_first()
        classification = response.xpath('''string(/html/body/section[1]/div[1]/a[2])''').extract_first()
        print(fiction_name, author, fiction_img, classification)
        li = response.xpath('''//section[@class="ml_main"]/dl/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time='', status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''//div[@class="ydleft"]/h2/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="yd_text2"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Liu5txt(scrapy.Spider):
    source = "65TXT小说下载网"
    name = '65txt'
    allowed_domains = ['65txt.com']
    start_urls = [
        "http://www.65txt.com/read/23/23422/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="mu_h1"]/h1)''').extract_first()
        author = response.xpath('''string(//div[@class="mu_beizhu"]/a)''').extract_first()
        fiction_img = ''
        classification = response.xpath('''string(//div[@class="location container"]/a[2])''').extract_first()
        fiction_update_time = response.xpath('''//div[@class="mu_beizhu"]/text()[3]''').extract_first().replace("\xa0", "").replace("更新时间：", "")
        print(fiction_name, author, classification, fiction_update_time)
        li = response.xpath('''//*[@id="list"]/ul/li/a/@href''').extract()

        for i in li:
            index = re.findall('''(\d+)\.html''', i)[0]
            url = response.url + index + '.html'
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):

        chapter_name = response.xpath('''//div[@class="style"]/h1/text()''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="yd_text2"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("\xa0\xa0\xa0\xa0", "<br>\n    ")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Er5645(scrapy.Spider):
    source = "156文学"
    name = '25645'
    allowed_domains = ['25645.com']
    start_urls = [
        "https://www.25645.com/read/5266/index.html",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//h1[@class="article-title"])''').extract_first()
        author = response.xpath('''string(//span[@class="muted"]/a)''').extract_first()
        fiction_img = ''
        classification = response.xpath('''string(//div[@class="breadcrumbs"]/a[2])''').extract_first()
        fiction_update_time = response.xpath('''string(//div[@class="meta meta_mulu"]/time)''').extract_first().replace("更新时间：", "")
        status = response.xpath('''string(//div[@class="meta meta_mulu"]/span[2])''').extract_first().replace("状态：", "")
        print(fiction_name, author, classification, fiction_update_time, status)
        li = response.xpath('''//*[@id="intro"]/li/a/@href''').extract()
        index = 0
        for i in li:
            url = 'https://www.25645.com' + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_update_time = response.xpath('''string(//time[@class="muted"])''').extract_first()
        chapter_name = response.xpath('''string(//h1[@class="article-title"])''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="htmlmain"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Wu21danmei(scrapy.Spider):
    source = "就要耽美网"
    name = 'm521danmei'
    allowed_domains = ['521danmei.com']
    start_urls = [
    ]
    for i in range(0, 18):
        start_urls.append("http://m.521danmei.com/tag/0/37/{}.html".format(i))

    def parse(self, response, ):
        li = response.xpath('''//*[@id="main"]/div/a/@href''').extract()
        for i in li:
            url = "http://m.521danmei.com" + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        fiction_name = response.xpath('''string(//span[@class="title"])''').extract_first().strip()
        author = response.xpath('''string(//p[@class="author"])''').extract_first().replace("作者：", "").strip()
        fiction_img = response.xpath('''//div[@class="synopsisArea_detail"]/img/@src''').extract_first().strip()
        classification = response.xpath('''string(//p[@class="sort"])''').extract_first().replace("类别：", "").strip()
        fiction_update_time = response.xpath('''string(/html/body/div[2]/div[1]/p[4])''').extract_first().replace("更新：", "").strip()
        status = response.xpath('''string(/html/body/div[2]/div[1]/p[2])''').extract_first().replace("状态：", "").strip()
        chapter_url = response.url + 'all.html'
        print(fiction_name, author, classification, fiction_update_time, status, fiction_img, chapter_url)
        yield Request(chapter_url,
                      callback=lambda response, fiction_name=fiction_name, classification=classification, author=author, fiction_img=fiction_img,
                                      fiction_update_time=fiction_update_time, status=status, viewing_count='':
                      self.get_chapter_url(response, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                      dont_filter=True
                      )

    def get_chapter_url(self, response, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        li = response.xpath('''//*[@id="chapterlist"]/p/a/@href''').extract()
        index = 0
        for i in li:
            url = 'http://m.521danmei.com' + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_update_time = fiction_update_time
        chapter_name = response.xpath('''string(//span[@class="title"])''').extract_first().replace("\xa0", "")
        chapter_con = response.xpath('''string(//*[@id="chaptercontent"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Liuyue(scrapy.Spider):
    source = "牛阅网"
    name = '6yue'
    allowed_domains = ['6yue.org']
    start_urls = [
        "https://www.6yue.org/top/1/",
    ]

    def parse(self, response, ):
        li = response.xpath('''//div[@class="col xs-4 text-right"]''')
        for i in li:
            url = i.xpath('''.//a/@href''').extract_first()
            url = 'https://www.6yue.org' + str(url)
            fiction_update_time = i.xpath('''.//span/text()''').extract_first()
            fiction_update_time = str(fiction_update_time).replace('[', '').replace(']', '')
            yield Request(url,
                          callback=lambda response, fiction_update_time=fiction_update_time:
                          self.get_fiction_info(response, fiction_update_time),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, fiction_update_time):
        fiction_name = response.xpath('''string(//h1[@class="book-title"])''').extract_first().strip()
        author = response.xpath('''string(//a[@class="book-author"])''').extract_first().strip()
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
        classification = '耽美肉文'
        status = response.xpath('''string(//div[@class="row text-center"])''').extract_first().split('/')[0]
        print(fiction_name, author, classification, fiction_img, status, fiction_update_time)
        li = response.xpath('''//div[@class="row text-hide"]/a/@href''').extract()
        for i in li:
            url = 'https://www.6yue.org' + i
            index = i.split('/')[-1].split('.')[0]
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_update_time = fiction_update_time

        driver = webdriver.Chrome()
        driver.get(response.url)
        try:
            chapter_name = driver.find_element_by_xpath('''//div[@class="box-border"]/h1''').text
            chapter_con = driver.find_element_by_xpath('''//div[@id="chapter-content"]''').text
            driver.close()
            chapter_content = ''
            for i in chapter_con:
                chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
            if len(chapter_content.strip()) == 0:
                is_vip = True
            else:
                is_vip = False

            ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)
        finally:
            driver.close()


class Yi1111s(scrapy.Spider):
    source = "五一小说网"
    name = '11111s'
    allowed_domains = ['11111s.net']
    start_urls = [
        "http://www.11111s.net/76/76718/",
        "http://www.11111s.net/75/75685/",
    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="infot"]/h1)''').extract_first()
        author = response.xpath('''string(//div[@class="infot"]/span)''').extract_first().replace("作者：", "")
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
        classification = response.xpath('''string(//ul[@class="bread-crumbs"]/li[2]/a)''').extract_first()
        fiction_update_time = ''
        status = ''
        print(fiction_name, author, classification, )
        li = response.xpath('''//div[@class="liebiao"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = 'http://www.11111s.net' + i
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(//div/h2)''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = ''
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Zhxs(scrapy.Spider):
    source = "纵横小说网"
    name = 'zhxs'
    allowed_domains = ['zhxs.org']
    start_urls = [
        "http://www.zhxs.org/xs/0/501/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//*[@id="a_main"]/div[2]/dl/dd[1]/h1)''').extract_first().replace("最新章节", "")
        author = response.xpath('''string(//*[@id="a_main"]/div[2]/dl/dd[2]/h3)''').extract_first().replace("作者：", "")
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
        classification = response.xpath('''string(//*[@id="a_main"]/div[2]/dl/dt/a[2])''').extract_first()
        fiction_update_time = ''
        status = ''
        viewing_count = ''
        print(fiction_name, author, classification, )
        li = response.xpath('''//*[@id="at"]/tr/td/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = response.url + i
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(//*[@id="amain"]/dl/dd[1]/h1)''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="contents"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Xinyushuwu(scrapy.Spider):
    source = "新御书屋"
    name = 'xinyushuwu'
    allowed_domains = ['xinyushuwu.com']
    start_urls = [
        "http://www.xinyushuwu.com/2/2297/",

    ]

    def parse(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="introduce"]/h1)''').extract_first()
        author = response.xpath('''string(//div[@class="introduce"]//p[@class="bq"]/span[2])''').extract_first().replace("作者：", "")
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
        classification = response.xpath('''string(//div[@class="catalog1"]/p/a[2])''').extract_first()
        fiction_update_time = response.xpath('''string(//div[@class="introduce"]//p[@class="bq"]/span[1])''').extract_first().replace("更新：", "")
        status = response.xpath('''string(//div[@class="introduce"]//p[@class="bq"]/span[3])''').extract_first().replace("状态：", "")
        viewing_count = response.xpath('''string(//div[@class="introduce"]//p[@class="bq"]/span[4])''').extract_first().replace("点击：", "")
        print(fiction_name, author, classification, fiction_update_time, status, viewing_count)
        li = response.xpath('''//div[@class="ml_list"]/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            index += 1
            url = response.url + i
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(//div[@class="nr_title"]/h3)''').extract_first()
        chapter_con = response.xpath('''string(//*[@id="articlecontent"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Qqc272(scrapy.Spider):
    source = "青青草小说"
    name = 'qqc272'
    allowed_domains = ['qqc272.com']
    start_urls = [
        "http://www.qqc272.com/meiwenxinshang/jingdianmeiwen/",
    ]

    for i in range(1, 378): start_urls.append("http://www.qqc272.com/listinfo-29-{}.html".format(i))
    for i in range(1, 71): start_urls.append("http://www.qqc272.com/listinfo-30-{}.html".format(i))
    for i in range(1, 3): start_urls.append("http://www.qqc272.com/listinfo-28-{}.html".format(i))
    for i in range(1, 4): start_urls.append("http://www.qqc272.com/zuowendaquan/qiangbaoxiaoshuo/index_{}.html".format(i))
    for i in range(1, 17): start_urls.append("http://www.qqc272.com/listinfo-18-{}.html".format(i))
    for i in range(1, 3): start_urls.append("http://www.qqc272.com/listinfo-10-{}.html".format(i))
    for i in range(1, 505): start_urls.append("http://www.qqc272.com/listinfo-16-{}.html".format(i))
    for i in range(1, 4): start_urls.append("http://www.qqc272.com/listinfo-38-{}.html".format(i))
    for i in range(1, 3): start_urls.append("http://www.qqc272.com/listinfo-14-{}.html".format(i))
    for i in range(1, 372): start_urls.append("http://www.qqc272.com/listinfo-26-{}.html".format(i))
    for i in range(1, 12): start_urls.append("http://www.qqc272.com/listinfo-32-{}.html".format(i))
    for i in range(1, 473): start_urls.append("http://www.qqc272.com/listinfo-50-{}.html".format(i))
    for i in range(1, 12): start_urls.append("http://www.qqc272.com/listinfo-77-{}.html".format(i))
    for i in range(1, 3): start_urls.append("http://www.qqc272.com/listinfo-13-{}.html".format(i))
    for i in range(1, 3): start_urls.append("http://www.qqc272.com/listinfo-67-{}.html".format(i))
    for i in range(1, 263): start_urls.append("http://www.qqc272.com/listinfo-15-{}.html".format(i))
    for i in range(1, 35): start_urls.append("http://www.qqc272.com/listinfo-17-{}.html".format(i))
    for i in range(1, 5): start_urls.append("http://www.qqc272.com/listinfo-22-{}.html".format(i))
    for i in range(1, 10): start_urls.append("http://www.qqc272.com/listinfo-23-{}.html".format(i))
    for i in range(1, 15): start_urls.append("http://www.qqc272.com/xinqingriji/jiedimeiluanlun/index_{}.html".format(i))

    def parse(self, response, ):
        li = response.xpath('''//ul/li/div/h3/a/@href''').extract()
        for i in li:
            url = i
            yield Request(url,
                          callback=lambda response,:
                          self.get_chapter_content(response, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="_title"]/h1)''').extract_first()
        author = response.xpath('''string(//div[@class="info"]/span/a)''').extract_first()
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
        classification = response.xpath('''string(//div[@class="title"]/a[2])''').extract_first()
        fiction_update_time = response.xpath('''string(///div[@class="info"]/span[3])''').extract_first().replace("时间: ", "")
        status = ''
        viewing_count = response.xpath('''string(///div[@class="info"]/span[4])''').extract_first().replace("阅读:", "").replace("次", "")
        chapter_name = fiction_name
        chapter_con = response.xpath('''string(//*[@id="zoomtext"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        index = 0
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Mayi02_long(scrapy.Spider):
    source = "蚂蚁小说"
    name = 'mayi02_long'
    allowed_domains = ['mayi02.xyz']
    start_urls = [
    ]
    for i in range(0, 2): start_urls.append("http://mayi02.xyz/longlist_89_{}.html".format(i))
    for i in range(0, 47): start_urls.append("http://mayi02.xyz/longlist_85_{}.html".format(i))
    for i in range(0, 8): start_urls.append("http://mayi02.xyz/longlist_86_{}.html".format(i))
    for i in range(0, 7): start_urls.append("http://mayi02.xyz/longlist_87_{}.html".format(i))
    for i in range(0, 16): start_urls.append("http://mayi02.xyz/longlist_88_{}.html".format(i))
    for i in range(0, 4): start_urls.append("http://mayi02.xyz/longlist_90_{}.html".format(i))

    def parse(self, response, ):
        li = response.xpath('''//div[@class="longNovelList"]/a/@href''').extract()
        for i in li:
            url = 'http://mayi02.xyz/' + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="longNoveldir"]/h1)''').extract_first()
        if "作者" in fiction_name:
            author = fiction_name.split("作者：")[-1]
        else:
            author = '未知'
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
        classification = response.xpath('''string(//div[@class="nav"]/a[2])''').extract_first()
        fiction_update_time = response.xpath('''string(//div[@class="date"])''').extract_first()
        status = ''
        viewing_count = ''
        print(fiction_name, author, classification, fiction_update_time)
        index = 0
        li = response.xpath('''//div[@class="dir"]/a/@href''').extract()
        for i in li:
            index += 1
            url = 'http://mayi02.xyz/' + i
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(//div[@class="t"])''').extract_first()
        chapter_con = response.xpath('''string(//input[@class="novelContentInput"]/@value)''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Mayi02_list(scrapy.Spider):
    source = "蚂蚁小说"
    name = 'mayi02_list'
    allowed_domains = ['mayi02.xyz']
    start_urls = [
    ]
    for i in range(0, 68): start_urls.append("http://mayi02.xyz/list_0_{}.html".format(i))
    for i in range(0, 50): start_urls.append("http://mayi02.xyz/list_6_{}.html".format(i))
    for i in range(0, 30): start_urls.append("http://mayi02.xyz/list_5_{}.html".format(i))
    for i in range(0, 13): start_urls.append("http://mayi02.xyz/list_4_{}.html".format(i))
    for i in range(0, 19): start_urls.append("http://mayi02.xyz/list_7_{}.html".format(i))
    for i in range(0, 9): start_urls.append("http://mayi02.xyz/list_8_{}.html".format(i))
    for i in range(0, 5): start_urls.append("http://mayi02.xyz/list_9_{}.html".format(i))
    for i in range(0, 21): start_urls.append("http://mayi02.xyz/list_10_{}.html".format(i))
    for i in range(0, 9): start_urls.append("http://mayi02.xyz/list_11_{}.html".format(i))
    for i in range(0, 12): start_urls.append("http://mayi02.xyz/list_12_{}.html".format(i))
    for i in range(0, 6): start_urls.append("http://mayi02.xyz/list_13_{}.html".format(i))
    for i in range(0, 7): start_urls.append("http://mayi02.xyz/list_14_{}.html".format(i))
    for i in range(0, 9): start_urls.append("http://mayi02.xyz/list_15_{}.html".format(i))
    for i in range(0, 76): start_urls.append("http://mayi02.xyz/list_16_{}.html".format(i))
    for i in range(0, 20): start_urls.append("http://mayi02.xyz/list_17_{}.html".format(i))
    for i in range(0, 9): start_urls.append("http://mayi02.xyz/list_18_{}.html".format(i))
    for i in range(0, 6): start_urls.append("http://mayi02.xyz/list_19_{}.html".format(i))
    for i in range(0, 25): start_urls.append("http://mayi02.xyz/list_20_{}.html".format(i))
    for i in range(0, 13): start_urls.append("http://mayi02.xyz/list_21_{}.html".format(i))
    for i in range(0, 26): start_urls.append("http://mayi02.xyz/list_22_{}.html".format(i))
    for i in range(0, 9): start_urls.append("http://mayi02.xyz/list_23_{}.html".format(i))
    for i in range(0, 20): start_urls.append("http://mayi02.xyz/list_24_{}.html".format(i))
    for i in range(0, 5): start_urls.append("http://mayi02.xyz/list_25_{}.html".format(i))
    for i in range(0, 13): start_urls.append("http://mayi02.xyz/list_26_{}.html".format(i))
    for i in range(0, 4): start_urls.append("http://mayi02.xyz/list_27_{}.html".format(i))
    for i in range(0, 33): start_urls.append("http://mayi02.xyz/list_28_{}.html".format(i))
    for i in range(0, 4): start_urls.append("http://mayi02.xyz/list_29_{}.html".format(i))
    for i in range(0, 7): start_urls.append("http://mayi02.xyz/list_30_{}.html".format(i))
    for i in range(0, 8): start_urls.append("http://mayi02.xyz/list_31_{}.html".format(i))
    for i in range(0, 4): start_urls.append("http://mayi02.xyz/list_32_{}.html".format(i))
    for i in range(0, 25): start_urls.append("http://mayi02.xyz/list_33_{}.html".format(i))
    for i in range(0, 6): start_urls.append("http://mayi02.xyz/list_34_{}.html".format(i))
    for i in range(0, 6): start_urls.append("http://mayi02.xyz/list_35_{}.html".format(i))
    for i in range(0, 16): start_urls.append("http://mayi02.xyz/list_36_{}.html".format(i))
    for i in range(0, 10): start_urls.append("http://mayi02.xyz/list_37_{}.html".format(i))
    for i in range(0, 11): start_urls.append("http://mayi02.xyz/list_38_{}.html".format(i))
    for i in range(0, 8): start_urls.append("http://mayi02.xyz/list_39_{}.html".format(i))
    for i in range(0, 21): start_urls.append("http://mayi02.xyz/list_40_{}.html".format(i))
    for i in range(0, 16): start_urls.append("http://mayi02.xyz/list_41_{}.html".format(i))
    for i in range(0, 6): start_urls.append("http://mayi02.xyz/list_42_{}.html".format(i))
    for i in range(0, 6): start_urls.append("http://mayi02.xyz/list_43_{}.html".format(i))
    for i in range(0, 7): start_urls.append("http://mayi02.xyz/list_44_{}.html".format(i))
    for i in range(0, 9): start_urls.append("http://mayi02.xyz/list_45_{}.html".format(i))
    for i in range(0, 7): start_urls.append("http://mayi02.xyz/list_46_{}.html".format(i))
    for i in range(0, 6): start_urls.append("http://mayi02.xyz/list_47_{}.html".format(i))
    for i in range(0, 5): start_urls.append("http://mayi02.xyz/list_48_{}.html".format(i))
    for i in range(0, 4): start_urls.append("http://mayi02.xyz/list_49_{}.html".format(i))
    for i in range(0, 1): start_urls.append("http://mayi02.xyz/list_50_{}.html".format(i))
    for i in range(0, 3): start_urls.append("http://mayi02.xyz/list_51_{}.html".format(i))
    for i in range(0, 1): start_urls.append("http://mayi02.xyz/list_52_{}.html".format(i))
    for i in range(0, 1): start_urls.append("http://mayi02.xyz/list_53_{}.html".format(i))

    def parse(self, response, ):
        li = response.xpath('''//div[@class="novelList"]/a/@href''').extract()
        for i in li:
            url = 'http://mayi02.xyz/' + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_chapter_content(response, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="col-xs-12 col-sm-9 col-md-10"]/h3)''').extract_first()
        if "作者" in fiction_name:
            author = fiction_name.split("作者：")[-1]
        else:
            author = '未知'
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
        classification = response.xpath('''string(//div[@class="nav"]/a[2])''').extract_first()
        fiction_update_time = response.xpath('''string(//div[@class="des"])''').extract_first()
        status = ''
        viewing_count = ''
        chapter_name = fiction_name
        chapter_con = response.xpath('''string(//input[@class="novelContentInput"]/@value)''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        index = 0
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Sis(scrapy.Spider):
    source = "SiS文学网"
    name = 'sis'
    allowed_domains = ['sis.la']
    start_urls = [
    ]
    for i in range(0, 332): start_urls.append("https://b.sis.la/page/{}".format(i))

    def parse(self, response, ):
        li = response.xpath('''//tr[@id="post-1318"]/td[@class="entry-content"]/a/@href''').extract()
        for i in li:
            url = 'https://b.sis.la' + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_chapter_content(response, ),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, ):
        fiction_name = response.xpath('''string(//h1[@class="entry-title"])''').extract_first()
        if "作者" in fiction_name:
            author = fiction_name.split("作者：")[-1]
        else:
            author = '未知'
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
        classification = response.xpath('''string(//div[@class="breadcrumbs"]/span[1]/span/text()[2])''').extract_first()
        fiction_update_time = ''
        status = ''
        viewing_count = ''
        chapter_name = fiction_name
        chapter_con = response.xpath('''string(//div[@class="entry-content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        index = 0
        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Kanunu8(scrapy.Spider):
    source = "努努书坊"
    name = 'kanunu8'
    allowed_domains = ['kanunu8.com']
    start_urls = [
    ]
    for i in range(1, 28): start_urls.append("http://www.kanunu8.com/files/chinese/29-{}.html".format(i))
    for i in range(1, 5): start_urls.append("http://www.kanunu8.com/files/dushi/2-{}.html".format(i))
    for i in range(1, 3): start_urls.append("http://www.kanunu8.com/files/old/{}.html".format(i))
    for i in range(1, 4): start_urls.append("http://www.kanunu8.com/files/xunhuan/12-{}.html".format(i))
    for i in range(1, 7): start_urls.append("http://www.kanunu8.com/files/sf/11-{}.html".format(i))
    for i in range(1, 29): start_urls.append("http://www.kanunu8.com/wuxia/{}.html".format(i))
    for i in range(1, 14): start_urls.append("http://www.kanunu8.com/tuili/list-{}.html".format(i))

    def parse(self, response, ):
        classification = response.xpath('''string(/html/body/div[1]/table[6]/tr/td[2]/font/a[2])''').extract_first()
        li = response.xpath('''//table/tr/td/table/tr/td/table/tr/td/a/@href''').extract()
        for i in li:
            url = "http://www.kanunu8.com" + i
            yield Request(url,
                          callback=lambda response, classification=classification:
                          self.get_fiction_info(response, classification),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, classification):
        fiction_name = response.xpath('''string(//h1)''').extract_first()
        author = response.xpath('''string(/html/body/div[1]/table[9]/tr[2]/td)''').extract_first()
        if "作者" in author:
            author = author.split("作者：")[-1].split()[0]
        else:
            author = '未知'
        fiction_img = 'https://ps.ssl.qhimg.com/sdmt/127_135_100/t01c2ec468bf4163b39.jpg'
        fiction_update_time = response.xpath('''string(/html/body/div[1]/table[9]/tr[2]/td)''').extract_first().split("：")[-1]
        status = ''
        viewing_count = ''
        print(fiction_name, author, classification, fiction_update_time)
        index = 0
        li = response.xpath('''//tr/td/a/@href''').extract()
        for i in li:
            # if re.match("\d+\.html", i):
            url = response.url.split("/")[-1]
            url = response.url.replace(url, '') + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(/html/body/div/table[4]/tr[1]/td)''').extract_first()
        if not chapter_name:
            chapter_name = response.xpath('''string(//h2)''').extract_first()
        chapter_con = response.xpath('''string(//td/p)''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Qirexiaoshuo(scrapy.Spider):
    source = "奇热小说"
    name = 'qirexiaoshuo'
    allowed_domains = ['qirexiaoshuo.com']

    def start_requests(self):
        url = "https://m.qirexiaoshuo.com/Book/ajax_book_cate_list"
        # FormRequest 是Scrapy发送POST请求的方法
        for i in range(1, 1300):  # 1300
            yield scrapy.FormRequest(
                url=url,
                formdata={"p": str(i), "sex": "2"},
                callback=self.parse
            )

    def parse(self, response, ):
        html = json.loads(response.text)['data']
        soup = BeautifulSoup(html, 'html.parser')
        li = soup.find_all("div", attrs={"class": "item"})
        for i in li:
            url = "https://m.qirexiaoshuo.com" + i.find("a").attrs.get("href")
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="body"]/h1)''').extract_first().strip()
        author = response.xpath('''string(//div[@class="body"]/p)''').extract_first().replace("作者：", "").strip()
        fiction_img = response.xpath('''string(//div[@class="entry"]/img/@src)''').extract_first()
        classification = response.xpath('''//div[@class="body"]/p[2]/text()''').extract_first().replace("类型：", "").replace("|", "").strip()
        fiction_update_time = response.xpath('''string(//div[@class="update"]/a[2]/span[2])''').extract_first()
        status = response.xpath('''//div[@class="body"]/p[2]/i/text()''').extract_first()
        viewing_count = response.xpath('''//div[@class="body"]/p[3]/text()''').extract_first().replace("名书友正在看", "")
        url = 'https://m.qirexiaoshuo.com' + response.xpath('''///div[@class="update"]/a[2]/@href''').extract_first()
        print(fiction_name, author, fiction_img, classification, fiction_update_time, status, viewing_count, url)
        yield Request(url,
                      callback=lambda response, fiction_name=fiction_name, classification=classification, author=author, fiction_img=fiction_img,
                                      fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                      self.get_chapter_content(response, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                      dont_filter=True
                      )

    def get_chapter_content(self, response, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        # driver = webdriver.Chrome()
        driver = webdriver.PhantomJS(executable_path='/opt/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
        driver.get(response.url)
        try:
            chapter_name = driver.find_element_by_xpath('''//h1[@class="title"]''').text
            chapter_con = driver.find_element_by_xpath('''//div[@id="read_conent_box"]''').text
            chapter_content = ''
            for i in chapter_con:
                chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
            if len(chapter_content.strip()) == 0:
                is_vip = True
            else:
                is_vip = False
            index = response.url.split("/")[-2]
            chapter_update_time = fiction_update_time
            ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)
            url = driver.find_element_by_xpath('''//div[@class="col"][3]/a''').get_attribute("href")
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, classification=classification, author=author, fiction_img=fiction_img, fiction_update_time=fiction_update_time,
                                          status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )
        finally:
            driver.close()


class Xiami77(scrapy.Spider):
    source = "虾米小说"
    name = 'xiami77'
    allowed_domains = ['xiami77.com']
    start_urls = [
        "https://www.xiami77.com/xy/index.html"
    ]

    for i in range(2, 73): start_urls.append("https://www.xiami77.com/xy/index_{}.html".format(i))  # 73

    def parse(self, response, ):
        li = response.xpath('''//td[@class="down_list"]/table/tr''')
        for i in li:
            url = i.xpath('''.//td[2]/b/a/@href''').extract_first()
            viewing_count = i.xpath('''string(.//td[5])''').extract_first()
            # print(url, viewing_count)
            if not url:
                continue
            yield Request(url,
                          callback=lambda response, viewing_count=viewing_count:
                          self.get_fiction_info(response, viewing_count),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, viewing_count):
        fiction_name = response.xpath('''string(//dd[@class="downInfoRowR"]/text()[1])''').extract_first()
        fiction_img = response.xpath('''string(//*[@id="downInfoArea"]/table/tr/td/img/@src)''').extract_first()
        author = response.xpath('''string(//dd[@class="downInfoRowR"]/text()[4])''').extract_first()
        classification = response.xpath('''string(//dd[@class="downInfoRowR"]/text()[5])''').extract_first()
        status = response.xpath('''string(//dd[@class="downInfoRowR"]/text()[7])''').extract_first()
        fiction_update_time = response.xpath('''string(//dd[@class="downInfoRowR"]/text()[10])''').extract_first()
        url = response.xpath('''//*[@id="downAddress"]/a[1]/@onclick''').extract_first()
        url = re.findall('''window.open\('(.*?')\)''', url)[0]
        print(fiction_name, fiction_img, author, classification, status, fiction_update_time, url, )
        yield Request(url,
                      callback=lambda response, fiction_name=fiction_name, index=0, classification=classification, author=author, fiction_img=fiction_img,
                                      fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                      self.get_chapter_url(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                      dont_filter=True
                      )

    def get_chapter_url(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        url = response.xpath('''/html/body/table/tr[1]/td/a/@href''').extract_first()
        url_ = response.url.replace(response.url.split("/")[-1], '')
        url_ = url_.replace(response.url.split("/")[-2], '')
        url = url_ + url.replace("../", '')

        chapter_name = fiction_name
        headers = {'content-type': 'application/json', "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"}
        ret = requests.get(url=url, headers=headers)
        ret.encoding = "gbk"
        chapter_content = ret.text
        chapter_content = chapter_content.replace("温馨提示：直接保存（或另存为）即可下载", '')
        chapter_content = chapter_content.replace("全本小说TXT电子书免费下载尽在 http://www.xiami77.com 虾米小说网", '')
        chapter_content = chapter_content.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Ayashu(scrapy.Spider):
    source = "阿雅小说网"
    name = 'ayashu'
    allowed_domains = ['ayashu.com']
    start_urls = [
    ]
    for i in range(1, 396): start_urls.append("http://www.ayashu.com/allvisit_{}/".format(i))  # 396

    def parse(self, response, ):
        li = response.xpath('''//div[@id="alistbox"]/div[@class="pic"]/a''')
        for i in li:
            url = i.xpath('''.//@href''').extract_first()
            fiction_img = i.xpath('''.//img/@src''').extract_first()
            yield Request(url,
                          callback=lambda response, fiction_img=fiction_img:
                          self.get_fiction_info(response, fiction_img),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, fiction_img):
        fiction_name = response.xpath('''string(//div[@class="infot"]/h1)''').extract_first()
        author = response.xpath('''string(//div[@class="infot"]/span)''').extract_first().replace("作者：", "")
        classification = response.xpath('''string(//ul[@class="bread-crumbs"]/li[2])''').extract_first().strip()
        print(fiction_name, author, classification)
        li = response.xpath('''//div[@id="defaulthtml4"]/table/tbody/tr/td/div[@class="dccss"]/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.ayashu.com" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time='', status='', viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(//div[@align="center"]/h2)''').extract_first()
        chapter_con = response.xpath('''string(//div[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Huaxi(scrapy.Spider):
    source = "花溪小说"
    name = 'huaxi'
    allowed_domains = ['huaxi.net']
    start_urls = [
    ]
    for i in range(1, 232): start_urls.append("http://www.huaxi.net/list?page={}".format(i))  # 232

    def parse(self, response, ):
        li = response.xpath('''//dl[@class="xq-cont-left-dl"]/dt/a/@href''').extract()
        for i in li:
            url = "http://www.huaxi.net" + i
            yield Request(url,
                          callback=lambda response,:
                          self.get_fiction_info(response, ),
                          dont_filter=True
                          )

    def get_fiction_info(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="title"]/h6)''').extract_first().strip()
        status = response.xpath('''string(//div[@class="title-f"]/text()[2])''').extract_first().strip()
        author = '未知'
        classification = response.xpath('''string(//dl[@class="xq-cont-left-dl"]/dd/ul/li[2])''').extract_first().strip()
        fiction_img = response.xpath('''string(//dl[@class="xq-cont-left-dl"]/dt/a/img/@src)''').extract_first().strip()
        fiction_update_time = response.xpath('''string(//div[@class="tx-k"]/h3/span)''').extract_first().replace("更新时间：", "").strip()
        print(fiction_name, status, classification, fiction_img, fiction_update_time)
        li = response.xpath('''//div[@class="b-cont"]/dl/dd/ul/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.huaxi.net" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(//h4[@class="wz-bt"])''').extract_first()
        chapter_con = response.xpath('''string(//div[@class="w-cont-wz"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if "PC端暂时不支持收费章节阅读" in chapter_content.strip():
            is_vip = True
        else:
            is_vip = False

        chapter_update_time = fiction_update_time
        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Ruokan(scrapy.Spider):
    source = "若看小说网"
    name = 'ruokan'
    allowed_domains = ['ruokan.net']
    start_urls = [
    ]
    for i in range(1, 10218): start_urls.append("http://www.ruokan.net/book/lastupdate_0_0_0_0_0_0_0_0_{}.html".format(i))  # 10218

    def parse(self, response, ):
        li = response.xpath('''//ul[@class="list-filter clearfix"]/li/span/a[1]/@href''').extract()
        for i in li:
            url = "http://www.ruokan.net" + i
            yield Request(url, callback=lambda response,: self.get_fiction_info(response, ), dont_filter=True)
            print(url)

    def get_fiction_info(self, response, ):
        fiction_name = response.xpath('''string(//div[@class="title"]/h1)''').extract_first().strip()
        status = response.xpath('''string(//span[@class="state"])''').extract_first().strip()
        author = response.xpath('''string(/html/body/div[2]/div/section[1]/div[2]/ul/li[2]/p)''').extract_first().strip()
        classification = response.xpath('''string(/html/body/div[2]/div/section[1]/div[2]/ul/li[1]/p)''').extract_first().strip()
        fiction_img = response.xpath('''string(//a[@class="img"]/img/@src)''').extract_first().strip()
        fiction_update_time = response.xpath('''string(/html/body/div[2]/div/section[1]/div[2]/ul/li[6]/p)''').extract_first().strip()
        viewing_count = response.xpath('''string(/html/body/div[2]/div/section[1]/div[2]/ul/li[4]/p)''').extract_first().strip()
        url = response.xpath('''string(//a[@class="all"]/@href)''').extract_first().strip()
        url = "http://www.ruokan.net" + url
        print(fiction_name, author, status, classification, fiction_img, fiction_update_time, viewing_count, url)
        yield Request(url,
                      callback=lambda response, fiction_name=fiction_name, classification=classification, author=author, fiction_img=fiction_img,
                                      fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                      self.get_chapter(response, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                      dont_filter=True
                      )

    def get_chapter(self, response, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        li = response.xpath('''//ul[@class="clearfix"]/li/a/@href''').extract()
        index = 0
        for i in li:
            url = "http://www.ruokan.net" + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count='':
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(//header/h1)''').extract_first()
        if not chapter_name:
            return
        chapter_con = response.xpath('''string(//div[@class="content clearfix"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False
        chapter_update_time = response.xpath('''string(//span[@class="time"])''').extract_first().replace("更新时间：", "")

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Fensebook(scrapy.Spider):
    source = "粉色书城"
    name = 'fensebook'
    allowed_domains = ['fensebook.com']
    start_urls = [
    ]
    for i in range(1, 395): start_urls.append("http://www.fensebook.com/index.php/Book/Booklist/catId/0/vips/0/words/0/progress/0/order/0/time/0/p/{}".format(i))  # 395

    def parse(self, response, ):
        li = response.xpath('''//div[@class="booklist"]/table/tbody/tr''')
        for i in li:
            fiction_name = i.xpath('''string(.//td[@class="name"]/div/a)''').extract_first().strip()
            author = i.xpath('''string(.//td[@class="author"])''').extract_first().strip()
            viewing_count = i.xpath('''string(.//td[@class="words"][2])''').extract_first().strip()
            fiction_update_time = i.xpath('''string(.//td[@class="time"])''').extract_first().strip()
            url = 'http://www.fensebook.com' + i.xpath('''string(.//td[@class="butt"]/a/@href)''').extract_first()
            yield Request(url, callback=lambda response, fiction_name=fiction_name, author=author, viewing_count=viewing_count, fiction_update_time=fiction_update_time:
            self.get_fiction_info(response, fiction_name, author, viewing_count, fiction_update_time), dont_filter=True)

    def get_fiction_info(self, response, fiction_name, author, viewing_count, fiction_update_time):
        status = response.xpath('''string(//p[@class="book-index-lable"]/span)''').extract_first().strip()
        fiction_img = response.xpath('''string(//div[@class="one1-left clearfix"]/img[@class="bookimg"]/@src)''').extract_first().strip()
        url = 'http://www.fensebook.com' + response.xpath('''string(//div[@class="one2"]/ul/li[1]/div/a/@href)''').extract_first().strip()
        yield Request(url,
                      callback=lambda response, fiction_name=fiction_name, author=author, fiction_img=fiction_img,
                                      fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                      self.get_chapter(response, fiction_name, author, fiction_update_time, status, fiction_img, viewing_count),
                      dont_filter=True
                      )

    def get_chapter(self, response, fiction_name, author, fiction_update_time, status, fiction_img, viewing_count):
        classification = response.xpath('''string(//p[@class="fl book-label"]/span)''').extract_first().strip()
        print(fiction_name, author, viewing_count, fiction_update_time, status, fiction_img, classification)
        li = response.xpath('''//ul[@class="directory-list clearfix"]/li/a/@href''').extract()
        index = 0
        for i in li:
            url = 'http://www.fensebook.com' + i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(//div[@class="til"]/h1)''').extract_first()
        if not chapter_name:
            return
        chapter_con = response.xpath('''string(//div[@class="main_read read-con"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False
        chapter_update_time = response.xpath('''string(//div[@class="til"]/p/span[2])''').extract_first().replace("发布时间：", "")

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Shanhuu(scrapy.Spider):
    source = "珊瑚文学"
    name = 'shanhuu'
    allowed_domains = ['shanhuu.com']
    start_urls = [
    ]
    for i in range(1, 4): start_urls.append("http://www.shanhuu.com/modules/article/articlefilter.php?order=lastupdate&page={}".format(i))  # 4

    def parse(self, response, ):
        li = response.xpath('''//tbody[@id="jieqi_page_contents"]/tr''')
        for i in li:
            fiction_name = i.xpath('''string(.//td[1])''').extract_first().strip()
            author = i.xpath('''string(.//td[3])''').extract_first().strip()
            status = i.xpath('''string(.//td[6])''').extract_first().strip()
            fiction_update_time = i.xpath('''string(.//td[5])''').extract_first().strip()
            url = i.xpath('''string(.//td[1]/a[2]/@href)''').extract_first()
            yield Request(url, callback=lambda response, fiction_name=fiction_name, author=author, status=status, fiction_update_time=fiction_update_time:
            self.get_fiction_info(response, fiction_name, author, status, fiction_update_time), dont_filter=True)

    def get_fiction_info(self, response, fiction_name, author, status, fiction_update_time):
        fiction_img = response.xpath('''//div[@class="divbox cf"]/div[1]/a/img/@src''').extract_first()
        classification = response.xpath('''string(//div[@class="tabvalue"]/table/tr[1]/td[1])''').extract_first().replace("作品分类：", "")
        viewing_count = response.xpath('''string(//*[@id="totalView"])''').extract_first()
        url = response.xpath('''string(//ul[@class="ulrow mt tc"]/li/a/@href)''').extract_first()
        yield Request(url,
                      callback=lambda response, fiction_name=fiction_name, author=author, fiction_img=fiction_img, classification=classification,
                                      fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                      self.get_chapter(response, fiction_name, author, fiction_update_time, status, fiction_img, viewing_count, classification),
                      dont_filter=True
                      )

    def get_chapter(self, response, fiction_name, author, fiction_update_time, status, fiction_img, viewing_count, classification):
        print(fiction_name, author, status, fiction_update_time, fiction_img, classification, viewing_count, )
        li = response.xpath('''//dl[@class="index"]/dd/a/@href''').extract()
        index = 0
        for i in li:
            url = i
            index += 1
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count):
        chapter_name = response.xpath('''string(//div[@class="atitle"])''').extract_first()
        if not chapter_name:
            return
        chapter_con = response.xpath('''string(//div[@id="acontent"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False
        chapter_update_time = response.xpath('''string(//div[@class="ainfo"])''').extract_first().split("\xa0\xa0\xa0\xa0")[1].replace("更新：", "")

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Qwsy(scrapy.Spider):
    source = "蔷薇书院"
    name = 'qwsy'
    allowed_domains = ['qwsy.com']
    start_urls = [
    ]
    for i in range(1, 327): start_urls.append("http://www.qwsy.com/shuku.aspx?&page={}".format(i))  # 327

    def parse(self, response, ):
        li = response.xpath('''//tbody[@id="tbody_list"]/tr''')
        for i in li:
            fiction_name = i.xpath('''string(.//td[3]/div/a)''').extract_first().strip()
            author = i.xpath('''string(.//td[6])''').extract_first().strip()
            classification = i.xpath('''string(.//td[2])''').extract_first().replace("[", "").replace("]", "").strip()
            url = 'http://www.qwsy.com' + i.xpath('''string(.//td[3]/div/a/@href)''').extract_first()
            if fiction_name:
                yield Request(url, callback=lambda response, fiction_name=fiction_name, author=author, classification=classification:
                self.get_fiction_info(response, fiction_name, author, classification), dont_filter=True)

    def get_fiction_info(self, response, fiction_name, author, classification):
        fiction_img = response.xpath('''//div[@class="zpdfmpic borgrey"]/img/@src''').extract_first()
        viewing_count = response.xpath('''//div[@class="zpdfmR2 noborder"]/span[2]/text()''').extract_first()
        fiction_update_time = response.xpath('''//div[@class="zpdfmR2 noborder"]/span[4]/text()''').extract_first()
        url = 'http://www.qwsy.com' + response.xpath('''string(//div[@class="zpdfmR4_frcon00"]/a/@href)''').extract_first()
        print(fiction_name, author, classification, viewing_count, fiction_update_time, fiction_img, url)
        yield Request(url,
                      callback=lambda response, fiction_name=fiction_name, author=author, fiction_img=fiction_img, classification=classification,
                                      fiction_update_time=fiction_update_time, status='', viewing_count=viewing_count:
                      self.get_chapter(response, fiction_name, author, fiction_update_time, status, fiction_img, viewing_count, classification),
                      dont_filter=True
                      )

    def get_chapter(self, response, fiction_name, author, fiction_update_time, status, fiction_img, viewing_count, classification):
        li = response.xpath('''//*[@id="fixed_wp"]/table/tr/td/div/a/@href''').extract()
        for i in li:
            index = i.split("=")[-1]
            url = 'http://www.qwsy.com' + i

            # driver = webdriver.Chrome()
            driver = webdriver.PhantomJS(executable_path='C:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')  # 这里的executable_path填你phantomJS的路径
            driver.get(url)
            try:
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
                ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)
            finally:
                driver.close()


class Inbook(scrapy.Spider):
    source = "花雨网"
    name = 'inbook'
    allowed_domains = ['inbook.net']
    start_urls = [
    ]
    for i in range(1, 97): start_urls.append("http://www.inbook.net/yclist_0_1_{}.html".format(i))  # 97

    def parse(self, response, ):
        li = response.xpath('''/html/body/div[2]/table/tr/td[3]/table/tr[2]/td/table/tr''')
        for i in li:
            fiction_name = i.xpath('''string(.//td[1]/@title)''').extract_first().strip()
            author = i.xpath('''string(.//td[2])''').extract_first().strip()
            classification = i.xpath('''string(.//td[3])''').extract_first().strip()
            status = i.xpath('''string(.//td[4])''').extract_first().strip()
            viewing_count = i.xpath('''string(.//td[6])''').extract_first().strip()
            fiction_update_time = i.xpath('''string(.//td[7])''').extract_first().strip()
            url = "http://www.inbook.net/" + i.xpath('''string(.//td[1]/a/@href)''').extract_first()
            if fiction_name:
                yield Request(url, callback=lambda response, fiction_name=fiction_name, author=author, classification=classification, status=status, viewing_count=viewing_count,
                                                   fiction_update_time=fiction_update_time:
                self.get_fiction_info(response, fiction_name, author, classification, status, viewing_count, fiction_update_time),
                              dont_filter=True)

    def get_fiction_info(self, response, fiction_name, author, classification, status, viewing_count, fiction_update_time):
        fiction_img = "http://www.inbook.net/" + response.xpath('''//div[@class="pic"]/a/img/@src''').extract_first()
        url = "http://www.inbook.net/" + response.xpath('''//div[@class="pic"]/a/@href''').extract_first()
        print(fiction_name, author, classification, status, viewing_count, fiction_update_time, fiction_img, url)
        yield Request(url,
                      callback=lambda response, fiction_name=fiction_name, author=author, fiction_img=fiction_img, classification=classification,
                                      fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count:
                      self.get_chapter(response, fiction_name, author, fiction_update_time, status, fiction_img, viewing_count, classification),
                      dont_filter=True
                      )

    def get_chapter(self, response, fiction_name, author, fiction_update_time, status, fiction_img, viewing_count, classification):
        li = response.xpath('''//div[@class="Div3_3"]/div[@class="Div3_3_1"]/div''')
        index = 0
        for i in li:
            index += 1
            chapter_name = i.xpath('''string(.//div[@id="tempLink1"])''').extract_first()
            chapter_update_time = i.xpath('''string(.//div[@class="Div3_3_1_1_2"])''').extract_first()
            url = 'http://www.inbook.net/' + i.xpath('''string(.//div[@id="tempLink1"]/a/@href)''').extract_first()
            yield Request(url,
                          callback=lambda response, fiction_name=fiction_name, index=index, classification=classification, author=author, fiction_img=fiction_img,
                                          fiction_update_time=fiction_update_time, status=status, viewing_count=viewing_count, chapter_name=chapter_name, chapter_update_time=chapter_update_time:
                          self.get_chapter_content(response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count, chapter_name, chapter_update_time),
                          dont_filter=True
                          )

    def get_chapter_content(self, response, index, fiction_name, classification, author, fiction_update_time, status, fiction_img, viewing_count, chapter_name, chapter_update_time):
        if not chapter_name:
            return
        chapter_con = response.xpath('''string(//div[@id="content"])''').extract()
        chapter_content = ''
        for i in chapter_con:
            chapter_content += i.replace("。", "。<br>").replace("\xa0", "")
        if len(chapter_content.strip()) == 0:
            is_vip = True
        else:
            is_vip = False

        ruku(self.source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, index)


class Comics(scrapy.Spider):
    source = "comics-porn.com"
    name = 'comics'
    allowed_domains = ['comics-porn.com']
    start_urls = [
        "http://www.comics-porn.com/",
    ]

    def parse(self, response, ):

        li = response.xpath('''//div[@class="cptmb"]/a''')
        for i in li:
            title = i.xpath('''.//@title''').extract_first()
            url = response.url + i.xpath('''.//@href''').extract_first()
            cover_image = response.url + i.xpath('''.//img/@src''').extract_first()
            print(title, cover_image, url)
            yield Request(url,
                          callback=lambda response, title=title, cover_image=cover_image:
                          self.get_img_content(response, title, cover_image),
                          dont_filter=True
                          )

    def get_img_content(self, response, title, cover_image):
        li = response.xpath('''//a/@href''').extract()
        sort = 0
        for i in li:
            if str(i).endswith(".jpg") and str(i).startswith("http://page-x.com"):
                sort += 1
                image = i
                if models.Comics.objects.filter(title=title).exists():
                    Comics = models.Comics.objects.get(title=title)
                else:
                    Comics = models.Comics(title=title, cover_image=cover_image)
                    Comics.save()
                if not models.Comics_img.objects.filter(title=Comics, sort=sort).exists():
                    s3 = boto3.resource('s3')
                    req = requests.get(url=image, headers=headers)
                    hash = hashlib.md5()
                    hash.update(image.encode('utf8'))
                    newfile = hash.hexdigest()
                    newfile = "{}.jpg".format(newfile)
                    s3.Bucket('jiangcomics').put_object(Key=newfile, Body=req.content)
                    s3_image = "https://s3.amazonaws.com/jiangcomics/{}".format(newfile)
                    models.Comics_img.objects.create(title=Comics, sort=sort, image=s3_image)
                    print(title, s3_image, sort, "入库成功", time.strftime("%F %T"))
                else:
                    print(title, image, sort, "已经存在", time.strftime("%F %T"))


class Adultgamestop(scrapy.Spider):
    source = "adultgamestop.com"
    name = 'adultgamestop'
    allowed_domains = ['adultgamestop.com']
    start_urls = [
    ]
    for i in range(1, 6): start_urls.append("http://www.adultgamestop.com/comics-sex.php?tag=&search=&p={}".format(i))  # 6

    def parse(self, response, ):
        li = response.xpath('''//div[@class="game w175"]''')
        for i in li:
            a_id = i.xpath('''.//a/@id''').extract_first()
            title = i.xpath('''string(.//span[@class="classic"])''').extract_first()
            cover_image = i.xpath('''.//a/img/@src''').extract_first()
            url = response.xpath('''//a[@id="{}"]/@href'''.format(a_id)).extract_first()
            print(title, cover_image, url)
            yield Request(url,
                          callback=lambda response, title=title, cover_image=cover_image:
                          self.get_img_content(response, title, cover_image),
                          dont_filter=True
                          )

    def get_img_content(self, response, title, cover_image):
        li = response.xpath('''//div[@class="th"]/a/@href''').extract()
        sort = 0
        for i in li:
            sort += 1
            image = i
            if models.Comics.objects.filter(title=title).exists():
                Comics = models.Comics.objects.get(title=title)
            else:
                Comics = models.Comics(title=title, cover_image=cover_image)
                Comics.save()
            if not models.Comics_img.objects.filter(title=Comics, sort=sort).exists():
                s3 = boto3.resource('s3')
                req = requests.get(url=image, headers=headers)
                hash = hashlib.md5()
                hash.update(image.encode('utf8'))
                newfile = hash.hexdigest()
                newfile = "{}.jpg".format(newfile)
                s3.Bucket('jiangcomics').put_object(Key=newfile, Body=req.content)
                s3_image = "https://s3.amazonaws.com/jiangcomics/{}".format(newfile)
                models.Comics_img.objects.create(title=Comics, sort=sort, image=s3_image)
                print(title, s3_image, sort, "入库成功", time.strftime("%F %T"))
            else:
                print(title, image, sort, "已经存在", time.strftime("%F %T"))


class Hentai(scrapy.Spider):
    source = "e-hentai.org"
    name = 'hentai'
    allowed_domains = ['e-hentai.org']
    start_urls = [
    ]
    start_index = 0
    if os.path.isfile("flag.log"):
        with open("flag.log") as f:
            start_index = int(f.read())
            start_index = start_index - 1
            if start_index < 0: start_index = 0
        os.system("/bin/cp flag.log /tmp/ ")
    for i in range(start_index, start_index + 3, ):
        start_urls.append("https://e-hentai.org/?f_doujinshi=on&f_manga=on&f_apply=Apply+Filter&page={}".format(i))  # 8700
        with open("flag.log", "w") as f:
            f.write("{}".format(i))

    # for i in range(0, 17000): start_urls.append("https://e-hentai.org/?page={}".format(i))  # 17000

    def parse(self, response, ):
        if "Your IP" in response.text or len(response.text.strip()) == 0:
            flag(response.url)
        li = response.xpath('''//tr/td[3]/div/div[@class="it5"]/a''')
        for i in li:
            url = i.xpath('''.//@href''').extract_first()
            name = i.xpath('''.//text()''').extract_first()
            if models.Hentai.objects.filter(name=name).exists():
                if models.Hentai_img.objects.filter(name__name=name).count() == int(models.Hentai.objects.filter(name=name)[0].length.split()[0]):
                    print(name, "已完成")
                    continue
            yield Request(url, callback=lambda response, response_url=response.url: self.get_info(response, response_url), dont_filter=True)

    def get_info(self, response, response_url):
        name = response.xpath('''string(//h1[@id="gn"])''').extract_first().replace("\xa0", "")
        if "Your IP" in response.text or len(response.text.strip()) == 0:
            flag(response_url)
        classification = response.xpath('''string(//div[@id="gdc"]/a/img/@src)''').extract_first().split("/")[-1].replace(".png", '')
        author = response.xpath('''string(//div[@id="gdn"])''').extract_first().replace("\xa0", "")
        posted = response.xpath('''string(//div[@id="gdd"]/table/tr[1]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        parent = response.xpath('''string(//div[@id="gdd"]/table/tr[2]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        language = response.xpath('''string(//div[@id="gdd"]/table/tr[4]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        if "English" not in language: return
        file_size = response.xpath('''string(//div[@id="gdd"]/table/tr[5]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        length = response.xpath('''string(//div[@id="gdd"]/table/tr[6]/td[@class="gdt2"])''').extract_first().replace("\xa0", "")
        url = response.xpath('''//div[@id="gdt"]/div[@class="gdtm"]/div/a/@href''').extract_first()
        if not models.Hentai.objects.filter(name=name, author=author).exists():
            Hentai = models.Hentai(name=name, author=author, posted=posted, parent=parent, language=language, file_size=file_size, length=length, classification=classification)
            Hentai.save()
        else:
            models.Hentai.objects.filter(name=name, author=author).update(posted=posted, parent=parent, language=language, file_size=file_size, length=length, classification=classification)
            Hentai = models.Hentai.objects.get(name=name, author=author)
        print(name, "-", classification, "-", author, "-", posted, "-", parent, "-", language, "-", file_size, "-", length, "-", url, "-", response.url)

        if models.Hentai_img.objects.filter(name__name=name).count() != int(length.split()[0]):
            yield Request(url,
                          callback=lambda response, name=name, author=author, posted=posted, parent=parent, language=language, file_size=file_size, length=length,
                                          classification=classification, Hentai=Hentai, response_url=response_url:
                          self.get_img_content(response, name, author, posted, parent, language, file_size, length, classification, Hentai, response_url),
                          dont_filter=True
                          )
        else:
            print(name, "-", classification, "-", author, "-", posted, "-", parent, "-", language, "-", file_size, "-", length, "-", url, "-", response.url, "已完成")

    def get_img_content(self, response, name, author, posted, parent, language, file_size, length, classification, Hentai, response_url):
        sort = response.url.split("-")[-1]
        url = response.xpath('''//a[@id="next"]/@href''').extract_first()
        image = response.xpath('''//img[@id="img"]/@src''').extract_first()
        if image.strip() == "https://ehgt.org/g/509.gif":
            flag(response_url)
        if not models.Hentai_img.objects.filter(name=Hentai, sort=sort).exists():
            s3 = boto3.resource('s3')
            req = requests.get(url=image, headers=headers)
            if req.status_code != 200:
                flag(response_url)
            hash = hashlib.md5()
            hash.update(image.encode('utf8'))
            newfile = hash.hexdigest()
            newfile = "{}.jpg".format(newfile)
            s3.Bucket('jiangalbum').put_object(Key=newfile, Body=req.content)
            s3_image = "https://s3.us-east-2.amazonaws.com/jiangalbum/{}".format(newfile)
            print(name, "-", image, '开始入库', sort, time.strftime("%F %T"))
            models.Hentai_img.objects.create(name=Hentai, image=s3_image, sort=sort)
            print(name, "-", s3_image, '入库成功 ', sort, time.strftime("%F %T"))
            # models.Hentai_img.objects.create(name=Hentai, image=image, sort=sort)
            # print(name, "-", sort, "-", image, '入库成功 ')
        else:
            print("{} - {} - {} 已存在".format(name, image, sort), time.strftime("%F %T"))
        if int(length.split()[0]) != int(sort):
            yield Request(url,
                          callback=lambda response, name=name, author=author, posted=posted, parent=parent, language=language, file_size=file_size, length=length,
                                          classification=classification, Hentai=Hentai, response_url=response_url:
                          self.get_img_content(response, name, author, posted, parent, language, file_size, length, classification, Hentai, response_url),
                          dont_filter=True
                          )


def flag(response_url):
    print("ip被封了，开始调用aws API自动换ip !")
    with open("flag.log", "w") as f:
        f.write("{}".format(response_url.split("=")[-1]))

    from botocore.exceptions import ClientError
    ec2 = boto3.client('ec2')
    try:
        allocation = ec2.allocate_address(Domain='vpc')
        response = ec2.associate_address(AllocationId=allocation['AllocationId'], InstanceId='i-0334d0ad0cc36ed6c')
        print(response)
    except ClientError as e:
        print(e)

    filters = [
        {'Name': 'domain', 'Values': ['vpc']}
    ]
    response = ec2.describe_addresses(Filters=filters)

    for i in response['Addresses']:
        if not i.get("PrivateIpAddress"):
            # print(i['AllocationId'])
            try:
                response = ec2.release_address(AllocationId=i['AllocationId'])
                print('Address released : {}'.format(i['AllocationId']))
            except ClientError as e:
                print(e)
    os.system('''ps aux|grep scrapy|grep hentai|awk '{print "kill -9 "$2}'|sh''')


class Hentai2read(scrapy.Spider):
    source = "hentai2read.com"
    name = 'hentai2read'
    allowed_domains = ['hentai2read.com']
    start_urls = [
    ]
    # for i in range(688, 0, -1): start_urls.append("https://hentai2read.com/latest/{}/".format(i))  # 666
    for i in range(1, 680, ): start_urls.append("https://hentai2read.com/latest/{}/".format(i))  # 666

    def parse(self, response, ):
        with open("flag.log", "w") as f:
            f.write("{}\n".format(response.url.split("/")[-2]))
        li = response.xpath('''//ul[@class="nav-users"]/li[@class="js-lts-grp ribbon ribbon-modern ribbon-primary ribbon-right"]''')
        for i in li:
            name = i.xpath('''string(.//a/text()[2])''').extract_first().strip()
            url = i.xpath('''string(.//a/@href)''').extract_first()
            print(name, url)
            yield Request(url,
                          callback=lambda response, name=name,:
                          self.get_img_info(response, name, ),
                          dont_filter=True
                          )

    def get_img_info(self, response, name, ):
        cover_image = response.xpath('''//a[@id="js-linkNext"]/img/@src''').extract_first()
        li = response.xpath('''//ul[@class="list list-simple-mini"]/li[@class="text-primary"]''')
        text_content = li.xpath('''string(.//a)''').extract()
        Parody = text_content[0].strip()
        Ranking = text_content[1].strip()
        Status = text_content[2].strip()
        Release_Year = text_content[3].strip()
        View = text_content[4].strip()
        Author = text_content[5].strip()
        Artist = text_content[6].strip()
        Category = text_content[7].strip()
        Content = text_content[8].strip()
        Character = text_content[9].strip()
        Language = text_content[10].strip()
        print(cover_image, text_content, )
        li = response.xpath('''//ul[@class="nav-chapters"]/li/div[@class="media"]''')
        for i in li:
            url = i.xpath('''.//a[@class="pull-left font-w600"]/@href''').extract_first()
            chapter_name = i.xpath('''string(.//a[@class="pull-left font-w600"])''').extract_first().split()[0] + ' - ' + name
            chapter_index = chapter_name.split()[0]
            chapter_index = re.sub("[a-z][A-Z]*", '', chapter_index)
            print(url, chapter_name)
            yield Request(url,
                          callback=lambda response, name=name, cover_image=cover_image, Parody=Parody, Ranking=Ranking, Status=Status, Release_Year=Release_Year, View=View, Author=Author,
                                          Artist=Artist, Category=Category, Content=Content, Character=Character, Language=Language, chapter_index=chapter_index, chapter_name=chapter_name:
                          self.get_img_url(response, name, cover_image, Parody, Ranking, Status, Release_Year, View, Author, Artist, Category, Content, Character, Language, chapter_index, chapter_name),
                          dont_filter=True
                          )

    def get_img_url(self, response, name, cover_image, Parody, Ranking, Status, Release_Year, View, Author, Artist, Category, Content, Character, Language, chapter_index, chapter_name):
        page = response.xpath('''//div[@class="controls-block dropdown"]/ul[@class="dropdown-menu scrollable-dropdown dropdown-menu-center"]''')[0]
        page = page.xpath('''.//li/a/text()''').extract()
        total = len(page)
        if models.Hentai2read_img.objects.filter(chapter_name__chapter_name__contains=chapter_name).count() >= total:
            print(chapter_name, "已经完成", time.strftime("%F %T"))
            return
        img_index = 0
        for i in page:
            img_index += 1
            if img_index == 1:
                url = response.url
            else:
                # break
                url = response.url + i.replace("Page", '').strip()
            yield Request(url,
                          callback=lambda response, name=name, cover_image=cover_image, Parody=Parody, Ranking=Ranking, Status=Status, Release_Year=Release_Year, View=View, Author=Author,
                                          Artist=Artist, Category=Category, Content=Content, Character=Character, Language=Language, img_index=img_index, chapter_index=chapter_index, chapter_name=chapter_name:
                          self.get_img_content(response, name, cover_image, Parody, Ranking, Status, Release_Year, View, Author, Artist, Category, Content, Character, Language, chapter_index, img_index, chapter_name),
                          dont_filter=True
                          )

    def get_img_content(self, response, name, cover_image, Parody, Ranking, Status, Release_Year, View, Author, Artist, Category, Content, Character, Language, chapter_index, img_index, chapter_name):
        image = response.xpath('''//img[@id="arf-reader"]/@src''').extract_first()
        if models.Hentai2read.objects.filter(name=name).exists():
            Hentai2read = models.Hentai2read.objects.get(name=name)
        else:
            Hentai2read = models.Hentai2read(name=name, cover_image=cover_image, Parody=Parody, Ranking=Ranking, Status=Status, Release_Year=Release_Year, View=View, Author=Author,
                                             Artist=Artist, Category=Category, Content=Content, Character=Character, Language=Language, )
            Hentai2read.save()
        if models.Hentai2read_chapter.objects.filter(name=Hentai2read, chapter_name__contains=chapter_name).exists():
            Hentai2read_chapter = models.Hentai2read_chapter.objects.get(name=Hentai2read, chapter_name__contains=chapter_name)
            models.Hentai2read_chapter.objects.filter(name=Hentai2read, chapter_name__contains=chapter_name, page_num__lte=img_index).update(page_num=img_index, chapter_name=chapter_name, )
            models.Hentai2read_chapter.objects.filter(name=Hentai2read, chapter_name__contains=chapter_name, page_num__isnull=True).update(page_num=img_index, chapter_name=chapter_name, )
        else:
            Hentai2read_chapter = models.Hentai2read_chapter(name=Hentai2read, chapter_index=chapter_index, chapter_name=chapter_name, page_num=img_index, )
            Hentai2read_chapter.save()
        if not models.Hentai2read_img.objects.filter(chapter_name=Hentai2read_chapter, img_index=img_index).exists():
            # s3 = boto3.resource('s3')
            # req = requests.get(url=image, headers=headers)
            # hash = hashlib.md5()
            # hash.update(image.encode('utf8'))
            # newfile = hash.hexdigest()
            # newfile = "{}.jpg".format(newfile)
            # s3.Bucket('jiangcomics').put_object(Key=newfile, Body=req.content)
            # s3_image = "https://s3.amazonaws.com/jiangcomics/{}".format(newfile)
            # models.Hentai2read_img.objects.create(chapter_name=Hentai2read_chapter, img_index=img_index, image=s3_image)
            # print(name, chapter_name, s3_image, img_index, "入库成功", time.strftime("%F %T"))
            image = "http://fiction.govpnback.com/anti_theft_chain_img/?img={}".format(image)
            # if models.Hentai2read_img.objects.filter(image=image).count() < 2:
            models.Hentai2read_img.objects.create(chapter_name=Hentai2read_chapter, img_index=img_index, image=image)
            print(chapter_name, image, img_index, "入库成功", time.strftime("%F %T"))
        else:
            print(chapter_name, image, img_index, "已经存在", time.strftime("%F %T"))


def ruku(source, classification, fiction_name, fiction_img, author, viewing_count, fiction_update_time, status, is_vip, chapter_name, chapter_content, chapter_update_time, order_by=0):
    '''
    入库
    :return:
    '''
    if not models.Classification.objects.filter(name=classification, source=source).exists():
        Classification = models.Classification(name=classification, source=source)
        Classification.save()
    else:
        Classification = models.Classification.objects.get(name=classification, source=source)

    if not models.Fiction_list.objects.filter(fiction_name=fiction_name, author=author, cassificationc=Classification).exists():
        Fiction_list = models.Fiction_list(cassificationc=Classification, fiction_name=fiction_name, viewing_count=viewing_count, author=author, update_time=fiction_update_time, status=status,
                                           image=fiction_img)
        Fiction_list.save()
    else:

        models.Fiction_list.objects.filter(fiction_name=fiction_name, author=author, cassificationc=Classification).update(cassificationc=Classification, viewing_count=viewing_count,
                                                                                                                           update_time=fiction_update_time, status=status, image=fiction_img)

        Fiction_list = models.Fiction_list.objects.get(fiction_name=fiction_name, author=author, cassificationc=Classification)

    if not models.Fiction_chapter.objects.filter(chapter_name=chapter_name, fiction_name=Fiction_list).exists():
        Fiction_chapter = models.Fiction_chapter(chapter_name=chapter_name, fiction_name=Fiction_list, is_vip=is_vip, chapter_content=chapter_content, update_time=chapter_update_time,
                                                 order_by=order_by)
        Fiction_chapter.save()

    else:
        if chapter_content:
            models.Fiction_chapter.objects.filter(chapter_name=chapter_name, fiction_name=Fiction_list).update(chapter_name=chapter_name, fiction_name=Fiction_list, is_vip=is_vip,
                                                                                                               order_by=order_by, chapter_content=chapter_content,
                                                                                                               update_time=chapter_update_time)
    print("来源：{} , 分类：{} , 书名：{} , 作者：{} , 章节：{} ".format(source, classification, fiction_name, author, chapter_name))
