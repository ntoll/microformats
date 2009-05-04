# -*- coding: UTF-8 -*-
"""
Forms tests for microformats 

Author: Nicholas H.Tollervey

"""
# python
import datetime

# django
from django.test.client import Client
from django.test import TestCase

# project
from microformats.forms import GeoForm, hCardForm, AdrForm, EmailForm, TelForm

class FormTestCase(TestCase):
        """
        Testing Forms 
        """
        # Reference fixtures here
        fixtures = []

        def test_geo(self):
            """
            Makes sure the validation for longitude and latitude works correctly
            """
            # Safe case
            data = {
                    'latitude': '37.408183',
                    'latitude_description': u'N 37° 24.491',
                    'longitude': '-122.13855',
                    'longitude_description': u'W 122° 08.313'
                    }
            f = GeoForm(data)
            self.assertEquals(True, f.is_valid())
            # Remove the non required fields
            data['latitude_description'] = ''
            data['longitude_description'] = ''
            f = GeoForm(data)
            self.assertEquals(True, f.is_valid())
            # Boundry check latitude
            # Upper
            data['latitude'] = '90'
            f = GeoForm(data)
            self.assertEquals(True, f.is_valid())
            data['latitude'] = '90.000001'
            f = GeoForm(data)
            self.assertEquals(False, f.is_valid())
            # Lower
            data['latitude'] = '-90'
            f = GeoForm(data)
            self.assertEquals(True, f.is_valid())
            data['latitude'] = '-90.000001'
            f = GeoForm(data)
            self.assertEquals(False, f.is_valid())
            data['latitude'] = '37.408183'
            # Boundry check for longitude
            # Upper
            data['longitude'] = '180'
            f = GeoForm(data)
            self.assertEquals(True, f.is_valid())
            data['longitude'] = '180.000001'
            f = GeoForm(data)
            self.assertEquals(False, f.is_valid())
            # Lower
            data['longitude'] = '-180'
            f = GeoForm(data)
            self.assertEquals(True, f.is_valid())
            data['longitude'] = '-180.000001'
            f = GeoForm(data)
            self.assertEquals(False, f.is_valid())
            data['longitude'] = '-122.13855'
            # Make sure required fields are correct
            data['latitude'] = ''
            f = GeoForm(data)
            self.assertEquals(False, f.is_valid())
            data['latitude'] = '37.408183'
            data['longitude'] = ''
            f = GeoForm(data)
            self.assertEquals(False, f.is_valid())

        def test_hcard(self):
            """
            Makes sure if long or lat are supplied then so should the other, and
            that it validates something useful for the fn
            """
            # Long and lat
            data = {
                    'given_name': 'John',
                    'longitude': '-122.13855'
                    }
            f = hCardForm(data)
            # No latitude
            self.assertEquals(False, f.is_valid())
            self.assertEquals(1, len(f.errors['longitude']))
            data['longitude'] = ''
            data['latitude'] = '37.408183'
            f = hCardForm(data)
            # No longitude
            self.assertEquals(False, f.is_valid())
            self.assertEquals(1, len(f.errors['latitude']))
            data['longitude'] = '-122.13855'
            # No fn related data
            data['given_name'] = ''
            f = hCardForm(data)
            self.assertEquals(False, f.is_valid())
            self.assertEquals(1, len(f.errors['__all__']))
            # given name is valid
            data['given_name'] = 'John'
            f = hCardForm(data)
            self.assertEquals(True, f.is_valid())
            # nickname is valid
            data['given_name'] = ''
            data['nickname'] = 'John'
            f = hCardForm(data)
            self.assertEquals(True, f.is_valid())
            # as is org
            data['nickname'] = ''
            data['org'] = 'Acme Corp.'
            f = hCardForm(data)
            self.assertEquals(True, f.is_valid())

        def test_adr(self):
            """
            Makes sure the types are rendered as an unordered list of checkboxes
            """
            f = AdrForm()
            p = f.as_p()
            self.assertEquals(True, p.find('type="checkbox" name="types"')>-1)

        def test_email(self):
            """
            Makes sure the types are rendered as an unordered list of checkboxes
            """
            f = EmailForm()
            p = f.as_p()
            self.assertEquals(True, p.find('type="checkbox" name="types"')>-1)

        def test_tel(self):
            """
            Makes sure the types are rendered as an unordered list of checkboxes
            """
            f = TelForm()
            p = f.as_p()
            self.assertEquals(True, p.find('type="checkbox" name="types"')>-1)

