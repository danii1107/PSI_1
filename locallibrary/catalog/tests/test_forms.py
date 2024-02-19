import datetime

from django.test import SimpleTestCase
from django.utils import timezone

from catalog.forms import RenewBookForm


aux = 'renewal_date'


class RenewBookFormTest(SimpleTestCase):
    def test_renew_form_date_field_label(self):
        form = RenewBookForm()
        t = (form.fields[aux].label is None)
        self.assertTrue(t or form.fields[aux].label == aux)

    def test_renew_form_date_field_help_text(self):
        form = RenewBookForm()
        t = 'Enter a date between now and 4 weeks (default 3).'
        self.assertEqual(form.fields[aux].help_text, t)

    def test_renew_form_date_in_past(self):
        date = timezone.localtime() - datetime.timedelta(days=1)
        form = RenewBookForm(data={aux: date})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors[aux], ['Invalid date - renewal in past'])

    def test_renew_form_date_too_far_in_future(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4, days=1)
        form = RenewBookForm(data={aux: date})
        self.assertFalse(form.is_valid())
        t = 'Invalid date - renewal more than 4 weeks ahead'
        self.assertEqual(form.errors[aux], [t])

    def test_renew_form_date_today(self):
        date = timezone.localtime()
        form = RenewBookForm(data={aux: date})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        date = timezone.localtime() + datetime.timedelta(weeks=4)
        form = RenewBookForm(data={aux: date})
        self.assertTrue(form.is_valid())
