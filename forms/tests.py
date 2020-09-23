# -*- coding: utf-8 -*-

"""Test for the forms app."""

from django import test as djt
from django.contrib.auth import models as djam
import pytest
from wagtail.tests import utils as wttu  # type: ignore[import]

from home.models import HomePage
from forms.models import FormPage



@pytest.fixture
def contact_form_page(db):
    # The first home page instance is created during migration. This
    # feature comes predefined with the Wagtail starter.
    home_page = HomePage.objects.first()

    # Additional pages can now be added as child pages to this one.
    contact_form_page = FormPage(title='Contact')
    home_page.add_child(instance=contact_form_page)
    contact_form_page.save()

    assert FormPage.objects.count() == 1

    yield contact_form_page


class TestFormPageTests:

    @pytest.mark.django_db
    def test_spammer_jammer_form_field_exists_on_plain_form(self, contact_form_page):
        first_form_page = FormPage.objects.first()
        jammer_field = first_form_page.form_fields.filter(
            label='Spammer Jammer',
        )
        assert jammer_field.exists()

    # def test_get_request(self):
    #     first_form_page = FormPage.objects.first()
    #     # https://docs.djangoproject.com/en/3.1/topics/testing/advanced/
    #     req_factory = djt.RequestFactory()
    #     req = req_factory.get(first_form_page.url)

    #     res = first_form_page.serve(req)

    #     # TODO: Update this test so that it makes sense. There should be
    #     #       something that is returned on GET.
    #     assert res is None


    # def test_post_request(self):
    #     first_form_page = FormPage.objects.first()

    #     req_factory = djt.RequestFactory()
    #     req = req_factory.post(
    #         first_form_page.url,
    #         {
    #             'spammer_jammer': '',
    #         },
    #     )
    #     req.user = djam.AnonymousUser()

    #     res = first_form_page.serve(req)
    #     assert res.status_code == 200

    # TODO: Test form payload saved when spam prot field empty
    # TODO: Test form payload not saved when spam prot field not empty
