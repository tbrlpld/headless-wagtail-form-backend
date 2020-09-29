# -*- coding: utf-8 -*-

"""
Module for a simple secondary page type the will hold a contact form.
"""

from grapple import models as gplm
from wagtail.core import models as wtm
from wagtail.core import fields as wtf
from wagtail.admin import edit_handlers as wtah


class ContentPage(wtm.Page):
    """Simple page to hold a form."""

    intro = wtf.RichTextField()

    content_panels = wtm.Page.content_panels + [
        wtah.FieldPanel('intro'),
    ]

    graphql_fields = [
        gplm.GraphQLString('intro'),
    ]
