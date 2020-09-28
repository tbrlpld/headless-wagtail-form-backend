# -*- coding: utf-8 -*-

"""Test for the forms app."""
import json

from django import test as djt
from django import utils as djutil
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
        contact_form_page = FormPage(
            title='Contact',
            from_address='contact-form@example.com',
            to_address='staff@example.com',
            subject='New form submission',
        )
        home_page.add_child(instance=contact_form_page)
        contact_form_page.save()
        assert FormPage.objects.count() == 1
        return contact_form_page

    @pytest.fixture
    def contact_form_page_w_email_field(self, contact_form_page):  # noqa: D102
        contact_form_page.form_fields.create(
            label='Email',
            field_type='email',
            required=True,
        )
        contact_form_page.save()
        return contact_form_page

    @pytest.fixture
    def request_factory(self):
        return djt.RequestFactory()

    def test_spam_check_form_field_exists_on_plain_form(
        self,
        contact_form_page,
    ):  # noqa: D102
        first_form_page = FormPage.objects.first()
        jammer_field = first_form_page.form_fields.filter(
            label='Spammer Jammer',
        )

        assert jammer_field.exists()

    def test_GET_success_resp(
        self,
        contact_form_page,
        client,
    ):  # noqa: D102, N802
        res = client.get(contact_form_page.url)

        assert res.status_code == 200

    def test_GET_shows_info(
        self,
        contact_form_page,
        client,
    ):  # noqa: D102, N802
        res = client.get(contact_form_page.url)

        assert b'form endpoint' in res.content

    def test_POST_empty_error_resp(
        self,
        contact_form_page,
        request_factory,
    ):  # noqa: D102, N802
        req = request_factory.post(
            contact_form_page.url,
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page.serve(req)

        assert res.status_code == 400

    def test_POST_empty_spam_field_success_resp(
        self,
        contact_form_page,
        request_factory,
    ):  # noqa: D102, N802
        req = request_factory.post(
            contact_form_page.url,
            {
                'spammer_jammer': '',
            },
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page.serve(req)

        assert res.status_code == 200

    def test_POST_nonempty_spam_field_success_resp(
        self,
        contact_form_page,
        request_factory,
    ):  # noqa: DAR101, N802
        """
        Non-empty spam field should still get a success response.

        I don't want to give spammers an indication that they should try again.
        So they should get a success response. The request will be accepted,
        but will be ignored for further processing.

        """
        req = request_factory.post(
            contact_form_page.url,
            {
                'spammer_jammer': 'Only spammers will fill this.',
            },
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page.serve(req)

        assert res.status_code == 200

    def test_POST_nonspam_payload_saved(
        self,
        contact_form_page_w_email_field,
        request_factory,
    ):  # noqa: D102, N802
        req = request_factory.post(
            contact_form_page_w_email_field.url,
            {
                'email': 'someone@example.com',
                'spammer_jammer': '',
            },
        )
        req.user = djam.AnonymousUser()
        submission_class = contact_form_page_w_email_field.get_submission_class()
        assert submission_class.objects.count() == 0

        res = contact_form_page_w_email_field.serve(req)

        assert res.status_code == 200
        assert submission_class.objects.count() == 1
        submission_last = submission_class.objects.last()
        assert submission_last.get_data().get('email') == 'someone@example.com'

    def test_POST_spam_payload_not_saved(
        self,
        contact_form_page_w_email_field,
        request_factory,
    ):  # noqa: D102, N802
        req = request_factory.post(
            contact_form_page_w_email_field.url,
            {
                'email': 'someone@example.com',
                'spammer_jammer': 'This should only be filled by spammers.',
            },
        )
        req.user = djam.AnonymousUser()
        submission_class = contact_form_page_w_email_field.get_submission_class()
        assert submission_class.objects.count() == 0

        res = contact_form_page_w_email_field.serve(req)

        assert res.status_code == 200
        assert submission_class.objects.count() == 0

    def test_POST_invalid_form_data_error_response(
        self,
        contact_form_page_w_email_field,
        request_factory,
    ):  # noqa: D102, N802
        req = request_factory.post(
            contact_form_page_w_email_field.url,
            {
                'email': 'This is not an email address',
                'spammer_jammer': '',
            },
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page_w_email_field.serve(req)

        assert res.status_code == 400

    def test_POST_invalid_form_data_response_contains_error_message(
        self,
        contact_form_page_w_email_field,
        request_factory,
    ):  # noqa: D102, N802
        req = request_factory.post(
            contact_form_page_w_email_field.url,
            {
                'email': 'This is not an email address',
                'spammer_jammer': '',
            },
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page_w_email_field.serve(req)

         # Convert byte response content to string
        res_text = str(res.content, encoding='utf-8')

        res_dict = json.loads(res_text)
        email_errors = res_dict.get('email')
        assert email_errors is not None
        assert email_errors[0]['message'] == 'Enter a valid email address.'
        assert email_errors[0]['code'] == 'invalid'

    def test_POST_valid_payload_sent_per_email_to_admin(
        self,
        contact_form_page_w_email_field,
        request_factory,
        mailoutbox,
    ):
        assert len(mailoutbox) == 0
        req = request_factory.post(
            contact_form_page_w_email_field.url,
            {
                'email': 'someone@something.com',
                'spammer_jammer': '',
            },
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page_w_email_field.serve(req)

        assert res.status_code == 200
        assert len(mailoutbox) == 1
        notification_email = mailoutbox[0]
        assert notification_email.from_email == 'contact-form@example.com'
        assert list(notification_email.to) == ['staff@example.com']
        assert notification_email.subject == 'New form submission'
        assert 'someone@something.com' in notification_email.body

    def test_POST_invalid_payload_not_sent_per_email_to_admin(
        self,
        contact_form_page_w_email_field,
        request_factory,
        mailoutbox,
    ):
        assert len(mailoutbox) == 0
        req = request_factory.post(
            contact_form_page_w_email_field.url,
            {
                'email': 'This is not an email address',
                'spammer_jammer': '',
            },
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page_w_email_field.serve(req)

        assert res.status_code == 400
        assert len(mailoutbox) == 0

    def test_POST_spam_payload_not_sent_per_email_to_admin(
        self,
        contact_form_page_w_email_field,
        request_factory,
        mailoutbox,
    ):
        assert len(mailoutbox) == 0
        req = request_factory.post(
            contact_form_page_w_email_field.url,
            {
                'email': 'someone@someone.com',
                'spammer_jammer': 'This is spam',
            },
        )
        req.user = djam.AnonymousUser()

        res = contact_form_page_w_email_field.serve(req)

        assert res.status_code == 200
        assert len(mailoutbox) == 0
