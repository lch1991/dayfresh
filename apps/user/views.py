import re

from django.shortcuts import render,redirect,reverse
from django.contrib.auth import authenticate, login, logout
from celery_tasks.tasks import send_register_active_email
from django.views.generic import View
from django.conf import settings
from django.http import HttpResponse
from django_redis import get_redis_connection
from apps.common.RedisKeys import RedisKeys
from apps.common.RedisUtil import RedisUtil
from apps.user.models import User, DfAddress
from apps.user import models
from apps.common.mixin import LoginRequiredMixin

from itsdangerous import TimedJSONWebSignatureSerializer as Serialize
from itsdangerous import SignatureExpired
import logging
import datetime
logger = logging.getLogger('django')


def register_index(request):
    if request.method == 'GET':
        return render(request,'register.html')
    else:
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '信息不完善！！'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请勾选协议！！'})
        models.DfUser.objects.create(user_name=username, password=password, email=email)
        # user.save()
        return redirect(reverse('goods:goods_index'))


class RegisterView(View):
    ''' 注册 '''
    def get(self,request):
        logger.info("进入注册页...")
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '信息不完善！！'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请勾选协议！！'})

        # 校验用户名是否存在
        try:
            # user = models.DfUser.objects.get(user_name=username)
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # user = models.DfUser.objects.create(user_name=username, password=password, email=email)
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.ctime = datetime.datetime.now()
        user.save()

        # 发送激活邮件，包含激活链接: http://127.0.0.1:8000/user/active/3
        # 激活链接中需要包含用户的身份信息, 并且要把身份信息进行加密

        # 加密用户的身份信息，生成激活token 有效期1小时
        serializer = Serialize(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        # 加密
        token = serializer.dumps(info)
        token = token.decode() # bytes 转 str
        logger.info("token:%s" % token)
        # 发邮件
        send_register_active_email.delay(email, username, token)

        return redirect(reverse('goods:index'))


class ActiveView(View):
    ''' 用户激活 '''
    def get(self,request,token):
        # 进行解密，获取要激活的用户信息
        serializer = Serialize(settings.SECRET_KEY, 3600)
        # 解密
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            logger.info("userId=%s" % (user_id,))
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as ex:
            return HttpResponse('此链接激活已过期')


class LoginView(View):
    ''' 登录页 '''
    def get(self,request):
        # 判断是否记住我
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        return render(request,'login.html', {'username':username,'checked':checked})

    def post(self,request):

        username = request.POST.get("username")
        password = request.POST.get("pwd")

        if not all([username, password]):
            return render(request, 'login.html', {'errmsg':'数据不完整'})

        # user = models.DfUser.objects.get(user_name=username,password=password)
        user = authenticate(username=username, password=password)

        if user is not None:
            # 已激活
            if user.is_active == 1:

                # 记录用户的登录状态
                login(request, user)

                # 获取登录后所要跳转到的地址
                # 默认跳转到首页
                next_url = request.GET.get('next', reverse('goods:index'))

                # 跳转到next_url
                response = redirect(next_url)  # HttpResponseRedirect

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')

                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')

                # 生成token
                # rediskey = RedisKeys()
                # token = rediskey.token + "_" + str(user.id)
                # redisUtil = RedisUtil()
                # redisUtil.set(token, user.id, 60 * 30) # 过期时间半小时

                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


class LogoutView(View):
    '''退出登录'''
    def get(self, request):
        '''退出登录'''
        # 清除用户的session信息
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))


class UserInfoView(LoginRequiredMixin, View):
    ''' 用户中心 信息页 '''
    def get(self,request):
        # 获取用户的个人信息
        user = request.user
        # address = DfAddress.objects.get_default_address(user)
        return render(request, 'user_center_info1.html', {'page':'user'})


class UserOrderView(LoginRequiredMixin, View):
    ''' 用户中心 订单页 '''
    def get(self,request):
        return render(request,'user_center_order1.html', {'page': 'order'})


class UserAddressView(LoginRequiredMixin, View):
    ''' 用户中心 地址页 '''
    def get(self,request):
        user = request.user

        try:
            address = models.DfAddress.objects.get(user_id=user.id, is_default=1)
        except DfAddress.DoesNotExist:
            address = None

        return render(request,'user_center_site1.html', {'page': 'address', 'address': address})

    def post(self, request):
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver, addr, phone, type]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        user = request.user

        address = DfAddress.objects.get_default_address(user)

        if address:
            is_default = 0
        else:
            is_default = 1  # 设置默认地址

        models.DfAddress.objects.create(user_id=user.id,
                                        receiver=receiver,
                                        addr=addr,
                                        zip_code=zip_code,
                                        mobile=phone,
                                        is_default=is_default)

        return redirect(reverse('user:address')) # get请求方式