"""
URL configuration for hospital_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""



from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from medicare import views


urlpatterns = [

    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path(
        'accounts/signup/',
        views.patient_signup,
        name='patient_signup'
    ),

    path(
        'accounts/login/',
        views.RoleBasedLoginView.as_view(),
        name='login'
    ),

    path(
        'accounts/logout/',
        LogoutView.as_view(next_page='home'),
        name='logout'
    ),

    # Home
    path('', views.home, name='home'),

    # Departments
    path(
        'departments/',
        views.department_list,
        name='department_list'
    ),

    path(
        'departments/<int:department_id>/doctors/',
        views.doctors_by_department,
        name='doctors_by_department'
    ),

    # Doctors
    path(
        'doctors/',
        views.doctor_list,
        name='doctor_list'
    ),

    # Patients
    path(
        'patients/',
        views.patient_list,
        name='patient_list'
    ),

    # Appointments
    path(
        'book-appointment/',
        views.book_appointment,
        name='book_appointment'
    ),

    path(
        'quick-book-appointment/',
        views.quick_book_appointment,
        name='quick_book_appointment'
    ),

    path(
        'my-appointments/',
        views.my_appointments,
        name='my_appointments'
    ),

    path(
        'appointments/',
        views.appointment_list,
        name='appointment_list'
    ),

    path(
        'get-doctors/',
        views.get_doctors_by_department,
        name='get_doctors_by_department'
    ),

    path(
        'doctor/appointments/<int:appointment_id>/prescribe/',
        views.prescribe_for_appointment,
        name='prescribe_for_appointment'
    ),

    path(
        'doctor/appointments/<int:appointment_id>/confirm/',
        views.confirm_appointment,
        name='confirm_appointment'
    ),

    # Doctor Dashboard
    path(
        'doctor-dashboard/',
        views.doctor_dashboard,
        name='doctor_dashboard'
    ),

    path(
        'doctor/availability/',
        views.toggle_doctor_availability,
        name='toggle_doctor_availability'
    ),

    # Billing
    path(
        'my-bills/',
        views.my_bills,
        name='my_bills'
    ),

    path(
        'bills/<int:invoice_id>/demo-pay/',
        views.demo_pay_bill,
        name='demo_pay_bill'
    ),

    # Medical Records
    path(
        'medical-records/',
        views.medical_record_list,
        name='medical_record_list'
    ),

    # Prescriptions
    path(
        'prescriptions/',
        views.prescription_list,
        name='prescription_list'
    ),

    # AI Chatbot
    path(
        'chatbot/',
        views.chatbot,
        name='chatbot'
    ),

    path(
        'chatbot-response/',
        views.chatbot_response,
        name='chatbot_response'
    ),

]


# Media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

