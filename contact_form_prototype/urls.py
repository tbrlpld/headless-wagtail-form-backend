from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.decorators import csrf as djvdcsrf  # type: ignore[import]

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.core import views as wagtail_views
from wagtail.documents import urls as wagtaildocs_urls

from grapple import urls as grapple_urls

from search import views as search_views

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('search/', search_views.search, name='search'),

    path(r'', include(grapple_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Replace the Wagtail serve view with itself, but wrapped with the Django CSRF
# exemption. This allows to send POST requests to the Wagtail URLs without
# having to pull the CRSF token into the forms first. This is makes it easier
# to use the Wagtail Form builder in a headless setup.
serve_filtered_wagtail_urls = [
    url for url in wagtail_urls.urlpatterns if url.name == 'wagtail_serve'
]
if serve_filtered_wagtail_urls:
    serve_url = serve_filtered_wagtail_urls[0]
    serve_url.callback = djvdcsrf.csrf_exempt(serve_url.callback)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
