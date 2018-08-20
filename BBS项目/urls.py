"""BBS项目 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from blog01 import views
from django.views.static import serve
from django.conf import settings
from blog01 import urls as blog01_url

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    ############ 注册01 ############
    url(r'^register/$', views.register),
    ############ 注册02 ############
    url(r'^register_new/$', views.Register_new.as_view()),
    ############ 登录 ############
    url(r'^login/$', views.Login.as_view()),
    ############ 简单的主页 ############
    url(r'^index/$', views.index),
    ############ 修改密码 ############
    url(r'^set_password/$', views.set_password),
    ############ 注销 ############
    url(r'^logout/$', views.logout),
    ############ 登录验证码 ############
    url(r'^v_code/$', views.v_code),
    ###### 给用户上传的文件配置一个处理的路由 #######
    url(r'^media/(?P<path>.*)',serve,{"document_root":settings.MEDIA_ROOT}),
    ############ 滑动验证码版本的登录 ############
    url(r'^pcgetcaptcha/$',views.pcgetcaptcha),
    url(r'^login_huadong/$',views.login_huadong),
    ############  BBS博客的主页  ############
    url(r'^index_new/$', views.Index.as_view()),
    ############  BBS项目的个人博客站点  ############
    url(r'^blog/',include(blog01_url)),
    ############  点赞或者踩灭  ############
    url(r'^upOrdown/$',views.upOrdown),
    ############  评论  ############
    url(r'^comment/$',views.comment),

    url(r'^$',views.Index.as_view()),
]


from django.conf import settings
from django.conf.urls import include, url

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns