from django.core.management.base import BaseCommand

from library.models import Book, Member


SAMPLE_BOOKS = [
    {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "9780132350884", "category": "TECHNOLOGY", "publisher": "Prentice Hall", "publish_year": 2008, "total_copies": 4},
    {"title": "A Brief History of Time", "author": "Stephen Hawking", "isbn": "9780553380163", "category": "SCIENCE", "publisher": "Bantam", "publish_year": 1988, "total_copies": 3},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "9780061120084", "category": "FICTION", "publisher": "Harper Perennial", "publish_year": 1960, "total_copies": 5},
    {"title": "Sapiens", "author": "Yuval Noah Harari", "isbn": "9780062316097", "category": "NON_FICTION", "publisher": "Harper", "publish_year": 2015, "total_copies": 3},
    {"title": "The Wright Brothers", "author": "David McCullough", "isbn": "9781476728742", "category": "BIOGRAPHY", "publisher": "Simon & Schuster", "publish_year": 2015, "total_copies": 2},
    {"title": "Guns, Germs, and Steel", "author": "Jared Diamond", "isbn": "9780393317558", "category": "HISTORY", "publisher": "W. W. Norton", "publish_year": 1997, "total_copies": 2},
    {"title": "Charlotte's Web", "author": "E. B. White", "isbn": "9780061124952", "category": "CHILDREN", "publisher": "Harper Collins", "publish_year": 1952, "total_copies": 4},
    {"title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "isbn": "9780262033848", "category": "TECHNOLOGY", "publisher": "MIT Press", "publish_year": 2009, "total_copies": 3},
]

SAMPLE_MEMBERS = [
    {"name": "Aditi Sharma", "email": "aditi.sharma@example.com", "phone": "+919812345001", "address": "12 MG Road, Karur"},
    {"name": "Rohan Verma", "email": "rohan.verma@example.com", "phone": "+919812345002", "address": "45 Anna Nagar, Chennai"},
    {"name": "Priya Nair", "email": "priya.nair@example.com", "phone": "+919812345003", "address": "8 Gandhi Street, Trichy"},
    {"name": "Karthik Raja", "email": "karthik.raja@example.com", "phone": "+919812345004", "address": "23 Bharathi Nagar, Karur"},
    {"name": "Sneha Iyer", "email": "sneha.iyer@example.com", "phone": "+919812345005", "address": "5 Lake View, Coimbatore"},
]


class Command(BaseCommand):
    help = "Seed the database with sample books and members for demonstration purposes."

    def handle(self, *args, **options):
        created_books = 0
        for data in SAMPLE_BOOKS:
            _, created = Book.objects.get_or_create(
                isbn=data["isbn"],
                defaults={**data, "available_copies": data["total_copies"]},
            )
            if created:
                created_books += 1

        created_members = 0
        for data in SAMPLE_MEMBERS:
            _, created = Member.objects.get_or_create(
                email=data["email"],
                defaults=data,
            )
            if created:
                created_members += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {created_books} books and {created_members} members added."
        ))
