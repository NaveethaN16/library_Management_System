from datetime import timedelta

from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, Member, Transaction
from .serializers import BookSerializer, MemberSerializer, TransactionSerializer

FINE_PER_DAY = 5
LOAN_PERIOD_DAYS = 14


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(author__icontains=search) | Q(isbn__icontains=search)
            )
        if category:
            qs = qs.filter(category=category)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.transactions.filter(status__in=['ISSUED', 'OVERDUE']).exists():
            return Response(
                {'detail': 'Cannot delete a book that currently has copies issued.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search))
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.transactions.filter(status__in=['ISSUED', 'OVERDUE']).exists():
            return Response(
                {'detail': 'Cannot delete a member with books currently issued.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    http_method_names = ['get', 'post', 'head']

    def _refresh_overdue(self):
        today = timezone.now().date()
        Transaction.objects.filter(status='ISSUED', due_date__lt=today).update(status='OVERDUE')

    def get_queryset(self):
        self._refresh_overdue()
        qs = super().get_queryset().select_related('book', 'member')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book')
        member_id = request.data.get('member')

        try:
            book = Book.objects.get(pk=book_id)
        except (Book.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'Selected book was not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            member = Member.objects.get(pk=member_id)
        except (Member.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'Selected member was not found.'}, status=status.HTTP_404_NOT_FOUND)

        if book.available_copies < 1:
            return Response({'detail': 'No available copies of this book right now.'}, status=status.HTTP_400_BAD_REQUEST)
        if not member.is_active:
            return Response({'detail': 'This member is not active.'}, status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction.objects.create(
            book=book,
            member=member,
            due_date=timezone.now().date() + timedelta(days=LOAN_PERIOD_DAYS),
        )
        book.available_copies -= 1
        book.save(update_fields=['available_copies'])

        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        transaction = self.get_object()
        if transaction.status == 'RETURNED':
            return Response({'detail': 'This book has already been returned.'}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()
        transaction.return_date = today
        if today > transaction.due_date:
            overdue_days = (today - transaction.due_date).days
            transaction.fine_amount = overdue_days * FINE_PER_DAY
        transaction.status = 'RETURNED'
        transaction.save()

        book = transaction.book
        book.available_copies += 1
        book.save(update_fields=['available_copies'])

        serializer = self.get_serializer(transaction)
        return Response(serializer.data)


def dashboard_stats(request):
    today = timezone.now().date()
    Transaction.objects.filter(status='ISSUED', due_date__lt=today).update(status='OVERDUE')

    books = Book.objects.all()
    total_books = books.count()
    total_copies = sum(b.total_copies for b in books) if total_books else 0
    available_copies = sum(b.available_copies for b in books) if total_books else 0

    total_members = Member.objects.count()
    active_members = Member.objects.filter(is_active=True).count()

    issued_count = Transaction.objects.filter(status='ISSUED').count()
    overdue_count = Transaction.objects.filter(status='OVERDUE').count()
    returned_count = Transaction.objects.filter(status='RETURNED').count()

    category_counts = list(
        Book.objects.values('category').annotate(count=Count('id')).order_by('-count')
    )

    recent_transactions = list(
        Transaction.objects.select_related('book', 'member')
        .order_by('-issue_date', '-id')[:6]
        .values('id', 'book__title', 'member__name', 'issue_date', 'due_date', 'status')
    )
    for item in recent_transactions:
        item['issue_date'] = item['issue_date'].isoformat() if item['issue_date'] else None
        item['due_date'] = item['due_date'].isoformat() if item['due_date'] else None

    return JsonResponse({
        'total_books': total_books,
        'total_copies': total_copies,
        'available_copies': available_copies,
        'total_members': total_members,
        'active_members': active_members,
        'issued_count': issued_count,
        'overdue_count': overdue_count,
        'returned_count': returned_count,
        'category_counts': category_counts,
        'recent_transactions': recent_transactions,
    })
