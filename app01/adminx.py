import xadmin
from app01 import models


class ClassificationAdmin(object):
    list_display = ['id', 'name', 'source']
    search_fields = ['id', 'name', 'source']


xadmin.site.register(models.Classification, ClassificationAdmin)


class Fiction_listAdmin(object):
    list_display = ['id', 'cassificationc', 'fiction_name', 'author', 'viewing_count', 'update_time', 'status', ]
    search_fields = ['id', 'fiction_name', 'author', 'update_time', 'status', ]


xadmin.site.register(models.Fiction_list, Fiction_listAdmin)


class Fiction_chapterAdmin(object):
    list_display = ['id', 'chapter_name', 'fiction_name', 'is_vip', 'update_time']
    search_fields = ['id', 'chapter_name', 'update_time']


xadmin.site.register(models.Fiction_chapter, Fiction_chapterAdmin)


class XiangqingAdmin(object):
    list_display = ['source', 'name', 'age', 'country_address', 'relationship', 'education', 'faith', 'have_kids',
                    'body_type', 'smoke', 'want_kids', 'height', 'drink', 'ethnicity', 'sex', "photo"]
    search_fields = ['source', 'name', ]


xadmin.site.register(models.Xiangqing, XiangqingAdmin)


class AppannieAdmin(object):
    list_display = ["device",
                    "country_region",
                    "category",
                    "ranking_type",
                    "index",
                    "app_id",
                    "app_name",
                    "app_img",
                    "app_company_website",
                    "compatibility",
                    "updated",
                    "version",
                    "size",
                    "only_32_bit",

                    "seller",
                    "headquarter_country_region",
                    "rating",
                    "family_sharing",
                    "requirements",
                    "bundle_ID",
                    "game_center",
                    "supports_apple_watch",
                    "supports_iMessage", "language", "app_description", "update_time", ]
    search_fields = ["device",
                     "country_region",
                     "category",
                     "ranking_type",
                     "index",
                     "app_id",
                     "app_name",
                     "app_img",

                     "app_company_website",
                     "compatibility",
                     "updated",
                     "version",
                     "size",
                     "only_32_bit",

                     "seller",
                     "headquarter_country_region",
                     "rating",
                     "family_sharing",
                     "requirements",
                     "bundle_ID",
                     "game_center",
                     "supports_apple_watch",
                     "supports_iMessage", "update_time"]
    list_filter = ["category", "ranking_type"]


xadmin.site.register(models.Appannie, AppannieAdmin)
