from django.conf.urls import url
from blog01 import views


urlpatterns = [
    # 文章管理后台 主页
    url(r'^article_manage/$', views.article_manage),

    # 文章管理后台 添加新文章
    url(r'^add_article/$',views.add_article),

    # 文章管理后台 上传图片
    url(r'^upload/$',views.upload),

    # 文章管理后台 删除文章
    url(r'^del_article/(\d+)',views.del_article),

    # 文章管理后台 编辑文章
    url(r'^edit_article/(\d+)/$', views.edit_article),

    # 个人博客站点 主页
    url(r'^(\w+)/$',views.blog_new),

    # 将个人博客站点的左侧侧边栏中的文章分类、文章标签、日期归档设置成可点击跳转到各个分类中的文章页面中(四合一)
    url(r'^(\w+)/(category|tag|archive)/(.*)/$', views.blog_new),

    # 文章详情页面
    url(r'^(\w+)/article/(\d+)/$',views.article),



]
"""
需求：将个人博客站点的左侧侧边栏中的文章分类、文章标签、日期归档设置成可点击跳转到各个分类中的文章页面中
解决方案：
    ------  第一版 ↓-----
    url(r'^(\w+)/category/(\w+)/$', views.category),
    url(r'^(\w+)/tag/(\w+)/$', views.tag),
    url(r'^(\w+)/archive/(\w+)/$', views.archive),

    ------  第二版 ↓（三合一）-----
    url(r'^(\w+)/(category|tag|archive)/(\w+)/$',views.threeinone),

    ------  第三版 ↓（四合一）-----
    
    url(r'^(\w+)/(category|tag|archive)/(.*)/$',views.blog_new),
"""
