## Online Shop for Pearl River Community College’s Bookstore
##
## Andrew Blythe
## Coding Technology Program, Pearl River Community College
## Capstone Coding Project
## Instructors: Dr. Silvia Preston and Said Otwane
## November 28, 2022

# Abstract
For the Capstone Project of the Coding Technology Program, I set out to create an online shopping website for the Bookstore at Pearl River Community College – Forrest County Campus using Django. The website was built to allow students to view and purchase the products offered by the Bookstore, also known as the Wildcat Den. The website features a home page where products are displayed after being fetched from the database. Users may filter by category or search for products by name. The online store also includes user accounts, account-linked sessions, a shopping cart similar to those typically found in online stores, and the groundwork for checkout and payment processing. Staff accounts are also included, allowing store staff to control the online shop.

## Main Users
The online bookstore website’s target user base is the Forrest County Campus of Pearl
River Community College students and faculty.

## Programming Languages Used
The website utilizes HTML, CSS, and JavaScript for the front end. The back end was
built using Django, a web framework written in Python. 

### Some notes
1. I have returned to this a few times in the past year (2023) to do some tweaks with the plan of one day using this code for a business with a friend. With what I have learned in the past year, I think this project will probably undergo many changes before that happens. 
2. There might be a couple packages in the requirements.txt file that I forgot to remove and are not actually required to run this app. 
3. To access the Django admin panel, append "/admin" to the URL. Login username is "admin" and password is "super3636?".
4. There is a debugging GUI panel that can be enabled by going to onlineShop\backend\settings\development.py and setting def show_toolbar to True.
5. Payment does not process yet, but the foundation for future implementation was started and is close to ready with Stripe. 


### Sources and References
[Youtube Tutorial I used](https://youtu.be/YZvRrldjf1Y)
[Just Django, the YouTube channel owner's website](https://justdjango.com/)
[CSS template I built from](https://mdbootstrap.com/freebies/jquery/e-commerce/#!)
[Formatting monetary numbers with 'humanize'](https://stackoverflow.com/a/347560)
[Account authentication: login, signup, etc](https://github.com/pennersr/django-allauth)
[Modern usage of Django alluth](https://www.webforefront.com/django/usermanagementallauth.html)
[Allowing users to edit account info](https://stackoverflow.com/a/62899728)
[USStateField with choices](https://stackoverflow.com/a/1831027)
[USStateField](https://github.com/django/django-localflavor)
[Django Software Foundation & Contributors](https://www.djangoproject.com/)
[Django localflavor (official)](https://github.com/django/django-localflavor)
[Stripe payment HTML/CSS](https://stripe.com/docs/payments/elements)
[Search products functionality](https://stackoverflow.com/a/54246572)
