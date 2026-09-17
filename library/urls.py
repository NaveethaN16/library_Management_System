from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('books', views.BookViewSet)
router.register('members', views.MemberViewSet)
router.register('transactions', views.TransactionViewSet)

urlpatterns = [
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
    path('', include(router.urls)),
]
