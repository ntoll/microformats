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
            a = microformats.models.adr()
            a.street_address = 'Broadcasting House'
            a.extended_address = 'Portland Place'
            a.locality = 'London'
            a.region = ''
            a.country_name = 'GB'
            a.postal_code = 'W1A 1AA'
            a.save()
            hc = microformats.models.hCalendar()
            hc.summary = 'Important Meeting'
            hc.location = 'BBC in London'
            hc.url = 'http://www.bbc.co.uk/'
            hc.dtstart = datetime.datetime(2009, 4, 11, 13, 30)
            hc.dtend = datetime.datetime(2009, 4, 11, 15, 30)
            hc.description = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.'
            hc.save()
            hc.adr = a
            hc.save()
            result = hcal(hc, autoescape=True)
            expected = u'\n<div id="hcalendar_1" class="vevent">\n    <a href="http://www.bbc.co.uk/" class="url">\n        \n        <abbr title="2009-04-11T13:30:00" class="dtstart">Sat 11 Apr 2009 1:30 p.m.</abbr>\n        \n        \n            &nbsp;-&nbsp;\n            \n            <abbr title="2009-04-11T15:30:00" class="dtend">All day event</abbr>\n            \n        \n        :&nbsp;\n        <span class="summary">Important Meeting</span>\n         at <span class="location">BBC in London</span>\n    </a>\n    \n<div class="adr">\n    \n    \n    \n    \n    \n    \n</div>\n\n    <p class="description">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>    \n</div>\n'
            self.assertEquals(expected, result)
            # Make sure things render correctly *if* all_day_event = True
            hc.all_day_event = True
            hc.save()
            result = hcal(hc, autoescape=True)
            expected = u'\n<div id="hcalendar_1" class="vevent">\n    <a href="http://www.bbc.co.uk/" class="url">\n        \n        <abbr title="2009-04-11T13:30:00" class="dtstart">Sat 11 Apr 2009</abbr>\n        \n        \n            &nbsp;-&nbsp;\n            \n            <abbr title="2009-04-11T15:30:00" class="dtend">All day event</abbr>\n            \n        \n        :&nbsp;\n        <span class="summary">Important Meeting</span>\n         at <span class="location">BBC in London</span>\n    </a>\n    \n<div class="adr">\n    \n    \n    \n    \n    \n    \n</div>\n\n    <p class="description">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>    \n</div>\n'
            self.assertEquals(expected, result)
            hc.all_day_event = False
            hc.save()
            # Lets cut things down to the essentials with a different end date
            hc.url = ''
            hc.location = ''
            hc.description = ''
            hc.adr = None
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
                " manure that is sure to help the garden."
            listing.lister_fn = "John Doe"
            listing.lister_email = "john.doe@isp.net"
            listing.lister_url = "http://isp.com/django_the_pony"
            listing.lister_tel = "+44(0) 1234 567456"
            listing.dtlisted = datetime.datetime(2009, 5, 6)
            listing.dtexpired = datetime.datetime(2009, 8, 19)
            listing.price = "£2500 ono"
            listing.item_fn = "Django the Pony"
            listing.item_url = "http://djangoproject.com/"
            listing.save()
            template = get_template('test.html')
            data = {
                    'contact': hc,
                    'loc': g,
                    'event': hcl, 
                    'listing': listing,
                    'person': x,
                    'c2': hc2,
                    'loc2': g2,
                    'event2': hcl2
                    }
            
            context = Context(data)
            import html_test
            path =  os.path.dirname(html_test.__file__)
            outfile = codecs.open(os.path.join(path, 'microformat_test.html'), 'w', 'utf-8')
            outfile.write(template.render(context))
            outfile.close()

