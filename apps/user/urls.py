from django.urls import path,re_path
from apps.user.views import RegisterView,ActiveView,LoginView,LogoutView,UserInfoView,UserOrderView,UserAddressView


urlpatterns = [
    # path('register/', register_index, name='index'),
    path('register/', RegisterView.as_view(), name='register'),# 注册
    re_path(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'), # 激活

    path('login/', LoginView.as_view(), name='login'), # 登录
    path('logout/', LogoutView.as_view(), name='logout'), # 注销登录

    path('info/', UserInfoView.as_view(), name='user'), # 用户中心-信息页
    re_path(r'^order/(?P<page>\d+)$', UserOrderView.as_view(), name='order'), # 用户中心-订单页
    path('address/', UserAddressView.as_view(), name='address'), # 用户中心-地址页
]
