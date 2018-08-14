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