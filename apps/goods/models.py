from django.db import models
import datetime


class DfGoodsBanner(models.Model):
    type_id = models.IntegerField()
    type = models.IntegerField()
    title = models.CharField(max_length=64, blank=True, null=True)
    image = models.CharField(max_length=128)
    sort = models.IntegerField(blank=True, null=True)
    ctime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'df_goods_banner'


class DfGoodsSku(models.Model):
    type_id = models.IntegerField()
    name = models.CharField(max_length=20)
    desc = models.CharField(max_length=200, blank=True, null=True)
    price = models.DecimalField(max_digits=16, decimal_places=3, blank=True, null=True)
    unite = models.CharField(max_length=20, blank=True, null=True)
    image = models.CharField(max_length=128)
    stock = models.IntegerField(blank=True, null=True,default=1)
    sales = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(default=1)
    ctime = models.DateTimeField(blank=True, null=True,default=datetime.datetime.now())
    utime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'df_goods_sku'


class DfGoodsType(models.Model):
    name = models.CharField(max_length=20)
    logo = models.CharField(max_length=20)
    image = models.CharField(max_length=128)
    ctime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'df_goods_type'
