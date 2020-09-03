# -*- coding: utf-8 -*-

"""Define form models."""

from django.db import models as djm  # type: ignore[import]
from modelcluster import fields as mcf  # type: ignore[import]
from wagtail.admin import edit_handlers as wtah  # type: ignore[import]
from wagtail.core import fields as wtf  # type: ignore[import]
from wagtail.contrib.forms import models as wtfm  # type: ignore[import]
from grapple import models as gplm  # type: ignore[import]


class FormField(wtfm.AbstractFormField):
    """Define fields available in admin to build form."""

    page = mcf.ParentalKey(
        'FormPage',
        on_delete=djm.CASCADE,
        related_name='form_fields',
    )


# class FormFieldType(graphene_django.DjangoObjectType):
#     class Meta:
#         model = FormField


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
