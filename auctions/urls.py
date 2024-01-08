from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create listing"),
    path("create_listing_page", views.create_listing_page, name="create"),
    path("categories", views.categories_page, name="categories"),
    path("watchlist", views.watchlist_page, name="watchlist"),
    path("edit_listing_page/<str:user>/<str:title>", views.edit_listing_page),
    path("listings/<str:user>/<str:category>/<str:title>", views.listing_page),
    path("categories/<str:category>", views.category_page ),
    path("delete_image/<str:user>/<str:title>", views.delete_image),
    path("edit_listing/<str:user>/<str:title>", views.edit_listing),
    path("delete_listing_page/<str:user>/<str:title>", views.delete_listing_page),
    path("delete_listing/<str:user>/<str:title>", views.delete_listing),
    path("post_bid/<str:user>/<str:title>/<str:catg>/<str:price>", views.post_bid),
    path("post_comment/<str:user>/<str:title>", views.post_comment),
    path("withdraw_bid/<str:bid_user>/<str:bid>/<str:listing>/<str:listing_user>", views.withdraw_bid),
    path("withdraw_bid_w/<str:bid_user>/<str:bid>/<str:listing>/<str:listing_user>", views.withdraw_bid_w),
    path("delete_comment/<str:comment_user>/<str:comment>/<str:listing>/<str:listing_user>", views.delete_comment),
    path("win/<str:winner>/<str:user>/<str:listing>", views.win_page),
    path("search", views.search, name="search"),
    path("<str:not_found>", views.not_found)
]
