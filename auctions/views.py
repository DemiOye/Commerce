from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Max

from .models import User, AuctionListings, Bids, Comments, Wins, Image
from .forms import CreateListingForm, PostBid, PostComment

categories = ["No Category", "Accessories", "Automobiles", "Clothing", "Cosmetics", "Devices", "Food", "Furniture", "Stationery", "Utensils"]


def index(request):
    listings = AuctionListings.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    

def categories_page(request):
    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category_page(request, category):
    for x in categories:
        if x == category:
            listings = AuctionListings.objects.filter(category=category)
            return render(request, "auctions/category.html", {
                "category": category,
                "listings": listings
            })
    for x in categories:
        if x != category:
            return render(request, "auctions/404.html")
        

def search(request):
    if request.method == "GET":
        title = request.GET.get('q')
        listings = AuctionListings.objects.filter(title=title.lower())
        return render(request, "auctions/search.html", {
            "title": title,
            "listings": listings
        })
    else:
        return render(request, "auctions/404.html")

                
def not_found(request, not_found):
    return render(request, "auctions/404.html")


def listing_page(request, user, category, title):
    listing = AuctionListings.objects.filter(user=user,title=title)
    bids = Bids.objects.filter(listing=title,listing_user=user)
    comments = Comments.objects.filter(listing=title,listing_user=user)
    if request.user.is_authenticated:
        return render(request, "auctions/listing.html", {
            "logged_in": True,
            "listing": listing,
            "bids": bids,
            "comments": comments,
            "title": title,
            "category": category,
            "place_bid": PostBid,
            "post_comment": PostComment,
            "active_user": request.user.username
        })
    else:
        return render(request, "auctions/listing.html", {
            "logged_in": False,
            "listing": listing,
            "bids": bids,
            "comments": comments,
            "title": title,
            "category": category
        })

def create_listing_page(request):
    if request.user.is_authenticated:
        return render(request, "auctions/create.html", {
            "logged_in": True,
            "create": CreateListingForm,
        })
    else:
        return render(request, "auctions/create.html", {
            "logged_in": False
        })
    

def edit_listing_page(request, user, title):
    if request.user.is_authenticated:
        edit = AuctionListings.objects.filter(user=user,title=title)
        if edit:
            return render(request, "auctions/edit.html", {
                "active_user": request.user.username,
                "listing": edit,
                "categories": categories
            })
        else:
            return render(request, "auctions/404.html")
    else:
        return render(request, "auctions/404.html")
    

def delete_listing_page(request, user, title):
    if request.user.is_authenticated:
        delete = AuctionListings.objects.filter(user=user,title=title)
        if delete:
            return render(request, "auctions/delete.html", {
                "deleted": False,
                "delete_listing": delete,
                "active_user": request.user.username
            })
        else:
            return render(request, "auctions/404.html")
    else:
        return render(request, "auctions/404.html")
    

def watchlist_page(request):
    if request.user.is_authenticated:
        user_bids = Bids.objects.filter(bid_user=request.user.username)
        user_wins = Wins.objects.filter(win_user=request.user.username)
        return render(request, "auctions/watch.html", {
            "logged_in": True,
            "user_bids": user_bids,
            "user_wins": user_wins
        })
    else:
        return render(request, "auctions/watch.html", {
            "logged_in": False
        })

    
###############################################################################################################
    
def create_listing(request):
    if request.method == "POST":
        listing_title = request.POST.get('title')
        new_title = listing_title.lower()
        image = request.FILES.get('image')
        check = AuctionListings.objects.filter(title=new_title,user=request.user.username)
        if not check:
            new_listing = CreateListingForm(request.POST, request.FILES)
            if new_listing.is_valid():
                new_listing.save()
                created_listing = AuctionListings.objects.get(title=listing_title,user="")
                created_listing.title = new_title
                created_listing.user = request.user.username
                created_listing.last_modified = timezone.now()
                created_listing.save()
                image_model = Image.objects.create(image=image,listing=new_title,user=request.user.username)
                image_model.save()
                catg = created_listing.category
                return redirect(listing_page,user=request.user.username,category=catg,title=new_title)
            else:
                return HttpResponse(f"Form not valid")
        else:
            return render(request, "auctions/create.html", {
                "logged_in": True,
                "create": CreateListingForm,
                "exists": True
            })
    else:
        return render(request, "auctions/404.html")
    
def edit_listing(request, user, title):
    if request.method == "POST":
        new_category = request.POST.get('category')
        new_price = request.POST.get('price')
        new_image = request.FILES.get('image')
        new_description = request.POST.get('description')
        edited_listing = AuctionListings.objects.get(title=title,user=user)
        edit_image_model = Image.objects.get(listing=title,user=user)
        if new_image:
            edited_listing.image = new_image
            edited_listing.category = new_category
            edited_listing.price = new_price
            edited_listing.description = new_description
            edited_listing.user = user
            edited_listing.last_modified = timezone.now()
            edited_listing.save()
            edit_image_model.image = new_image
            edit_image_model.save()
            #return HttpResponse(f"Image")
        else:
            edited_listing.category = new_category
            edited_listing.price = new_price
            edited_listing.description = new_description
            edited_listing.user = user
            edited_listing.last_modified = timezone.now()
            edited_listing.save() 
            #return HttpResponse(f"No Image")
        return redirect(listing_page,user=user,category=new_category,title=title)
    else:
        return render(request, "auctions/404.html")
    
def delete_image(request, user, title):  
    if request.method == "POST":
        listing = AuctionListings.objects.get(title=title,user=user)
        image_model = Image.objects.get(listing=title,user=user)
        image_model.image.delete()
        listing.image.delete()
        return redirect(edit_listing_page,user=user,title=title)
    else:
        return render(request, "auctions/404.html")   

#def post_bid(request, user, title, catg, price):
    #if request.method == "POST":
        #bid = request.POST.get('bid')
        #time_posted = timezone.now()
        #post_bid = Bids.objects.create(bid=bid,bid_user=request.user.username,listing=title,listing_user=user,listing_catg=catg,listing_price=price,time_posted=time_posted)
        #post_bid.save()
        #return redirect(x)
    #else:
        #return HttpResponse(f"404")  
    
def delete_listing(request, user, title):
    if request.method =="POST":
        delete_listing = AuctionListings.objects.get(user=user,title=title)
        current_bids = Bids.objects.filter(listing_user=user,listing=title)
        comments = Comments.objects.filter(listing_user=user,listing=title)
        image = Image.objects.get(user=user,listing=title)
        if current_bids:
            higgest_bid = current_bids.aggregate(Max('bid'))['bid__max']
            winning_bid = Bids.objects.get(bid=higgest_bid,listing=title,listing_user=user)
            winner = winning_bid.bid_user
            amount = winning_bid.bid
            price = delete_listing.price
            description = delete_listing.description
            won_listing_catg = winning_bid.listing_catg
            win = Wins.objects.create(listing=title,listing_user=user,listing_category=won_listing_catg,listing_price=price,listing_description=description,win_user=winner,win_amount=amount,time_closed=timezone.now())
            win.save()
            win_message = Wins.objects.filter(listing=title,listing_user=user,listing_category=won_listing_catg,listing_price=price,listing_description=description,win_user=winner,win_amount=amount)
            if comments:
                delete_listing.delete()
                current_bids.delete()
                comments.delete()
                return render(request, "auctions/delete.html", {
                    "deleted": True,
                    "deleted_listing": title,
                    "win": True,
                    "win_message": win_message
                })
            else:
                delete_listing.delete()
                current_bids.delete()
                return render(request, "auctions/delete.html", {
                    "deleted": True,
                    "deleted_listing": title,
                    "win": True,
                    "win_message": win_message
                })
        else:
            if comments:
                delete_listing.delete()
                comments.delete()
                image.delete()
                return render(request, "auctions/delete.html", {
                    "deleted": True,
                    "deleted_listing": title,
                })
            else:
                delete_listing.delete()
                image.delete()
                return render(request, "auctions/delete.html", {
                    "deleted": True,
                    "deleted_listing": title,
                })
    else:
        return render(request, "auctions/404.html")      

def post_bid(request, user, title, catg, price):
    listing = AuctionListings.objects.filter(user=user,title=title)
    bids = Bids.objects.filter(listing=title,listing_user=user)
    comments = Comments.objects.filter(listing=title,listing_user=user)
    if request.method == "POST":
        bid_amount = request.POST.get('bid')
        bid_int = int(bid_amount)
        price_int = int(price)
        time_posted = timezone.now()
        listing_bids = Bids.objects.filter(listing=title,listing_user=user)
        if listing_bids:
            highest_bid = listing_bids.aggregate(Max('bid'))['bid__max']
            if highest_bid >= bid_int:
                return render(request, "auctions/listing.html", {
                    "logged_in": True,
                    "listing": listing,
                    "bids": bids,
                    "comments": comments,
                    "title": title,
                    "category": catg,
                    "place_bid": PostBid,
                    "post_comment": PostComment,
                    "active_user": request.user.username,
                    "low_bid": True,
                    "higgest_bid": highest_bid
                })
            else:
                user_bid = Bids.objects.filter(listing=title,listing_user=user,bid_user=request.user.username)
                if user_bid:
                    clear_bid = Bids.objects.get(listing=title,listing_user=user,bid_user=request.user.username)
                    clear_bid.delete()
                    new_user_bid = Bids.objects.create(bid=bid_amount,bid_user=request.user.username,listing=title,listing_user=user,listing_catg=catg,listing_price=price,time_posted=time_posted)
                    new_user_bid.save()
                    return redirect(listing_page,user=user,category=catg,title=title)
                else:
                    new_bid = Bids.objects.create(bid=bid_amount,bid_user=request.user.username,listing=title,listing_user=user,listing_catg=catg,listing_price=price,time_posted=time_posted)
                    new_bid.save()
                    return redirect(listing_page,user=user,category=catg,title=title)
        else:
            if price_int > bid_int:
                return render(request, "auctions/listing.html", {
                    "logged_in": True,
                    "listing": listing,
                    "bids": bids,
                    "comments": comments,
                    "title": title,
                    "category": catg,
                    "place_bid": PostBid,
                    "post_comment": PostComment,
                    "active_user": request.user.username,
                    "low_start": True
                })
            else:
                post_bid = Bids.objects.create(bid=bid_amount,bid_user=request.user.username,listing=title,listing_user=user,listing_catg=catg,listing_price=price,time_posted=time_posted)
                post_bid.save()
                return redirect(listing_page,user=user,category=catg,title=title)
    else:
        return render(request, "auctions/404.html")        

def post_comment(request, user, title):
    if request.method == "POST":
        comment = request.POST.get('comment')
        time_posted = timezone.now()
        post_comment = Comments.objects.create(comment=comment,comment_user=request.user.username,listing=title,listing_user=user,time_posted=time_posted)
        post_comment.save()
        get_catg = AuctionListings.objects.get(user=user,title=title)
        catg = get_catg.category
        return redirect(listing_page,user=user,category=catg,title=title)
    else:
        return render(request, "auctions/404.html")

def withdraw_bid(request, bid_user, bid, listing, listing_user):
    if request.method == "POST":
        delete_bid = Bids.objects.get(bid=bid,bid_user=bid_user,listing=listing,listing_user=listing_user)
        catg = delete_bid.listing_catg
        delete_bid.delete()
        return redirect(listing_page,user=listing_user,category=catg,title=listing)
    else:
        return render(request, "auctions/404.html")
    
def withdraw_bid_w(request, bid_user, bid, listing, listing_user):
    if request.method == "POST":
        delete_bid = Bids.objects.get(bid=bid,bid_user=bid_user,listing=listing,listing_user=listing_user)
        delete_bid.delete()
        return redirect(watchlist_page)
    else:
        return render(request, "auctions/404.html")

def delete_comment(request, comment_user, comment, listing, listing_user):
    if request.method == "POST":
        delete_comment = Comments.objects.get(comment=comment,comment_user=comment_user,listing=listing,listing_user=listing_user)
        get_catg = AuctionListings.objects.get(user=listing_user,title=listing)
        catg = get_catg.category
        delete_comment.delete()
        return redirect(listing_page,user=listing_user,category=catg,title=listing)
    else:
        return render(request, "auctions/404.html")
    
def win_page(request, winner, user, listing):
    if request.user.is_authenticated:
        win_details = Wins.objects.filter(win_user=winner,listing_user=user,listing=listing)
        win_img = Image.objects.filter(listing=listing,user=user)
        if win_details:
            return render(request, "auctions/win.html", {
                "win": win_details,
                "active_user": request.user.username,
                "image": win_img
            })
        else:
            return render(request, "auctions/404.html")
    else:
        return render(request, "auctions/404.html")    
