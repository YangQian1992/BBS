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
from django.conf.urls import url
from django.contrib import admin
from blog01 import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    ############ 注册 ############
    url(r'^register/', views.register),
    ############ 登录 ############
    url(r'^login/', views.Login.as_view()),
    ############ 主页 ############
    url(r'^index/', views.index),
    ############ 修改密码 ############
    url(r'^set_password/', views.set_password),
    ############ 注销 ############
    url(r'^logout/', views.logout),
    ############ 登录验证码 ############
    url(r'^v_code/', views.v_code),
]
