from django.contrib import admin
from blog01 import models

# 在Django自带的admin管理后台
admin.site.register(models.UserInfo)


class ArticleConfig(admin.ModelAdmin):
    list_display = ["title","create_time"]
    search_fields = ["title"]
    list_filter = ["user","category","tags","title"]

admin.site.register(models.Article,ArticleConfig)
admin.site.register(models.Artcle_Tag)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Comment)
admin.site.register(models.Blog)
admin.site.register(models.ArtcleUpDown)
admin.site.register(models.ArticleDetail)
