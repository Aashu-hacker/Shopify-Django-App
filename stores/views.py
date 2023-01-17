from django.conf import settings
from django.views import View
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from shopify_auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from stores import serializers

from stores.models import AuthAppShopUser, Order

import json


class ViewMixin(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_metafields(self, obj):
        return obj.metafields()

    def get_context(self):
        return {
            'SHOPIFY_APP_API_KEY': settings.SHOPIFY_APP_API_KEY,
            'SHOPIFY_APP_NAME': settings.SHOPIFY_APP_NAME
        }


class HomeView(ViewMixin):
    template_name = 'home.html'


class ProductView(ViewMixin):
    template_name = 'product.html'

    def get_context(self):
        context = super().get_context()
        store = self.request.user
        product = store.client.shopify.Product().find(self.request.GET['id'])
        context.update({
            'product': product,
            'custom_price': self.get_custom_prices(product)
        })
        return context

    def get_custom_prices(self, product):
        metafields = self.get_metafields(product)
        metafield = None
        for metafield in metafields:
            if metafield.namespace == 'custom' and metafield.key == 'prices':
                values = []
                for value in json.loads(metafield.value):
                    value["price"] = value["price"] / 100
                    values.append(value)
                return {
                    "namespace": "custom",
                    "key": "prices",
                    "value": values,
                    "id": metafield.id
                }
        return {
            "namespace": "custom",
            "key": "prices",
            "value": list()
        }


class UpdateCustomPriceProductAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CustomPriceMetafieldSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'store': request.user})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({})


class DeleteProductMetafield(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        metafield = request.user.client.get_metafield(
            request.data['metafield_id'])
        metafield.destroy()
        return Response({})


class OrderWebhook(View):

    def post(self, request, *args, **kwargs):

        order_data = json.loads(request.body.decode('utf-8'))

        store_domain = request.META.get('HTTP_X_SHOPIFY_SHOP_DOMAIN')
        store = AuthAppShopUser.get_by_domain(store_domain)

        if not store:
            return JsonResponse({}, status=200)

        Order.from_raw_data(store, order_data)

        return JsonResponse({}, status=200)
