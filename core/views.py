from django.views.generic import ListView, DetailView, View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order, Voucher, VoucherForm

# Create your views here.


def products(request):
    context = { 'items': Item.objects.all()    }
    return render(request,"product-page.html", context)

def checkout(request):
    context = {'items': Item.objects.all()    }
    return render(request,"checkout-page.html", context)

def faq(request):
    return render(request,"faq.html")

#Homepage MVC
class HomeView(ListView):
    model = Item
    template_name = "home-page.html"
    #return render(request, template_name, context)    

#@login_required does not require as LoginRequiredMixin is inherited.
class OrderSummaryView(LoginRequiredMixin,View):
    # model = Order
    # template_name = "order_summary.html"
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            
            context = { 'object': order    }

            return render(self.request, 'order_summary.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


class CheckoutView(LoginRequiredMixin,View):
    # model = Order
    # template_name = "order_summary.html"
    def get(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            
            #form = CheckoutForm()  
            #'form': form, 

            context = { 'order': order , 'voucherform': VoucherForm()   }

            
            
            return render(self.request, 'checkout-page.html', context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")


#Product MVC
class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"
    #return render(request, template_name, context)

@login_required
def add_to_cart(request, slug):
    
    item = get_object_or_404(Item, slug=slug)

    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    
    if order_qs.exists():   #if order query set exists //& stock available add to card
        order = order_qs[0] 
        #Check if item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            if item.out_of_stock is False:
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "Item quantity is updated.")
                return redirect("core:order-summary")
            else:
                messages.info(request, "Unable to add to order! Selected item is out of stock.")
                return redirect("core:order-summary")

        else:
            if item.out_of_stock is False:
                messages.info(request, "Item has been succesfully added to cart!")
                order.items.add(order_item)
                return redirect("core:order-summary")
            else:
                messages.info(request, "Unable to add to order! Selected item is out of stock.")
                return redirect("core:order-summary")
    else:
        if item.out_of_stock is False:
            ordered_date = timezone.now()
            order = Order.objects.create(user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            messages.info(request, "Item has been succesfully added to cart!")
            return redirect("core:order-summary")
        else:
            messages.info(request, "Unable to add to order! Selected item is out of stock.")
            return redirect("core:order-summary")

@login_required
def remove_from_cart(request, slug):
    
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    
    if order_qs.exists():   #if order query set exists //& stock available add to card
        order = order_qs[0] 
        
        #Check if item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "Item has been succesfully removed from your cart!")
            
            return redirect("core:order-summary")  
        else:
            #display order NOT exist
            messages.info(request, "This item is not in your cart.")
            return redirect("core:product", slug=slug)
    else:
        #display order NOT exist
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    
    if order_qs.exists():   #if order query set exists //& stock available add to card
        order = order_qs[0] 
        
        #Check if item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            
            if order_item.quantity > 1:

                order_item.quantity -= 1
                order_item.save()
                
            else:
                order.items.remove(order_item)
            messages.info(request, "Item quantity has been updated")
            
            return redirect("core:order-summary")  
        else:
            #display order NOT exist
            messages.info(request, "This item is not in your cart")
            return redirect("core:order-summary", slug=slug)
    else:
        #display order NOT exist
        messages.info(request, "You do not have an active order")
        return redirect("core:order-summary", slug=slug)

def get_voucher(request, code):
    try:
        voucher = Voucher.objects.get(code=code)
        return voucher

    except ObjectDoesNotExist:
        messages.info(request, "The voucher submitted does not exist")
        return redirect("core:checkout")



def add_voucher(request):
    if request.method == "POST":
        form = VoucherForm(request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=request.user, ordered=False)
                order.voucher = get_voucher(request, code)
                order.save()
                messages.success(request, "Successfully added voucher")
                return redirect("core:checkout")

            except ObjectDoesNotExist:
                messages.info(request, "You do not have an active order")
                return redirect("core:checkout")
            
    #else display err

            