import time, re, os, sys, json
from django.core.wsgi import get_wsgi_application

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 定位到你的django根目录
print(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fiction.settings")  # 你的django的settings文件
application = get_wsgi_application()
from app01 import models


def ruhu(source, name, age, photo, country_address, instructions, relationship, education, faith, have_kids, body_type,
         smoke, want_kids, height, drink, ethnicity, more, photo_gallery, sex, INTERESTS_and_PORTS, What_She_is_Looking_For):
    if models.Xiangqing.objects.filter(source=source, name=name).exists():
        models.Xiangqing.objects.filter(source=source, name=name) \
            .update(age=age, photo=photo, country_address=country_address,
                    instructions=instructions,
                    relationship=relationship,
                    education=education, faith=faith,
                    have_kids=have_kids, body_type=body_type,
                    smoke=smoke, want_kids=want_kids,
                    height=height, drink=drink,
                    ethnicity=ethnicity,
                    more=more, photo_gallery=photo_gallery,
                    sex=sex,
                    INTERESTS_and_PORTS=INTERESTS_and_PORTS, What_She_is_Looking_For=What_She_is_Looking_For)
    else:
        models.Xiangqing.objects.create(source=source, name=name, age=age,
                                        photo=photo, country_address=country_address,
                                        instructions=instructions,
                                        relationship=relationship,
                                        education=education, faith=faith,
                                        have_kids=have_kids, body_type=body_type,
                                        smoke=smoke, want_kids=want_kids,
                                        height=height, drink=drink,
                                        ethnicity=ethnicity,
                                        more=more, photo_gallery=photo_gallery,
                                        sex=sex,
                                        INTERESTS_and_PORTS=INTERESTS_and_PORTS, What_She_is_Looking_For=What_She_is_Looking_For)

    print("来源：{} ， 姓名：{}".format(source, name))
