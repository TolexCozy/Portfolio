from django.urls import path, include
from port import views


urlpatterns = [
    path('',views.home,name='home'),
    path('authapp/', include('authapp.urls')),
    path('about',views.about,name='about'),
    path('contact',views.contact,name='contact'),
    path('thanks',views.thanks,name='thanks'),
    path('resume',views.resume,name='resume'),
    path('blog',views.handleblog,name='handleblog'),
    path('services',views.cv_view,name='cv_view'),
    path('internshipdetails',views.internshipdetails,name='internshipdetails'),
]
