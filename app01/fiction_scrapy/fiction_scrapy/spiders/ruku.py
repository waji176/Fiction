from django.core.wsgi import get_wsgi_application
import os, sys

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))  # 定位到你的django根目录
# print(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fiction.settings")  # 你的django的settings文件
application = get_wsgi_application()
from app01 import models


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

    if not models.Fiction_list.objects.filter(fiction_name=fiction_name, author=author):
        Fiction_list = models.Fiction_list(cassificationc=Classification, fiction_name=fiction_name,
                                           viewing_count=viewing_count, author=author, update_time=fiction_update_time,
                                           status=status, image=fiction_img)
        Fiction_list.save()
    else:

        models.Fiction_list.objects.filter(fiction_name=fiction_name, author=author).update(
            cassificationc=Classification,
            viewing_count=viewing_count,
            update_time=fiction_update_time,
            status=status, image=fiction_img)

        Fiction_list = models.Fiction_list.objects.get(fiction_name=fiction_name, author=author)

    if not models.Fiction_chapter.objects.filter(chapter_name=chapter_name, fiction_name=Fiction_list):
        Fiction_chapter = models.Fiction_chapter(chapter_name=chapter_name, fiction_name=Fiction_list, is_vip=is_vip,
                                                 chapter_content=chapter_content, update_time=chapter_update_time,
                                                 order_by=order_by)
        Fiction_chapter.save()

    else:
        if chapter_content:
            models.Fiction_chapter.objects.filter(chapter_name=chapter_name, fiction_name=Fiction_list).update(
                chapter_name=chapter_name, fiction_name=Fiction_list, is_vip=is_vip, order_by=order_by,
                chapter_content=chapter_content, update_time=chapter_update_time)
    print(
        "来源：{} , 分类：{} , 书名：{} , 作者：{} , 章节：{} ".format(source, classification, fiction_name, author,
                                                        chapter_name)
    )
