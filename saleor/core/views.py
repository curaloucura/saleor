from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..dashboard.views import staff_member_required
from ..cart.forms import CountryForm
from ..product.utils import products_with_availability, products_for_homepage

COOKIE_COUNTRY = 'country_cookie'


def home(request):
    products = products_for_homepage()[:8]
    products = products_with_availability(
        products, discounts=request.discounts, local_currency=request.currency,
        country=request.country)
    return TemplateResponse(
        request, 'home.html',
        {'products': products, 'parent': None})


@staff_member_required
def styleguide(request):
    return TemplateResponse(request, 'styleguide.html')


def set_country(request):
    form = CountryForm(request.POST or None)
    next_url = request.POST.get('next')
    if not next_url:
        next_url = 'home'
    response = redirect(next_url)
    if form.is_valid():
        country = form.cleaned_data['country']
        request.session[COOKIE_COUNTRY] = country
    return response
