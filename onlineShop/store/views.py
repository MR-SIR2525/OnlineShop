import random
import string
from django.urls import reverse_lazy

import stripe
from django.conf import settings
from django.contrib import messages #ability to send alerts to templates/pages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.views.generic import ListView, DetailView, View, UpdateView, TemplateView

from .forms import AccountUpdateForm, CheckoutForm, CouponForm, RefundForm, PaymentForm
from .models import Category, Item, OrderItem, Order, Address, Payment, Coupon, Refund, Account

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)

def is_valid_form(values):
    """Returns false if any fields are empty."""
    valid = True
    for field in values:

        if field == '':
            valid = False
    return valid


class AccountEditView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountUpdateForm
    template_name = 'accounts/account_edit.html'
    success_url = reverse_lazy('store:account-edit')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Account information updated successfully.')
        return super().form_valid(form)

# class AccountView(LoginRequiredMixin, View):
#     template_name = 'account_edit.html'
#     fields = ('username', 'email', 'first_name', 'last_name')
#     form_class = AccountUpdateForm

#     def get(self, request, *args, **kwargs):
#         form = self.form_class(instance=self.request.user)
#         context = {'form': form}
#         return render(request, self.template_name, context)

#     def post(self, request, *args, **kwargs):
#         form = AccountUpdateForm(self.request.POST, instance=self.request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Your account was updated successfully."))
#             return redirect("account_edit")
#         else:
#             messages.error(request, _("Your account was not updated."))
#             context = {'form': form}
#             return render(request, self.template_name, context)



class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})
            return render(self.request, "checkout.html", context)
            
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("store:checkout")
        except ValueError:
            messages.warning(self.request, "Invalid information supplied.")
            return redirect("store:checkout")

    def post(self, *args, **kwargs):
        """If you supply blank information but pick a payment method, it breaks this.
           I don't have time to fix this. No combination of try-except blocks that I
           have tried were able to catch the error and redirect to a proper error message."""
        try:
            form = CheckoutForm(self.request.POST or None)
        except:
            messages.info(self.request, "You didn't supply the necessary information.")
            return redirect("store:checkout")
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                """Shipping has all be commented out because the bookstore won't be shipping
                   anything. It's left here for future use."""
                # use_default_shipping = form.cleaned_data.get('use_default_shipping')

                # ******** Shipping address ********
                # if use_default_shipping:
                #     print("Using the default shipping address")
                #     address_qs = Address.objects.filter(
                #         user=self.request.user,
                #         address_type='S',
                #         default=True
                #     )
                #     if address_qs.exists():
                #         shipping_address = address_qs[0]
                #         order.shipping_address = shipping_address
                #         order.save()
                #     else:
                #         messages.info(
                #             self.request, "No default shipping address available")
                #         return redirect('store:checkout')
                # else:
                #     print("User is entering a new shipping address")
                #     shipping_address1 = form.cleaned_data.get(
                #         'shipping_address')
                #     shipping_address2 = form.cleaned_data.get(
                #         'shipping_address2')
                #     shipping_country = form.cleaned_data.get(
                #         'shipping_country')
                #     shipping_zip = form.cleaned_data.get('shipping_zip')

                #     if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                #         shipping_address = Address(
                #             user=self.request.user,
                #             street_address=shipping_address1,
                #             apartment_address=shipping_address2,
                #             country=shipping_country,
                #             zip=shipping_zip,
                #             address_type='S'
                #         )
                #         shipping_address.save()

                #         order.shipping_address = shipping_address
                #         order.save()

                #         set_default_shipping = form.cleaned_data.get(
                #             'set_default_shipping')
                #         if set_default_shipping:
                #             shipping_address.default = True
                #             shipping_address.save()

                #     else:
                #         messages.info(
                #             self.request, 
                #             "Please fill in the required shipping address fields"
                #         )
                #         return redirect('store:checkout')


                # ******** Billing address ********
                use_default_billing = form.cleaned_data.get('use_default_billing')
                # same_billing_address = form.cleaned_data.get('same_billing_address')

                # if same_billing_address:
                #     billing_address = shipping_address
                #     billing_address.pk = None
                #     billing_address.save()
                #     billing_address.address_type = 'B'
                #     billing_address.save()
                #     order.billing_address = billing_address
                #     order.save()

                # elif use_default_billing:
                if use_default_billing:
                    """Currently disabled in the form"""
                    print("Using the default billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('store:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_city = form.cleaned_data.get('billing_city')
                    billing_state = form.cleaned_data.get('billing_state')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')


                    if is_valid_form([
                        billing_address1, billing_city, billing_state, 
                        billing_country, billing_zip
                    ] ):

                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            city = billing_city,
                            state = billing_state,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )

                        try:
                            billing_address.save()

                            order.billing_address = billing_address
                            order.save()

                            set_default_billing = form.cleaned_data.get('set_default_billing')
                            if set_default_billing:
                                billing_address.default = True
                                billing_address.save()
                        except Exception:
                            messages.info(self.request, "Unable to save information. Check 'CheckoutView' > billing address")
                            return redirect("store:checkout")

                    else:
                        messages.info(self.request, "Please fill in the required billing address fields")
                        return redirect("store:checkout")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('store:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('store:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('store:checkout')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("store:cart")
        except Exception:
            messages.warning(self.request, "Invalid information given.")
            return redirect("store:checkout")




class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY
            }
            account = self.request.user.account
            if account.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    account.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("store:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = Account.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class HomeView(ListView):
    model = Item
    paginate_by = 12
    template_name = "home.html"
    
    # Taken from my Django helloWorld project:
    def get_context_data(self, **kwargs):
        """Override super method to pass additional context variables to the template.\n
        https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Generic_views"""
        # Call the base implementation to get the normal context
        context = super(HomeView, self).get_context_data(**kwargs)
        # additional context:
        context['categories'] = Category.get_all().order_by('name')
        return context

    def get_queryset(self):
        """If search is used, returns what is searched. Or can filter by category.
           Otherwise, returns all items. Refactored by ChatGPT on 1/8/22.\n
           Reference: https://stackoverflow.com/questions/13416502/django-search-form-in-class-based-listview
        """
        search = self.request.GET.get('search')
        category_abbrev = self.request.GET.get('category')
        
        if search and category_abbrev:
            # Both search and category filter are present
            object_list = self.model.objects.filter(
                title__icontains=search, category_id=category_abbrev)
        elif search:
            # Only search is present
            object_list = self.model.objects.filter(title__icontains=search)
        elif category_abbrev:
            # Only category filter is present
            object_list = self.model.objects.filter(category_id=category_abbrev)
        else:
            # No search or category filter is present
            object_list = self.model.objects.all()
            
        return object_list


class OrderSummaryView(LoginRequiredMixin, View):
    """Aka, Cart or Shopping Cart"""
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False # making sure we get only non-fulfilled order contents 
    )

    order_queryset = Order.objects.filter(user=request.user, ordered=False) 
    
    if order_queryset.exists():
        order = order_queryset[0]
        
        #if OrderItem is already in cart, add 1 to quantity
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item quantity was updated.")
            return redirect("store:cart")

        #...else, add it to cart
        else:
            order.items.add(order_item)
            messages.info(request, f'"{item}" was added to your cart.')
            return redirect("store:cart") 

            # ↑ consider making this redirect to "added to cart, continue shopping or view cart?"
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("store:cart")



@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_queryset = Order.objects.filter(user=request.user, ordered=False)
    
    if order_queryset.exists():
        order = order_queryset[0]
        # check if the orderItem is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, f'"{item}" was removed from your cart.')
            return redirect("store:cart")
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect("store:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("store:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_queryset = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_queryset.exists():
        order = order_queryset[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("store:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("store:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("store:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("store:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("store:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("store:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("store:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("store:request-refund")


class ColorComparisonsView(TemplateView):
    """A view to handle the developer page for color comparisons."""
    template_name = 'developer/colorComparisons.html'


# ***************** Old or unused code ***************

# class AccountView(View):
#     """Allow users to view their account information."""
#     model = UserProfile
#     template_name = "account_view.html"

#     # @login_required
#     def get(self, request):
#         current_user = request.user
#         account = get_object_or_404(UserProfile, email=current_user.email)
#         context = {
#             'user': current_user,
#             'account': account,
#             'error_message': "The field is blank",
#         }
#         return render(request, self.template_name, context)