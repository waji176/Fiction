from django.db import models


class Classification(models.Model):
    source = models.CharField(max_length=255, default="", verbose_name="小说来源")
    name = models.CharField(max_length=255, verbose_name="小说分类")

    def __str__(self):
        return "{}-{}".format(self.source, self.name)

    class Meta:
        unique_together = ["source", "name"]
        verbose_name_plural = "小说分类"
        verbose_name = "小说分类"


class Fiction_list(models.Model):
    cassificationc = models.ForeignKey(Classification, verbose_name="小说分类")
    fiction_name = models.CharField(max_length=255, verbose_name="小说名称")
    author = models.CharField(max_length=255, verbose_name="作者")
    viewing_count = models.CharField(max_length=255, default="", verbose_name="浏览数/点击数")
    update_time = models.CharField(default="", max_length=255, verbose_name="小说更新时间", )
    status = models.CharField(max_length=255, verbose_name='小说状态', default="连载")
    image = models.CharField(default="", max_length=255, verbose_name="小说封面图片", )

    def __str__(self):
        return self.fiction_name

    class Meta:
        unique_together = ["fiction_name", "author", 'cassificationc']
        verbose_name_plural = "小说"
        verbose_name = "小说"


class Fiction_chapter(models.Model):
    fiction_name = models.ForeignKey(Fiction_list, verbose_name="小说名称")
    chapter_name = models.CharField(max_length=255, verbose_name="章节名称")
    chapter_content = models.TextField(verbose_name="章节内容")
    is_vip = models.BooleanField(default=False, verbose_name="是否是VIP章节")
    update_time = models.CharField(default="", max_length=255, verbose_name="章节更新时间", )
    order_by = models.IntegerField(default=0, verbose_name="排序")

    def __str__(self):
        return self.chapter_name

    class Meta:
        unique_together = ["chapter_name", "fiction_name"]
        verbose_name_plural = "章节"
        verbose_name = "章节"


class Xiangqing(models.Model):
    source = models.CharField(max_length=255, verbose_name="来源网站", )
    name = models.CharField(max_length=255, verbose_name="姓名", )
    age = models.CharField(max_length=255, verbose_name="年龄", default='')
    photo = models.CharField(max_length=255, verbose_name="头像", default='')
    country_address = models.CharField(max_length=255, verbose_name="国家地区", default='')
    instructions = models.TextField(verbose_name="交友说明", default='')
    relationship = models.CharField(max_length=255, verbose_name="状态：是否单身", default='')
    education = models.CharField(max_length=255, verbose_name="学历", default='')
    faith = models.CharField(max_length=255, verbose_name="宗教信仰", default='')
    have_kids = models.CharField(max_length=255, verbose_name="是否有小孩", default='')
    body_type = models.CharField(max_length=255, verbose_name="体型", default='')
    smoke = models.CharField(max_length=255, verbose_name="是否抽烟", default='')
    want_kids = models.CharField(max_length=255, verbose_name="打不打算要小孩", default='')
    height = models.CharField(max_length=255, verbose_name="身高", default='')
    drink = models.CharField(max_length=255, verbose_name="喝不喝酒", default='')
    ethnicity = models.CharField(max_length=255, verbose_name="种族", default='')
    more = models.TextField(verbose_name="更多信息", default='')
    photo_gallery = models.TextField(verbose_name="照片库", default='')
    sex = models.CharField(max_length=255, verbose_name="性别", default='')
    INTERESTS_and_PORTS = models.TextField(verbose_name="兴趣爱好", default='')
    What_She_is_Looking_For = models.TextField(verbose_name="她在寻找什么", default='')

    def __str__(self):
        return "{}-{}".format(self.source, self.name)

    class Meta:
        unique_together = ["source", "name"]
        verbose_name_plural = "交友网站信息"
        verbose_name = "交友网站信息"


class Appannie(models.Model):
    device = models.CharField(max_length=255, verbose_name="设备", default='')
    country_region = models.CharField(max_length=255, verbose_name="国家/地区", default='')
    category = models.CharField(max_length=255, verbose_name="类别", default='')
    ranking_type = models.CharField(max_length=255, verbose_name="排行 类型", default='')
    index = models.IntegerField(verbose_name="排名", default=0)
    app_id = models.CharField(max_length=255, verbose_name="APP ID", default='')
    app_name = models.CharField(max_length=255, verbose_name="APP NAME", default='')
    app_img = models.CharField(max_length=255, verbose_name="APP 图片", default='')
    app_description = models.TextField(verbose_name="APP 说明", default='')
    app_company_website = models.CharField(max_length=255, verbose_name="APP 公司网站", default='')
    compatibility = models.CharField(max_length=255, verbose_name="兼容性", default='')
    updated = models.CharField(max_length=255, verbose_name="更新", default='')
    version = models.CharField(max_length=255, verbose_name="版本", default='')
    size = models.CharField(max_length=255, verbose_name="大小", default='')
    only_32_bit = models.CharField(max_length=255, verbose_name="仅限32位", default='')
    language = models.TextField(verbose_name="语言", default='')
    seller = models.CharField(max_length=255, verbose_name="出版商", default='')
    headquarter_country_region = models.CharField(max_length=255, verbose_name="总部所在国家/地区", default='')
    rating = models.CharField(max_length=255, verbose_name="评级", default='')
    family_sharing = models.CharField(max_length=255, verbose_name="家庭共享", default='')
    requirements = models.CharField(max_length=255, verbose_name="要求", default='')
    bundle_ID = models.CharField(max_length=255, verbose_name="套餐 ID", default='')
    game_center = models.CharField(max_length=255, verbose_name="游戏中心", default='')
    supports_apple_watch = models.CharField(max_length=255, verbose_name="支持Apple Watch", default='')
    supports_iMessage = models.CharField(max_length=255, verbose_name="支持iMessage", default='')

    update_time = models.CharField(max_length=255, verbose_name="本条数据更新时间", default='')

    def __str__(self):
        return self.id


class Hentai(models.Model):
    name = models.CharField(max_length=255, verbose_name="名称", default='')
    author = models.CharField(max_length=255, verbose_name="作者")
    posted = models.CharField(default="", max_length=255, verbose_name="更新时间", )
    parent = models.CharField(default="", max_length=255, )
    language = models.CharField(default="", max_length=255, verbose_name="语言", )
    file_size = models.CharField(default="", max_length=255, verbose_name="文件大小", )
    length = models.CharField(default="", max_length=255, verbose_name="长度", )
    classification = models.CharField(default="", max_length=255, verbose_name="分类", )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ["name", "author", ]


class Hentai_img(models.Model):
    name = models.ForeignKey(Hentai, verbose_name="名称")
    image = models.CharField(max_length=255, verbose_name="图片", unique=True)
    sort = models.IntegerField(verbose_name="排序", )

    def __str__(self):
        return self.image

    class Meta:
        unique_together = ["name", 'sort']


class Comics(models.Model):
    title = models.CharField(max_length=255, unique=True)
    cover_image = models.CharField(max_length=255, unique=True, verbose_name="封面图片")

    def __str__(self):
        return self.title


class Comics_img(models.Model):
    title = models.ForeignKey(Comics)
    image = models.CharField(max_length=255, verbose_name="图片", unique=True)
    sort = models.IntegerField(verbose_name="排序", )

    def __str__(self):
        return self.image

    class Meta:
        unique_together = ["title", 'sort']


class Hentai2read(models.Model):
    name = models.CharField(max_length=255, verbose_name="名称", unique=True)
    cover_image = models.CharField(max_length=255, verbose_name="封面", default='')
    Parody = models.CharField(max_length=255, default='')
    Ranking = models.CharField(max_length=255, default='')
    Status = models.CharField(max_length=255, default='')
    Release_Year = models.CharField(max_length=255, default='')
    View = models.CharField(max_length=255, default='')
    Author = models.CharField(max_length=255, default='')
    Artist = models.CharField(max_length=255, default='')
    Category = models.CharField(max_length=255, default='')
    Content = models.CharField(max_length=255, default='')
    Character = models.CharField(max_length=255, default='')
    Language = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.name


class Hentai2read_chapter(models.Model):
    name = models.ForeignKey(Hentai2read, verbose_name="名称", )
    chapter_name = models.CharField(max_length=255, verbose_name="章节名")
    chapter_index = models.FloatField(verbose_name='章节索引', default=0)
    page_num = models.IntegerField(verbose_name="图片数量", null=True)

    class Meta:
        unique_together = ["name", 'chapter_index']


class Hentai2read_img(models.Model):
    chapter_name = models.ForeignKey(Hentai2read_chapter, verbose_name="章节名", )
    img_index = models.IntegerField(verbose_name='图片索引')
    image = models.CharField(max_length=255, verbose_name="图片", )

    class Meta:
        unique_together = ["chapter_name", 'img_index']


class Hentai2read_flag(models.Model):
    name = models.CharField(max_length=255, verbose_name="名称", unique=True)


class Hentai2read_chapter_flag(models.Model):
    chapter_name = models.CharField(max_length=255, verbose_name="名称", unique=True)


class Hentai_flag(models.Model):
    name = models.CharField(max_length=255, verbose_name="名称", unique=True)


class Hentai_chapter_flag(models.Model):
    chapter_name = models.CharField(max_length=255, verbose_name="名称", unique=True)
