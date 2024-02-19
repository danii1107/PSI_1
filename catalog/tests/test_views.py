from django.test import TestCase
from django.urls import reverse
from catalog.models import Author
import datetime as dt
from django.utils import timezone as tz
from django.contrib.auth import get_user_model
from catalog.models import BookInstance, Book, Genre, Language
import uuid
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Dominique {author_id}',
                last_name=f'Surname {author_id}',
            )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['author_list']), 3)

    def test_lists_all_authors(self):
        # Get second page and confirm it has (exactly) remaining 3 items
        response = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['author_list']), 3)


User = get_user_model()
p1 = '1X<ISRUkw+tuK'
p2 = '2HJ1vRV0Z&3iD'
u1 = 'testuser1'
u2 = 'testuser2'


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username=u1, password=p1)
        test_user2 = User.objects.create_user(username=u2, password=p2)

        test_user1.save()
        test_user2.save()

        # Create a book
        a = Author.objects
        test_author = a.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = tz.localtime() + dt.timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        rp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(rp, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username=u1, password=p1)
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), u1)
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        t = 'catalog/bookinstance_list_borrowed_user.html'
        self.assertTemplateUsed(response, t)

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username=u1, password=p1)
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), u1)
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), u1)
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual(bookitem.status, 'o')

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()

        login = self.client.login(username=u1, password=p1)
        response = self.client.get(reverse('my-borrowed'))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), u1)
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


class RenewBookInstancesViewTest(TestCase):
    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(username=u1, password=p1)
        test_user2 = User.objects.create_user(username=u2, password=p2)

        test_user1.save()
        test_user2.save()

        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Create a book
        a = Author.objects
        test_author = a.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Create a BookInstance object for test_user1
        return_date = dt.date.today() + dt.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user1,
            status='o',
        )

        # Create a BookInstance object for test_user2
        return_date = dt.date.today() + dt.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book,
            imprint='Unlikely Imprint, 2016',
            due_back=return_date,
            borrower=test_user2,
            status='o',
        )

    def test_redirect_if_not_logged_in(self):
        t = 'renew-book-librarian'
        c = self.client
        r = c.get(reverse(t, kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username=u1, password=p1)
        t = 'renew-book-librarian'
        u = self.client
        r = u.get(reverse(t, kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(r.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username=u2, password=p2)
        t = 'renew-book-librarian'
        c = self.client
        r = c.get(reverse(t, kwargs={'pk': self.test_bookinstance2.pk}))
        self.assertEqual(r.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username=u2, password=p2)
        t = 'renew-book-librarian'
        c = self.client
        r = c.get(reverse(t, kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(r.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid = uuid.uuid4()
        login = self.client.login(username=u2, password=p2)
        t = 'renew-book-librarian'
        response = self.client.get(reverse(t, kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username=u2, password=p2)
        t = 'renew-book-librarian'
        c = self.client
        response = c.get(reverse(t, kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username=u2, password=p2)
        t = 'renew-book-librarian'
        c = self.client
        response = c.get(reverse(t, kwargs={'pk': self.test_bookinstance1.pk}))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = dt.date.today() + dt.timedelta(weeks=3)
        r = response.context['form']
        self.assertEqual(r.initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username=u2, password=p2)
        valid_date_in_future = dt.date.today() + dt.timedelta(weeks=2)
        t = 'renew-book-librarian'
        c = self.client
        s = self.test_bookinstance1.pk
        v = valid_date_in_future
        r = c.post(reverse(t, kwargs={'pk': s, }), {'renewal_date': v})
        self.assertRedirects(r, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username=u2, password=p2)
        date_in_past = dt.date.today() - dt.timedelta(weeks=1)
        t = 'renew-book-librarian'
        c = self.client
        s = self.test_bookinstance1.pk
        d = date_in_past
        r = c.post(reverse(t, kwargs={'pk': s}), {'renewal_date': d})
        self.assertEqual(r.status_code, 200)
        a = r.context['form']
        c = 'renewal_date'
        self.assertFormError(a, c, 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username=u2, password=p2)
        invalid_date_in_future = dt.date.today() + dt.timedelta(weeks=5)
        t = 'renew-book-librarian'
        s = self.test_bookinstance1.pk
        i = invalid_date_in_future
        c = self.client
        response = c.post(reverse(t, kwargs={'pk': s}), {'renewal_date': i})
        self.assertEqual(response.status_code, 200)
        r = response.context['form']
        t = 'renewal_date'
        s = 'Invalid date - renewal more than 4 weeks ahead'
        self.assertFormError(r, t, s)


class AuthorCreateViewTest(TestCase):
    """Test case for the AuthorCreate view (Created as Challenge)."""

    def setUp(self):
        # Create a user
        self.test_user = User.objects.create_user(
            username='test_user', password='some_password')

        # Get permission
        content_type = ContentType.objects.get_for_model(Author)
        permission = Permission.objects.get(
            codename='add_author',
            content_type=content_type,
        )

        # Assign permission to the user
        self.test_user.user_permissions.add(permission)
        self.test_user.save()

        # URL for creating a new author
        self.create_author_url = reverse('author-create')

    def test_redirect_if_not_logged_in(self):
        r = self.client.get(self.create_author_url)
        s = self.create_author_url
        self.assertRedirects(r, f'/accounts/login/?next={s}')

    def test_logged_in_with_permission(self):
        self.client.login(username='test_user', password='some_password')
        response = self.client.get(self.create_author_url)
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_author_if_logged_in(self):
        self.client.login(username='test_user', password='some_password')
        c = self.client
        response = c.get(reverse('author-detail', kwargs={'pk': '1234'}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        self.client.login(username='test_user', password='some_password')
        response = self.client.get(self.create_author_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_form_date_of_death_initially_set_to_expected_date(self):
        self.client.login(username='test_user', password='some_password')
        response = self.client.get(self.create_author_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="11/11/2023"')

    def test_redirects_to_detail_view_on_success(self):
        self.client.login(username='test_user', password='some_password')
        c = self.client
        s = self.create_author_url
        f = 'First'
        t = 'Last'
        b = '01/01/1950'
        d = '11/11/2023'
        a = {'first_name': f, 'last_name': t}
        a = {**a, 'date_of_birth': b, 'date_of_death': d}
        r = c.post(s, a)
        self.assertEqual(r.status_code, 302)

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='test_user', password='some_password')
        permission = Permission.objects.get(codename='add_author')
        self.test_user.user_permissions.remove(permission)
        self.test_user.save()
        response = self.client.get(self.create_author_url)
        self.assertEqual(response.status_code, 403)
