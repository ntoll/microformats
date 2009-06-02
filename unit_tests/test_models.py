# -*- coding: UTF-8 -*-
"""
Model tests for Microformats 

Author: Nicholas H.Tollervey

"""
# python
import datetime

# django
from django.test.client import Client
from django.test import TestCase
from django.contrib.auth.models import User

# project
from microformats.models import *

class ModelTestCase(TestCase):
        """
        Testing Models 
        """
        # Reference fixtures here
        fixtures = []

        def test_geo(self):
            """
            Make sure the string representation of the geolocation looks correct
            """
            g = geo()
            g.latitude = 37.408183
            g.longitude = -122.13855
            g.latitude_description = 'N 37 24.491'
            g.longitude_description = 'W 122 08.313'
            g.save()
            self.assertEquals('lat 37.408183 long -122.13855', g.__unicode__())

        def test_hCardComplete(self):
            """
            Check that the n() and fn() methods return the correct values
            """
            hc = hCardComplete()
            hc.honorific_prefix = 'Mr'
            hc.given_name = 'Joe'
            hc.additional_name = 'Arthur'
            hc.family_name = 'Blogs'
            hc.honorific_suffix = 'PhD'
            hc.save()
            self.assertEquals('Mr Joe Arthur Blogs PhD', hc.n())
            # Make sure we get a useful name back *NOT* "Mr PhD"
            hc.given_name = ''
            hc.additional_name = ''
            hc.family_name = ''
            hc.save()
            self.assertEquals('', hc.n())
            # Make sure fn() returns the same as n() if is_org isn't passed
            hc.given_name = 'Joe'
            hc.additional_name = 'Arthur'
            hc.family_name = 'Blogs'
            self.assertEquals('Mr Joe Arthur Blogs PhD', hc.fn())
            # Make sure we don't let whitespace or empty into the result of n()
            hc.honorific_prefix = """       
            """ # some spaces, tabs and a newline
            hc.honorific_suffix = '' # empty
            hc.save()
            self.assertEquals('Joe Arthur Blogs', hc.n())
            # Lets add an organization to the hCard
            o = org()
            o.hcard = hc
            o.name = 'Acme Corp.'
            o.unit = 'Widget Development'
            o.primary = True
            o.save()
            self.assertEquals('Widget Development, Acme Corp.',
                    hc.fn(is_org=True))
            o.unit = ''
            o.save()
            self.assertEquals('Acme Corp.', hc.fn(is_org=True))
            o.primary = False
            o.save()
            # If we don't have an organization by do have some name information
            # then fall back on that
            self.assertEquals('Joe Arthur Blogs', hc.fn(is_org=True))
            o2 = org()
            o2.hcard = hc
            o2.name = 'Mega Corp.'
            o2.unit = 'Sales'
            o2.primary = True
            o2.save()
            o.primary = True
            o.save()
            # check that two organizations marked as primary doesn't result in
            # an error
            self.assertEquals('Acme Corp.', hc.fn(is_org=True))
            # Check that despite being associated with an organization fn()
            # doesn't return it if is_org isn't passed
            self.assertEquals('Joe Arthur Blogs', hc.fn())
            # Finally, make sure we get something sensible if nothing else is
            # available for fn() to create something
            # No name information so fall back on organization
            hc.given_name = ''
            hc.additional_name = ''
            hc.family_name = ''
            self.assertEquals('Acme Corp.', hc.fn())
            o.delete()
            o2.delete()
            self.assertEquals('None', hc.fn())

        def test_adr(self):
            """ 
            Make sure the string representation of the address looks correct
            """
            a = adr()
            a.street_address = 'Flat 29a'
            a.extended_address = '123 Somewhere Street'
            a.locality = 'Townsville'
            a.region = 'Countyshire'
            a.country_name = 'GB'
            a.postal_code = 'CS23 6YT'
            a.post_office_box = 'PO Box 6754'
            expected = 'Flat 29a, 123 Somewhere Street, Townsville,'\
                    ' Countyshire, United Kingdom, CS23 6YT,'\
                    ' PO Box 6754'
            self.assertEquals(expected, a.__unicode__())
            # Lets check we ignore whitespace and empty fields
            a.post_office_box = """    
                """ # whitespace of various sorts
            a.extended_address = '' # empty
            expected = 'Flat 29a, Townsville, Countyshire, United Kingdom,'\
                    ' CS23 6YT'
            self.assertEquals(expected, a.__unicode__())

        def test_org(self):
            """ 
            Make sure the string representation of the organization looks correct
            """
            hc = hCardComplete()
            hc.given_name = 'test'
            hc.save()
            o = org()
            o.hcard = hc
            o.name = 'Acme Corp.'
            o.unit = 'Widget Development'
            o.primary = True
            o.save()
            self.assertEquals('Widget Development, Acme Corp.', o.__unicode__())
            o.unit = ''
            o.save()
            self.assertEquals('Acme Corp.', o.__unicode__())

        def test_hCalendar(self):
            """
            Make sure the string representation of the hCalendar looks correct
            """
            hc = hCalendar()
            hc.summary = 'This is a summary'
            hc.dtstart = datetime.datetime(2009, 4, 11, 13, 30)
            hc.save()
            expected = hc.dtstart.strftime('%a %b %d %Y, %I:%M%p')+' - This is'\
                    ' a summary'
            self.assertEquals(expected, hc.__unicode__())

        def test_xfn(self):
            """
            Make sure the string representation of the XFN looks correct
            """
            # Set things up
            u = User.objects.create_user('john', 'john@smith.com', 'password')
            URL = 'http://twitter.com/ntoll'
            tgt = 'Nicholas Tollervey'
            x = xfn()
            x.source = u
            x.target = tgt 
            x.save()
            xfnv1 = xfn_values.objects.get(value='friend')
            xfnv2 = xfn_values.objects.get(value='met')
            xfnv3 = xfn_values.objects.get(value='colleague')
            x.relationships.add(xfnv1)
            x.relationships.add(xfnv2)
            x.relationships.add(xfnv3)
            x.save()
            # default case
            expected = 'Nicholas Tollervey (Colleague, Friend, Met)'
            self.assertEquals(expected, x.__unicode__())
            # with valid target but no relationships
            x.relationships.clear()
            x.save()
            expected = 'Nicholas Tollervey'
            self.assertEquals(expected, x.__unicode__())

        def test_hfeed(self):
            """
            Make sure the string representation of teh hFeed looks correct
            """
            # Set things up
            f = hFeed()
            f.save()
            self.assertEqual(u'Uncategorized feed', f.__unicode__())
            f.category = u'Some, tags'
            f.save()
            self.assertEqual(u'Some, tags', f.__unicode__())

