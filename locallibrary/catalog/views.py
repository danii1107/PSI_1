from django.shortcuts import render
from .models import *


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_genres = Genre.objects.count()

    num_books_containing_word = Book.objects.all().filter(
        title__icontains='a').count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_containing_word': num_books_containing_word,
        'num_visits':num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.views.generic.detail import DetailView
from django.views import generic

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

from django.contrib.auth.mixins import LoginRequiredMixin


class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Vista genérica basada en clases que enumera los libros prestados al usuario actual.
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(LoginRequiredMixin,generic.ListView):
    """
    Vista genérica basada en clases que enumera los libros prestados al usuario actual.
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_all_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')



from django.contrib.auth.decorators import permission_required, login_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

from .forms import RenewBookForm

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    context = {
        'form': form,
        'book_instance': book_inst,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author
from django.contrib.auth.mixins import PermissionRequiredMixin 
from django.contrib.auth.mixins import UserPassesTestMixin


class PermissionRequiredMixin1(UserPassesTestMixin):
    """Mixin que requiere que el usuario sea miembro del staff o tenga un permiso específico."""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.has_perm('catalog.add_author')

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

    
from .models import Book

from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Book

class StaffOrPermissionRequiredMixin(UserPassesTestMixin):
    """Mixin que requiere que el usuario sea miembro del staff o tenga un permiso específico."""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.has_perm('catalog.can_mark_returned')

class BookCreate(StaffOrPermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']

class BookUpdate(StaffOrPermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title','author','summary','isbn', 'genre', 'language']

class BookDelete(StaffOrPermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')