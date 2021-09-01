from carts.models import CartItem
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, ProductGallery, ReviewRating
from category.models import Category
from carts.views import _cart_id
from .forms import ReviewForm
from django.contrib import messages
from orders.models import Order_Product

def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by("id")
        product_count = products.count()
    
    paginator = Paginator(products, 2)
    page = request.GET.get('page')
    paged_product = paginator.get_page(page)
    context = {
        'products': paged_product,
        'count': product_count
    }

    return render(request, 'store/store.html', context)




def prod_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    try:
        order_product = Order_Product.objects.filter(user=request.user, product=single_product).exists()
    except:
        order_product = None
    
    reviews = ReviewRating.objects.filter(product=single_product, status=True)
    product_gallery = ProductGallery.objects.filter(product=single_product)
    context = {
        'product': single_product,
        'order_product': order_product,
        "reviews": reviews,
        "product_gallery": product_gallery

    }
    return render(request, "store/product_detail.html", context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products = Product.objects.order_by("-created_date").filter(Q(prod_description__icontains=keyword) | Q(prod_name__icontains=keyword))
            product_count = products.count()
    context = {
        "products": products,
        "count": product_count
    }
    return render(request, "store/store.html", context)

def submit_review(request, product_id):
    url = request.META.get("HTTP_REFERER")
    product = Product.objects.get(id=product_id)
    if request.method == "POST":
        try:
            review = ReviewRating.objects.get(user=request.user, product=product)
            print(review)
            form = ReviewForm(request.POST, instance=review) 
            form.save()
            messages.success(request, "Thank you rewiew has been updated!")
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data["subject"]
                data.rating = form.cleaned_data["rating"]
                data.review = form.cleaned_data["review"]
                data.ip = request.META.get("REMOTE_ADDR")
                data.product = product
                data.user = request.user
                data.save()
                messages.success(request, "Thank you! You review has been submitted")
                return redirect(url)