from django.conf import settings

import hmac
import hashlib

from stores.models import AuthAppShopUser
from django.contrib import auth


def _get_proxy_hmac(shopify_params):
    """
    Calculate the signature of the given query dict as per Shopify's documentation
    for proxy requests.
    See: http://docs.shopify.com/api/tutorials/application-proxies#security
    """
    signature = hmac.new(
        settings.SHOPIFY_APP_API_SECRET.encode('utf-8'),
        shopify_params.encode('utf-8'), hashlib.sha256)
    return signature.hexdigest()


def hmac_is_valid(shopify_params):
    try:
        signature_to_verify = shopify_params['X-Shopify-Shop-Hmac']
    except Exception:
        return False

    calculated_signature = _get_proxy_hmac(shopify_params)

    # Try to use compare_digest() to reduce vulnerability to timing attacks.
    # If it's not available, just fall back to regular string comparison.
    try:
        return hmac.compare_digest(
            calculated_signature.encode('utf-8'),
            signature_to_verify.encode('utf-8')
        )
    except AttributeError:
        return calculated_signature == signature_to_verify.encode('utf-8')


class StoreSetupMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        shopify_params = request.headers.get('X-Shopify-Shop-Params')
        user = None
        if not shopify_params:
            # Hack for redirection after installation
            store_domain = request.GET.get('shop')
            if not store_domain:
                return self.get_response(request)

            user = AuthAppShopUser.get_by_domain(store_domain)
            if not user or (request.user.is_authenticated and user and user.id != request.user.id):
                auth.logout(request)

            return self.get_response(request)

        if not shopify_params:
            # Apparently this request doesn't come from an
            # embeded app. Move forward
            return self.get_response(request)

        if not hmac_is_valid(shopify_params):
            # Well, hmac is not valid. Move on.
            return self.get_response(request)

        # If hmac is valid, then move forward
        store_domain = request.headers.get('X-Shopify-Shop-Domain')
        if not store_domain:
            store_domain = request.GET.get('shop')

        user = AuthAppShopUser.get_by_domain(store_domain)
        if not user or (request.user.is_authenticated and user and user.id != request.user.id):
            auth.logout(request)
        return self.get_response(request)
