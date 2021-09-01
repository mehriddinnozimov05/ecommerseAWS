import requests
from django.contrib import messages, auth
from accounts.models import Account, UserProfile
from carts.models import Cart, CartItem
from orders.models import Order, Order_Product
from carts.views import _cart_id
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RegistrationForm, ProfileForm, UserForm 
from django.contrib.auth.decorators import login_required


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, message

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name=first_name, password=password, last_name=last_name, email=email, username=username)
            user.phone_number = phone_number
            user.save()

            current_site = get_current_site(request)
            mail_subject = "Please activate your account"
            message = render_to_string("accounts/account_verification.html", {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user)
            })
            send_email = EmailMessage(mail_subject, message, to=[email])
            try:
                send_email.send()
            except:
                print("email o`xshamadi")

            return redirect("/accounts/login/?cmd=verification&email="+ email)
    else:
        form = RegistrationForm()
    context = {
        "form": form
    }
    return render(request, "accounts/register.html", context)

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exist:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variations = []
                    prod_id = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variations.append(list(variation))
                        prod_id.append(item.id)
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    for pr in product_variations:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            prod_index = product_variations.index(pr)
                            item_id = id[index]
                            prod_item_id = prod_id[prod_index]
                            item = CartItem.objects.get(id=item_id)
                            prod_item = CartItem.objects.get(id=prod_item_id)
                            item.quantity += prod_item.quantity
                            item.cart = None
                            item.user = user
                            item.save()
                        else:  
                            index = product_variations.index(pr)
                            item_id = prod_id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.cart = None
                            item.user = user
                            item.save()
                    cart.delete()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split("=") for x in query.split("&"))
                if 'next' in params:
                    return redirect(params["next"])
            except:
                print("o`xshamadi")
            return redirect("dashboard")
        else:
            messages.error(request, 'Invalid login credentials!')
            return redirect("login")
    return render(request, 'accounts/login.html')

@login_required(login_url = "login")
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulations! Your account is activated.")
        return redirect("login")
    else:
        messages.error(request, "Invalid activation link.")
        return redirect("register")

@login_required(login_url = "login")
def dashboard(request):
    orders = Order.objects.order_by("created_at").filter(user=request.user, is_ordered=True)
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile()
        profile.user = request.user
        profile.save()
    orders_count = orders.count()
    context = {
        "orders_count": orders_count,
        "profile": profile
    }
    return render(request, "accounts/dashboard.html", context)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            message = render_to_string("accounts/resetpassword_validate.html", {
                "user": user,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user)
            })
            send_email = EmailMessage(mail_subject, message, to=[email])
            send_email.send()

            messages.success(request, "Password reset email has been sent to your email address!")
            return redirect("login")
        else:
            messages.error(request, "Acoount does not exist!")
    return render(request, "accounts/forgot_password.html")


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password.")
        return redirect("reset_password")
    else:
        messages.error(request, "This link has been expired!")
        return redirect("login")

def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Password does not match!")
        elif len(password) < 8:
            messages.error(request, "Password too short")
        else:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful!")
            return redirect("login")
    return render(request, "accounts/reset_password.html")



@login_required(login_url = "login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by("created_at")
    context = {
        "orders": orders
    }
    return render(request, "accounts/my_orders.html", context)



@login_required(login_url = "login")
def order_detail(request, order_id):
    try:
        order = Order.objects.get(user=request.user, id=order_id)
        ordered_products = Order_Product.objects.filter(order=order, user=request.user)
        context = {
            "order": order,
            "ordered_products": ordered_products,
            "sub_total": order.order_total - order.tax
        }
        return render(request, "accounts/order_detail.html", context)
    except:
        return redirect("home")
    


@login_required(login_url = "login")
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=user_profile)
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "user_profile": user_profile
    }
    return render(request, "accounts/edit_profile.html", context)

@login_required(login_url = "login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        user = Account.objects.get(username__exact=request.user.username)

        if new_password != confirm_password:
            messages.error(request, "Password does not match")
        elif len(new_password) < 8:
            messages.error(request, "Password too short")
        elif new_password == current_password:
            messages.error(request, "New Password must be different from the old password")
        elif user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password updated successfully")
        else:
            messages.error(request, "Please enter valid current password")
        print(user.check_password(current_password))
        return redirect("change_password")
    return render(request, "accounts/change_password.html")