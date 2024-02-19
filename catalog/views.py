from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required, login_required
import datetime as dt

from .models import Book, Author, Genre
from .models import BookInstance as BII
from .forms import RenewBookForm


def index(request):
    """View function for home page of site."""
    num_books = Book.objects.all().count()
    num_instances = BII.objects.all().count()
    a = 'a'
    num_instances_available = BII.objects.filter(status__exact=a).count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    nbc_w = Book.objects.filter(title__icontains=a).count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_containing_word': nbc_w,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 2


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 3


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BII
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        u = self.request.user
        bii = BII.objects.filter(borrower=u)
        return bii.filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(LoginRequiredMixin, generic.ListView):
    model = BII
    template_name = 'catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BII.objects.filter(status__exact='o').order_by('due_back')


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BII, pk=pk)
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = dt.date.today() + dt.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_inst,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class PermissionRequiredMixin1(UserPassesTestMixin):
    """El usuario sea miembro del staff o tenga un permiso específico."""
    def test_func(self):
        u = self.request.user
        return u.is_staff or u.has_perm('catalog.add_author')


class AuthorCreate(PermissionRequiredMixin1, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.change_author'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'


class StaffOrPermissionRequiredMixin(UserPassesTestMixin):
    """El usuario sea miembro del staff o tenga un permiso específico."""
    def test_func(self):
        u = self.request.user
        return u.is_staff or u.has_perm('catalog.can_mark_returned')


class BookCreate(StaffOrPermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']


class BookUpdate(StaffOrPermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']


class BookDelete(StaffOrPermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
