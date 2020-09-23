# -*- coding: utf-8 -*-

"""Test for the forms app."""

from wagtail.tests import utils as wttu  # type: ignore[import]

from home.models import HomePage
from forms.models import FormPage


class FormPageTests(wttu.WagtailPageTests):
    def setUp(self):
        # The first home page instance is created during migration. This
        # feature comes predefined with the Wagtail starter.
        home_page = HomePage.objects.first()

        # Additional pages can now be added as child pages to this one.
        contact_form_page = FormPage(title='Contact')
        home_page.add_child(instance=contact_form_page)
        contact_form_page.save()

        self.assertEquals(FormPage.objects.count(), 1)

    def test_spammer_jammer_form_field_exists(self):
        first_form_page = FormPage.objects.first()
        jammer_field = first_form_page.form_fields.filter(
            label='Spammer Jammer',
        )
        self.assertTrue(jammer_field.exists())
