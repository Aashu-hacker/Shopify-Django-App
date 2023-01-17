from django.conf import settings

from shopify.session import ValidationException # noqa
import shopify
from api_wrapper.requests import RequestBase


WEBHOOKS = {
    "orders/create": "{application_url}/stores/webhooks/orders/",
    "orders/updated": "{application_url}/stores/webhooks/orders/"
}


class Client(RequestBase):

    def __init__(self, myshopify_domain, token=None):
        self.store_domain = myshopify_domain.strip()
        self.token = token
        self.api_url = f"https://{self.store_domain}/admin/api/{settings.SHOPIFY_APP_API_VERSION}"  # noqa
        self.shopify = shopify
        self.shopify.ShopifyResource.activate_session(self._session)
        self.application_url = settings.APPLICATION_URL

    @property
    def _session(self):
        self.session = shopify.Session(
            self.store_domain,
            getattr(settings, 'SHOPIFY_APP_API_VERSION', 'unstable'),
            token=self.token
        )
        self.session.api_key = settings.SHOPIFY_APP_API_KEY
        return self.session

    @property
    def _temp_session(self):
        return shopify.Session.temp(self.store_domain, self.token)

    def _get_auth_url(self, url):
        return self.session.create_permission_url(settings.SHOPIFY_APP_API_SCOPE, url)

    def request_token(self, params):
        return self.session.request_token(params)

    @property
    def _headers(self):
        return {
            'X-Shopify-Access-Token': self.token,
            'Content-Type': 'application/json'
        }

    def get_product(self, product_id):
        return self.shopify.Product.get(product_id)

    def delete_metafield(self, metafield_id):
        return self.shopify.Metafield.delete(metafield_id)

    def get_metafield(self, metafield_id):
        return self.shopify.Metafield.find(metafield_id)

    def create_product_metafields(self, product_id, metafield_data):
        metafields = {
            "metafield": metafield_data
        }
        url = f"{self.api_url}/products/{product_id}/metafields.json"
        response = self.post(url=url, json_data=metafields, headers=self._headers)
        return self.get_response(response)

    def get_inventory_levels(self, inventory_id):
        url = f"{self.api_url}/inventory_levels.json?inventory_item_ids={inventory_id}"
        response = self.get(url=url, headers=self._headers)
        return self.get_response(response)["inventory_levels"]

    def get_location_details(self, location_id):
        return self.shopify.Location.get(location_id)

    def create_variant_metafields(self, product_id, variant_id, metafield_data):
        metafields = {
            "metafield": metafield_data
        }
        url = f"{self.api_url}/products/{product_id}/variants/{variant_id}/metafields.json" # noqa
        response = self.post(url=url, json_data=metafields, headers=self._headers)
        return self.get_response(response)

    def create_webhooks(self):
        """
        Delete Previous Created Webhooks to avoid duplicate creation
        of topic for the store or raising exception for Topic alredy exists
        """
        self.delete_webhooks()
        webhooks_url = f"{self.api_url}/webhooks.json"
        for topic, url in WEBHOOKS.items():
            data = {
                "webhook": {
                    "topic": topic,
                    "address": url.format(application_url=self.application_url),
                    "format": "json",
                }
            }
            response = self.post(
                url=webhooks_url, json_data=data,
                headers=self._headers)
            response.raise_for_status()

    def delete_webhooks(self):
        webhooks_url = f"{self.api_url}/webhooks.json"
        response = self.get(webhooks_url, headers=self._headers)
        webhooks = self.get_response(response)['webhooks']

        for webhook in webhooks:
            webhook_url = f"{self.api_url}/webhooks/{webhook['id']}.json"
            response = self.delete(webhook_url, headers=self._headers)
            response.raise_for_status()

    def get_order(self, order_id):
        return self.shopify.Order.find(order_id)

    def update_order(self, order_id, payload):
        url = f'{self.api_url}/orders/{order_id}.json'
        response = self.put(url, payload, headers=self._headers)
        return self.get_response(response)['order']
