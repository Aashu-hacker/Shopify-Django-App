from rest_framework import serializers
from pyactiveresource.connection import ResourceNotFound

import json


class CustomPriceMetafieldSerializer(serializers.Serializer):
    product_id = serializers.CharField(required=True)
    metafield_id = serializers.CharField(required=False, allow_null=True)
    value = serializers.JSONField(required=True)

    class Meta:
        fields = ('metafield_id', 'value')

    @property
    def client(self):
        return self.context['store'].client

    def get_metafield(self):
        try:
            return self.client.get_metafield(
                self.validated_data.get('metafield_id') or 1111)
        except ResourceNotFound:
            return None

    def save(self, **kwargs):
        instance = self.get_metafield()
        if instance:
            return self.update(instance, **kwargs)
        return self.create(**kwargs)

    def update(self, instance, **kwargs):
        instance.value = json.dumps(self.validated_data['value'])
        instance.save()
        return instance

    def create(self, **kwargs):
        metafield_data = {
            "namespace": "custom",
            "key": "prices",
            "value": json.dumps(self.validated_data['value']),
            "type": "json"
        }
        return self.client.create_product_metafields(
            product_id=self.validated_data['product_id'],
            metafield_data=metafield_data)
