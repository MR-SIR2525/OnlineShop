from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.dispatch import receiver
from django.shortcuts import reverse
from django.contrib.auth.models import AbstractUser, User

from django_countries.fields import CountryField
from localflavor.us.models import USStateField


"""For error saying: table_name already exists, or other db errors, do this:
   https://stackoverflow.com/questions/59999242/django-db-utils-internalerror-1050-table-django-content-type-already-exist
   """
"""
Or...
python manage.py makemigrations app_name --name migration_name --empty

"""

LABEL_CHOICES = (
    ('n', 'none'),
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class UserProfile(models.Model):
    """UserProfile model that extends the "User" model from Django allauth. Adds stripe_customer_id
       and one_click_purchasing boolean (defaults to false).\n
       Methods include:
       - get_full_name() \n
       - get_short_name() \n"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.email

    @property
    def get_full_name(self):
        return self.user.get_full_name
    
    @property
    def get_short_name(self):
        return self.user.get_short_name


# Signal to create an UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_or_update_UserProfile(Sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

    instance.UserProfile.save()


    

class Category(models.Model):
    abbreviation = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(max_length=50)
    plural = models.CharField(max_length=50, blank=True, null=True)
    cover_image = models.URLField(
        default='https://mr-sir2525.github.io/BBNLT/media/products/Product-Image-Coming-Soon.png')
  
    @staticmethod
    def get_all():
        return Category.objects.all()

    @staticmethod
    def get_id_for_(catName):

        return Category.objects.filter(name=catName)        
  
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = 'Categories'


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True) #category_id in db
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("store:product", kwargs={
            'slug': self.slug
        })

    @staticmethod
    def get_by_categoryid(category_id):
        if category_id:
            return Item.objects.filter(category=category_id)
        else:
            print("Could not filter by category id... returning all.")
            return Item.objects.all()
        
    @staticmethod
    def get_by_category(categoryName):
        if categoryName:
            return Item.objects.filter(category=categoryName)
        else:
            print("Could not filter by category name... returning all.")
            return Item.objects.all()

    def get_add_to_cart_url(self):
        """Returns the URL needed for templates/pages to add items to cart"""
        return reverse("store:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("store:remove-from-cart", kwargs={
            'slug': self.slug
        })
    
    class Meta:
        verbose_name = "Item/Product"
        verbose_name_plural = 'Items/Products'


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price  # type: ignore

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)

    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        """It's better not to return __str__ method as foreign key for models. 
           A conflict happens if username is 'None.'\n

           AttributeError at /admin/orders2/order/11/change/ 'NoneType' object has 
           no attribute 'username' -> https://stackoverflow.com/q/61545746"""
        if self.user is None:
            return '<No user>'
        return str(self.user.id)


    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = USStateField(default='MS')
    country = CountryField(default='US')
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
        # ↑ causes issue in admin template for viewing Order entities.
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id}: ${self.amount}"

    # def __str__(self):
    #     if self.user is not None:
    #         return self.user.username
    #     #TODO: This is an issue that needs to be resolved. Should I return something else?
    #     return "<No user tied to payment>"


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"



# Old code for creating a user profile
# def userprofile_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         userprofile = UserProfile.objects.create(user=instance)

# post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)