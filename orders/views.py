from django.http.response import JsonResponse
from store.models import Product
from orders.models import Order, Order_Product, Payment
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from carts.models import CartItem
from .forms import OrderForm
import json
import datetime
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False)

    payment = Payment(
        user=request.user,
        payment_id = body["transID"],
        payment_method = body["payment_method"],
        status = body["status"],
        payment_paid = order.order_total,
    )

    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for cart_item in cart_items:
        order_product = Order_Product()
        order_product.order = order
        order_product.payment = payment
        order_product.user = request.user
        order_product.product = cart_item.product
        order_product.quantity = cart_item.quantity
        order_product.product_price = cart_item.product.price
        order_product.is_ordered = True
        order_product.save()


        product_variation = cart_item.variations.all()
        order_product.variation.set(product_variation)
        order_product.save()
        product = Product.objects.get(id=cart_item.product.id)
        product.stock -= cart_item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()

    mail_subject = "Thank you for your order!"
    message = render_to_string("orders/order_recieved_email.html", {
        "user": request.user,
        "order": order
    })
    send_email = EmailMessage(mail_subject, message, to=[request.user.email])
    send_email.send()

    data = {
        'order_number': order.order_number,
        "transID": payment.payment_id
    }
    return JsonResponse(data)

    return render(request, "orders/payments.html")



@login_required(login_url="login")
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count < 1:
        return redirect("store")

    if request.method == "POST":
        total = 0
        quantity = 0

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (20 * total)/100
        grand_total = total + tax
        try:
            order = Order.objects.get(user=current_user, is_ordered=False)
        except:
            form = OrderForm(request.POST)
            if form.is_valid():
                data = Order()
                data.user = current_user
                data.first_name = form.cleaned_data["first_name"]
                data.last_name = form.cleaned_data["last_name"]
                data.phone = form.cleaned_data["phone"]
                data.email = form.cleaned_data["email"]
                data.address_line1 = form.cleaned_data["address_line1"]
                data.address_line2 = form.cleaned_data["address_line2"]
                data.country = form.cleaned_data["country"]
                data.state = form.cleaned_data["state"]
                data.city = form.cleaned_data["city"]
                data.order_note = form.cleaned_data["order_note"]
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get("REMOTE_ADDR")
                data.save()
                year = int(datetime.date.today().strftime("%Y"))
                day = int(datetime.date.today().strftime("%d"))
                month = int(datetime.date.today().strftime("%m"))
                date = datetime.date(year, month, day) 
                current_date = date.strftime("%Y%m%d")
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()

        order = Order.objects.get(user=current_user, is_ordered=False)
        context = {
            "order": order,
            "cart_items": cart_items,
            "total": total,
            "tax": tax,
            "grand_total": grand_total
        }
        return render(request, "orders/payments.html", context)
    else:
        return redirect("checkout")
    
def order_complete(request):
    order_number = request.GET.get("order_number")
    transId = request.GET.get("transID")

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = Order_Product.objects.filter(order=order)
        payment = Payment.objects.get(payment_id=transId)
        context = {
            "order": order,
            "ordered_products": ordered_products,
            "transId": transId,
            "payment": payment,
            "sub_total": order.order_total - order.tax
        }

        return render(request, "orders/order_complete.html", context)
    except Order.DoesNotExist:
        redirect("home")
    