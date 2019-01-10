from django.contrib import admin

from app01 import models


class ClassificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'source']
    search_fields = ['id', 'name', 'source']


admin.site.register(models.Classification, ClassificationAdmin)


class Fiction_listAdmin(admin.ModelAdmin):
    list_display = ['id', 'cassificationc', 'fiction_name', 'author', 'viewing_count', 'update_time', 'status', ]
    search_fields = ['id', 'fiction_name', 'author', 'update_time', 'status', ]


admin.site.register(models.Fiction_list, Fiction_listAdmin)


class Fiction_chapterAdmin(admin.ModelAdmin):
    list_display = ['id', 'chapter_name', 'fiction_name', 'is_vip', 'update_time']
    search_fields = ['id', 'chapter_name', 'update_time']


admin.site.register(models.Fiction_chapter, Fiction_chapterAdmin)


class XiangqingAdmin(admin.ModelAdmin):
    list_display = ['source', 'name', 'age', 'country_address', 'relationship', 'education', 'faith', 'have_kids',
                    'body_type', 'smoke', 'want_kids', 'height', 'drink', 'ethnicity', 'sex', "photo"]
    search_fields = ['source', 'name', ]


admin.site.register(models.Xiangqing, XiangqingAdmin)


# class AppannieAdmin(admin.ModelAdmin):
#     list_display = ['source', 'name', 'age', 'country_address', 'relationship', 'education', 'faith', 'have_kids',
#                     'body_type', 'smoke', 'want_kids', 'height', 'drink', 'ethnicity', 'sex', "photo"]
#     search_fields = ['source', 'name', ]
#
#
# admin.site.register(models.Appannie, AppannieAdmin)

class HentaiAdmin(admin.ModelAdmin):
    list_display = ['classification', 'name', 'author', 'posted', 'parent', 'language', 'file_size', 'length']
    search_fields = ['classification', 'name', ]


admin.site.register(models.Hentai, HentaiAdmin)


class Hentai_imgAdmin(admin.ModelAdmin):
    list_display = ['name', 'image', 'sort', ]


admin.site.register(models.Hentai_img, Hentai_imgAdmin)
admin.site.register(models.Comics)
admin.site.register(models.Comics_img)


class Hentai2readAdmin(admin.ModelAdmin):
    list_display = ['name', 'cover_image', 'Parody', 'Status', 'View', 'Author', 'Artist', 'Category', 'Content', 'Language']
    search_fields = ['name']


admin.site.register(models.Hentai2read, Hentai2readAdmin)


class Hentai2read_chapterAdmin(admin.ModelAdmin):
    list_display = ['name', 'chapter_name', 'chapter_index', 'page_num', ]
    search_fields = ['name', 'chapter_name']


admin.site.register(models.Hentai2read_chapter, Hentai2read_chapterAdmin)
admin.site.register(models.Hentai2read_img)
