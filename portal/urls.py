from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('dashboard/', views.dashboard_view, name='dashboard'),     path('register/', views.register_view, name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('report/<str:item_type>/', views.report_item_view, name='report'),
    
     # APIs for AJAX and RapidFuzz
    path('api/search/', views.search_matches_api, name='search_api'),
    
    # Updated Chat APIs to support Owner 1-on-1 replies
    path('api/chat/inquiries/<int:item_id>/', views.get_inquiries_api, name='get_inquiries'),
    path('api/chat/get/<int:item_id>/<int:other_user_id>/', views.get_messages_api, name='get_messages_owner'),
    path('api/chat/get/<int:item_id>/', views.get_messages_api, name='get_messages'),
    path('api/chat/send/<int:item_id>/<int:other_user_id>/', views.send_message_api, name='send_message_owner'),
    path('api/chat/send/<int:item_id>/', views.send_message_api, name='send_message'),
]