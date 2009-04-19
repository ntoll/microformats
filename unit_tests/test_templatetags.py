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
            expected = u'<div class="geo">&nbsp;'\
                    u'<abbr class="latitude" title="37.408183">'\
                    u'N 37° 24.491'\
                    u'</abbr>&nbsp;'\
                    u'<abbr class="longitude" title="-122.13855">'\
                    u'W 122° 08.313'\
                    u'</abbr></div>'
            self.assertEquals(expected, result) 
            # With an arg
            result = geo(g, arg="Geo", autoescape=True)
            expected = u'<div class="geo">Geo&nbsp;'\
                    u'<abbr class="latitude" title="37.408183">'\
                    u'N 37° 24.491'\
                    u'</abbr>&nbsp;'\
                    u'<abbr class="longitude" title="-122.13855">'\
                    u'W 122° 08.313'\
                    u'</abbr></div>'
            self.assertEquals(expected, result) 
            # An instance without any description fields
            g.latitude_description = ''
            g.longitude_description = ''
            g.save()
            result = geo(g, autoescape=True)
            expected = u'<div class="geo">&nbsp;'\
                    u'<abbr class="latitude" title="37.408183">'\
                    u'37.408183'\
                    u'</abbr>&nbsp;'\
                    u'<abbr class="longitude" title="-122.13855">'\
                    u'-122.13855'\
                    u'</abbr></div>'
            self.assertEquals(expected, result) 
            # Test Geocode fragments
            result = geo(g.latitude, arg="lat", autoescape=True)
            expected = u'<abbr class="latitude">37.408183</abbr>'
            self.assertEquals(expected, result) 
            result = geo(g.longitude, arg="long", autoescape=True)
            expected = u'<abbr class="longitude">-122.13855</abbr>'
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
            hc.save()
            e = microformats.models.email()
            e.hcard=hc
            e.value = 'joe.blogs@acme.com'
            e.save()
            e2 = microformats.models.email()
            e2.hcard=hc
            e2.value = 'joe.blogs@home-isp.com'
            e2.save()
            tt1 = microformats.models.tel_type.objects.get(id=1)
            tt2 = microformats.models.tel_type.objects.get(id=2)
            tt3 = microformats.models.tel_type.objects.get(id=3)
            tt4 = microformats.models.tel_type.objects.get(id=4)
            tel1 = microformats.models.tel()
            tel1.value = '+44(0)1234 567876'
            tel1.hcard = hc
            tel1.save()
            tel1.types.add(tt1)
            tel1.types.add(tt2)
            tel1.save()
            tel2 = microformats.models.tel()
            tel2.value = '+44(0)7865 754345'
            tel2.hcard = hc
            tel2.save()
            tel2.types.add(tt3)
            tel2.types.add(tt4)
            tel2.save()
            at = microformats.models.adr_type.objects.get(id=5)
            a = microformats.models.adr()
            a.street_address = '5445 N. 27th Street'
            a.extended_address = ''
            a.locality = 'Milwaukee'
            a.region = 'WI'
            a.country_name = 'US'
            a.postal_code = '53209'
            a.hcard=hc
            a.save()
            a.types.add(at)
            a.save()
            t = microformats.models.title()
            t.hcard = hc
            t.name = 'Vice President'
            t.save()
            o = microformats.models.org()
            o.hcard = hc
            o.name = 'Acme Corp.'
            o.unit = 'Production Resources'
            o.title = t
            o.primary = True
            o.save()
            result = hcard(hc, autoescape=True)
            expected = u'<div id="hcard_Mr_Joe_Arthur_Blogs_PhD" class="vcard"><div class="fn n"><a class="url" href="http://acme.com/"><span class="honorific_prefix">Mr</span>&nbsp;<span class="given-name">Joe</span>&nbsp;<span class="additional-name">Arthur</span>&nbsp;<span class="family-name">Blogs</span>&nbsp;<span class="honorific_suffix">PhD</span></a></div><span class="title">Vice President</span>&nbsp;<div class="org"><span class="organization-unit">Production Resources</span>,&nbsp;<span class="organization-name">Acme Corp.</span></div><a class="email" href="mailto:joe.blogs@acme.com">joe.blogs@acme.com</a><br/><a class="email" href="mailto:joe.blogs@home-isp.com">joe.blogs@home-isp.com</a><br/><div class="adr"><div><abbr class="type" title="home">Home</abbr>&nbsp;Address</div><div class="street-address">5445 N. 27th Street</div><span class="locality">Milwaukee</span>&nbsp;<span class="region">WI</span>&nbsp;<span class="postal-code">53209</span>&nbsp;<span class="region">United States</span></div><div class="tel"><span class="value">+44(0)1234 567876</span>&nbsp;[&nbsp;<abbr class="type" title="voice">Voice</abbr>&nbsp<abbr class="type" title="home">Home</abbr>&nbsp]</div><div class="tel"><span class="value">+44(0)7865 754345</span>&nbsp;[&nbsp;<abbr class="type" title="msg">Message Service</abbr>&nbsp<abbr class="type" title="work">Work</abbr>&nbsp]</div></div>'
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
            expected = u'<div id="hcard_Production_Resources,_Acme_Corp." class="vcard"><div class="fn n"><a class="url" href="http://acme.com/"><span class="org">Acme Corp.</span></a></div><a class="email" href="mailto:joe.blogs@acme.com">joe.blogs@acme.com</a><br/><a class="email" href="mailto:joe.blogs@home-isp.com">joe.blogs@home-isp.com</a><br/><div class="adr"><div><abbr class="type" title="home">Home</abbr>&nbsp;Address</div><div class="street-address">5445 N. 27th Street</div><span class="locality">Milwaukee</span>&nbsp;<span class="region">WI</span>&nbsp;<span class="postal-code">53209</span>&nbsp;<span class="region">United States</span></div><div class="tel"><span class="value">+44(0)1234 567876</span>&nbsp;[&nbsp;<abbr class="type" title="voice">Voice</abbr>&nbsp<abbr class="type" title="home">Home</abbr>&nbsp]</div><div class="tel"><span class="value">+44(0)7865 754345</span>&nbsp;[&nbsp;<abbr class="type" title="msg">Message Service</abbr>&nbsp<abbr class="type" title="work">Work</abbr>&nbsp]</div></div>'
            self.assertEquals(expected, result)
            # No address, org, url and email and minimum telephone information
            a.delete() 
            hc.url = ''
            e.delete()
            e2.delete()
            hc.honorific_prefix = 'Mr'
            hc.given_name = 'Joe'
            hc.additional_name = 'Arthur'
            hc.family_name = 'Blogs'
            hc.honorific_suffix = 'PhD'
            hc.save()
            tel1.types.clear()
            tel1.save()
            tel2.types.clear()
            tel2.save()
            o.delete()
            result = hcard(hc, autoescape=True)
            expected = u'<div id="hcard_Mr_Joe_Arthur_Blogs_PhD" class="vcard"><div class="fn n"><span class="honorific_prefix">Mr</span>&nbsp;<span class="given-name">Joe</span>&nbsp;<span class="additional-name">Arthur</span>&nbsp;<span class="family-name">Blogs</span>&nbsp;<span class="honorific_suffix">PhD</span></div><div class="tel"><span class="value">+44(0)1234 567876</span></div><div class="tel"><span class="value">+44(0)7865 754345</span></div></div>'
            self.assertEquals(expected, result)
            # Absolute minimum
            hc.honorific_prefix = ''
            hc.additional_name = ''
            hc.honorific_suffix = ''
            hc.save()
            tel1.delete()
            tel2.delete()
            result = hcard(hc, autoescape=True)
            expected = u'<div id="hcard_Joe_Blogs" class="vcard"><div class="fn n"><span class="given-name">Joe</span>&nbsp;<span class="family-name">Blogs</span>&nbsp;</div></div>'
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
            expected = u'<div class="adr"><div><abbr class="type" title="home">Home</abbr>&nbsp;Address</div><div class="street-address">Flat 29a</div><div class="extended-address">123 Somewhere Street</div><span class="locality">Townsville</span>&nbsp;<span class="region">Countyshire</span>&nbsp;<span class="postal-code">CS23 6YT</span>&nbsp;<span class="region">United Kingdom</span></div>'
            self.assertEquals(expected, result)
            # Without type
            a.types.clear()
            a.save()
            result = adr(a, autoescape=True)
            expected = u'<div class="adr"><div class="street-address">Flat 29a</div><div class="extended-address">123 Somewhere Street</div><span class="locality">Townsville</span>&nbsp;<span class="region">Countyshire</span>&nbsp;<span class="postal-code">CS23 6YT</span>&nbsp;<span class="region">United Kingdom</span></div>'
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
            expected = u'<div id="hcalendar_Important_Meeting" class="vevent"><a href="http://www.bbc.co.uk/" class="url"><abbr title="2009-04-11T13:30:00" class="dtstart">Sat Apr 11 2009, 01:30PM</abbr>&nbsp;-&nbsp;<abbr title="2009-04-11T15:30:00" class="dtend">03:30PM</abbr>:&nbsp;<span class="summary">Important Meeting</span> at <span class="location">BBC in London</span></a><div class="adr"><div class="street-address">Broadcasting House</div><div class="extended-address">Portland Place</div><span class="locality">London</span>&nbsp;<span class="postal-code">W1A 1AA</span>&nbsp;<span class="region">United Kingdom</span></div><p class="description">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p></div>'
            self.assertEquals(expected, result)
            # Make sure things render correctly *if* all_day_event = True
            hc.all_day_event = True
            hc.save()
            result = hcal(hc, autoescape=True)
            expected = u'<div id="hcalendar_Important_Meeting" class="vevent"><a href="http://www.bbc.co.uk/" class="url"><abbr title="2009-04-11T13:30:00" class="dtstart">Sat Apr 11 2009</abbr>&nbsp;-&nbsp;<abbr title="2009-04-11T15:30:00" class="dtend">All day event</abbr>:&nbsp;<span class="summary">Important Meeting</span> at <span class="location">BBC in London</span></a><div class="adr"><div class="street-address">Broadcasting House</div><div class="extended-address">Portland Place</div><span class="locality">London</span>&nbsp;<span class="postal-code">W1A 1AA</span>&nbsp;<span class="region">United Kingdom</span></div><p class="description">Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p></div>'
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
            expected = u'<div id="hcalendar_Important_Meeting" class="vevent"><abbr title="2009-04-11T13:30:00" class="dtstart">Sat Apr 11 2009, 01:30PM</abbr>&nbsp;-&nbsp;<abbr title="2009-04-15T15:30:00" class="dtend">Wed Apr 15 2009, 03:30PM</abbr>:&nbsp;<span class="summary">Important Meeting</span></div>'
            self.assertEquals(expected, result)
            # Absolute minimum
            hc.dtend = None
            hc.dtstart = datetime.datetime(2009, 4, 15)
            result = hcal(hc, autoescape=True)
            # We probably want to separate the date and time of dtstart and
            # dtend so we don't default to midnight... ToDo: Fix date/time
            expected = u'<div id="hcalendar_Important_Meeting" class="vevent"><abbr title="2009-04-15T00:00:00" class="dtstart">Wed Apr 15 2009, 12:00AM</abbr>:&nbsp;<span class="summary">Important Meeting</span></div>'
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
            use
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
            hc.save()
            e = microformats.models.email()
            e.hcard=hc
            e.value = 'joe.blogs@acme.com'
            e.save()
            e2 = microformats.models.email()
            e2.hcard=hc
            e2.value = 'joe.blogs@home-isp.com'
            e2.save()
            tt1 = microformats.models.tel_type.objects.get(id=1)
            tt2 = microformats.models.tel_type.objects.get(id=2)
            tt3 = microformats.models.tel_type.objects.get(id=3)
            tt4 = microformats.models.tel_type.objects.get(id=4)
            tel1 = microformats.models.tel()
            tel1.value = '+44(0)1234 567876'
            tel1.hcard = hc
            tel1.save()
            tel1.types.add(tt1)
            tel1.types.add(tt2)
            tel1.save()
            tel2 = microformats.models.tel()
            tel2.value = '+44(0)7865 754345'
            tel2.hcard = hc
            tel2.save()
            tel2.types.add(tt3)
            tel2.types.add(tt4)
            tel2.save()
            at = microformats.models.adr_type.objects.get(id=5)
            a = microformats.models.adr()
            a.street_address = '5445 N. 27th Street'
            a.extended_address = ''
            a.locality = 'Milwaukee'
            a.region = 'WI'
            a.country_name = 'US'
            a.postal_code = '53209'
            a.hcard=hc
            a.save()
            a.types.add(at)
            a.save()
            t = microformats.models.title()
            t.hcard = hc
            t.name = 'Vice President'
            t.save()
            o = microformats.models.org()
            o.hcard = hc
            o.name = 'Acme Corp.'
            o.unit = 'Production Resources'
            o.title = t
            o.primary = True
            o.save()
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
            hc2.save()
            tel3 = microformats.models.tel()
            tel3.value = '+44(0)1234 567876'
            tel3.hcard = hc2
            tel3.save()
            tel3.types.add(tt1)
            tel3.types.add(tt2)
            tel3.save()
            at1 = microformats.models.adr_type.objects.get(id=6)
            a1 = microformats.models.adr()
            a1.street_address = 'Barbican Centre'
            a1.extended_address = 'Silk Street'
            a1.locality = 'London'
            a1.region = ''
            a1.country_name = 'GB'
            a1.postal_code = 'EC2Y 8DS'
            a1.save()
            a1.types.add(at1)
            a1.hcard=hc2
            a1.save()
            t2 = microformats.models.title()
            t2.hcard = hc2
            t2.name = 'Principal Tuba Player'
            t2.save()
            o2 = microformats.models.org()
            o2.hcard = hc2
            o2.name = 'The London Symphony Orchestra'
            o2.unit = ''
            o2.title = t2
            o2.primary = True
            o2.save()
            hcl2 = microformats.models.hCalendar()
            hcl2.summary = 'Operation Overlord'
            hcl2.location = 'Normandy, France'
            hcl2.url = 'http://en.wikipedia.org/wiki/Operation_Overlord'
            hcl2.dtstart = datetime.datetime(1944, 6, 6)
            hcl2.dtend = datetime.datetime(1944, 8, 30)
            hcl2.description = 'You are about to embark upon the Great Crusade, toward which we have striven these many months. The eyes of the world are upon you. The hopes and prayers of liberty-loving people everywhere march with you. In company with our brave Allies and brothers-in-arms on other Fronts, you will bring about the destruction of the German war machine, the elimination of Nazi tyranny over the oppressed peoples of Europe, and security for ourselves in a free world.'
            hcl2.save()
            template = Template("""{% load microformat_extras %}
            <html>
                <head>
                    <title>Testing Microformats</title>
                    <meta http-equiv="content-type" content="text/html;
                    charset=utf-8" />
                    <script type="text/javascript"
                    src="jquery-1.2.6.min.js"></script>
                    <script type="text/javascript" src="oomphx.js"></script>
                    <link rel="stylesheet" href="ufstyle.css" type="text/css"
                    media="screen" />

                </head>
                <body>
                    <div id="ufContainer">
                    <div id='ufTitle'>
                    <h1>Microformat Test Card</h1>
                    </div>
                    <div id='ufContent'>
                    <p>
                    This page contains examples of microformats as rendered by
                    the microformats Django application. <a
                    href="http://microformats.org/">Microformats</a> are a means
                    of adding semantic information that is
                    <em>both</em> human and machine readable to a web-site. In
                    order to work with Microformats you need to use a toolkit
                    such as <a href="http://visitmix.com/Lab/oomph">Oomph</a>
                    (included as a javascript plugin with this page - if you're
                    online you should see it's logo in the top left hand side of
                    the screen) or the <a
                    href="https://addons.mozilla.org/en-US/firefox/addon/4106">Operator
                    Add-on</a> for Firefox (that supports more types of
                    microformat).
                    </p>

                    <h2>Geo</h2>
                    {{loc|geo:"A Geo-location"}}

                    <h2>hCard</h2>
                    {{contact|hcard}}

                    <h2>hCalendar</h2>
                    {{event|hcal}}

                    <h2>XFN</h2>
                    {{person|xfn}}

                    <h2>Some Free Text Examples</h2>

                    <h3>Geo</h3>
                    <p class="geo">We spent a long time trying to find Fred's
                    house using the GPS to lead us to
                    {{loc2.latitude|geo:"lat"}}/
                    {{loc2.longitude|geo:"long"}}, but we got there in the end.
                    </p>

                    <h3>hCard</h3>
                    <p class="vcard">
                    Whilst researching my programme notes for the upcoming
                    performance of the Vaughan-William's Tuba Concerto, I found
                    a recording with <span
                    class="fn">{{c2.given_name|hcard:"given-name"}}
                    {{c2.family_name|hcard:"family-name"}}</span> as the
                    soloist. He was the {{lso.title|hcard:"role"}} in the
                    {{lso.name|hcard:"org"}}. More information can be found by
                    contacting their offices at
                    <span clas="adr">
                    {{lso_adr.street_address|hcard:"street-address"}} in
                    {{lso_adr.locality|hcard:"locality"}}</span>.
                    </p>

                    <h3>hCalendar</h3>
                    <p class="vevent">
                    In the early hours of 
                    {{event2.dtstart|hcal:"dtstart %B %d %Y"}}
                    {{event2.summary|hcal:"summary"}} commenced throughout 
                    {{event2.location|hcal:"location"}}. The aims of this
                    operation were summarised thus,
                    <q>{{event2.description|hcal:"description"}}</q>
                    </p>
                    </div>
                    <div id="ufFooter">
                    &copy; 2009 <a href="http://ntoll.org/">Nicholas H.Tollervey</a>
                    </div>
                    </div>
                </body>
            </html>""")
            
            data = {
                    'contact': hc,
                    'loc': g,
                    'event': hcl, 
                    'person': x,
                    'c2': hc2,
                    'lso': o2,
                    'lso_adr': a1,
                    'loc2': g2,
                    'event2': hcl2
                    }
            
            context = Context(data)
            import html_test
            path =  os.path.dirname(html_test.__file__)
            outfile = codecs.open(os.path.join(path, 'microformat_test.html'), 'w', 'utf-8')
            outfile.write(template.render(context))
            outfile.close()

