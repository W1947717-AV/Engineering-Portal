from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='messages_inbox'),
    path('new/', views.new_message, name='new_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('drafts/', views.drafts, name='drafts'),
    path('<int:id>/', views.view_message, name='view_message'),
]