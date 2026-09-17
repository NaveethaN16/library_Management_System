from django.shortcuts import render


def dashboard(request):
    return render(request, 'index.html')


def books_page(request):
    return render(request, 'books.html')


def members_page(request):
    return render(request, 'members.html')


def transactions_page(request):
    return render(request, 'transactions.html')
