# -*- coding: utf-8 -*-

"""Define custom schema for forms app."""

import graphene_django  # type: ignore[import]

from forms import models


class FormFieldType(graphene_django.DjangoObjectType):
    """Auto-generate Graphene type for FormField."""

    class Meta:  # noqa: D106, WPS306
        model = models.FormField
