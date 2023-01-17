from celery import shared_task
from stores.models import Order


@shared_task()
def post_order_create(order_id, created):
    order = Order.objects.get(id=order_id)
    order.post_order_create(created)
