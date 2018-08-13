from django.shortcuts import render,redirect,HttpResponse
from blog01.forms import Register_Form
from django.contrib import auth
from django.contrib.auth.decorators  import login_required
# from django.contrib.auth.models import User

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
    return render(request,'register.html',{'form_obj':form_obj})

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
    print(request.user,request.user.is_authenticated())
    return render(request,'index.html')


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
        old_password = request.POST.get('old_password','')  # 旧密码
        new_password = request.POST.get('new_password','')  # 新密码
        repeat_password = request.POST.get('repeat_password','')    # 确认密码
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
    return render(request,'set_password.html',{'err_msg':err_msg})



################ CBV 版的登录 #######################
from django import views
from django.http import JsonResponse
from blog01.forms02 import Login_Form


class Login(views.View):

    def get(self,request):
        form_obj = Login_Form()
        return render(request,'login_ajax.html',{'form_obj':form_obj})

    def post(self,request):
        res = {"code":0}
        print(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        # 去数据库校验用户名和密码是否正确
        user = auth.authenticate(request, username=username, password=password)
        if user:
            # 表示用户名密码正确
            # 让当前用户登录,给cookie和session写入数据
            auth.login(request, user)
        else:
            res["code"] = 1
            res["msg"] = '用户名密码不正确'
        return JsonResponse(res)

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
#     font_obj = ImageFont.truetype('static/font/kumo.ttf',size=28)   # 加载本地的字体文件
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
#             font=font_obj # 字体
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
#     font_obj = ImageFont.truetype('static/font/kumo.ttf',size=28)   # 加载本地的字体文件
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
#             font=font_obj # 字体
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
        (250, 35),  # 生成图片的大小
        random_color()  # 随机生成图片的颜色
    )

    # 生成一个准备写字的画笔
    from PIL import ImageDraw, ImageFont
    draw_obj = ImageDraw.Draw(image_obj)  # 在哪里写
    font_obj = ImageFont.truetype('static/font/kumo.ttf', size=28)  # 加载本地的字体文件

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
            [random.randint(0,width),random.randint(0,height)],
            fill=random_color(),
        )
        x = random.randint(0,width)
        y = random.randint(0,height)
        draw_obj.arc(
            (x,y,x+4,y+4),
            0,
            90,
            fill=random_color()
        )

    # 得到最终的验证码
    v_code = ''.join(tmp)

    # 由于设置为全局变量，多个浏览器没办法区别验证码，故保存为全局变量是万万不可的！
    # 将盖茨请求生成的验证码保存在该请求对应的session数据中
    request.session["v_code"] = v_code.upper()

    # 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f, 'png')
    # 从内存中读取图片数据
    data = f.getvalue()
    return HttpResponse(data, content_type='image/png')