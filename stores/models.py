from django.db import models


from shopify_auth.models import AbstractShopUser, ShopUserManager

from api_wrapper.shopify import Client


class AuthAppShopUserManager(ShopUserManager):

    def create_user(self, myshopify_domain, password=None):
        """
        Creates and saves a ShopUser with the given domain and password.
        """
        if not myshopify_domain:
            raise ValueError('ShopUsers must have a myshopify domain')

        user = self.model(myshopify_domain=myshopify_domain)

        # Never want to be able to log on externally.
        # Authentication will be taken care of by Shopify OAuth.
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, myshopify_domain, password):
        """
        Creates and saves a ShopUser with the given domains and password.
        """
        user = self.create_user(myshopify_domain, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()


class AuthAppShopUser(AbstractShopUser):
    myshopify_domain = models.CharField(
        max_length=255, unique=True, editable=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'myshopify_domain'
    objects = AuthAppShopUserManager()

    @property
    def session(self):
        shopify = Client(self.myshopify_domain, self.token)
        return shopify.create_temp_session()

    def get_full_name(self):
        return self.myshopify_domain

    def get_short_name(self):
        return self.myshopify_domain

    # this methods are require to login super user from admin panel
    def has_perm(self, perm, obj=None):
        return True

    # this methods are require to login super user from admin panel
    def has_module_perms(self, app_label):
        return True

    @property
    def _headers(self):
        return {
            'X-Shopify-Access-Token': self.token,
            'Content-Type': 'application/json'
        }

    @classmethod
    def get_by_domain(cls, shopify_domain):
        try:
            return cls.objects.get(
                myshopify_domain=shopify_domain
            )
        except Exception:
            return None

    @property
    def client(self):
        # Returns an isntance of the ShopifyAPI Wrapper
        return Client(
            myshopify_domain=self.myshopify_domain,
            token=self.token
        )


class Order(models.Model):
    store = models.ForeignKey('stores.AuthAppShopUser',
                              on_delete=models.CASCADE)
    shopify_id = models.CharField(max_length=64)
    customer_id = models.CharField(max_length=128)
    fulfillment_status = models.CharField(
        max_length=256, null=True, blank=True)
    is_tagged = models.BooleanField(default=False)
    raw_data = models.JSONField(default=dict)

    @classmethod
    def from_raw_data(cls, store, raw_data):
        if 'customer' not in raw_data and raw_data["customer"]:
            return
        instance, created = cls.objects.update_or_create(
            store=store,
            shopify_id=raw_data['id'],
            defaults={
                "customer_id": raw_data["customer"]["id"],
                "fulfillment_status": raw_data.get('fulfillment_status'),
                "raw_data": raw_data
            }
        )
        from stores.tasks import post_order_create
        post_order_create.delay(instance.id, created)

    def post_order_create(self, is_created=False):
        orders = Order.objects.filter(
            customer_id=self.customer_id).exclude(
                fulfillment_status='fulfilled')

        if not is_created:
            orders = orders.filter(is_tagged=False)

        if orders.count() > 1:
            payloads = [order.get_tags_payload(
                orders.exclude(id=order.id)) for order in orders]
            orders.update(is_tagged=True)
        else:
            orders = Order.objects.filter(
                customer_id=self.customer_id,
                is_tagged=True)
            fulfilled_orders = orders.filter(fulfillment_status='fulfilled')
            if not fulfilled_orders.exists():
                return False
            payloads = [order.get_remove_tags_payload()
                        for order in fulfilled_orders]
            fulfilled_orders.update(is_tagged=False)
            if payloads:
                payloads.extend([order.get_tags_payload(
                    orders.exclude(id=order.id)) for order in orders.exclude(
                        fulfillment_status='fulfilled')])
        if payloads:
            Order.update_orders(self.store.client, payloads)

    def get_tags_payload(self, orders):
        return {
            "order": {
                "id": self.shopify_id,
                "tags": ", ".join(
                    [order.raw_data["name"] for order in orders]),
            }
        }

    def get_remove_tags_payload(self):
        return {
            "order": {
                "id": self.shopify_id,
                "tags": "",
                "note_attributes": []
            }
        }

    @staticmethod
    def update_orders(client, payloads):
        for payload in payloads:
            client.update_order(payload["order"]["id"], payload)
