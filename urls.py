from django.conf.urls.defaults import patterns, include, url
from videos.views import grab_and_redirect, converter_page, basicsearch, catpage
from content.views import homepage, paypal_proxy
from convert.views import convert, getpending
from amember.views import showauth
from pages.views import show_page
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gafv.views.home', name='home'),
    # url(r'^gafv/', include('gafv.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^videos/rawid/(.*)/', grab_and_redirect),
    url(r'^dev/index.php/converter/view/(.*)/.*', grab_and_redirect),
    url(r'^converter/view/(.*)/.*', grab_and_redirect),
    url(r'^category/(.*)/', catpage),
    url(r'^videos/search/', basicsearch),
    url(r'^videos/(.*)/', converter_page),
    url(r'^convert/', convert),
    url(r'^getpending/', getpending),
    url(r'^auth/', showauth),
    url(r'^$', homepage),
    url(r'^amemberpro/plugins/payment/paypal_r/ipn.php', paypal_proxy),
    url(r'^members/plugins/payment/paypal_r/ipn.php', paypal_proxy),
    url(r'^(.*)/', show_page),

)
