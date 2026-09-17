from django.contrib import admin
from django.urls import path, include
from library import page_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('library.urls')),
    path('', page_views.dashboard, name='dashboard'),
    path('books/', page_views.books_page, name='books'),
    path('members/', page_views.members_page, name='members'),
    path('transactions/', page_views.transactions_page, name='transactions'),
]
