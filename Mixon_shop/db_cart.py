from .models import Cart, CartItem, Product


class DBCart:
    def __init__(self, request):
        self.user = request.user
        self.cart, _ = Cart.objects.get_or_create(user=self.user)

    def add(self, product, quantity=1, update_quantity=False):
        cart_item, created = CartItem.objects.get_or_create(cart=self.cart, product=product)
        if update_quantity:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity
        cart_item.save()

    def remove(self, product):
        CartItem.objects.filter(cart=self.cart, product=product).delete()

    def __iter__(self):
        for item in self.cart.items.select_related('product'):
            yield {
                'product': item.product,
                'quantity': item.quantity,
                'total_price': item.total_price(),
            }

    def get_total_price(self):
        return self.cart.get_total_price()

    def clear(self):
        self.cart.items.all().delete()
