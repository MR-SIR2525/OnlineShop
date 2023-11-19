from django import forms

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from localflavor.us.forms import USStateField
from localflavor.us.us_states import STATE_CHOICES

from allauth.account.forms import SignupForm

from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

# from django.contrib.auth.models import User
from .models import UserProfile


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class CustomSignupForm(SignupForm):
    """Includes allauth's form but adds email, first name, and last name fields."""

    #override
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email", 
                "placeholder": _("Email address"),
                "autocomplete": "email",
            }
        )
    )
    first_name = forms.CharField(
        label=_(""),
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("First name"), 
                "autocomplete": "given-name",
            }
        ),
    )
    last_name = forms.CharField(
        required=True,
        label=_(""),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Last name"), 
                "autocomplete": "family-name"
            }
        ),
    )

class AccountUpdateForm(forms.ModelForm):
    """Form to allow users to update their information. Inherits from the User model 
       provided by Djano allauth and includes fields `email`, `first_name`, 
       `last_name`, and `password`. A validator checks that the password is at least 
       8 characters long and contains at least one special character and one number. 
       A validator also checks that the password is not the same as the user's email address."""
    password = forms.CharField(
        widget=forms.PasswordInput(),
        validators=[
            MinLengthValidator(8),
            RegexValidator(
                regex=r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                message="Password must be at least 8 characters long and contain at least one special character and one number."
            )
        ]
    )    

    class Meta:
        fields = ('email', 'first_name', 'last_name', 'password', 'phone_number')
        model = UserProfile
        widgets = {
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'family-name'}),
            'phone_number': forms.TextInput(attrs={'autocomplete': 'phone-number'}),
        }
        
        

# the CustomSignupForm and AccountForm seem to do the same thing, but ChatGPT advised 
# me to retain both, saying:
#
# The CustomSignupForm extends the default SignupForm provided by allauth to include email, 
# first name, and last name fields. On the other hand, the AccountForm extends the SignupForm 
# and includes fields to update the user account information such as username, email, 
# first name, and last name. It also includes a password field with a validator that makes 
# sure the password is at least 8 characters long. These two forms serve different purposes, 
# one to sign up and one to update an existing account, so they need to be kept separate.




class CheckoutForm(forms.Form):
    # PRCC bookstore doesn't ship... leaving shipping here for future use but it 
    # will be not used now
    # shipping_address = forms.CharField(required=True)
    # shipping_address2 = forms.CharField(required=False)
    # shipping_city = forms.CharField(required=True)
    # shipping_state = USStateField(required=True)
    # shipping_zip = forms.CharField(required=True)
    # shipping_country = CountryField(blank_label='(select country)').formfield(
    #     required=True,
    #     initial='US',
    #     disabled=True,
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100',
    #     }))


    #billing address
    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_city = forms.CharField(required=False)
    billing_state = USStateField(widget=forms.Select(choices=STATE_CHOICES), required=True)
        #use USStateField with choices:  https://stackoverflow.com/a/1831027
    billing_zip = forms.CharField(required=True)
    billing_country = CountryField(blank_label="(select country)").formfield(
        required=False,
        initial='US',
        disabled=True, #disabled cause we won't be serving outside the U.S.
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        })
    ) # Just ignore the error on "CountryField's blank_label..."

    same_billing_address = forms.BooleanField(required=False)
    # set_default_shipping = forms.BooleanField(required=False)
    # use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
