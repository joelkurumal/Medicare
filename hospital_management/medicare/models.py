
from django.db import models
from django.contrib.auth.models import User


# 1. Department Model
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to='departments/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


# 2. Doctor Model
class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='doctors'
    )
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=150)
    experience = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=15)
    profile_image = models.ImageField(
        upload_to='doctors/',
        blank=True,
        null=True
    )
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"


# 3. Patient Model
class Patient(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# 4. Appointment Model
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.appointment_date}"


# 5. Medical Record Model
class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    diagnosis = models.TextField()
    consultation_notes = models.TextField(blank=True)
    released_to_patient = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medical Record - {self.patient}"


# 6. Prescription Model
class Prescription(models.Model):
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.medicine_name


# 7. Patient Billing / Invoice Model
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='invoices'
    )
    appointment = models.ForeignKey(
        Appointment, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='invoices'
    )
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Bill #{self.pk} - {self.patient}"
