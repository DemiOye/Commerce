from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListings(models.Model):
    title = models.CharField(max_length=50)
    CATEGORIES = (("No Category","No Category"),("Accessories","Accessories"),("Automobiles","Automobiles"),("Clothing","Clothing"),("Cosmetics","Cosmetics"),("Devices","Devices"),("Food","Food"),("Furniture","Furniture"),("Stationery","Stationery"),("Utensils","Utensils"))
    category = models.CharField(max_length=50,choices=CATEGORIES,default="No Category")
    price = models.IntegerField()
    image = models.ImageField(upload_to="images/",blank=True)
    description = models.TextField()
    user = models.CharField(max_length=50)
    last_modified = models.DateTimeField(null=True)

    def __str__(self):
        return self.title
    
    
class Bids(models.Model):
    bid = models.IntegerField()
    bid_user = models.CharField(max_length=50)
    listing = models.CharField(max_length=50)
    listing_catg = models.CharField(max_length=50)
    listing_price = models.CharField(max_length=50)
    listing_user = models.CharField(max_length=50)
    time_posted = models.DateTimeField(null=True)

    def __str__(self):
        return self.bid_user
    
    
class Comments(models.Model):
    comment = models.CharField(max_length=50)
    comment_user = models.CharField(max_length=50)
    listing = models.CharField(max_length=50)
    listing_user = models.CharField(max_length=50)
    time_posted = models.DateTimeField(null=True) 

    def __str__(self):
        return self.comment 
    
class Wins(models.Model):
    listing = models.CharField(max_length=50)
    listing_category = models.CharField(max_length=50)
    listing_description = models.TextField()
    listing_price = models.CharField(max_length=50)
    listing_user = models.CharField(max_length=50)
    win_user = models.CharField(max_length=50)
    win_amount = models.CharField(max_length=50)
    time_closed = models.DateTimeField(null=True)

    def __str__(self):
        return self.listing

class Image(models.Model):
    listing = models.CharField(max_length=50)
    image = models.ImageField(upload_to="images/",blank=True)
    user = models.CharField(max_length=50)

    def __str__(self):
        return self.listing