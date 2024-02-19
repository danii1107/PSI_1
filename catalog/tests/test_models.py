from django.test import TestCase
from catalog.models import Author, Genre, Book, BookInstance, Language
from django.contrib.auth.models import User
from datetime import date


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Crear un objeto Author y guardarlo como una variable de clase
        cls.author = Author.objects.create(first_name='Big', last_name='Bob')

    def test_date_of_birth_label(self):
        # Usar la referencia del autor almacenada en vez de buscar por ID
        field_label = self.author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(field_label, 'birth')

    def test_first_name_label(self):
        # Similar para los demás métodos
        field_label = self.author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_date_of_death_label(self):
        field_label = self.author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'died')

    def test_first_name_max_length(self):
        max_length = self.author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        exp = f'{self.author.last_name}, {self.author.first_name}'
        self.assertEqual(str(self.author), exp)

    def test_get_absolute_url(self):
        expected_url = f'/catalog/author/{self.author.id}'
        self.assertEqual(self.author.get_absolute_url(), expected_url)


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        a = Author.objects.create(first_name='John', last_name='Doe')
        la = Language.objects.create(name='English')
        b = Book.objects
        y = 'A Test Book'
        t = 'Test Summary'
        i = '1234567890123'
        cls.book = b.create(title=y, author=a, summary=t, isbn=i, language=la)
        genre1 = Genre.objects.create(name='Science Fiction')
        genre2 = Genre.objects.create(name='Fantasy')
        cls.book.genre.set([genre1, genre2])

    def test_title_label(self):
        field_label = self.book._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_author_label(self):
        field_label = self.book._meta.get_field('author').verbose_name
        self.assertEqual(field_label, 'author')

    def test_summary_label(self):
        field_label = self.book._meta.get_field('summary').verbose_name
        self.assertEqual(field_label, 'summary')

    def test_isbn_label(self):
        field_label = self.book._meta.get_field('isbn').verbose_name
        self.assertEqual(field_label, 'ISBN')

    def test_language_label(self):
        field_label = self.book._meta.get_field('language').verbose_name
        self.assertEqual(field_label, 'language')

    def test_genre_label(self):
        field_label = self.book._meta.get_field('genre').verbose_name
        self.assertEqual(field_label, 'genre')

    def test_object_name_is_title(self):
        expected_object_name = self.book.title
        self.assertEqual(str(self.book), expected_object_name)

    def test_display_genre(self):
        x = self.book.genre
        expected = ', '.join([genre.name for genre in x.all()[:3]])
        self.assertEqual(self.book.display_genre(), expected)

    def test_get_absolute_url(self):
        expected_url = f'/catalog/book/{self.book.id}'
        self.assertEqual(self.book.get_absolute_url(), expected_url)


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.genre = Genre.objects.create(name='Historical Fiction')

    def test_name_label(self):
        field_label = self.genre._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        max_length = self.genre._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_name(self):
        expected_object_name = self.genre.name
        self.assertEqual(str(self.genre), expected_object_name)


class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        a = Author.objects.create(first_name='John', last_name='Doe')
        genre = Genre.objects.create(name='Fantasy')
        la = Language.objects.create(name='English')
        b = Book.objects
        t = 'Test Book'
        s = 'Test Summary'
        i = '1234567890123'
        bk = b.create(title=t, summary=s, isbn=i, author=a, language=la)
        bk.genre.add(genre)
        u = User.objects.create_user(username='testuser', password='12345')
        r = date.today()
        b = BookInstance.objects
        t = 'Unittest Imprint'
        cls.bookinstance = b.create(book=bk, imprint=t, due_back=r, borrower=u)

    def test_is_overdue(self):
        book_instance = BookInstance.objects.get(id=self.bookinstance.id)
        self.assertFalse(book_instance.is_overdue)

    def test_str(self):
        book_instance = BookInstance.objects.get(id=self.bookinstance.id)
        expected_string = f'{book_instance.id} ({book_instance.book.title})'
        self.assertEqual(str(book_instance), expected_string)

    def test_imprint_label(self):
        book_instance = BookInstance.objects.get(id=self.bookinstance.id)
        field_label = book_instance._meta.get_field('imprint').verbose_name
        self.assertEqual(field_label, 'imprint')

    def test_imprint_max_length(self):
        book_instance = BookInstance.objects.get(id=self.bookinstance.id)
        max_length = book_instance._meta.get_field('imprint').max_length
        self.assertEqual(max_length, 200)

    def test_due_back_label(self):
        book_instance = BookInstance.objects.get(id=self.bookinstance.id)
        field_label = book_instance._meta.get_field('due_back').verbose_name
        self.assertEqual(field_label, 'due back')


class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.language = Language.objects.create(name='Spanish')

    def test_name_label(self):
        field_label = self.language._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        max_length = self.language._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_object_name_is_name(self):
        expected_object_name = self.language.name
        self.assertEqual(str(self.language), expected_object_name)
