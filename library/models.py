from datetime import timedelta

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="Enter a valid phone number (7 to 15 digits, optional leading +)."
)


class Book(models.Model):
    CATEGORY_CHOICES = [
        ('FICTION', 'Fiction'),
        ('NON_FICTION', 'Non-Fiction'),
        ('SCIENCE', 'Science'),
        ('TECHNOLOGY', 'Technology'),
        ('HISTORY', 'History'),
        ('BIOGRAPHY', 'Biography'),
        ('CHILDREN', 'Children'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    isbn = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    publisher = models.CharField(max_length=150, blank=True)
    publish_year = models.PositiveIntegerField(null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    available_copies = models.PositiveIntegerField(default=1)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author}"


class Member(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=17, validators=[phone_validator])
    address = models.CharField(max_length=255, blank=True)
    membership_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='transactions')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='transactions')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ISSUED')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ['-issue_date', '-id']

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} -> {self.member.name} ({self.status})"
