from django.db import models
from django.conf import settings
from django.shortcuts import reverse
 # for forms
from django import forms

CATEGORY_CHOICES = (
    ('R','Running'),
    ('T','Trainers'),
    ('HT','High-tops')
)

LABEL_CHOICES = (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
)

# Create your models here.

#Item(s) in shop
class Item(models.Model):    
    title = models.CharField(max_length = 100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    out_of_stock = models.BooleanField(default=False)
    #image = models.ImageField()
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={'slug':self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={'slug':self.slug})
    
    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={'slug':self.slug})

    

#Item(s) in cart
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    ordered = models.BooleanField(default=False)
    savings = False
    item = models.ForeignKey(Item, on_delete = models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    
    def get_total_item_price(self):
        if (self.item.discount_price):
            total_item_price = self.quantity * self.item.discount_price
            savings = True
            return total_item_price
        else:
            total_item_price = self.quantity * self.item.price  
            return total_item_price
    
    def get_item_savings(self):
        amount_saved = (self.item.price * self.quantity) - self.get_total_item_price()
        return amount_saved

#orders containing item(s)
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)

    ordered = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField()
    voucher = models.ForeignKey('Voucher',on_delete=models.SET_NULL, blank=True, null=True)
    #ordered_date = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.user.username

    def get_order_total(self):
        total = 0 #assignment
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        if self.voucher:
            total -= self.voucher.amount
        return total

class Voucher(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    
    def __str__(self):
        return self.code



class VoucherForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(
        attrs=
        { 
            'class': 'form-control',
            'placeholder': 'Apply voucher code',
            'aria-label': 'Recipient\'s username',
            'aria-describedby': 'basic-addon2' 
        }))