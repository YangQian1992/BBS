import os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BBS项目.settings")
    import django
    django.setup()

    from blog01 import models

    ret = models.Article.objects.extra(
        select={
            "key":"DATE_FORMAT(create_time,'%%Y-%%m')"
        }
    ).values('key')
    print(ret)