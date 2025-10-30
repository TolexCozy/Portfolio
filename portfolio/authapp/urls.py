from django.urls import path
from authapp import views


urlpatterns = [
    path('signup/',views.signup,name='signup'),
    path('login/',views.handlelogin,name='handlelogin'),
    path('logout/',views.handlelogout,name='handlelogout'),
    path('verify/', views.verify_email, name='verify_email'),
    path('resend_pin/', views.resend_pin, name='resend_pin'),
]
