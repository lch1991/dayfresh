from django.urls import path
from apps.goods.views import goodsIndexView

urlpatterns = [
    path('', goodsIndexView.as_view(), name='index')
]
