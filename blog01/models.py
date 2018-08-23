from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    '''
    用户信息表
    '''
    # nickname = models.CharField(max_length=32,verbose_name='昵称')
    # phone = models.CharField(max_length=11,unique=True,null=True,verbose_name='手机号')
    phone = models.CharField(max_length=11,unique=True,null=True)   # 手机号
    # avatar = models.FileField(upload_to='static/avatar',default='static/avatar/default.png')    # 头像
    avatar = models.FileField(upload_to='avatar/',default='static/imgs/default.png')    # 头像字段的正确写法

    # blog_site = models.OneToOneField(to='BlogSite',null=True,to_field='id',on_delete=models.CASCADE)
    blog = models.OneToOneField(to='Blog',null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name


class Blog(models.Model):
    '''
    博客信息表
    '''
    # title = models.CharField(max_length=32,verbose_name='个人博客标题')
    # theme = models.CharField(max_length=255,verbose_name='个人博客的主题')
    title = models.CharField(max_length=64) # 个人博客标题
    theme = models.CharField(max_length=255) # 博客主题

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '博客'
        verbose_name_plural = verbose_name


class Category(models.Model):
    '''
    博客文章分类表
    '''
    # title = models.CharField(max_length=32,verbose_name='文章分类的标题')
    # user = models.ForeignKey(to='UserInfo',to_field='id',on_delete=models.CASCADE,null=True,)
    title = models.CharField(max_length=32) # 分类标题
    blog = models.ForeignKey(to='Blog',on_delete=models.CASCADE) # 外键关联博客，一个博客站点可以有多个分类

    def __str__(self):
        return '{}-{}'.format(self.blog.title,self.title)

    class Meta:
        verbose_name = '文章分类'
        verbose_name_plural = verbose_name


class Tag(models.Model):
    '''
    文章标签表
    '''
    # title = models.CharField(max_length=32,verbose_name='文章的标题')
    # user =  models.ForeignKey(to='UserInfo',to_field='id',on_delete=models.CASCADE,null=True,)
    title = models.CharField(max_length=32) # 标签名
    blog =  models.ForeignKey(to='Blog',on_delete=models.CASCADE)    # 外键关联博客，一个博客站点可以有多个标签

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name


class Article(models.Model):
    '''
    文章表
    '''
    # content = models.TextField(verbose_name='文章内容')
    # title = models.CharField(max_length=32,verbose_name='文章标题')
    # create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    # comment_count = models.IntegerField(default=0,verbose_name='评论数量')
    # up_count = models.IntegerField(default=0,verbose_name='点赞数量')
    # down_count = models.IntegerField(default=0,verbose_name='踩灭数量')
    title = models.CharField(max_length=50) # 文章标题
    desc = models.CharField(max_length=255) # 文章描述
    create_time = models.DateTimeField(auto_now_add=True)   # 创建时间

    # 点赞的数量
    up_count = models.IntegerField(default=0)
    # 踩灭的数量
    down_count = models.IntegerField(default=0)
    # 评论的数量
    comment_count = models.IntegerField(default=0)

    user = models.ForeignKey(to='UserInfo',on_delete=models.CASCADE) # 作者
    category = models.ForeignKey(to='Category',null=True,on_delete=models.CASCADE)   # 文章分类
    tags = models.ManyToManyField(
        to='Tag',
        through='Artcle_Tag',
        through_fields=('article','tag'),
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name


class ArticleDetail(models.Model):
    '''
    文章详情表
    '''
    content = models.TextField() # 文章内容
    article = models.OneToOneField(to='Article',on_delete=models.CASCADE)

    class Meta:
        verbose_name = '文章详情'
        verbose_name_plural = verbose_name


class Artcle_Tag(models.Model):
    '''
    文章和标签的多对多关系表
    '''
    article = models.ForeignKey(to='Article',on_delete=models.CASCADE)
    tag = models.ForeignKey(to='Tag',on_delete=models.CASCADE)

    def __str__(self):
        return '{}-{}'.format(self.article,self.tag)

    class Meta:
        unique_together = (('article','tag')),
        verbose_name = '文章-标签'
        verbose_name_plural = verbose_name


class Comment(models.Model):
    '''
    文章评论表
    '''
    # user = models.ForeignKey(to='UserInfo',to_field='id',on_delete=models.CASCADE,null=True,)
    # article = models.ForeignKey(to='Article',to_field='id',on_delete=models.CASCADE,null=True)
    # parent_comment = models.ForeignKey(to='Comment',on_delete=models.CASCADE,null=True,)
    content = models.CharField(max_length=255) # 评论内容
    create_time = models.DateTimeField(auto_now_add=True) # 评论时间
    article = models.ForeignKey(to='Article',on_delete=models.CASCADE) # 外键关联文章，一篇文章可以有多条评论
    user = models.ForeignKey(to='UserInfo',on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self',null=True,blank=True,on_delete=models.CASCADE)   # 父评论，自己关联自己

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name


class ArtcleUpDown(models.Model):
    '''
    文章点赞表
    '''
    article = models.ForeignKey(to='Article',null=True,on_delete=models.CASCADE)
    user = models.ForeignKey(to='UserInfo',null=True,on_delete=models.CASCADE)
    updown = models.BooleanField(default=True)  # 点赞还是踩灭

    def __str__(self):
        return  '{}-{}'.format(self.user_id,self.article_id)

    class Meta:
        unique_together = (
            ('user','article')      # 同一个人只能给一篇文章点赞或踩灭一次
        ),
        verbose_name = '点赞',
        verbose_name_plural = verbose_name




