from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from blog01 import models


def register(request):
    '''
    用 form 组件 和 auth 认证 来写注册函数
    :param request: 接收对象
    :return:response对象
    '''
    form_obj = Register_Form()
    if request.method == 'POST':
        print(request.POST)
        form_obj = Register_Form(request.POST)
        if form_obj.is_valid():
            form_data = form_obj.cleaned_data
            print(form_data)
            form_data.pop('re_password')
            print(form_data)
            # User.objects.create_user(**form_data)
            models.UserInfo.objects.create_user(**form_data)
            return HttpResponse('注册成功！')
    return render(request, 'register.html', {'form_obj': form_obj})


################ CBV 版的注册02 版本 #######################
from django import views
from blog01.forms import Register_Form
from django.contrib import auth


class Register_new(views.View):

    def get(self, request):
        form_obj = Register_Form()  # form组件写html
        return render(request, 'register_new.html', {'form_obj': form_obj})

    def post(self, request):
        print('request.POST-->', request.POST)
        res = {"code": 0}
        # 先进行 验证码的校验
        v_code = request.POST.get('v_code', '')
        # 验证码正确后，使用form组件进行校验
        if v_code.upper() == request.session.get('v_code'):
            print('验证码填写正确！')
            form_obj = Register_Form(request.POST)  # form组件做校验
            print('form_obj---->', form_obj)
            # 用户输入的数据有效
            if form_obj.is_valid():
                # 1、注册用户
                form_cleaned_data = form_obj.cleaned_data
                print('form_cleaned_data----->', form_cleaned_data)
                # 注意移除不需要的re_password
                form_cleaned_data.pop('re_password')
                print(form_cleaned_data)

                # 获取到用户上传的头像文件
                avatar_file = request.FILES.get('avatar')

                # 利用auth 认证去校验注册的用户是否在数据库中已存在
                user = auth.authenticate(username=form_cleaned_data['username'], password=form_cleaned_data['password'])
                if user:
                    #  数据库中有此用户则不需要注册
                    res["code"] = 3
                    res["msg"] = "用户名已占用！"
                else:
                    #  数据库中没有此用户则需要注册
                    models.UserInfo.objects.create_user(**form_cleaned_data, avatar=avatar_file)
                    #  注册成功之后跳转到登录页面
                    res["msg"] = "/login/"
            # 用户填写的数据不符合要求
            else:
                res["code"] = 1
                # 所有字段的错误信息是通过以下form组件的命令获取
                res["msg"] = form_obj.errors
        # 验证码验证失败
        else:
            res["code"] = 2
            res["msg"] = "验证码错误！"
        return JsonResponse(res)


# def login(request):
#     '''
#     用 auth 认证 来写登录函数
#     :param request: 接收对象
#     :return: response对象
#     '''
#     error_msg = ''
#     if request.method == 'POST':
#         username = request.POST.get("user")
#         password = request.POST.get("pwd")
#         # 去数据库校验用户名和密码是否正确
#         user = auth.authenticate(request, username=username, password=password)
#         if user:
#             # 表示用户名密码正确
#             # 让当前用户登录,给cookie和session写入数据
#             auth.login(request,user)
#             return redirect('/index/')
#         else:
#             error_msg = '用户名密码不正确'
#     return  render(request,'login.html',{'error_msg':error_msg})

@login_required
def index(request):
    '''
    登录之后进入主页的函数
    :param request: 接收对象
    :return: response对象
    '''
    # request.user.is_authenticated()   判断当前的request.user是否经过认证，经过认证返回True,没有经过认证返回False
    print(request.user, request.user.is_authenticated())
    return render(request, 'index.html')


###################  bbs博客首页   ################
from utils.mypage import MyPage


class Index(views.View):

    def get(self, request):
        article_list = models.Article.objects.all()
        print('article_list---->', article_list)
        # 分页
        data_amount = article_list.count()  # 文章总数量
        page_num = request.GET.get('page', 1)  # 通过url 的get请求获取到当前页面
        page_obj = MyPage(page_num, data_amount, per_page_data=2, url_prefix=request.path_info[1:-1])
        # 按照分页的设置对总数据进行切片
        data = article_list[page_obj.start:page_obj.end]
        page_html = page_obj.ret_html()
        return render(request, 'index_new.html', {"article_list": data, "page_html": page_html})

    def post(self, request):
        res = {"code": 0}
        return JsonResponse(res)


def logout(request):
    '''
    用auth 认证 来写注销用户的函数
    :param request: 接收对象
    :return: response对象
    '''
    # 将当前请求的sessoin数据删除
    auth.logout(request)
    return redirect('/login/')


@login_required
def set_password(request):
    '''
    登录之后修改密码：
        1、登录的用户才能修改密码
        2、修改密码之前先校验原密码是否正确
    :param request:接收对象
    :return:response对象
    '''
    user = request.user
    err_msg = ''
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')  # 旧密码
        new_password = request.POST.get('new_password', '')  # 新密码
        repeat_password = request.POST.get('repeat_password', '')  # 确认密码
        # 检查旧密码是否正确
        if user.check_password(old_password):
            if not new_password:
                err_msg = '新密码不能为空！'
            elif new_password != repeat_password:
                err_msg = '两次密码不一致！'
            else:
                user.set_password(new_password)
                user.save()
                return redirect('/login/')
        else:
            err_msg = '原密码输入错误！'
    return render(request, 'set_password.html', {'err_msg': err_msg})


# ################ CBV 版的登录 #######################
# from django import views
# from django.http import JsonResponse
# from blog01.forms02 import Login_Form
#
#
# class Login(views.View):
#
#     def get(self,request):
#         form_obj = Login_Form()
#         return render(request,'login_ajax.html',{'form_obj':form_obj})
#
#     def post(self,request):
#         res = {"code":0}
#         print(request.POST)
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         # 去数据库校验用户名和密码是否正确
#         user = auth.authenticate(request, username=username, password=password)
#         if user:
#             # 表示用户名密码正确
#             # 让当前用户登录,给cookie和session写入数据
#             auth.login(request, user)
#         else:
#             res["code"] = 1
#             res["msg"] = '用户名或密码不正确！'
#         return JsonResponse(res)

################ 登录验证码 版本1 #######################
# def v_code(request):
# # 随机生成图片
#     from PIL import Image
#     import random
#     # 生成随机颜色的方法
#     def random_color():
#         return random.randint(0,255),random.randint(0,255),random.randint(0,255)
#     # 生成图片对象
#     image_obj = Image.new(
#         'RGB',  # 生成图片的模式
#         (250,35), # 生成图片的大小
#         random_color()  # 随机生成图片的颜色
#     )
# # 直接将生成的图片保存在内存中
#     from io import BytesIO
#     f = BytesIO()
#     image_obj.save(f,'png')
#     # 从内存中读取图片数据
#     data = f.getvalue()
#     return HttpResponse(data,content_type='image/png')

################ 登录验证码 版本2 #######################
# def v_code(request):
# # 随机生成图片
#     from PIL import Image
#     import random
#     # 生成随机颜色的方法
#     def random_color():
#         return random.randint(0,255),random.randint(0,255),random.randint(0,255)
#     # 生成图片对象
#     image_obj = Image.new(
#         'RGB',  # 生成图片的模式
#         (250,35), # 生成图片的大小
#         random_color()  # 随机生成图片的颜色
#     )
#
# # 生成一个准备写字的画笔
#     from PIL import ImageDraw , ImageFont
#     draw_obj = ImageDraw.Draw(image_obj)    # 在哪里写
#     font_obj = ImageFont.truetype('static/fonts/kumo.ttf',size=28)   # 加载本地的字体文件
#
# # 生成随机验证码
#     tmp = []
#     for i in range(5):
#         n = str(random.randint(0,9))
#         l = chr(random.randint(65,90))
#         u = chr(random.randint(97,122))
#         r = random.choice([n,l,u])
#         tmp.append(r)
#         # 每一次取到要写的东西之后，往图片上写
#         draw_obj.text(
#             (i * 45 + 25 , 0), # 坐标---->（x,y）
#             r,  # 内容
#             fill=random_color(), # 颜色
#             fonts=font_obj # 字体
#         )
#
# # 得到最终的验证码
#     v_code = ''.join(tmp)
#
# # 由于设置为全局变量，多个浏览器没办法区别验证码，故保存为全局变量是万万不可的！
# # 将盖茨请求生成的验证码保存在该请求对应的session数据中
#     request.session["v_code"] = v_code.upper()
#
#
# # 直接将生成的图片保存在内存中
#     from io import BytesIO
#     f = BytesIO()
#     image_obj.save(f,'png')
#     # 从内存中读取图片数据
#     data = f.getvalue()
#     return HttpResponse(data,content_type='image/png')


################ 登录验证码 版本3 #######################
# def v_code(request):
# # 随机生成图片
#     from PIL import Image
#     import random
#     # 生成随机颜色的方法
#     def random_color():
#         return random.randint(0,255),random.randint(0,255),random.randint(0,255)
#     # 生成图片对象
#     image_obj = Image.new(
#         'RGB',  # 生成图片的模式
#         (250,35), # 生成图片的大小
#         random_color()  # 随机生成图片的颜色
#     )
#
# # 生成一个准备写字的画笔
#     from PIL import ImageDraw , ImageFont
#     draw_obj = ImageDraw.Draw(image_obj)    # 在哪里写
#     font_obj = ImageFont.truetype('static/fonts/kumo.ttf',size=28)   # 加载本地的字体文件
#
# # 生成随机验证码
#     tmp = []
#     for i in range(5):
#         n = str(random.randint(0,9))
#         l = chr(random.randint(65,90))
#         u = chr(random.randint(97,122))
#         r = random.choice([n,l,u])
#         tmp.append(r)
#         # 每一次取到要写的东西之后，往图片上写
#         draw_obj.text(
#             (i * 45 + 25 , 0), # 坐标---->（x,y）
#             r,  # 内容
#             fill=random_color(), # 颜色
#             fonts=font_obj # 字体
#         )
#
# # 加干扰线
#     width = 250 # 图片宽度(防止越界)
#     height = 35 # 图片高度(防止越界)
#     for i in range(5):
#         x1 = random.randint(0,width)
#         x2 = random.randint(0,width)
#         y1 = random.randint(0,height)
#         y2 = random.randint(0,height)
#         draw_obj.line(
#             (x1,y1,x2,y2),
#             fill=random_color(), # 随机生成颜色
#         )
#
# # 得到最终的验证码
#     v_code = ''.join(tmp)
#
# # 由于设置为全局变量，多个浏览器没办法区别验证码，故保存为全局变量是万万不可的！
# # 将盖茨请求生成的验证码保存在该请求对应的session数据中
#     request.session["v_code"] = v_code.upper()
#
#
# # 直接将生成的图片保存在内存中
#     from io import BytesIO
#     f = BytesIO()
#     image_obj.save(f,'png')
#     # 从内存中读取图片数据
#     data = f.getvalue()
#     return HttpResponse(data,content_type='image/png')


################ 登录验证码 版本4 #######################
# 返回响应的时候告诉浏览器不要缓存
from django.views.decorators.cache import never_cache


@never_cache
def v_code(request):
    # 随机生成图片
    from PIL import Image
    import random
    # 生成随机颜色的方法
    def random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 生成图片对象
    image_obj = Image.new(
        'RGB',  # 生成图片的模式
        (240, 30),  # 生成图片的大小
        random_color()  # 随机生成图片的颜色
    )

    # 生成一个准备写字的画笔
    from PIL import ImageDraw, ImageFont
    draw_obj = ImageDraw.Draw(image_obj)  # 在哪里写
    font_obj = ImageFont.truetype('static/fonts/kumo.ttf', size=28)  # 加载本地的字体文件

    # 生成随机验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0, 9))
        l = chr(random.randint(65, 90))
        u = chr(random.randint(97, 122))
        r = random.choice([n, l, u])
        tmp.append(r)
        # 每一次取到要写的东西之后，往图片上写
        draw_obj.text(
            (i * 45 + 25, 0),  # 坐标---->（x,y）
            r,  # 内容
            fill=random_color(),  # 颜色
            font=font_obj  # 字体
        )

    # 加干扰线
    width = 250  # 图片宽度(防止越界)
    height = 35  # 图片高度(防止越界)
    for i in range(5):
        x1 = random.randint(0, width)
        x2 = random.randint(0, width)
        y1 = random.randint(0, height)
        y2 = random.randint(0, height)
        draw_obj.line(
            (x1, y1, x2, y2),
            fill=random_color(),  # 随机生成颜色
        )

    # 加干扰点
    width = 250  # 图片宽度(防止越界)
    height = 35  # 图片高度(防止越界)
    for i in range(5):
        draw_obj.point(
            [random.randint(0, width), random.randint(0, height)],
            fill=random_color(),
        )
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw_obj.arc(
            (x, y, x + 4, y + 4),
            0,
            90,
            fill=random_color()
        )

    # 得到最终的验证码
    v_code = ''.join(tmp)

    # 由于设置为全局变量，多个浏览器没办法区别验证码，故保存为全局变量是万万不可的！
    # 将get请求生成的验证码保存在该请求对应的session数据中
    request.session["v_code"] = v_code.upper()

    # 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f, 'png')
    # 从内存中读取图片数据
    data = f.getvalue()
    return HttpResponse(data, content_type='image/png')


################ CBV 版的登录02版本 #######################
from django import views
from django.http import JsonResponse
from blog01.forms02 import Login_Form


class Login(views.View):

    def get(self, request):
        form_obj = Login_Form()
        return render(request, 'login_ajax.html', {'form_obj': form_obj})


    def post(self, request):
        res = {"code": 0}
        print(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        v_code = request.POST.get('v_code')
        print(v_code)
        # 先判断验证码是否正确
        if v_code.upper() != request.session.get('v_code', ''):
            print(111)
            res["code"] = 1
            res["msg"] = "验证码错误！"
        else:
            print(222)
            # 去数据库校验用户名和密码是否正确
            user = auth.authenticate(request, username=username, password=password)
            if user:
                # 表示用户名密码正确
                # 让当前用户登录,给cookie 和 session 写入数据
                auth.login(request, user)
            else:
                # 表示用户名或密码不正确
                res["code"] = 1
                res["msg"] = '用户名或密码不正确！'
        return JsonResponse(res)


###########################  滑动验证码  ##############################
from utils.geetest import GeetestLib

# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 滑动验证码版本的登录函数
def login_huadong(request):
    res = {"code": 0}
    if request.method == "POST":
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 滑动验证码校验通过
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(username=username, password=password)
            if user:
                # 用户名和密码正确
                auth.login(request, user)
            else:
                # 用户名或者密码不正确
                res["code"] = 1
                res["msg"] = "用户名或者密码不正确！"
        else:
            # 滑动验证码校验失败
            res["code"] = 2
            res["msg"] = "验证码错误！"
        return JsonResponse(res)
    form_obj = Login_Form()
    return render(request, 'login_ajax_huadong.html', {"form_obj": form_obj})


######################## BBS项目的个人博客站点 版本01 #######################################
class Blog(views.View):

    def get(self, request, username):
        # 从数据库UserInfo表中找到此用户
        user_objs_list = models.UserInfo.objects.filter(username=username)
        print('user_objs_list---->', user_objs_list)
        user_obj = user_objs_list.first()
        article_category = user_obj.blog.tag_set.all()
        print('article_category---->', article_category)
        article_tag = user_obj.blog.tag_set.all()
        print('article_tag---->', article_tag)
        article_obj = user_obj.article_set.all()
        print('article_obj--->', article_obj)

        # 分页
        data_amount = article_obj.count()  # 文章总数量
        page_num = request.GET.get('page', 1)  # 通过url 的get请求获取到当前页面
        page_obj = MyPage(page_num, data_amount, per_page_data=1, url_prefix='blog')
        # 按照分页的设置对总数据进行切片
        data = article_obj[page_obj.start:page_obj.end]
        page_html = page_obj.ret_html()

        return render(request, 'blog.html', {"user_obj": user_obj, "data": data, "page_html": page_html, })


###################################### BBS项目的个人博客站点 版本03 #######################################
from django.shortcuts import get_object_or_404
from django.db.models import Count


def blog_new(request, username, *args):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    article_list = models.Article.objects.filter(user=user_obj)
    # 对当前用户博客站点所对应的所有文章按照年月的格式化时间来分组，来进行日期归档和显示文章数量
    archive_list = article_list.extra(
        select={
            "y_m": "DATE_FORMAT(create_time,'%%Y-%%m')"
        }
    ).values('y_m').annotate(article_count=Count('id')).values('y_m', 'article_count')
    print('archive_list--->', archive_list)

    # 左侧侧边栏点击文章分类、文章标签、日期归档跳转到各分类中的文章页面
    print('args--->', args)
    # 判断args 是否为空，若是空，则说明没有点击左侧侧边栏上的各分类；若不为空，则说明进入各分类中的文章页面
    if args:
        if args[0] == 'category':
            # 表示按照文章分类查询
            article_list = article_list.filter(category__title=args[1])
        elif args[0] == 'tag':
            # 表示按照文章的标签查询
            article_list = article_list.filter(tags__title=args[1])
        else:
            # 表示按照文章的日期归档查询（注意：在settings.py将时区改为False）
            # 先将args[1]的值切割，注意用户可能在-左右乱写一通，故需要异常处理
            try:
                year, month = args[1].split('-')
                article_list = article_list.filter(create_time__year=year, create_time__month=month)
            except Exception as e:
                article_list = []

    # 分页
    data_amount = article_list.all().count()  # 文章总数量
    page_num = request.GET.get('page', 1)  # 通过url 的get请求获取到当前页面
    page_obj = MyPage(page_num, data_amount, per_page_data=2, url_prefix=request.path_info[1:-1])
    # 按照分页的设置对总数据进行切片
    data = article_list[page_obj.start:page_obj.end]
    page_html = page_obj.ret_html()

    return render(request, 'blog_new.html',
                  {"username": username,
                   "blog": blog,
                   "article_list": data,
                   "page_html": page_html,
                   })


###### BBS项目的文章详情 版本01  ###########
def article(request, username, id):
    user_obj = get_object_or_404(models.UserInfo, username=username)
    blog = user_obj.blog
    article = models.Article.objects.filter(user=user_obj, id=id).first()
    comment_list = models.Comment.objects.filter(article=article)

    return render(request, 'article.html',
                  {
                      "username": username,
                      "article": article,
                      "blog": blog,
                      "comment_list":comment_list,
                  })


################ 点赞或踩灭函数 ######################
from django.db import transaction
from django.db.models import F


def upOrdown(request):
    if request.method == 'POST':
        res = {"code": 0}
        print('request.POST--->', request.POST)  # <QueryDict: {'userId': ['5'], 'articleId': ['3'], 'isUp': ['true']}>
        user_id = request.POST.get('userId')
        article_id = request.POST.get('articleId')

        is_up = request.POST.get('isUp')
        print("is_up--->{},type(is_up)--->{}".format(is_up, type(is_up)))  # is_up--->true,type(is_up)---><class 'str'>
        # 由于request.POST获取到的数据都是字符串形式，后续操作需要用到is_up是布尔值形式的，故需要转化成布尔值
        is_up = True if is_up.upper() == 'TRUE' else False

        # 5. 不能给自己的文章点赞
        # 首先获取到数据库中是否有给自己文章点赞或踩灭的记录
        article_obj = models.Article.objects.filter(id=article_id, user_id=user_id)
        print('article_obj--->', article_obj)
        # 如果有给自己文章点赞或踩灭的
        if article_obj:
            print(111)
            res["code"] = 1
            res["msg"] = "不能给自己的文章点赞！" if is_up else "不能给自己的文章踩灭！"
        else:
            # 3. 同一个人只能给同一篇文章点赞一次 且 4. 点赞或踩灭只能二选一
            # 3.1 首先判断一下当前这个人和这篇文章 在点赞表中 有没有记录(对象)
            is_exist = models.ArtcleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
            # 3.2.a 如果有记录，就直接返回错误提示信息
            if is_exist:
                print(222)
                res["code"] = 2
                # 3.3.a 表示已经点赞过或踩灭过（点赞或踩灭只能二选一）
                res["msg"] = "已经点赞过！" if is_exist.updown else "已经踩灭过！"
            else:
                print(333)
                # 3.2.b 如果没有记录，就真正点赞或踩灭（注意：事务操作）
                with transaction.atomic():
                    # 3.3.b 先创建点赞或踩灭的记录(往数据库中添加记录)
                    models.ArtcleUpDown.objects.create(user_id=user_id, article_id=article_id, updown=is_up)
                    # 3.4.b 再更新文章表中的点赞数和踩灭数
                    if is_up:
                        # 表示点赞，更新文章表中的点赞数
                        models.Article.objects.filter(id=article_id).update(up_count=F('up_count') + 1)
                    else:
                        # 表示踩灭，更新文章表中的踩灭数
                        models.Article.objects.filter(id=article_id).update(down_count=F('down_count') + 1)

                    # 3.5.b 往点赞表中成功添加记录 并 成功更新文章表中的点赞数和踩灭数， 然后进行添加提示信息
                res["msg"] = "点赞成功！" if is_up else "踩灭成功！"

        return JsonResponse(res)

################ 评论函数 ################
def comment(request):
    if request.method == "POST":
        res = {"code":0}
        # 获取父评论的id
        parent_id = request.POST.get('parent_id')
        # 获取用户的id
        user_id = request.POST.get('user_id')
        # 获取文章的id
        article_id = request.POST.get('article_id')
        # 获取评论的内容
        content = request.POST.get('content')

        # 向数据库中创建评论内容
        with transaction.atomic():
            # 1. 先去创建新评论
            if parent_id:
                # 添加子评论
                comment_obj = models.Comment.objects.create(
                    content= content,
                    user_id=user_id,
                    article_id=article_id,
                    parent_comment_id=parent_id,
                )
            else:
                # 添加父评论
                comment_obj = models.Comment.objects.create(
                    content=content,
                    user_id=user_id,
                    article_id=article_id,
                )

            # 2. 去更新该文章的评论数
            models.Article.objects.filter(id=article_id).update(comment_count=F('comment_count') + 1)

            res["data"] = {
                "id":comment_obj.id,
                "content":comment_obj.content,
                "create_time":comment_obj.create_time,
                "username":comment_obj.user.username,
            }

        return JsonResponse(res)