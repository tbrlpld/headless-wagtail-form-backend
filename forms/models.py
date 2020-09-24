# -*- coding: utf-8 -*-

"""Define form models."""

from django.db import models as djm  # type: ignore[import]
from django import http as djhttp
from modelcluster import fields as mcf  # type: ignore[import]
from wagtail.admin import edit_handlers as wtah  # type: ignore[import]
from wagtail.core import fields as wtf  # type: ignore[import]
from wagtail.contrib.forms import models as wtfm  # type: ignore[import]
from grapple import models as gplm  # type: ignore[import]
import logging

logger = logging.getLogger(__name__)

class FormField(wtfm.AbstractFormField):
    """Define fields available in admin to build form."""

    page = mcf.ParentalKey(
        'FormPage',
        on_delete=djm.CASCADE,
        related_name='form_fields',
    )


class FormPage(wtfm.AbstractEmailForm):
    """Page that defines the form."""

    intro = wtf.RichTextField(blank=True)
    thank_you_text = wtf.RichTextField(blank=True)

    content_panels = wtfm.AbstractEmailForm.content_panels + [
        wtah.FieldPanel('intro', classname='full'),
        wtah.InlinePanel('form_fields', label='Form Fields'),
        wtah.FieldPanel('thank_you_text', classname='full'),
        wtah.MultiFieldPanel(
            [
                wtah.FieldRowPanel([
                    wtah.FieldPanel('from_address', classname='col6'),
                    wtah.FieldPanel('to_address', classname='col6'),
                ]),
                wtah.FieldPanel('subject'),
            ],
            'Email',
        ),
    ]

    graphql_fields = [
        gplm.GraphQLString('intro'),
        gplm.GraphQLField(
            'form_fields',
            'forms.schema.FormFieldType',
            is_list=True,
        ),
        gplm.GraphQLString('thank_you_text'),
        gplm.GraphQLString('from_address'),
        gplm.GraphQLString('to_address'),
        gplm.GraphQLString('subject'),
    ]

    spam_protection_field = {
        'label': 'Spammer Jammer',
        'help_text': 'Blank field for spam protection',
    }

    def save(self, *args, **kwargs):
        """Override form page save method to enforce existence of hidden field."""
        if not self.form_fields.filter(
            label=self.spam_protection_field['label']
        ):
            self.form_fields.create(
                label=self.spam_protection_field['label'],
                field_type='hidden',
                required=False,
                help_text=self.spam_protection_field['help_text'],
                sort_order=self.form_fields.count(),  # Always last field
            )
        super().save(*args, **kwargs)

    def get_data_fields(self):
        """Override method to remove spam protection field from data fields."""
        data_fields = super().get_data_fields()
        return [
            (clean_name, label)
            for clean_name, label in data_fields
            if label != self.spam_protection_field['label']
        ]

    def handle_POST(self, request, *args, **kwargs):
        """Handle POST request."""
        # logger.debug(f'{request.POST = }')
        spammer_jammer = request.POST.get('spammer_jammer')
        if spammer_jammer is None:
            # If the spammer_jammer field is missing, then the request is
            # malformed.
            return djhttp.HttpResponseBadRequest()
        elif spammer_jammer == '':
            return super().serve(request, *args, *kwargs)

    def handle_GET(self, request, *args, **kwargs):
        """Handle GET request."""
        return super().serve(request, *args, *kwargs)

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.handle_POST(request, *args, **kwargs)
        else:
            return self.handle_GET(request, *args, **kwargs)
