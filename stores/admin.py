from django.contrib import admin

from stores.models import AuthAppShopUser, Order


@admin.register(AuthAppShopUser)
class AuthAppShopUserAdmin(admin.ModelAdmin):
    list_display = ('myshopify_domain', 'is_active', 'is_superuser', 'created')
    search_fields = ('myshopify_domain', )
    list_filter = ('is_staff', 'is_superuser', 'modified', 'created')
    actions = ["create_webhooks", "delete_webhooks"]

    def create_webhooks(self, request, queryset):
        for query in queryset:
            query.client.create_webhooks()

    def delete_webhooks(self, request, queryset):
        for query in queryset:
            query.client.delete_webhooks()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('store', 'shopify_id', 'customer_id', 'fulfillment_status')
    search_fields = ('shopify_id', 'customer_id')
