from django.urls import path
from .views import (
    SummaryView, CategoryWiseView,
    MonthlyTrendView, WeeklyTrendView, RecentActivityView,
)

urlpatterns = [
    path('summary/',        SummaryView.as_view(),       name='dashboard-summary'),
    path('category-wise/',  CategoryWiseView.as_view(),  name='dashboard-category'),
    path('trends/',         MonthlyTrendView.as_view(),  name='dashboard-monthly'),
    path('trends/weekly/',  WeeklyTrendView.as_view(),   name='dashboard-weekly'),
    path('recent/',         RecentActivityView.as_view(), name='dashboard-recent'),
]