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


################ CBV 版的注册02 版本 #######################
from django import views
from blog01.forms import Register_Form
from django.contrib import auth


class Register_new(views.View):

    def get(self,request):
        form_obj = Register_Form()  # form组件写html
        return render(request,'register_new.html',{'form_obj':form_obj})

    def post(self,request):
        print(222)
        print(request.POST)
        res = {"code":0}
        # 先进行 验证码的校验
        v_code = request.POST.get('v_code','')
        # 验证码正确后，使用form组件进行校验
        if v_code.upper() == request.session.get('v_code'):
            print('验证码填写正确！')
            form_obj = Register_Form(request.POST)  # form组件做校验
            print('form_obj---->',form_obj)
            # 用户输入的数据有效
            if form_obj.is_valid():
                # 1、注册用户
                form_cleaned_data = form_obj.cleaned_data
                print('form_cleaned_data----->',form_cleaned_data)
                # 注意移除不需要的re_password
                form_cleaned_data.pop('re_password')
                print(form_cleaned_data)

                # 获取到用户上传的头像文件
                avatar_file = request.FILES.get('avatar')

                # 利用auth 认证去校验注册的用户是否在数据库中已存在
                user = auth.authenticate(username=form_cleaned_data['username'],password=form_cleaned_data['password'])
                if user:
                    #  数据库中有此用户则不需要注册
                    res["code"] = 3
                    res["msg"] = "用户名已占用！"
                else:
                    #  数据库中没有此用户则需要注册
                    models.UserInfo.objects.create_user(**form_cleaned_data , avatar = avatar_file)
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


def login(request):
    '''
    用 auth 认证 来写登录函数
    :param request: 接收对象
    :return: response对象
    '''
    error_msg = ''
    if request.method == 'POST':
        username = request.POST.get("user")
        password = request.POST.get("pwd")
        # 去数据库校验用户名和密码是否正确
        user = auth.authenticate(request, username=username, password=password)
        if user:
            # 表示用户名密码正确
            # 让当前用户登录,给cookie和session写入数据
            auth.login(request,user)
            return redirect('/index/')
        else:
            error_msg = '用户名密码不正确'
    return  render(request,'login.html',{'error_msg':error_msg})

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



# ################ CBV 版的登录 #######################
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
            res["msg"] = '用户名或密码不正确！'
        return JsonResponse(res)

################ 登录验证码 版本1 #######################
def v_code(request):
# 随机生成图片
    from PIL import Image
    import random
    # 生成随机颜色的方法
    def random_color():
        return random.randint(0,255),random.randint(0,255),random.randint(0,255)
    # 生成图片对象
    image_obj = Image.new(
        'RGB',  # 生成图片的模式
        (250,35), # 生成图片的大小
        random_color()  # 随机生成图片的颜色
    )
# 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f,'png')
    # 从内存中读取图片数据
    data = f.getvalue()
    return HttpResponse(data,content_type='image/png')

################ 登录验证码 版本2 #######################
def v_code(request):
# 随机生成图片
    from PIL import Image
    import random
    # 生成随机颜色的方法
    def random_color():
        return random.randint(0,255),random.randint(0,255),random.randint(0,255)
    # 生成图片对象
    image_obj = Image.new(
        'RGB',  # 生成图片的模式
        (250,35), # 生成图片的大小
        random_color()  # 随机生成图片的颜色
    )

# 生成一个准备写字的画笔
    from PIL import ImageDraw , ImageFont
    draw_obj = ImageDraw.Draw(image_obj)    # 在哪里写
    font_obj = ImageFont.truetype('static/fonts/kumo.ttf',size=28)   # 加载本地的字体文件

# 生成随机验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0,9))
        l = chr(random.randint(65,90))
        u = chr(random.randint(97,122))
        r = random.choice([n,l,u])
        tmp.append(r)
        # 每一次取到要写的东西之后，往图片上写
        draw_obj.text(
            (i * 45 + 25 , 0), # 坐标---->（x,y）
            r,  # 内容
            fill=random_color(), # 颜色
            font=font_obj # 字体
        )

# 得到最终的验证码
    v_code = ''.join(tmp)

# 由于设置为全局变量，多个浏览器没办法区别验证码，故保存为全局变量是万万不可的！
# 将盖茨请求生成的验证码保存在该请求对应的session数据中
    request.session["v_code"] = v_code.upper()


# 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f,'png')
    # 从内存中读取图片数据
    data = f.getvalue()
    return HttpResponse(data,content_type='image/png')


################ 登录验证码 版本3 #######################
def v_code(request):
# 随机生成图片
    from PIL import Image
    import random
    # 生成随机颜色的方法
    def random_color():
        return random.randint(0,255),random.randint(0,255),random.randint(0,255)
    # 生成图片对象
    image_obj = Image.new(
        'RGB',  # 生成图片的模式
        (250,35), # 生成图片的大小
        random_color()  # 随机生成图片的颜色
    )

# 生成一个准备写字的画笔
    from PIL import ImageDraw , ImageFont
    draw_obj = ImageDraw.Draw(image_obj)    # 在哪里写
    font_obj = ImageFont.truetype('static/fonts/kumo.ttf',size=28)   # 加载本地的字体文件

# 生成随机验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0,9))
        l = chr(random.randint(65,90))
        u = chr(random.randint(97,122))
        r = random.choice([n,l,u])
        tmp.append(r)
        # 每一次取到要写的东西之后，往图片上写
        draw_obj.text(
            (i * 45 + 25 , 0), # 坐标---->（x,y）
            r,  # 内容
            fill=random_color(), # 颜色
            font=font_obj # 字体
        )

# 加干扰线
    width = 250 # 图片宽度(防止越界)
    height = 35 # 图片高度(防止越界)
    for i in range(5):
        x1 = random.randint(0,width)
        x2 = random.randint(0,width)
        y1 = random.randint(0,height)
        y2 = random.randint(0,height)
        draw_obj.line(
            (x1,y1,x2,y2),
            fill=random_color(), # 随机生成颜色
        )

# 得到最终的验证码
    v_code = ''.join(tmp)

# 由于设置为全局变量，多个浏览器没办法区别验证码，故保存为全局变量是万万不可的！
# 将盖茨请求生成的验证码保存在该请求对应的session数据中
    request.session["v_code"] = v_code.upper()


# 直接将生成的图片保存在内存中
    from io import BytesIO
    f = BytesIO()
    image_obj.save(f,'png')
    # 从内存中读取图片数据
    data = f.getvalue()
    return HttpResponse(data,content_type='image/png')


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


################ CBV 版的登录02版本 #######################
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
        v_code = request.POST.get('v_code')
        print(v_code)
        # 先判断验证码是否正确
        if v_code.upper() != request.session.get('v-code',''):
            res["code"] = 1
            res["msg"] = "验证码错误！"
        else:
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



from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Register_Form(forms.Form):
    username = forms.CharField(
        label='用户名',
        min_length=2,
        max_length=30,
        error_messages={
            'min_length':'用户名不得少于2位',
            'max_length':'用户名不得超过30位',
            'required':'不能为空!'
        },
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control"},
        )
    )
    password = forms.CharField(
        label='密码',
        min_length=8,
        max_length=30,
        error_messages={
            'required':'不能为空！',
            'min_length':'密码不能少于8位',
            'max_length':'密码不能超过30位',
        },
        widget=forms.widgets.PasswordInput(
            attrs={'class':'form-control'},
            render_value=True,
        ),
    )
    re_password = forms.CharField(
        label='确认密码',
        min_length=8,
        error_messages={
            'required':'不能为空！',
            'min_length':'密码不能少于8位',
        },
        widget=forms.widgets.PasswordInput(
            attrs={'class':'form-control'},
            render_value=True,
        ),
    )
    email = forms.CharField(
        label='邮箱',
        max_length=120,
        error_messages={
            'required':'不能为空！',
            'max_length':'密码不能超过120位',
        },
        widget=forms.widgets.TextInput(
            attrs={'class':'form-control'},
        ),
        validators=[
            RegexValidator(
                r'\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}',
                '邮箱格式不正确！'
            )
        ]
    )
    phone = forms.CharField(
        label='手机号',
        max_length=11,
        error_messages={
            'required':'不能为空！',
            'max_length':'手机号不能超过11位！',
        },
        validators=[
            RegexValidator(r'^1[3|4|5|6|7|8|9]\d{9}$','手机号码格式不正确！'),
        ],
        widget=forms.widgets.TextInput(
            attrs={'class':'form-control'},
        )
    )
    def clean(self):
        # 重写父类的clean方法
        # 该clean方法，在每个字段都在自己校验自己通过之后才调用执行
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_password')

        print(pwd)
        print(re_pwd)
        if re_pwd and re_pwd == pwd:
            # 确认密码和密码相同，正常
            return self.cleaned_data
        else:
            # 确定密码和密码不同
            self.add_error('re_password','两次密码不一致')
            raise ValidationError('两次密码不一致')