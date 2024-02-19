from datetime import date
import uuid  # Requerida para las instancias de libros únicos

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Genre(models.Model):
    """
    Modelo que representa un género literario
    """
    text = "Ingrese el género (p.ej.Ciencia Ficción, Poesía Francesa..)"
    name = models.CharField(max_length=200, help_text=text)

    def __str__(self):
        """
        Cadena que representa a la instancia particular del modelo
        """
        return self.name


class Book(models.Model):
    """
    Modelo que representa un libro (pero no un Ejemplar específico).
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    text = "Ingrese una breve descripción del libro"
    summary = models.TextField(max_length=1000, help_text=text)
    t = "href=\"https://www.isbn-international.org/content/what-isbn\""
    text = f"13 Caracteres <a {t}>ISBN number</a>"
    isbn = models.CharField('ISBN', max_length=13, help_text=text)
    genre = models.ManyToManyField(Genre, help_text="Seleccione un genero")
    laux = "language"
    language = models.ForeignKey(laux, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["title"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def display_genre(self):
        """
        Creates a string to display genre in Admin.
        """
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

    def __str__(self):
        """
        String que representa al objeto Book
        """
        return self.title

    def get_absolute_url(self):
        """
        Devuelve el URL a una instancia particular de Book
        """
        return reverse('book-detail', args=[str(self.id)])


class BookInstance(models.Model):
    """
    Modelo que representa una copia específica de un libro
    """
    t = "ID único para este libro particular en toda la biblioteca"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text=t)
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    a = models.SET_NULL
    borrower = models.ForeignKey(User, on_delete=a, null=True, blank=True)

    @property
    def is_overdue(self):
        return self.due_back and date.today() > self.due_back

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    t = 'Disponibilidad del libro'
    c = LOAN_STATUS
    aux = models.CharField
    status = aux(max_length=1, choices=c, blank=True, default='m', help_text=t)

    class Meta:
        ordering = ["due_back"]

    def __str__(self):
        """
        String para representar el Objeto del Modelo
        """
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """
    Modelo que representa un autor
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    b = 'birth'
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=b)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def get_absolute_url(self):
        """
        Retorna la url para acceder a una instancia particular de un autor.
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """
        String para representar el Objeto Modelo
        """
        return f'{self.last_name}, {self.first_name}'


class Language(models.Model):
    """
    Modelo que representa un lenguaje
    """
    t = "Ingrese el nombre del lenguaje (pe., Inglés, Español, Francés, etc.)"
    name = models.CharField(max_length=200, help_text=t)

    def __str__(self):
        """
        String para representar el Objeto Modelo
        """
        return self.name
