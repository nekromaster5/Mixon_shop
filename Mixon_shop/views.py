from django.shortcuts import redirect, render
from django.urls import reverse_lazy as _
from django.views import View


class HomePage(View):
    def get(self, request):
        return render(request, 'product.html')


class ProdBlock(View):
    def get(self, request):
        return render(request, 'product_block.html')
