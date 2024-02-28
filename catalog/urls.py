from django.urls import path
from . import views
from .views import AuthorDetailView as ADV
from .views import LoanedBooksByUserListView as LBULV
from .views import LoanedBooksListView as LBLV
from .views import AuthorUpdate as AU
from .views import AuthorDelete as AD
from .views import BookUpdate as BU
from .views import BookDelete as BD

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('author/<int:pk>', ADV.as_view(), name='author-detail'),
]

urlpatterns += [
    path('mybooks/', LBULV.as_view(), name='my-borrowed'),
]

urlpatterns += [
    path('allbooks/', LBLV.as_view(), name='all-borrowed'),
]
t = 'renew-book-librarian'
urlpatterns += [
    path('book/<int:pk>/renew/', views.renew_book_librarian, name=t),
]


urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', AU.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', AD.as_view(), name='author-delete'),
]

urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', BU.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', BD.as_view(), name='book-delete'),
]
