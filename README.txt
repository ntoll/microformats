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

This application attempts to help in two ways:

1) You get models for the supported microformats so you can store data in the
database (you don't have to use these models - see below for more information)

2) You get markup: there are some example templates for the supported
microformats in the /microformats/templates directory and I've written some
template filters that wrap around these templates so you get a convenient
shortcut.

Currently the supported microformats are:

* hCard - for representing people or organizations
* geo - for representing a geolocation
* adr - for representing an address
* hCalendar - for representing an event
* hListing - for representing an advertisement
* hReview - for representing an opinion 
* XFN - for representing friends and relationships

More will follow.

In the code, you get the following:

* Models relating to the geo, hCard, adr, hCalendar, hListing, hReview and XFN 
microformats. hCard has two models:
    
    1) hCard - a "flat" model containing only the most common fields

    2) hCardComplete - a full implementation of the vCard specification (and
    related tables)

* Simplified forms for the geo, hCard, adr, org, email, tel and hCalendar,
hListing and hReview microformats and fragments.

* Some useful admin functionality.

* Template filters for the geo, hCard, adr, hCalendar, hListing, hReview and 
XFN microformats.

To use the template filters you need to register the application and add:

{% load microformat_extras %}

to the top of the template you're using.

If you have an instance of a microformat model in your context you can use the
appropriate template filter to display it:

{{hCardInstance|hcard}}

will result in:

<div id="hcard_1" class="vcard">
    <div class="fn n">
        <a href="http://acme.com/" class="url">
            <span class="honorific-prefix">Mr</span>
            <span class="given-name">Joe</span>
            <span class="additional-name">Arthur</span>
            <span class="family-name">Blogs</span>
            <span class="honorific-suffix">PhD</span>
        </a>
    </div>
    <span class="title">Vice President</span>
    <div class="org">Acme Corp.</div>
    <a class="email" href="mailto:joe.blogs@acme.com">joe.blogs@acme.com</a> [work]<br/> 
    <a class="email" href="mailto:joeblogs2000@home-isp.com">joeblogs2000@home-isp.com</a> [home]<br/> 
    <div class="adr">
    <div class="street-address">5445 N.  27th Street</div>
        <span class="locality">Milwaukee</span>&nbsp;
        <span class="region">WI</span>&nbsp;
        <span class="postal-code">53209</span>&nbsp;
        <span class="country-name">United States</span>
    </div>
    <div class="tel"><span class="value">+44(0)1234 567890</span> [<abbr class="type" title="work">work</abbr>]</div>
    <div class="tel"><span class="value">+44(0)1324 234123</span> [<abbr class="type" title="home">home</abbr>]</div>
</div>

(This markup is based upon that produced by the hCard creator found at
http://microformats.org/code/hcard/creator)

In addition you can pass individual fields thus:

{{hCardInstance.role|hcard:'role'}}

Which will result in the following markup:

<span class="role">Vice President</span>

The template filters are clever enough to deal with different "types" of field.
For example, if you pass a datetime value like this:

{{datetimeInstance|hcal:'dtstart'}}

You'll get this:

<abbr class="dtstart" title="2009-04-11T13:30:00">Sat 11 Apr 2009 1:30 p.m.</abbr>

You can even do this:

{{datetimeInstance|hcal:'dtstart %B %d %Y"}}

To get this:

<abbr class="dtstart" title="1944-06-06T00:00:00">June 06 1944</abbr>

(Notice the passing of arguments for strftime.)

You don't even have to pass instances of the microformat models for the
template filters to work. The templates the filters wrap arround simply assume
the same field names as found in the microformat specifications (where '-' is 
replaced with the more Pythonic '_' so 'given-name' becomes 'given_name').

For example, you could create a dictionary thus:

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
hc['street_address'] = '5445 N.  27th Street'
hc['extended_address'] = ''
hc['locality'] = 'Milwaukee'
hc['region'] = 'WI'
hc['country_name'] = 'US'
hc['postal_code'] = '53209'
hc['title'] = 'Vice President'
hc['org'] = 'Acme Corp.'

And pass it to the 'hcard' template filter to get similar markup to that shown
above.

Finally, you don't even have to use the supplied microformat templates for the
filters. You can use your own by adding a reference to the appropriate template
in the following constants in the settings.py file of your project:

GEO_MICROFORMAT_TEMPLATE
HCARD_MICROFORMAT_TEMPLATE
HCAL_MICROFORMAT_TEMPLATE
HLISTING_MICROFORMAT_TEMPLATE
HREVIEW_MICROFORMAT_TEMPLATE
ADR_MICROFORMAT_TEMPLATE

For more examples check out the end of the following test file:

microformats/unit_tests/test_templatetags.py

and take a look at:

microformats/templates/test.html

Running the unit tests (./manage.py test microformats) will result in an example
file demonstrating the HTML markup produced by the template filters:

microformats/unit_tests/html_test/microformat_test.html

I've included the Oomph javascript library so you can play with the
microformats. A more fully featured library is the Operator add-on for Firefox.
IE8 will support Microformats natively.

Feedback is most welcome by sending email to the contact details found here:

http://ntoll.org/contact
