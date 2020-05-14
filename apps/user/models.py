import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    '''用户模型类'''
    mobile = models.CharField(max_length=11, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True, default=0)
    ctime = models.DateTimeField(blank=True, null=True, default=datetime.datetime.now())
    utime = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    '''地址模型管理器类'''
    # 1.改变原有查询的结果集:all()
    # 2.封装方法:用户操作模型类对应的数据表(增删改查)
    def get_default_address(self, user):
        '''获取用户默认收货地址'''
        # self.model:获取self对象所在的模型类
        try:
            address = self.get(user_id=user.id, is_default=1)  # models.Manager
        except self.model.DoesNotExist:
            # 不存在默认收货地址
            address = None

        return address


class DfAddress(models.Model):
    user_id = models.IntegerField()
    receiver = models.CharField(max_length=20, blank=True, null=True)
    addr = models.CharField(max_length=256)
    zip_code = models.CharField(max_length=6, blank=True, null=True)
    mobile = models.CharField(max_length=11)
    is_default = models.IntegerField(blank=True, null=True,default=0)
    ctime = models.DateTimeField(blank=True, null=True,default=datetime.datetime.now())
    utime = models.DateTimeField(blank=True, null=True)

    # 自定义一个模型管理器对象
    objects = AddressManager()

    class Meta:
        managed = False
        db_table = 'df_address'