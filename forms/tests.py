# -*- coding: utf-8 -*-

"""Test for the forms app."""

from django import test as djt
from django.contrib.auth import models as djam
import pytest
from wagtail.tests import utils as wttu  # type: ignore[import]

from home.models import HomePage
from forms.models import FormPage




class TestFormPage(object):
    """Test form page."""

    @pytest.fixture
    def contact_form_page(self, db):  # noqa: D102
        # The first home page instance is created during migration. This
        # feature comes predefined with the Wagtail starter.
        home_page = HomePage.objects.first()
        # Additional pages can now be added as child pages to this one.
        contact_form_page = FormPage(title='Contact')
        home_page.add_child(instance=contact_form_page)
        contact_form_page.save()
        assert FormPage.objects.count() == 1
        return contact_form_page

    @pytest.fixture
    def request_factory(self):
        return djt.RequestFactory()

    def test_spammer_jammer_form_field_exists_on_plain_form(
        self,
        contact_form_page,
    ):  # noqa: D102
        first_form_page = FormPage.objects.first()
        jammer_field = first_form_page.form_fields.filter(
            label='Spammer Jammer',
        )
        assert jammer_field.exists()

    def test_get_request(
        self,
        contact_form_page,
        client,
    ):
        res = client.get(contact_form_page.url)

        assert res.status_code == 200
        assert b'form endpoint' in res.content

    def test_empty_post_request(
        self,
        contact_form_page,
        request_factory,
    ):  # noqa: D102
        req = request_factory.post(
            contact_form_page.url,
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page.serve(req)

        assert res.status_code == 400

    def test_post_request(
        self,
        contact_form_page,
        request_factory,
    ):  # noqa: D102
        req = request_factory.post(
            contact_form_page.url,
            {
                'spammer_jammer': '',
            },
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page.serve(req)

        assert res.status_code == 200

    # TODO: Test form payload saved when spam prot field empty
    # TODO: Test form payload not saved when spam prot field not empty
