from django import template
from blog01 import models
from django.db.models import Count


# 实例必须叫这个名字
register = template.Library()

@register.inclusion_tag(filename='left_menu.html')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username = username).first()

    # 查找当前用户所关联的blog对象
    blog = user_obj.blog

    # 查找当前blog对应的文章分类有哪些？
    category_list = models.Category.objects.filter(blog=blog)

    # 查找当前blog所对应的文章标签有哪些？
    tag_list = models.Tag.objects.filter(blog=blog)

    # 查找当前用户写的所有文章有哪些？
    article_list = models.Article.objects.filter(user = user_obj)

    # 按照文章的创建时间（年月）来进行分组查询并统计每组的文章数量
    archive_list = article_list.extra(
        select={
            "y_m":"DATE_FORMAT(create_time,'%%Y-%%m')"
        }
    ).values('y_m').annotate(article_count = Count('id')).values('y_m','article_count')

    return {
        "username":username,
        "category_list":category_list,
        "tag_list":tag_list,
        "archive_list":archive_list,
    }
