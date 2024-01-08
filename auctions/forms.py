from django import forms
from .models import AuctionListings, Bids, Comments

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListings
        #widgets = {'user': forms.HiddenInput(), 'last_modified': forms.HiddenInput()}
        #fields = "__all__"
        exclude = ['user','last_modified']    


class PostBid(forms.ModelForm):
    class Meta:
        model = Bids
        exclude = ['bid_user','listing','listing_catg','listing_price','listing_user','time_posted']     


class PostComment(forms.ModelForm):
    class Meta:
        model = Comments
        exclude = ['comment_user','listing','listing_user','time_posted']              