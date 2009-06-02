# -*- coding: UTF-8 -*-
"""
Custom templatetags tests for microformats 

Author: Nicholas H.Tollervey

"""
# python
import datetime
import codecs
import os

# django
from django.test.client import Client
from django.test import TestCase
from django.template import Context, Template
from django.template.loader import get_template
from django.contrib.auth.models import User

# project
import microformats.models 
from microformats.templatetags.microformat_extras import *

class TemplateTagsTestCase(TestCase):
        """
        Testing custom templatetags 
        """
        # Reference fixtures here
        fixtures = []

        def test_geo(self):
            """
            Make sure we can render the geo microformat correctly 
            """
            # Safe case with an instance
            g = microformats.models.geo()
            g.latitude = 37.408183
            g.latitude_description = 'N 37° 24.491'
            g.longitude = -122.13855
            g.longitude_description = 'W 122° 08.313'
            g.save()
            # With no arg
            result = geo(g, autoescape=True)
            expected = u'''\n<div class="geo">\n    <abbr class="latitude" title="37.408183">\n    N 37\xb0 24.491\n    </abbr>&nbsp;\n    <abbr class="longitude" title="-122.13855">\n    W 122\xb0 08.313\n    </abbr>\n</div>\n'''
            self.assertEquals(expected, result) 
            # With an arg
            result = geo(g, arg="Geo", autoescape=True)
            expected = u'\n<div class="geo">\n    <abbr class="latitude" title="37.408183">\n    N 37\xb0 24.491\n    </abbr>&nbsp;\n    <abbr class="longitude" title="-122.13855">\n    W 122\xb0 08.313\n    </abbr>\n</div>\n'
            self.assertEquals(expected, result) 
            # An instance without any description fields
            g.latitude_description = ''
            g.longitude_description = ''
            g.save()
            result = geo(g, autoescape=True)
            expected = u'\n<div class="geo">\n    <abbr class="latitude" title="37.408183">\n    37.408183\n    </abbr>&nbsp;\n    <abbr class="longitude" title="-122.13855">\n    -122.13855\n    </abbr>\n</div>\n'
            self.assertEquals(expected, result) 
            # Test Geocode fragments
            result = geo(g.latitude, arg="latitude", autoescape=True)
            expected = u'<abbr class="latitude" title="37.408183">37.408183</abbr>'
            self.assertEquals(expected, result) 
            result = geo(g.longitude, arg="longitude", autoescape=True)
            expected = u'<abbr class="longitude" title="-122.13855">-122.13855</abbr>'
            self.assertEquals(expected, result) 

        def test_fragment(self):
            """
            The fragment function being exercised
            """
            # Test that an unknown arg results in the return of the raw value in
            # an appropriatly formatted span

            # Generic call results in the span
            result = fragment("foo", arg="bar", autoescape=True)
            expected = u'<span class="bar">foo</span>'
            self.assertEquals(expected, result) 

            # multiple classes in the arg result in the correct class
            result = fragment("foo", arg="bar baz", autoescape=True)
            expected = u'<span class="bar baz">foo</span>'
            self.assertEquals(expected, result) 

            # override the formatting of date-time data
            dt = datetime.datetime.today()
            result = fragment(dt, arg="dtstart %a %b %d %Y", autoescape=True)
            expected = u'<abbr class="dtstart" title="%s">%s</abbr>' % (
                            dt.isoformat(),
                            dt.strftime('%a %b %d %Y')
                            )
            self.assertEquals(expected, result)
            result = fragment(dt, arg="dtstart right now", autoescape=True)
            expected = u'<abbr class="dtstart" title="%s">right now</abbr>' % (
                            dt.isoformat(),
                            )
            self.assertEquals(expected, result)
            result = fragment(dt, arg="dtstart", autoescape=True)
            expected = u'<abbr class="dtstart" title="%s">%s</abbr>' % (
                            dt.isoformat(),
                            dt.strftime('%c')
                            )
            self.assertEquals(expected, result)

            # Check for geo related abbr pattern
            result = fragment(37.408183, arg="latitude", autoescape=True)
            expected = u'<abbr class="latitude" title="37.408183">37.408183</abbr>'
            self.assertEquals(expected, result)

            result = fragment(37.408183, arg="lat", autoescape=True)
            self.assertEquals(expected, result)

            result = fragment(-122.13855, arg="longitude", autoescape=True)
            expected = u'<abbr class="longitude" title="-122.13855">-122.13855</abbr>'
            self.assertEquals(expected, result)

            result = fragment(-122.13855, arg="long", autoescape=True)
            self.assertEquals(expected, result)

            # Check for email address anchor element (this depends on the value
            # of the field *NOT* the name of the class passed as an arg)
            result = fragment('joe@blogs.com', arg='foo', autoescape=True)
            expected = u'<a class="foo" href="mailto:joe@blogs.com">joe@blogs.com</a>'
            self.assertEquals(expected, result)

            # Check for URL anchor element (works in the same way as email but
            # with a different regex)
            result = fragment('http://foo.com', arg='bar', autoescape=True)
            expected = u'<a class="bar" href="http://foo.com">http://foo.com</a>'
            self.assertEquals(expected, result)

            # Lets make sure we can handle ints and floats
            result = fragment(1.234, arg='foo', autoescape=True)
            expected = u'<span class="foo">1.234</span>'
            self.assertEquals(expected, result)

            result = fragment(1234, arg='foo', autoescape=True)
            expected = u'<span class="foo">1234</span>'
            self.assertEquals(expected, result)

        def test_non_microformat_model_rendering(self):
            """
            Make sure we can render objects that are not microformat models from
            this application but that have attributes that conform to the
            microformat naming conventions.
            """
            # Lets just test this with a dict 
            hc = dict()
            hc['honorific_prefix'] = 'Mr'
            hc['given_name'] = 'Joe'
            hc['additional_name'] = 'Arthur'
            hc['family_name'] = 'Blogs'
            hc['honorific_suffix'] = 'PhD'
            hc['url'] = 'http://acme.com/'
            hc['email_work'] = 'joe.blogs@acme.com'
            hc['email_home'] = 'joe.blogs@home-isp.com'
            hc['tel_work'] = '+44(0)1234 567876'
            hc['tel_home'] = '+44(0)1543 234345'
            hc['street_address'] = '5445 N. 27th Street'
            hc['extended_address'] = ''
            hc['locality'] = 'Milwaukee'
            hc['region'] = 'WI'
            hc['country_name'] = 'US'
            hc['postal_code'] = '53209'
            hc['title'] = 'Vice President'
            hc['org'] = 'Acme Corp.'
            result = hcard(hc, autoescape=True)
            expected = u'\n<div id="hcard_" class="vcard">\n    <div class="fn n">\n        <a href="http://acme.com/" class="url">\n        \n            <span class="honorific-prefix">Mr</span>\n            <span class="given-name">Joe</span>\n            <span class="additional-name">Arthur</span>\n            <span class="family-name">Blogs</span>\n            <span class="honorific-suffix">PhD</span>\n        \n        </a>\n    </div>\n    \n    <span class="title">Vice President</span>\n    \n    <div class="org">Acme Corp.</div>\n    \n    \n    <a class="email" href="mailto:joe.blogs@acme.com">joe.blogs@acme.com</a> [work]<br/> \n    <a class="email" href="mailto:joe.blogs@home-isp.com">joe.blogs@home-isp.com</a> [home]<br/> \n    \n<div class="adr">\n    <div class="street-address">5445 N. 27th Street</div>\n    \n    <span class="locality">Milwaukee</span>&nbsp;\n    <span class="region">WI</span>&nbsp;\n    <span class="postal-code">53209</span>&nbsp;\n    <span class="country-name">US</span>\n</div>\n\n    <div class="tel"><span class="value">+44(0)1234 567876</span> [<abbr class="type" title="work">work</abbr>]</div>\n    <div class="tel"><span class="value">+44(0)1543 234345</span> [<abbr class="type" title="home">home</abbr>]</div>\n    \n</div>\n'
            self.assertEquals(expected, result)

        def test_hcard(self):
            """
            Make sure we have a pass-able means of rendering an hCard
            """
            # Start with a happy case
            hc = microformats.models.hCard()
            hc.honorific_prefix = 'Mr'
            hc.given_name = 'Joe'
            hc.additional_name = 'Arthur'
            hc.family_name = 'Blogs'
            hc.honorific_suffix = 'PhD'
            hc.url = 'http://acme.com/'
            hc.email_work = 'joe.blogs@acme.com'
            hc.email_home = 'joe.blogs@home-isp.com'
            hc.tel_work = '+44(0)1234 567876'
            hc.tel_home = '+44(0)1543 234345'
            hc.street_address = '5445 N. 27th Street'
            hc.extended_address = ''
            hc.locality = 'Milwaukee'
            hc.region = 'WI'
            hc.country_name = 'US'
            hc.postal_code = '53209'
            hc.title = 'Vice President'
            hc.org = 'Acme Corp.'
            hc.save()
            result = hcard(hc, autoescape=True)
            expected = u'\n<div id="hcard_1" class="vcard">\n    <div class="fn n">\n        <a href="http://acme.com/" class="url">\n        \n            <span class="honorific-prefix">Mr</span>\n            <span class="given-name">Joe</span>\n            <span class="additional-name">Arthur</span>\n            <span class="family-name">Blogs</span>\n            <span class="honorific-suffix">PhD</span>\n        \n        </a>\n    </div>\n    \n    <span class="title">Vice President</span>\n    \n    <div class="org">Acme Corp.</div>\n    \n    \n    <a class="email" href="mailto:joe.blogs@acme.com">joe.blogs@acme.com</a> [work]<br/> \n    <a class="email" href="mailto:joe.blogs@home-isp.com">joe.blogs@home-isp.com</a> [home]<br/> \n    \n<div class="adr">\n    <div class="street-address">5445 N. 27th Street</div>\n    \n    <span class="locality">Milwaukee</span>&nbsp;\n    <span class="region">WI</span>&nbsp;\n    <span class="postal-code">53209</span>&nbsp;\n    <span class="country-name">United States</span>\n</div>\n\n    <div class="tel"><span class="value">+44(0)1234 567876</span> [<abbr class="type" title="work">work</abbr>]</div>\n    <div class="tel"><span class="value">+44(0)1543 234345</span> [<abbr class="type" title="home">home</abbr>]</div>\n    \n</div>\n'
            self.assertEquals(expected, result)
            # Lets make sure we can get a valid hCard when it is for an
            # organisation
            hc.honorific_prefix = ''
            hc.given_name = ''
            hc.additional_name = ''
            hc.family_name = ''
            hc.honorific_suffix = ''
            hc.save()
            result = hcard(hc, autoescape=True)
            expected = u'\n<div id="hcard_1" class="vcard">\n    <div class="fn n">\n        <a href="http://acme.com/" class="url">\n        \n        <span class="org">Acme Corp.</span>\n        \n        </a>\n    </div>\n    \n    <a class="email" href="mailto:joe.blogs@acme.com">joe.blogs@acme.com</a> [work]<br/> \n    <a class="email" href="mailto:joe.blogs@home-isp.com">joe.blogs@home-isp.com</a> [home]<br/> \n    \n<div class="adr">\n    <div class="street-address">5445 N. 27th Street</div>\n    \n    <span class="locality">Milwaukee</span>&nbsp;\n    <span class="region">WI</span>&nbsp;\n    <span class="postal-code">53209</span>&nbsp;\n    <span class="country-name">United States</span>\n</div>\n\n    <div class="tel"><span class="value">+44(0)1234 567876</span> [<abbr class="type" title="work">work</abbr>]</div>\n    <div class="tel"><span class="value">+44(0)1543 234345</span> [<abbr class="type" title="home">home</abbr>]</div>\n    \n</div>\n'
            self.assertEquals(expected, result)
            # No address, org, url and email and minimum telephone information
            hc.url = ''
            hc.email_work = ''
            hc.email_home = ''
            hc.street_address = ''
            hc.extended_address = ''
            hc.locality = ''
            hc.region = ''
            hc.country_name = ''
            hc.postal_code = ''
            hc.title = ''
            hc.org = ''
            hc.url = ''
            hc.honorific_prefix = 'Mr'
            hc.given_name = 'Joe'
            hc.additional_name = 'Arthur'
            hc.family_name = 'Blogs'
            hc.honorific_suffix = 'PhD'
            hc.save()
            result = hcard(hc, autoescape=True)
            expected = u'\n<div id="hcard_1" class="vcard">\n    <div class="fn n">\n        \n        \n            <span class="honorific-prefix">Mr</span>\n            <span class="given-name">Joe</span>\n            <span class="additional-name">Arthur</span>\n            <span class="family-name">Blogs</span>\n            <span class="honorific-suffix">PhD</span>\n        \n        \n    </div>\n    \n    \n    \n    \n     \n     \n    \n<div class="adr">\n    \n    \n    \n    \n    \n    \n</div>\n\n    <div class="tel"><span class="value">+44(0)1234 567876</span> [<abbr class="type" title="work">work</abbr>]</div>\n    <div class="tel"><span class="value">+44(0)1543 234345</span> [<abbr class="type" title="home">home</abbr>]</div>\n    \n</div>\n'
            self.assertEquals(expected, result)
            # Absolute minimum
            hc.honorific_prefix = ''
            hc.additional_name = ''
            hc.honorific_suffix = ''
	    hc.tel_work = ''
	    hc.tel_home = ''
	    hc.save()
            result = hcard(hc, autoescape=True)
            expected = u'\n<div id="hcard_1" class="vcard">\n    <div class="fn n">\n        \n        \n            \n            <span class="given-name">Joe</span>\n            \n            <span class="family-name">Blogs</span>\n            \n        \n        \n    </div>\n    \n    \n    \n    \n     \n     \n    \n<div class="adr">\n    \n    \n    \n    \n    \n    \n</div>\n\n    \n    \n    \n</div>\n'
            self.assertEquals(expected, result)

        def test_adr(self):
            """
            Lets make sure we get a good address with or without types
            """
            # With type
            at = microformats.models.adr_type.objects.get(id=5)
            a = microformats.models.adr()
            a.street_address = 'Flat 29a'
            a.extended_address = '123 Somewhere Street'
            a.locality = 'Townsville'
            a.region = 'Countyshire'
            a.country_name = 'GB'
            a.postal_code = 'CS23 6YT'
            a.save()
            a.types.add(at)
            a.save()
            result = adr(a, autoescape=True)
            expected = u'\n<div class="adr">\n    <div class="street-address">Flat 29a</div>\n    <div class="extended-address">123 Somewhere Street</div>\n    <span class="locality">Townsville</span>&nbsp;\n    <span class="region">Countyshire</span>&nbsp;\n    <span class="postal-code">CS23 6YT</span>&nbsp;\n    <span class="country-name">United Kingdom</span>\n</div>\n'
            self.assertEquals(expected, result)
            # Without type
            a.types.clear()
            a.save()
            result = adr(a, autoescape=True)
            expected = u'\n<div class="adr">\n    <div class="street-address">Flat 29a</div>\n    <div class="extended-address">123 Somewhere Street</div>\n    <span class="locality">Townsville</span>&nbsp;\n    <span class="region">Countyshire</span>&nbsp;\n    <span class="postal-code">CS23 6YT</span>&nbsp;\n    <span class="country-name">United Kingdom</span>\n</div>\n'
            self.assertEquals(expected, result)

        def test_hcal(self):
            """
            Check we get the expected results for an hCalendar
            """
            hc = microformats.models.hCalendar()
            hc.summary = 'Important Meeting'
            hc.location = 'BBC in London'
            hc.url = 'http://www.bbc.co.uk/'
            hc.dtstart = datetime.datetime(2009, 4, 11, 13, 30)
            hc.dtend = datetime.datetime(2009, 4, 11, 15, 30)
            hc.description = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            hc.street_address = 'Broadcasting House'
            hc.extended_address = 'Portland Place'
            hc.locality = 'London'
            hc.region = ''
            hc.country_name = 'GB'
            hc.postal_code = 'W1A 1AA'
            hc.save()
            hc.save()
            result = hcal(hc, autoescape=True)
            expected = u'\n<div id="hcalendar_1" class="vevent">\n    <a href="http://www.bbc.co.uk/" class="url">\n        \n        <abbr title="2009-04-11T13:30:00" class="dtstart">Sat 11 Apr 2009 1:30 p.m.</abbr>\n        \n        \n            &nbsp;-&nbsp;\n            \n            <abbr title="2009-04-11T15:30:00" class="dtend">All day event</abbr>\n            \n        \n        :&nbsp;\n        <span class="summary">Important Meeting</span>\n         at <span class="location">BBC in London</span>\n    </a>\n    \n<div class="adr">\n    <div class="street-address">Broadcasting House</div>\n    <div class="extended-address">Portland Place</div>\n    <span class="locality">London</span>&nbsp;\n    \n    <span class="postal-code">W1A 1AA</span>&nbsp;\n    <span class="country-name">United Kingdom</span>\n</div>\n\n    <p class="description">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>    \n</div>\n'
            self.assertEquals(expected, result)
            # Make sure things render correctly *if* all_day_event = True
            hc.all_day_event = True
            hc.save()
            result = hcal(hc, autoescape=True)
            expected = u'\n<div id="hcalendar_1" class="vevent">\n    <a href="http://www.bbc.co.uk/" class="url">\n        \n        <abbr title="2009-04-11T13:30:00" class="dtstart">Sat 11 Apr 2009</abbr>\n        \n        \n            &nbsp;-&nbsp;\n            \n            <abbr title="2009-04-11T15:30:00" class="dtend">All day event</abbr>\n            \n        \n        :&nbsp;\n        <span class="summary">Important Meeting</span>\n         at <span class="location">BBC in London</span>\n    </a>\n    \n<div class="adr">\n    <div class="street-address">Broadcasting House</div>\n    <div class="extended-address">Portland Place</div>\n    <span class="locality">London</span>&nbsp;\n    \n    <span class="postal-code">W1A 1AA</span>&nbsp;\n    <span class="country-name">United Kingdom</span>\n</div>\n\n    <p class="description">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>    \n</div>\n'
            self.assertEquals(expected, result)
            hc.all_day_event = False
            hc.save()
            # Lets cut things down to the essentials with a different end date
            hc.url = ''
            hc.location = ''
            hc.description = ''
            hc.street_address = ''
            hc.extended_address = ''
            hc.locality = ''
            hc.region = ''
            hc.country_name = ''
            hc.postal_code = ''
            hc.dtend = datetime.datetime(2009, 4, 15, 15, 30)
            hc.save()
            result = hcal(hc, autoescape=True)
            expected = u'\n<div id="hcalendar_1" class="vevent">\n    \n        \n        <abbr title="2009-04-11T13:30:00" class="dtstart">Sat 11 Apr 2009 1:30 p.m.</abbr>\n        \n        \n            &nbsp;-&nbsp;\n            \n            <abbr title="2009-04-15T15:30:00" class="dtend">3:30 p.m.</abbr>\n            \n        \n        :&nbsp;\n        <span class="summary">Important Meeting</span>\n        \n    \n    \n<div class="adr">\n    \n    \n    \n    \n    \n    \n</div>\n\n        \n</div>\n'
            self.assertEquals(expected, result)
            # Absolute minimum
            hc.dtend = None
            hc.dtstart = datetime.datetime(2009, 4, 15)
            result = hcal(hc, autoescape=True)
            # We probably want to separate the date and time of dtstart and
            # dtend so we don't default to midnight... ToDo: Fix date/time
            expected = u'\n<div id="hcalendar_1" class="vevent">\n    \n        \n        <abbr title="2009-04-15T00:00:00" class="dtstart">Wed 15 Apr 2009 midnight</abbr>\n        \n        \n        :&nbsp;\n        <span class="summary">Important Meeting</span>\n        \n    \n    \n<div class="adr">\n    \n    \n    \n    \n    \n    \n</div>\n\n        \n</div>\n'
            self.assertEquals(expected, result)

        def test_hlisting(self):
            """
            Check we get the expected results for an hListing
            """
            listing = microformats.models.hListing()
            listing.listing_action = "sell"
            listing.summary = "Pony requires a good home"
            listing.description = "A young pony who answers to the name Django"\
                " requires a new home having outgrown his current host. Easy"\
                " going and fun to play with Django also provides rainbow"\
                " manure that is sure to help the garden grow."
            listing.lister_fn = "John Doe"
            listing.lister_email = "john.doe@isp.net"
            listing.lister_url = "http://isp.com/django_the_pony"
            listing.lister_tel = "+44(0) 1234 567456"
            listing.dtlisted = datetime.datetime(2009, 5, 6)
            listing.dtexpired = datetime.datetime(2009, 8, 19)
            listing.price = "£2500 ono"
            listing.item_fn = "Django the Pony"
            listing.item_url = "http://djangoproject.com/"
            listing.locality = "Brighton"
            listing.country_name = "GB"
            listing.save()
            result = hlisting(listing, autoescape=True)
            expected = u'\n<div class="hlisting">\n    <p>\n        <span class="item vcard">\n        <a href="http://djangoproject.com/" class="url">\n            <span class="fn">Django the Pony</span>\n        </a>\n        \n        <span class="location">\n        \n<div class="adr">\n    \n    \n    <span class="locality">Brighton</span>&nbsp;\n    \n    \n    <span class="country-name">United Kingdom</span>\n</div>\n\n        </span>\n        \n        </span>\n        <span class="sell">To sell</span>\n        (<abbr class="dtlisted" title="2009-05-06T00:00:00">Wed 06 May 2009</abbr>)\n        <p class="summary">Pony requires a good home</p>\n        <p class="description">A young pony who answers to the name Django requires a new home having outgrown his current host. Easy going and fun to play with Django also provides rainbow manure that is sure to help the garden grow.</p>\n        \n        <p>Available from: <abbr class="dtexpired" title="2009-08-19T00:00:00">Wed 19 Aug 2009</abbr></p>\n        \n        \n        <p>Price: <span class="price">\xa32500 ono</span></p>\n        \n        <div class="lister vcard">\n            <p>For more information, please contact\n            <a href="http://isp.com/django_the_pony" class="url">\n                <span class="fn">John Doe</span>\n            </a>\n            <a href="mailto:john.doe@isp.net" class="email">john.doe@isp.net</a>\n            <span class="tel"><span class="value">+44(0) 1234 567456</span></span>\n            </p>\n        </div>\n    </p>\n</div>\n'
            self.assertEquals(expected, result)
            # Lets cut things down to the minimum
            listing.summary = ""
            listing.description = "A young pony who answers to the name Django"\
                " requires a new home having outgrown his current host. Easy"\
                " going and fun to play with Django also provides rainbow"\
                " manure that is sure to help the garden grow."
            listing.lister_fn = "John Doe"
            listing.lister_email = ""
            listing.lister_url = ""
            listing.lister_tel = ""
            listing.dtlisted = None 
            listing.dtexpired = None
            listing.price = ""
            listing.item_fn = "Django the Pony"
            listing.item_url = ""
            listing.locality = ""
            listing.country_name = ""
            listing.save()
            result = hlisting(listing, autoescape=True)
            expected=u'\n<div class="hlisting">\n    <p>\n        <span class="item vcard">\n        \n            <span class="fn">Django the Pony</span>\n        \n        \n        </span>\n        <span class="sell">To sell</span>\n        \n        \n        <p class="description">A young pony who answers to the name Django requires a new home having outgrown his current host. Easy going and fun to play with Django also provides rainbow manure that is sure to help the garden grow.</p>\n        \n        \n        <div class="lister vcard">\n            <p>For more information, please contact\n            \n                <span class="fn">John Doe</span>\n            \n            \n            \n            </p>\n        </div>\n    </p>\n</div>\n'
            self.assertEquals(expected, result)

        def test_hreview(self):
            """
            Check we get the expected results for an hReview
            """
            rev1 = microformats.models.hReview()
            rev1.summary="Acme's new services rock!"
            rev1.type='business'
            rev1.description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.'
            rev1.rating=4
            rev1.dtreviewed=datetime.datetime(2009,4,10)
            rev1.reviewer='John Smith'
            rev1.fn='Acme Corp'
            rev1.url='http://acme.com'
            rev1.tel='+44(0)1234 567456'
            rev1.street_address = '5445 N. 27th Street'
            rev1.extended_address = ''
            rev1.locality = 'Milwaukee'
            rev1.region = 'WI'
            rev1.country_name = 'US'
            rev1.postal_code = '53209'
            rev1.save()
            rev2 = microformats.models.hReview()
            rev2.summary = 'A phenomenal tuba recital'
            rev2.description = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.'
            rev2.rating=5
            rev2.type='event'
            rev2.reviewer='John Doe'
            rev2.fn='John Fletcher - One man and his Tuba'
            rev2.url='http://www.johnfletcher-tuba.co.uk/'
            rev2.dtstart = datetime.datetime(1987, 10, 3, 19, 30)
            rev2.street_address = 'The Pro Arte Theatre'
            rev2.locality = 'London'
            rev2.save()
            rev3 = microformats.models.hReview()
            rev3.summary = 'Latest Star-Wars is Sucko-Barfo'
            rev3.description = 'Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.'
            rev3.rating=1
            rev3.type='film'
            rev3.reviewer='Barry Norman'
            rev3.fn='Star Wars - Revenge of the Sith'
            rev3.url='http://www.starwars.com/movies/episode-iii/'
            rev3.save()
            # Test for a review concerning something represented by an hCard
            result = hreview(rev1, autoescape=True) 
            expected = u'\n<div class="hreview">\n    <strong class="summary">Acme&#39;s new services rock!</strong>\n    <abbr class="type" title="business"> Business</abbr> Review\n    <br/>\n    \n    <abbr title="" class="dtreviewed">Fri 10 Apr 2009</abbr>\n    \n    by\n    <span class="reviewer vcard"><span class="fn">John Smith</span></span>\n    \n        \n    <div class="item vcard">\n        \n        <a class="url fn org" href="http://acme.com">\n        \n        Acme Corp\n        \n        </a>\n        \n        <div class="tel">+44(0)1234 567456</div>\n        \n        \n<div class="adr">\n    <div class="street-address">5445 N. 27th Street</div>\n    \n    <span class="locality">Milwaukee</span>&nbsp;\n    <span class="region">WI</span>&nbsp;\n    <span class="postal-code">53209</span>&nbsp;\n    <span class="country-name">United States</span>\n</div>\n\n        \n    </div>\n        \n    \n    \n    \n    \n    \n    <abbr class="rating" title="4">\u2605\u2605\u2605\u2605\u2606</abbr>\n    \n    \n    \n    <blockquote class="description">\n        Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.\n    </blockquote>\n    \n</div>\n'
            self.assertEquals(expected, result)
            # Test for a review concerning something represented by an hCalendar
            result = hreview(rev2, autoescape=True) 
            expected = u'\n<div class="hreview">\n    <strong class="summary">A phenomenal tuba recital</strong>\n    <abbr class="type" title="event"> Event</abbr> Review\n    <br/>\n    \n    by\n    <span class="reviewer vcard"><span class="fn">John Doe</span></span>\n    \n    <div class ="item vevent">\n        <a href="http://www.johnfletcher-tuba.co.uk/" class="url">\n        \n        <abbr title="1987-10-03T19:30:00" class="dtstart">Sat 03 Oct 1987 7:30 p.m.</abbr>\n        \n        \n        </a> -\n        <span class="summary">John Fletcher - One man and his Tuba</span>\n        \n        \n<div class="adr">\n    <div class="street-address">The Pro Arte Theatre</div>\n    \n    <span class="locality">London</span>&nbsp;\n    \n    \n    \n</div>\n\n        \n    </div>\n    \n    \n    \n    \n    \n    \n    <abbr class="rating" title="5">\u2605\u2605\u2605\u2605\u2605</abbr>\n    \n    \n    <blockquote class="description">\n        Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.\n    </blockquote>\n    \n</div>\n'
            self.assertEquals(expected, result)
            # Test for a review about anything else
            result = hreview(rev3, autoescape=True) 
            expected = u'\n<div class="hreview">\n    <strong class="summary">Latest Star-Wars is Sucko-Barfo</strong>\n    <abbr class="type" title="film"> Film</abbr> Review\n    <br/>\n    \n    by\n    <span class="reviewer vcard"><span class="fn">Barry Norman</span></span>\n    \n        \n            \n    <div class="item">\n        \n        <a class="url fn" href="http://www.starwars.com/movies/episode-iii/">\n        \n        Star Wars - Revenge of the Sith\n        \n        </a>\n        \n    </div>\n            \n        \n    \n    \n    <abbr class="rating" title="1">\u2605\u2606\u2606\u2606\u2606</abbr>\n    \n    \n    \n    \n    \n    \n    <blockquote class="description">\n        Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.\n    </blockquote>\n    \n</div>\n'
            self.assertEquals(expected, result)
            # Test for minimal review
            rev3.summary = ''
            rev3.description = ''
            rev3.rating = 1
            rev3.type = 'film'
            rev3.reviewer = 'Barry Norman'
            rev3.fn = 'Star Wars - Revenge of the Sith'
            rev3.url = ''
            result = hreview(rev3, autoescape=True) 
            expected = u'\n<div class="hreview">\n    \n    <abbr class="type" title="film"> Film</abbr> Review\n    <br/>\n    \n    by\n    <span class="reviewer vcard"><span class="fn">Barry Norman</span></span>\n    \n        \n            \n    <div class="item">\n        \n        <span class="fn">\n        \n        Star Wars - Revenge of the Sith\n        \n        </span>\n        \n    </div>\n            \n        \n    \n    \n    <abbr class="rating" title="1">\u2605\u2606\u2606\u2606\u2606</abbr>\n    \n    \n    \n    \n    \n    \n</div>\n'
            self.assertEquals(expected, result)

        def test_xfn(self):
            """
            Make sure XFN links render correctly
            """
            # Set things up
            u = User.objects.create_user('john', 'john@smith.com', 'password')
            URL = 'http://twitter.com/ntoll'
            tgt = 'Nicholas Tollervey'
            x = microformats.models.xfn()
            x.source = u
            x.target = tgt 
            x.url = URL
            x.save()
            xfnv1 = microformats.models.xfn_values.objects.get(value='friend')
            xfnv2 = microformats.models.xfn_values.objects.get(value='met')
            xfnv3 = microformats.models.xfn_values.objects.get(value='colleague')
            x.relationships.add(xfnv1)
            x.relationships.add(xfnv2)
            x.relationships.add(xfnv3)
            x.save()
            result = xfn(x, autoescape=True)
            expected = u'<a href="http://twitter.com/ntoll" rel="colleague friend met">Nicholas Tollervey</a>'
            self.assertEquals(expected, result)

        def test_template_output(self):
            """ 
            Generates an html file containing various examples of the tags in
            use for testing with screen-scrapers and browser plugins.
            """
            g = microformats.models.geo()
            g.latitude = 37.408183
            g.latitude_description = 'N 37° 24.491'
            g.longitude = -122.13855
            g.longitude_description = 'W 122° 08.313'
            g.save()
            hc = microformats.models.hCard()
            hc.honorific_prefix = 'Mr'
            hc.given_name = 'Joe'
            hc.additional_name = 'Arthur'
            hc.family_name = 'Blogs'
            hc.honorific_suffix = 'PhD'
            hc.url = 'http://acme.com/'
            hc.email_work = 'joe.blogs@acme.com'
            hc.email_home = 'joeblogs2000@home-isp.com'
            hc.tel_work = '+44(0)1234 567890'
            hc.tel_home = '+44(0)1324 234123'
            hc.street_address = '5445 N. 27th Street'
            hc.extended_address = ''
            hc.locality = 'Milwaukee'
            hc.region = 'WI'
            hc.country_name = 'US'
            hc.postal_code = '53209'
            hc.org = "Acme Corp."
            hc.title = 'Vice President'
            hc.save()
            hcl = microformats.models.hCalendar()
            hcl.summary = 'Important Meeting'
            hcl.location = 'BBC in London'
            hcl.url = 'http://www.bbc.co.uk/'
            hcl.dtstart = datetime.datetime(2009, 4, 11, 13, 30)
            hcl.dtend = datetime.datetime(2009, 4, 11, 15, 30)
            hcl.description = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            hcl.street_address = 'Broadcasting House'
            hcl.extended_address = 'Portland Place'
            hcl.locality = 'London'
            hcl.region = ''
            hcl.country_name = 'GB'
            hcl.postal_code = 'W1A 1AA'
            hcl.save()
            u = User.objects.create_user('john', 'john@smith.com', 'password')
            URL = 'http://twitter.com/ntoll'
            tgt = 'Nicholas Tollervey'
            x = microformats.models.xfn()
            x.source = u
            x.target = tgt 
            x.url = URL
            x.save()
            xfnv1 = microformats.models.xfn_values.objects.get(value='friend')
            xfnv2 = microformats.models.xfn_values.objects.get(value='met')
            xfnv3 = microformats.models.xfn_values.objects.get(value='colleague')
            x.relationships.add(xfnv1)
            x.relationships.add(xfnv2)
            x.relationships.add(xfnv3)
            x.save()
            g2 = microformats.models.geo()
            g2.latitude = 45.498677
            g2.latitude_description = "45°34' 13"" N"
            g2.longitude = -73.570260 
            g2.longitude_description = "73°29' 55"" W" 
            g2.save()
            hc2 = microformats.models.hCard()
            hc2.honorific_prefix = 'Mr'
            hc2.given_name = 'John'
            hc2.additional_name = ''
            hc2.family_name = 'Fletcher'
            hc2.honorific_suffix = 'MA(cantab)'
            hc2.url = 'http://lso.co.uk/'
            hc2.tel_work = '+44(0)1234 567456'
            hc2.street_address = 'The Barbican Centre'
            hc2.extended_address = 'Silk Street'
            hc2.locality = 'London'
            hc2.country_name = 'GB'
            hc2.postal_code = 'EC2Y 8DS'
            hc2.org = 'London Symphony Orchestra'
            hc2.title = 'Principal Tuba Player'
            hc2.save()
            hcl2 = microformats.models.hCalendar()
            hcl2.summary = 'Operation Overlord'
            hcl2.location = 'Normandy, France'
            hcl2.url = 'http://en.wikipedia.org/wiki/Operation_Overlord'
            hcl2.dtstart = datetime.datetime(1944, 6, 6)
            hcl2.dtend = datetime.datetime(1944, 8, 30)
            hcl2.description = 'You are about to embark upon the Great Crusade, toward which we have striven these many months. The eyes of the world are upon you. The hopes and prayers of liberty-loving people everywhere march with you. In company with our brave Allies and brothers-in-arms on other Fronts, you will bring about the destruction of the German war machine, the elimination of Nazi tyranny over the oppressed peoples of Europe, and security for ourselves in a free world.'
            hcl2.save()
            listing = microformats.models.hListing()
            listing.listing_action = "sell"
            listing.summary = "Pony requires a good home"
            listing.description = "A young pony who answers to the name Django"\
                " requires a new home having outgrown his current host. Easy"\
                " going and fun to play with Django also provides rainbow"\
                " manure that is sure to help the garden grow."
            listing.lister_fn = "John Doe"
            listing.lister_email = "john.doe@isp.net"
            listing.lister_url = "http://isp.com/django_the_pony"
            listing.lister_tel = "+44(0) 1234 567456"
            listing.dtlisted = datetime.datetime(2009, 5, 6)
            listing.dtexpired = datetime.datetime(2009, 8, 19)
            listing.price = "£2500 ono"
            listing.item_fn = "Django the Pony"
            listing.item_url = "http://djangoproject.com/"
            listing.locality = "Brighton"
            listing.country_name = "GB"
            listing.save()
            rev1 = microformats.models.hReview()
            rev1.summary="Acme's new services rock!"
            rev1.type='business'
            rev1.description='Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.'
            rev1.rating=4
            rev1.dtreviewed=datetime.datetime(2009,4,10)
            rev1.reviewer='John Smith'
            rev1.fn='Acme Corp'
            rev1.url='http://acme.com'
            rev1.tel='+44(0)1234 567456'
            rev1.street_address = '5445 N. 27th Street'
            rev1.extended_address = ''
            rev1.locality = 'Milwaukee'
            rev1.region = 'WI'
            rev1.country_name = 'US'
            rev1.postal_code = '53209'
            rev1.save()
            rev2 = microformats.models.hReview()
            rev2.summary = 'A phenomenal tuba recital'
            rev2.description = 'Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.'
            rev2.rating=5
            rev2.type='event'
            rev2.reviewer='John Doe'
            rev2.fn='John Fletcher - One man and his Tuba'
            rev2.url='http://www.johnfletcher-tuba.co.uk/'
            rev2.dtstart = datetime.datetime(1987, 10, 3, 19, 30)
            rev2.street_address = 'The Pro Arte Theatre'
            rev2.locality = 'London'
            rev2.save()
            rev3 = microformats.models.hReview()
            rev3.summary = "Mr Bloggs children's entertainer flops"
            rev3.description = 'Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.'
            rev3.rating=2
            rev3.type='person'
            rev3.reviewer='Melvyn Bragg'
            rev3.fn='Mr Bloggs'
            rev3.tel='01234 567456'
            rev3.save()
            rev4 = microformats.models.hReview()
            rev4.summary = 'Latest Star-Wars is Sucko-Barfo'
            rev4.description = 'Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.'
            rev4.rating=1
            rev4.type='film'
            rev4.reviewer='Barry Norman'
            rev4.fn='Star Wars - Revenge of the Sith'
            rev4.url='http://www.starwars.com/movies/episode-iii/'
            rev4.save()
            rev5 = microformats.models.hReview()
            rev5.rating=1
            rev5.type='film'
            rev5.fn='Star Wars - The Phantom Menace'
            rev5.save()
            feed = microformats.models.hFeed()
            feed.save()
            entry1 = microformats.models.hEntry()
            entry1.hfeed = feed
            entry1.entry_title = 'Entry 1 Title'
            entry1.entry_content = 'Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.'
            entry1.entry_summary = 'Lorem ipsum dolor sit amet doo-dah whatsit thingymajig'
            entry1.author = 'A.N.Other'
            entry1.bookmark = 'http://website.com/entry1'
            entry1.updated = datetime.datetime(2009, 6, 1)
            entry1.save()
            entry2 = microformats.models.hEntry()
            entry2.hfeed = feed
            entry2.entry_title = 'Entry 2 Title'
            entry2.entry_content = 'Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.'
            entry2.entry_summary = 'Lorem ipsum dolor sit amet doo-dah whatsit thingymajig'
            entry2.author = 'Sidney Humphries'
            entry2.bookmark = 'http://website.com/entry2'
            entry2.updated = datetime.datetime(2009, 3, 14)
            entry2.save()
            entry3 = microformats.models.hEntry()
            entry3.hfeed = feed
            entry3.entry_title = 'Entry 3 Title'
            entry3.entry_content = 'Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.'
            entry3.entry_summary = 'Lorem ipsum dolor sit amet doo-dah whatsit thingymajig'
            entry3.author = 'Nicholas Hawkesmoor'
            entry3.bookmark = 'http://website.com/entry3'
            entry3.updated = datetime.datetime(2008, 12, 28)
            entry3.save()
            entry4 = microformats.models.hEntry()
            entry4.entry_title = 'Entry 4 Title'
            entry4.entry_content = 'Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.'
            entry4.entry_summary = 'Lorem ipsum dolor sit amet doo-dah whatsit thingymajig'
            entry4.author = 'Fred Blogs'
            entry4.bookmark = 'http://website.com/entry4'
            entry4.updated = datetime.datetime(2008, 11, 15)
            entry4.save()

            # All the data is defined so lets render the test template...
            template = get_template('test.html')
            data = {
                    'contact': hc,
                    'loc': g,
                    'event': hcl, 
                    'listing': listing,
                    'review1': rev1,
                    'review2': rev2,
                    'review3': rev3,
                    'review4': rev4,
                    'review5': rev5,
                    'person': x,
                    'c2': hc2,
                    'loc2': g2,
                    'event2': hcl2,
                    'feed': feed,
                    'entry': entry4,
                    }
            context = Context(data)
            import html_test
            path =  os.path.dirname(html_test.__file__)
            outfile = codecs.open(os.path.join(path, 'microformat_test.html'), 'w', 'utf-8')
            outfile.write(template.render(context))
            outfile.close()
