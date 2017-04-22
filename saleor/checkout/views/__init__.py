from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse

from .discount import add_voucher_form, validate_voucher
from .shipping import (anonymous_user_shipping_address_view,
                       user_shipping_address_view)
from .summary import (
    summary_with_shipping_view, anonymous_summary_without_shipping,
    summary_without_shipping)
from .validators import (
    validate_cart, validate_shipping_address,
    validate_shipping_method, validate_is_shipping_required)
from ..core import load_checkout
from ..forms import ShippingMethodForm
from ...registration.forms import LoginForm
from ...userprofile.models import Address


@load_checkout
@validate_cart
@validate_is_shipping_required
def index_view(request, checkout):
    return redirect('checkout:shipping-address')


@load_checkout
@validate_voucher
@validate_cart
@validate_is_shipping_required
@add_voucher_form
def shipping_address_view(request, checkout):
    if request.user.is_authenticated():
        return user_shipping_address_view(request, checkout)
    return anonymous_user_shipping_address_view(request, checkout)


@load_checkout
@validate_voucher
@validate_cart
@validate_is_shipping_required
@validate_shipping_address
@add_voucher_form
def shipping_method_view(request, checkout):
    country_code = checkout.shipping_address.country.code
    shipping_method_form = ShippingMethodForm(
        country_code, request.POST or None, initial={'method': checkout.shipping_method})
    if shipping_method_form.is_valid():
        checkout.shipping_method = shipping_method_form.cleaned_data['method']
        return redirect('checkout:summary')
    return TemplateResponse(request, 'checkout/shipping_method.html', context={
        'shipping_method_form': shipping_method_form, 'checkout': checkout})


@load_checkout
@validate_voucher
@validate_cart
@add_voucher_form
def summary_view(request, checkout):
    if checkout.is_shipping_required:
        view = validate_shipping_address(summary_with_shipping_view)
        view = validate_shipping_method(view)
        return view(request, checkout)
    elif request.user.is_authenticated():
        return summary_without_shipping(request, checkout)
    else:
        return anonymous_summary_without_shipping(request, checkout)


@load_checkout
@validate_cart
def login(request, checkout):
    """
    Allows user to choose if he wants to login before checkout or continue
    as an anonymous user
    """
    if request.user.is_authenticated:
        return redirect('checkout:index')
    form = LoginForm()
    ctx = {'form': form}
    return TemplateResponse(request, 'checkout/login.html', ctx)


@load_checkout
@validate_cart
@add_voucher_form
def review_for_different_country(request, checkout):
    address_id = request.GET.get('address_id', None)
    address_type = request.GET.get('address_type', None)
    if address_id:
        address = get_object_or_404(Address, pk=address_id)
        if address_type == 'billing':
            checkout.billing_address = address
        if address_type == 'shipping':
            checkout.shipping_address = address
    ctx = {'checkout': checkout, 'total': checkout.get_total(),
           'deliveries': checkout.deliveries}
    return TemplateResponse(request, 'checkout/_review_section.html', ctx)
