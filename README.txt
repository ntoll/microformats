Django Microformat Application v0.1 (alpha)

(c) 2009 Nicholas H.Tollervey (http://ntoll.org/contact)

See the file LICENSE.txt for the licensing terms and conditions.

This Django application makes it easier to integrate and use Microformats in
your web-application.

Microformats (http://microformats.org/) are a means of adding semantic 
information that is both human and machine readable to a web-site. In order to 
work with Microformats you need to use a toolkit such as Oomph  (included as a
javascript plugin with the unit tests - see http://visitmix.com/Lab/oomph)
or the Operator Add-on for Firefox (that supports more types of microformat) -
see https://addons.mozilla.org/en-US/firefox/addon/4106.

You get the following:

* Models relating to the geo, hCard, adr, hCalendar and XFN microformats.

* Simplified forms for the geo, hCard, adr, org, email, tel and hCalendar
microformats and fragments.

* The bare minimum admin functionality.

* Template filters for the geo, hCard, adr, hCalendar and XFN microformats.

To use the template filters you need to register the application and add:

{% load microformat_extras %}

to the top of the template you're using.

For an example of this in use check out the end of the following test file:

microformats/unit_tests/test_templatetags.py

Running the unit tests (./manage.py test microformats) will result in an example
file demonstrating the HTML markup produced by the template filters:

microformats/unit_tests/html_test/microformat_test.html

I've included the Oomph javascript library so you can play with the
microformats. A more fully featured library is the Operator add-on for Firefox.
IE8 will support Microformats natively.

*** WARNING ***

This is a first shot at integrating Microformats into Django. There are missing
microformats and I'm pretty sure some of the models could be improved as could
the template filters. Inevitably the code could be cleaned up too. I'll be using
this library in a new web-application so expect this code to change as I find
flaws and gremlins through using it "in anger".
