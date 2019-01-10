from django.shortcuts import render, HttpResponse
import requests, json, MySQLdb
from app01 import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection


def write_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.connection.commit()
    try:
        raise Exception("some thing goes wrong! :(")
    except Exception:
        connection.connection.rollback()


def read_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    nRet = cursor.fetchall()
    return nRet


# Create your views here.
# def index(request):
#     Classification = models.Classification.objects.all().order_by("id")
#     Classification_id = request.GET.get("classification_id") if request.GET.get("classification_id") else 1
#     Fiction_list = models.Fiction_list.objects.filter(cassificationc=models.Classification.objects.get(id=Classification_id))
#
#     return render(request, "index.html", {"Classification": Classification, "Fiction_list": Fiction_list,
#                                           "Classification_id": Classification_id})
#
#
# def fiction(request):
#     Classification = models.Classification.objects.all().order_by("id")
#     fiction_id = request.GET.get("fiction_id") if request.GET.get("fiction_id") else 1
#
#     Fiction_chapter = models.Fiction_chapter.objects.filter(fiction_name=models.Fiction_list.objects.get(id=fiction_id)).order_by("order_by", 'id')
#
#     return render(request, 'fiction.html', {"Classification": Classification, "Fiction_chapter": Fiction_chapter})
#
#
# def chapter_content(request):
#     Classification = models.Classification.objects.all().order_by("id")
#     chapter_content_id = request.GET.get("chapter_content_id") if request.GET.get("chapter_content_id") else 1
#     chapter_content = models.Fiction_chapter.objects.filter(id=chapter_content_id)
#     return render(request, 'chapter_content.html', {"Classification": Classification, "chapter_content": chapter_content})

def index(request):
    Classification = models.Classification.objects.all().order_by("id")
    Classification_id = request.GET.get("classification_id") if request.GET.get("classification_id") else 25

    Fiction_list = models.Fiction_list.objects.filter(
        cassificationc=models.Classification.objects.get(id=Classification_id))

    Ranking_list = models.Fiction_list.objects.filter(
        cassificationc=models.Classification.objects.get(id=26))

    Recommend_list = models.Fiction_list.objects.filter(
        cassificationc=models.Classification.objects.get(id=27))
    return render(request, "index.html", {"Classification": Classification, "Fiction_list": Fiction_list, "Ranking_list": Ranking_list, "Recommend_list": Recommend_list, "Classification_id": Classification_id})


def fiction(request):
    Classification = models.Classification.objects.all().order_by("id")
    fiction_id = request.GET.get("fiction_id") if request.GET.get("fiction_id") else 1
    Fiction_chapter = models.Fiction_chapter.objects.filter(fiction_name=models.Fiction_list.objects.get(id=fiction_id)).order_by("order_by", 'id')

    return render(request, 'fiction.html', {"Classification": Classification, "Fiction_chapter": Fiction_chapter})


def chapter_content(request):
    Classification = models.Classification.objects.all().order_by("id")
    chapter_content_id = request.GET.get("chapter_content_id") if request.GET.get("chapter_content_id") else 1
    chapter_content = models.Fiction_chapter.objects.filter(id=chapter_content_id)
    fiction_id = request.GET.get("fiction_id") if request.GET.get("fiction_id") else 1
    Fiction_chapter = models.Fiction_chapter.objects.filter(fiction_name=models.Fiction_list.objects.get(id=fiction_id)).order_by("order_by", 'id')
    all_id = []
    for i in Fiction_chapter:
        all_id.append(i.id)

    return render(request, 'chapter_content.html', {"Classification": Classification, "chapter_content": chapter_content, "all_id": all_id})


def itunes_store_web_service_search(request):
    term = request.POST.get('term')
    if term:
        ret = requests.get(url="https://itunes.apple.com/search", params={"term": term, "country": request.POST.get('country'), "media": request.POST.get('media'), "limit": request.POST.get('limit')})
        results = ret.json()['results']
        return render(request, "itunes-store-web-service-search.html", {"results": json.dumps(results)}, )
    return render(request, "itunes-store-web-service-search.html", {"results": json.dumps([])})


def hentaiindex(request):
    li = read_sql('''select t1.id from app01_hentai t1, (select count(name_id) as img_num,name_id from app01_hentai_img group by name_id) t2 where replace(t1.length,' pages','')=t2.img_num and t1.id=t2.name_id;''')
    id_in = []
    for i in li:
        id_in.append(i[0])
    Hentai = models.Hentai.objects.filter(id__in=id_in).order_by("-posted")
    current_page = request.GET.get('p')
    every_page_shows = request.GET.get('every_page_shows')
    every_page_shows = every_page_shows if every_page_shows else 100
    paginator = Paginator(Hentai, every_page_shows)
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    hentai_id = request.GET.get("hentai_id")
    if hentai_id:
        hentai_img = models.Hentai_img.objects.filter(name_id=hentai_id).order_by('sort')
        return render(request, "hentai.html", {"hentai_img": hentai_img, })
    return render(request, "hentaiindex.html", {"Hentai": posts, "every_page_shows": every_page_shows})


def hentai_doujinshi_manga(request):
    li = read_sql('''select t1.id from app01_hentai t1, (select count(name_id) as img_num,name_id from app01_hentai_img group by name_id) t2 where replace(t1.length,' pages','')=t2.img_num and t1.id=t2.name_id;''')
    id_in = []
    for i in li:
        id_in.append(i[0])
    Hentai = models.Hentai.objects.filter(classification__in=['doujinshi', 'manga'], language__contains="English", id__in=id_in).order_by("-posted")
    current_page = request.GET.get('p')
    paginator = Paginator(Hentai, 100)
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "hentaiindex.html", {"Hentai": posts, })


def hentai_statistics(request):
    write_sql("delete from app01_hentai  where name=''")
    classification_ = request.GET.get("classification")
    if classification_:
        language = read_sql('''select language,count(id) from app01_hentai where classification='{}'  group by language'''.format(classification_))
        all_count = models.Hentai.objects.filter(classification=classification_).count()
        language_li = []
        for i in language:
            language_li.append({
                "language": i[0],
                "num": i[1],
                "percentage": round(i[1] / all_count * 100, 3)
            })
        return render(request, 'language.html', {"language": language_li, "all_count": all_count})

    all_count = models.Hentai.objects.all().count()
    mb = read_sql('''select sum(replace(file_size,'MB','')) from app01_hentai where file_size like '%MB%' ''')[0][0]
    gb = read_sql('''select sum(replace(file_size,'GB','')) from app01_hentai where file_size like '%GB%' ''')[0][0]
    kb = read_sql('''select sum(replace(file_size,'KB','')) from app01_hentai where file_size like '%KB%' ''')[0][0]
    all_mb = mb + gb * 1024 + kb / 1024
    all_gb = all_mb / 1024
    classification = read_sql('''select classification,count(id) from app01_hentai  group by classification''')
    classification_li = []

    language = read_sql('''select language,count(id) from app01_hentai  group by language''')
    language_li = []
    for i in language:
        language_li.append({
            "language": i[0],
            "num": i[1],
            "percentage": round(i[1] / all_count * 100, 3)
        })

    classification_mb = read_sql('''select classification,sum(replace(file_size,'MB','')) from app01_hentai where file_size like '%MB%' group by classification''')
    classification_gb = read_sql('''select classification,sum(replace(file_size,'GB','')) from app01_hentai where file_size like '%GB%' group by classification''')
    classification_kb = read_sql('''select classification,sum(replace(file_size,'KB','')) from app01_hentai where file_size like '%KB%' group by classification''')

    classification_GB = {}
    for i in classification_gb: classification_GB[i[0]] = i[1]
    for i in classification_mb:
        try:
            classification_GB[i[0]] += i[1] / 1024
        except:
            classification_GB[i[0]] = i[1] / 1024
    for i in classification_kb:
        try:
            classification_GB[i[0]] += i[1] / 1024 / 1024
        except:
            classification_GB[i[0]] = i[1] / 1024 / 1024
            # print(classification_GB)
    for i in classification:
        classification_li.append({
            "classification": i[0],
            "num": i[1],
            "percentage": round(i[1] / all_count * 100, 3),
            "gb": classification_GB[i[0]]
        })
    return render(request, "hentai_statistics.html", {"classification": classification_li, "all_gb": all_gb, "all_count": all_count, "language": language_li, "classification_gb": classification_GB, "total": 0})


def comics(request):
    Hentai = models.Comics.objects.all()
    current_page = request.GET.get('p')
    paginator = Paginator(Hentai, 10)
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    hentai_id = request.GET.get("hentai_id")
    if hentai_id:
        hentai_img = models.Comics_img.objects.filter(title_id=hentai_id).order_by('sort')
        return render(request, "comics.html", {"hentai_img": hentai_img, })
    return render(request, "comicsindex.html", {"Hentai": posts, })


def hentai2read(request):
    li = read_sql('''select name_id from app01_hentai2read_chapter where id in ( select chapter_name_id from app01_hentai2read_img group by chapter_name_id having count(chapter_name_id)<5)''')
    id_in = []
    for i in li:
        id_in.append(i[0])
    li1 = read_sql('''select name_id from app01_hentai2read_chapter where id in ( select chapter_name_id from app01_hentai2read_img where img_index=1  )''')
    id_in1 = []
    for i in li1:
        id_in1.append(i[0])
    Hentai = models.Hentai2read.objects.filter(id__in=id_in1).exclude(id__in=id_in).order_by('-id')
    current_page = request.GET.get('p')
    every_page_shows = request.GET.get('every_page_shows')
    every_page_shows = every_page_shows if every_page_shows else 100
    paginator = Paginator(Hentai, every_page_shows)
    try:
        posts = paginator.page(current_page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    hentai2read_id = request.GET.get("hentai2read_id")

    if hentai2read_id:
        name = models.Hentai2read_chapter.objects.filter(name_id=hentai2read_id).order_by('chapter_index')
        return render(request, "hentai2read_chapter.html", {"name": name, })

    chapter_id = request.GET.get("chapter_id")
    if chapter_id:
        hentai2read_img = models.Hentai2read_img.objects.filter(chapter_name_id=chapter_id)
        return render(request, "hentai2read_img.html", {"hentai2read_img": hentai2read_img, })
    return render(request, "hentai2read.html", {"Hentai": posts, "every_page_shows": every_page_shows})


def images(request):
    img = request.GET.get("img")
    return render(request, 'image.html', {"img": img})


def anti_theft_chain_img(request):
    img = request.GET.get("img")
    req = requests.get(url=img)
    return HttpResponse(req.content)


def exec_script(request, tid, fiction_name):
    import pymysql, os
    from concurrent.futures import ThreadPoolExecutor
    def insert_mysql(sql):
        conn = pymysql.connect(host='jwh.cvsx8eqaeyh0.ap-northeast-2.rds.amazonaws.com', port=3306, user='jwh', passwd='jiangwenhui', db='fiction', charset='UTF8')
        cur = conn.cursor()
        cur.execute(sql)
        nRet = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return nRet

    def done(request, *args, **kwargs):  #
        result = request.result()
        print(result, args, kwargs)

    classification = insert_mysql('''select type_name from wmcms.wm_novel_type where type_id={}'''.format(tid))[0][0]
    fiction_dir = os.path.join("/usr/local/nginx/html/files/txt/novel", classification, fiction_name)
    if not os.path.isdir(fiction_dir):
        os.makedirs(os.path.join(fiction_dir))
    else:
        return HttpResponse("ok")
    chanper = insert_mysql(
        r'''select chapter_name,chapter_content from app01_fiction_chapter where fiction_name_id in (select id from app01_fiction_list where replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(fiction_name,'*',''),'?',''),'/',''),':',''),'\n',''),'[',''),']',''),'|',''),' ',''),'\\',''),'\"',''),'\t',''),'\r',''),'>',''),'<','')='{}'  )'''.format(
            fiction_name))

    def func(i):
        chapter_name = i[0]
        chapter_name = str(chapter_name).replace("?", '').replace("/", '').replace(":", '').replace("\n", '').replace("?", '').replace("/", '').replace("\\", '').replace("\"", '').replace(":", '').replace("\n", ''). \
            replace("*", '').replace("\t", "").replace("\r", "").replace("|", "").replace(">", "").replace("<", "").strip()
        chapter_content = i[1]
        with open(os.path.join(fiction_dir, "{}.txt".format(chapter_name)), "w", encoding="utf-8") as f:
            chapter_content = str(chapter_content).replace("<p>", "\n").replace("</p>", "\n").replace("<br>", '\n').replace("</br>", '\n').replace("&nbsp;", ' ')
            f.write("{}\n\n    {}\n\n".format(chapter_name, chapter_content.strip()))
            print(fiction_name, chapter_name, "写入文件成功")

    pool = ThreadPoolExecutor(100)
    for i in chanper:
        v_ = pool.submit(func, i)
        v_.add_done_callback(done)
    pool.shutdown(wait=True)
    return HttpResponse("ok")
