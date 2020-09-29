# -*- coding: utf-8 -*-

"""
Module for a simple secondary page type the will hold a contact form.
"""

from django.db import models as djm
from grapple import models as gplm
from wagtail.core import models as wtm
from wagtail.core import fields as wtf
from wagtail.admin import edit_handlers as wtah


class SomePage(wtm.Page):
    """Simple page to hold a form."""

    intro = wtf.RichTextField()
    contact_form = djm.ForeignKey(
        'forms.FormPage',
        null=True,
        blank=True,
        on_delete=djm.SET_NULL,
    )

    content_panels = wtm.Page.content_panels + [
        wtah.FieldPanel('intro'),
        wtah.FieldPanel('contact_form'),
    ]

    graphql_fields = [
        gplm.GraphQLString('intro'),
        gplm.GraphQLForeignKey(
            'contact_form',
            'forms.FormPage',
        ),
    ]
