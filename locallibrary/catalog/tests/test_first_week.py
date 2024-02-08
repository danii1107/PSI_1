"""
First Week Tests
Created by JAMI
EPS-UAM 2024
"""

import sys
import os
from django.test import TestCase
from django.urls import reverse
from catalog.views import index
from catalog.models import Book, BookInstance, Language, Genre, Author

def check_environment():
    """ Check if we are using a python defined in a virtual enviroment
    or in a conda enviroment different from 'base'"""
    result = False
    # Check if we are inside a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        result = True
   # check if we are inside a conda environment different from base
    elif os.environ.get('CONDA_DEFAULT_ENV') is not None:
        if os.environ.get('CONDA_DEFAULT_ENV') != 'base':
            result = True
    return result
    
class FirstWeekTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        try:
            from populate_catalog import populate
            populate()
        except ImportError:
            print('The module populate_catalog does not exist')
        except NameError:
            print('The function populate() does not exist or is not correct')
        except Exception:
            print('Something went wrong in the populate() function :-(')
            raise


    def test_running_inside_virtualenv(self):
       vi_on = check_environment()
       self.assertTrue(vi_on)


    def test_admin_pattern(self):
        try:
            from locallibrary.urls import urlpatterns as urlp
            self.assertIn('admin', str(urlp[0]))
        except Exception:
            print('Did you define urlpatterns? Something is wrong with that!')
            raise


    def test_catalog_pattern(self):
        try:
            from locallibrary.urls import urlpatterns as urlp
            self.assertIn('catalog.urls', str(urlp[1]))
        except Exception:
            print('Did you define urlpatterns? Something is wrong with that!')
            raise


    def test_date_of_birth_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(field_label, 'birth') 


    def test_booK_with_two_genres(self):
        book = Book.objects.get(id=1)
        self.assertTrue((book.genre.count()>= 2))


    def test_due_back_book_on_loan(self):
        bi = BookInstance.objects.filter(book__title='The Shining', status='o').first()
        self.assertEqual(str(bi.due_back), '2021-10-10')


    def test_books_on_loan(self):
        bi = BookInstance.objects.filter(status='o').count()
        self.assertTrue((bi>=2))


    def test_challenge_one_1(self):
        try:
            l1 = language = Language.objects.filter(name__contains='English').first()
            fl = l1._meta.get_field('name').verbose_name
            self.assertEqual(fl, 'name')
        except Exception:
            print('Did you work on the Language Model Challenge? Something is wrong with that!')
            raise


    def test_challenge_one_2(self):
        try:
            l1 = language = Language.objects.filter(name__contains='English').values()[0]['name']
            self.assertEqual(l1, 'English')
        except Exception:
            print('Did you work on the Language Model Challenge? Something is wrong with that!')
            raise


    def test_challenge_one_3(self):
        try:
            l2 = language = Language.objects.filter(name__contains='Spanish').values()[0]['name']
            self.assertEqual(l2, 'Spanish')
        except Exception:
            print('Did you work on the Language Model Challenge? Something is wrong with that!')
            raise

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Author.objects.create(first_name='John', last_name='Doe')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'Died')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEqual(str(author), expected_object_name)


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name='Fiction')

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        field_label = genre._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_name(self):
        genre = Genre.objects.get(id=1)
        expected_object_name = genre.name
        self.assertEqual(str(genre), expected_object_name)

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name='John', last_name='Doe')
        genre = Genre.objects.create(name='Fiction')
        language = Language.objects.create(name='Spanish')
        Book.objects.create(title='The Book', author=author, summary='This is a good book.', isbn='0123456789012', language=language)

    def test_title_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_summary_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('summary').verbose_name
        self.assertEqual(field_label, 'summary')

    def test_isbn_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('isbn').verbose_name
        self.assertEqual(field_label, 'ISBN')

    def test_language_label(self):
        book = Book.objects.get(id=1)
        field_label = book._meta.get_field('language').verbose_name
        self.assertEqual(field_label, 'language')

    def test_title_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_summary_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('summary').max_length
        self.assertEqual(max_length, 1000)

    def test_isbn_max_length(self):
        book = Book.objects.get(id=1)
        max_length = book._meta.get_field('isbn').max_length
        self.assertEqual(max_length, 13)

    def test_object_name_is_title(self):
        book = Book.objects.get(id=1)
        expected_object_name = book.title
        self.assertEqual(str(book), expected_object_name)


class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name='John', last_name='Doe')
        genre = Genre.objects.create(name='Fiction')
        language = Language.objects.create(name='Spanish')
        book = Book.objects.create(title='The Book', author=author, summary='This is a good book.', isbn='0123456789012', language=language)
        BookInstance.objects.create(id=1, book=book, imprint='X Publisher', due_back='2022-01-21')

    def test_imprint_label(self):
        book_instance = BookInstance.objects.get(id=1)
        field_label = book_instance._meta.get_field('imprint').verbose_name
        self.assertEqual(field_label, 'imprint')

    def test_due_back_label(self):
        book_instance = BookInstance.objects.get(id=1)
        field_label = book_instance._meta.get_field('due_back').verbose_name
        self.assertEqual(field_label, 'due back')

class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Language.objects.create(name='Spanish')

    def test_name_label(self):
        language = Language.objects.get(id=1)
        field_label = language._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        language = Language.objects.get(id=1)
        max_length = language._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_name(self):
        language = Language.objects.get(id=1)
        expected_object_name = language.name
        self.assertEqual(str(language), expected_object_name)

    """def test_get_absolute_url(self):
        language = Language.objects.get(id=1)
        absolute_url = language.get_absolute_url()
        expected_url = reverse('language-detail', args=[str(language.id)])
        self.assertEqual(absolute_url, expected_url) """

class IndexViewTest(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'wow')

    #def test_get_absolute_url(self):
        #author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        #self.assertEqual(author.get_absolute_url(), '/catalog/author/1') 