# -*- coding: UTF-8 -*-
from django.contrib import admin
from models import *

class geoAdmin(admin.ModelAdmin):
    """ Django admin class for geo microformat """
    list_filter = ('latitude', 'longitude')
    save_on_top = True

class hCardAdmin(admin.ModelAdmin):
    """ Django admin class for flat hCard microformat """
    list_display = ('given_name', 'family_name', 'org', 'url')
    list_display_links = ('given_name', 'org')
    list_filter = ('family_name', 'org')
    save_on_top = True
    search_fields = ('given_name', 'family_name', 'org')

class hCalendarAdmin(admin.ModelAdmin):
    """ Django admin class for flat hCalendar microformat """
    list_display = ('dtstart', 'dtend', 'summary', 'location')
    list_display_links = ('dtstart', 'summary')
    list_filter = ('dtstart', 'dtend')
    save_on_top = True
    search_fields = ('summary', 'description', 'location')

class hListingAdmin(admin.ModelAdmin):
    """ Django admin class for hListing microformat """
    list_display = (
            'listing_action', 
            'description', 
            'lister_fn', 
            'item_fn',
            'price',
            )
    list_display_links = ('listing_action', 'description')
    list_filter = ('listing_action',)
    save_on_top = True
    search_fields = ('description', 'lister_fn', 'item_fn')

class hReviewAdmin(admin.ModelAdmin):
    """ Django admin class for hReview microformat """
    list_display = ('fn', 'reviewer', 'rating', 'summary')
    list_display_links = ('fn', 'rating', 'summary')
    list_filter = ('fn', 'rating')
    save_on_top = True
    search_fields = ('fn', 'reviewer', 'description', 'summary')

class hEntryAdmin(admin.ModelAdmin):
    """ Django admin class for hEntry microformat """
    list_display = ('entry_title', 'author', 'updated', 'entry_summary')
    list_display_links = ('entry_title',)
    list_filter = ('author', 'updated')
    save_on_top = True
    search_fields = ('entry_title', 'entry_content', 'entry_summary', 'author')

admin.site.register(geo, geoAdmin)
admin.site.register(hCard, hCardAdmin)
admin.site.register(hCalendar, hCalendarAdmin)
admin.site.register(hListing, hListingAdmin)
admin.site.register(hReview, hReviewAdmin)
admin.site.register(hEntry, hEntryAdmin)
admin.site.register(adr_type)
admin.site.register(adr)
admin.site.register(tel_type)
admin.site.register(tel)
admin.site.register(email_type)
admin.site.register(email)
admin.site.register(photo)
admin.site.register(logo)
admin.site.register(sound)
admin.site.register(title)
admin.site.register(role)
admin.site.register(org)
admin.site.register(note)
admin.site.register(key)
admin.site.register(mailer)
admin.site.register(xfn_values)
admin.site.register(xfn)
admin.site.register(hFeed)
