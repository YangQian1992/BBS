from django import template
from blog01 import models


register = template.Library()

@register.inclusion_tag(filename='daohang.html')
def daohang(username):
    user_obj = models.UserInfo.objects.filter(username= username).first()
    blog = user_obj.blog
    return {
        "user_obj":user_obj,
        "blog":blog
    }