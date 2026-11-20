from django.contrib import admin

from .models import *


# Register your models here.







# MediCare Admin Branding

admin.site.site_header = "MediCare Hospital Administration"
admin.site.site_title = "MediCare Admin Portal"
admin.site.index_title = "Hospital Management Dashboard"


# Department Admin

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        'name',
    )

    search_fields = (
        'name',
    )


# Doctor Admin

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'department',
        'specialization',
        'qualification',
        'experience',
        'available',
    )

    list_filter = (
        'department',
        'available',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'specialization',
    )


# Patient Admin

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'phone',
        'gender',
        'blood_group',
    )

    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'phone',
    )

    list_filter = (
        'gender',
        'blood_group',
    )


# Appointment Admin

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        'patient',
        'doctor',
        'appointment_date',
        'appointment_time',
        'status',
    )

    list_filter = (
        'status',
        'appointment_date',
    )

    search_fields = (
        'patient__user__username',
        'doctor__user__username',
    )


# Medical Record Admin

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):

    list_display = (
        'patient',
        'doctor',
        'created_at',
        'released_to_patient',
    )

    list_filter = (
        'released_to_patient',
        'created_at',
    )

    search_fields = (
        'patient__user__username',
        'doctor__user__username',
    )


# Prescription Admin

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'description', 'amount', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'due_date', 'created_at')
    search_fields = ('patient__user__username', 'patient__user__first_name', 'description', 'payment_reference')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):

    list_display = (
        'medicine_name',
        'medical_record',
        'created_at',
    )

    search_fields = (
        'medicine_name',
    )

