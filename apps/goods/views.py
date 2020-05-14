from django.shortcuts import render,redirect,reverse
from django.views.generic import View
from django.db import models

from apps.goods import models


class goodsIndexView(View):

    def get(self, request):
        # 商品种类list
        types = models.DfGoodsType.objects.all()
        # 首页banner图
        banner_indexs = models.DfGoodsBanner.objects.filter(type=1).order_by('sort')
        # 活动图
        banner_activitys = models.DfGoodsBanner.objects.filter(type=3).order_by('sort')

        for type in types:
            goods_lists = models.DfGoodsBanner.objects.filter(type=2, type_id = type.id)
            type.goods_lists = goods_lists

        context = {'types': types,
                   'goods_banners': banner_indexs,
                   'promotion_banners': banner_activitys}

        return render(request,'index.html', context)

