# -*- coding: utf-8 -*-

"""Define custom Graphene schema for app."""

from grapple.schema import schema as gplschema  # type: ignore[import]
import graphene  # type: ignore[import]

from forms import schema as forms_schema


custom_types = [
    forms_schema.FormFieldType,
]
types = gplschema.types + custom_types

schema = graphene.Schema(
    query=gplschema.Query,
    subscription=gplschema.Subscription,
    types=types,
)
