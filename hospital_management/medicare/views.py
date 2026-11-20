
import json
import requests

from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import (
    Department,
    Doctor,
    Patient,
    Appointment,
    MedicalRecord,
    Prescription,
    Invoice,
)

from .forms import AppointmentBookingForm, PatientSignUpForm


# ==================================================
# ROLE-BASED LOGIN
# ==================================================

class RoleBasedLoginView(LoginView):

    template_name = 'login.html'

    def get_success_url(self):

        user = self.request.user

        # Admin login
        if user.is_staff or user.is_superuser:

            messages.success(
                self.request,
                'Welcome to MediCare Administration!'
            )

            return reverse('admin:index')

        # Doctor login
        try:

            user.doctor_profile

            messages.success(
                self.request,
                f'Welcome Doctor {user.get_full_name() or user.username}!'
            )

            return reverse('doctor_dashboard')

        except Doctor.DoesNotExist:
            pass

        # Patient login
        try:

            user.patient_profile

            messages.success(
                self.request,
                f'Welcome to MediCare, {user.get_full_name() or user.username}!'
            )

            return self.get_redirect_url() or reverse('my_appointments')

        except Patient.DoesNotExist:
            pass

        # Account without a patient or doctor profile
        logout(self.request)

        messages.error(
            self.request,
            'Your account does not have a patient or doctor profile. '
            'Please contact the administrator.'
        )

        return reverse('home')


# ==================================================
# PATIENT SIGN UP
# ==================================================

def patient_signup(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        form = PatientSignUpForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                user = form.save()

                Patient.objects.create(
                    user=user,
                    phone=form.cleaned_data['phone'],
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    gender=form.cleaned_data['gender'],
                    address=form.cleaned_data['address'],
                    blood_group=form.cleaned_data['blood_group']
                )

            login(
                request,
                user,
                backend='django.contrib.auth.backends.ModelBackend'
            )

            messages.success(
                request,
                'Your MediCare account has been created successfully!'
            )

            return redirect('my_appointments')

    else:
        form = PatientSignUpForm()

    return render(request, 'signup.html', {
        'form': form
    })


# ==================================================
# HOME PAGE
# ==================================================

def home(request):
    departments = Department.objects.all().order_by('name')
    return render(request, 'home.html', {'departments': departments})


# ==================================================
# DEPARTMENT LIST
# ==================================================

def department_list(request):

    departments = Department.objects.all().order_by('name')

    return render(request, 'department_list.html', {
        'departments': departments
    })


# ==================================================
# ALL DOCTORS
# ==================================================

def doctor_list(request):

    doctors = Doctor.objects.select_related(
        'user',
        'department'
    ).all().order_by('user__first_name')

    return render(request, 'doctor_list.html', {
        'doctors': doctors
    })


# ==================================================
# DOCTORS BY DEPARTMENT
# ==================================================

def doctors_by_department(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    doctors = Doctor.objects.filter(
        department=department
    ).select_related(
        'user',
        'department'
    ).order_by('user__first_name')

    return render(request, 'doctor_list.html', {
        'doctors': doctors,
        'department': department
    })


# ==================================================
# PATIENT LIST - ADMIN / STAFF ONLY
# ==================================================

@staff_member_required
def patient_list(request):

    patients = Patient.objects.select_related(
        'user'
    ).all()

    return render(request, 'patient_list.html', {
        'patients': patients
    })


# ==================================================
# ROLE-AWARE APPOINTMENTS, MEDICAL RECORDS, PRESCRIPTIONS
# Admins see all data; doctors see their own assigned data; patients see only their own data.
# ==================================================

@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related(
        'patient__user', 'doctor__user'
    )

    if request.user.is_staff or request.user.is_superuser:
        appointments = appointments.all()
    else:
        try:
            patient = request.user.patient_profile
            appointments = appointments.filter(patient=patient)
        except Patient.DoesNotExist:
            try:
                doctor = request.user.doctor_profile
                appointments = appointments.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                messages.error(request, 'Your account is not registered as a patient or doctor.')
                return redirect('home')

    appointments = appointments.order_by('-appointment_date', '-appointment_time')
    if not appointments.exists():
        messages.info(request, 'No appointments are available for your account yet.')
    return render(request, 'appointment_list.html', {'appointments': appointments})


@login_required
def medical_record_list(request):
    records = MedicalRecord.objects.select_related(
        'patient__user', 'doctor__user', 'appointment'
    )

    if request.user.is_staff or request.user.is_superuser:
        records = records.all()
    else:
        try:
            patient = request.user.patient_profile
            records = records.filter(patient=patient, released_to_patient=True)
        except Patient.DoesNotExist:
            try:
                doctor = request.user.doctor_profile
                records = records.filter(doctor=doctor)
            except Doctor.DoesNotExist:
                messages.error(request, 'Your account is not registered as a patient or doctor.')
                return redirect('home')

    records = records.order_by('-created_at')
    if not records.exists():
        messages.info(request, 'No medical records are available for your account yet.')
    return render(request, 'medical_record_list.html', {'medical_records': records})


@login_required
def prescription_list(request):
    prescriptions = Prescription.objects.select_related(
        'medical_record__patient__user', 'medical_record__doctor__user'
    )

    if request.user.is_staff or request.user.is_superuser:
        prescriptions = prescriptions.all()
    else:
        try:
            patient = request.user.patient_profile
            prescriptions = prescriptions.filter(
                medical_record__patient=patient,
                medical_record__released_to_patient=True
            )
        except Patient.DoesNotExist:
            try:
                doctor = request.user.doctor_profile
                prescriptions = prescriptions.filter(medical_record__doctor=doctor)
            except Doctor.DoesNotExist:
                messages.error(request, 'Your account is not registered as a patient or doctor.')
                return redirect('home')

    prescriptions = prescriptions.order_by('-created_at')
    if not prescriptions.exists():
        messages.info(request, 'No prescriptions are available for your account yet.')
    return render(request, 'prescription_list.html', {'prescriptions': prescriptions})

# ==================================================
# PATIENT - BOOK APPOINTMENT PAGE
# ==================================================

@login_required
def book_appointment(request):

    try:

        patient = request.user.patient_profile

    except Patient.DoesNotExist:

        messages.error(
            request,
            'This login does not have a patient profile. '
            'Please sign in with your patient account or register '
            'as a new patient before booking.'
        )

        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/medicare/appointment/add/')

        return redirect('patient_signup')

    if request.method == 'POST':

        form = AppointmentBookingForm(request.POST)

        if form.is_valid():

            appointment = form.save(commit=False)

            appointment.patient = patient
            appointment.status = 'Pending'

            appointment.save()

            messages.success(
                request,
                'Your appointment request has been submitted successfully!'
            )

            return redirect('my_appointments')

    else:

        initial_data = {}

        selected_doctor_id = request.GET.get('doctor')

        if selected_doctor_id:

            selected_doctor = Doctor.objects.filter(
                id=selected_doctor_id,
                available=True
            ).select_related('department').first()

            if selected_doctor:

                initial_data['doctor'] = selected_doctor

                if selected_doctor.department_id:
                    initial_data['department'] = selected_doctor.department

            else:

                messages.warning(
                    request,
                    'That doctor is currently unavailable. '
                    'Please choose another doctor.'
                )

        form = AppointmentBookingForm(initial=initial_data)

    return render(request, 'appointment_book.html', {
        'form': form
    })


# ==================================================
# QUICK APPOINTMENT BOOKING FROM DOCTOR CARD MODAL
# ==================================================

@login_required
@require_POST
def quick_book_appointment(request):

    # Confirm that the logged-in user is a patient
    try:

        patient = request.user.patient_profile

    except Patient.DoesNotExist:

        messages.error(
            request,
            'Only registered patients can book appointments.'
        )

        return redirect('doctor_list')


    # Validate doctor ID
    doctor_id = request.POST.get('doctor_id', '').strip()

    try:

        doctor_id = forms.IntegerField(min_value=1).clean(doctor_id)

    except ValidationError:

        messages.error(
            request,
            'Please select a valid doctor.'
        )

        return redirect('doctor_list')


    # Check doctor availability
    doctor = Doctor.objects.filter(
        pk=doctor_id,
        available=True
    ).select_related('user', 'department').first()

    if doctor is None:

        messages.error(
            request,
            'This doctor is currently unavailable. '
            'Please select another doctor.'
        )

        return redirect('doctor_list')


    # Read appointment details
    date_value = request.POST.get('appointment_date', '').strip()
    time_value = request.POST.get('appointment_time', '').strip()
    reason = request.POST.get('reason', '').strip()


    # Validate date and time
    try:

        appointment_date = forms.DateField().clean(date_value)
        appointment_time = forms.TimeField().clean(time_value)

    except ValidationError:

        messages.error(
            request,
            'Please select a valid appointment date and time.'
        )

        return redirect('doctor_list')


    # Validate appointment date
    today = timezone.localdate()

    if appointment_date < today:

        messages.error(
            request,
            'You cannot book an appointment for a past date.'
        )

        return redirect('doctor_list')


    # Validate appointment time for today
    now = timezone.localtime()

    if (
        appointment_date == today
        and appointment_time <= now.time().replace(
            second=0,
            microsecond=0
        )
    ):

        messages.error(
            request,
            'Please select a future appointment time.'
        )

        return redirect('doctor_list')


    # Check for an existing appointment at the same doctor/date/time
    already_booked = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status__in=['Pending', 'Confirmed']
    ).exists()

    if already_booked:

        messages.error(
            request,
            'This appointment slot is already booked. '
            'Please select another date or time.'
        )

        return redirect('doctor_list')


    # Create appointment
    Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        reason=reason,
        status='Pending'
    )


    messages.success(
        request,
        'Your appointment request has been submitted successfully! '
        'The hospital will confirm it shortly.'
    )

    return redirect('my_appointments')


# ==================================================
# PATIENT - MY APPOINTMENTS
# ==================================================

@login_required
def my_appointments(request):

    try:

        patient = request.user.patient_profile

    except Patient.DoesNotExist:

        messages.error(
            request,
            'This page is available only to patient accounts.'
        )

        return redirect('home')

    appointments = Appointment.objects.filter(
        patient=patient
    ).select_related(
        'doctor__user',
        'doctor__department'
    ).order_by(
        '-appointment_date',
        '-appointment_time'
    )

    return render(request, 'my_appointments.html', {
        'appointments': appointments
    })


# ==================================================
# GET AVAILABLE DOCTORS BY DEPARTMENT
# ==================================================

def get_doctors_by_department(request):

    department_id = request.GET.get('department_id')

    doctors = Doctor.objects.filter(
        department_id=department_id,
        available=True
    ).select_related('user')

    doctor_data = []

    for doctor in doctors:

        doctor_data.append({
            'id': doctor.id,
            'name': (
                doctor.user.get_full_name()
                or doctor.user.username
            ),
            'specialization': doctor.specialization
        })

    return JsonResponse({
        'doctors': doctor_data
    })


# ==================================================
# DOCTOR DASHBOARD
# ==================================================

@login_required
def doctor_dashboard(request):

    try:

        doctor = request.user.doctor_profile

    except Doctor.DoesNotExist:

        messages.error(
            request,
            'This dashboard is available only to doctors.'
        )

        return redirect('home')

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related(
        'patient__user'
    ).order_by(
        '-appointment_date',
        '-appointment_time'
    )

    return render(request, 'doctor_dashboard.html', {
        'doctor': doctor,
        'appointments': appointments
    })


# ==================================================
# DOCTOR - CONFIRM APPOINTMENT
# ==================================================

@login_required
@require_POST
def confirm_appointment(request, appointment_id):
    """Confirm only a Pending appointment assigned to the logged-in doctor."""
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        messages.error(request, 'Only registered doctors can confirm appointments.')
        return redirect('home')

    appointment = get_object_or_404(
        Appointment, pk=appointment_id, doctor=doctor
    )

    if appointment.status != 'Pending':
        messages.warning(request, 'Only pending appointments can be confirmed.')
    else:
        appointment.status = 'Confirmed'
        appointment.save(update_fields=['status'])
        messages.success(request, 'Appointment confirmed successfully.')

    return redirect('doctor_dashboard')


# ==================================================
# DOCTOR - CHANGE AVAILABILITY
# ==================================================

@login_required
@require_POST
def toggle_doctor_availability(request):

    try:

        doctor = request.user.doctor_profile

    except Doctor.DoesNotExist:

        messages.error(
            request,
            'Only doctors can change availability.'
        )

        return redirect('home')

    doctor.available = not doctor.available

    doctor.save(update_fields=['available'])

    if doctor.available:

        messages.success(
            request,
            'Your availability status is now Available.'
        )

    else:

        messages.warning(
            request,
            'Your availability status is now Unavailable.'
        )

    return redirect('doctor_dashboard')


# ==================================================
# PATIENT BILLING
# ==================================================

@login_required
def my_bills(request):

    try:

        patient = request.user.patient_profile

    except Patient.DoesNotExist:

        messages.error(
            request,
            'Billing is available only to patient accounts.'
        )

        return redirect('home')

    invoices = Invoice.objects.filter(
        patient=patient
    ).select_related(
        'appointment'
    ).order_by('-created_at')

    from django.db.models import Sum

    totals = invoices.aggregate(
        pending_total=Sum(
            'amount',
            filter=models.Q(status='Pending')
        ),
        paid_total=Sum(
            'amount',
            filter=models.Q(status='Paid')
        )
    )

    return render(request, 'my_bills.html', {
        'invoices': invoices,
        'pending_total': totals['pending_total'] or 0,
        'paid_total': totals['paid_total'] or 0,
    })


# ==================================================
# DEMO BILL PAYMENT
# ==================================================

@login_required
@require_POST
def demo_pay_bill(request, invoice_id):

    """
    Demonstration-only payment flow.
    No real money is charged.
    """

    try:

        patient = request.user.patient_profile

    except Patient.DoesNotExist:

        messages.error(
            request,
            'Only patients can make bill payments.'
        )

        return redirect('home')

    invoice = get_object_or_404(
        Invoice,
        pk=invoice_id,
        patient=patient
    )

    if invoice.status == 'Paid':

        messages.info(
            request,
            'This bill has already been marked as paid.'
        )

        return redirect('my_bills')

    if invoice.status != 'Pending':

        messages.error(
            request,
            'This bill is not available for payment.'
        )

        return redirect('my_bills')

    invoice.status = 'Paid'

    invoice.payment_method = 'Demo payment'

    invoice.payment_reference = (
        f'DEMO-{invoice.pk}-{timezone.now():%Y%m%d%H%M%S}'
    )

    invoice.paid_at = timezone.now()

    invoice.save(
        update_fields=[
            'status',
            'payment_method',
            'payment_reference',
            'paid_at'
        ]
    )

    messages.success(
        request,
        'Demo payment recorded. No real payment was processed.'
    )

    return redirect('my_bills')


# ==================================================
# AI HOSPITAL CHATBOT - OLLAMA
# ==================================================

def chatbot(request):

    return render(request, 'chatbot.html')


# ==================================================
# AI CHATBOT RESPONSE
# ==================================================

@require_POST
def chatbot_response(request):

    try:

        data = json.loads(request.body)

        user_message = data.get('message', '').strip()

        if not user_message:

            return JsonResponse({
                'reply': 'Please enter a message.'
            }, status=400)

        if len(user_message) > 1000:

            return JsonResponse({
                'reply': 'Please keep your message under 1000 characters.'
            }, status=400)


        # Hospital departments
        departments = Department.objects.all()


        # Available doctors
        doctors = Doctor.objects.filter(
            available=True
        ).select_related(
            'user',
            'department'
        )


        department_info = "\n".join([
            f"- {department.name}: {department.description}"
            for department in departments
        ])


        doctor_info = "\n".join([
            f"- Dr. {doctor.user.get_full_name() or doctor.user.username}, "
            f"Specialization: {doctor.specialization}, "
            f"Department: "
            f"{doctor.department.name if doctor.department else 'Not assigned'}"
            for doctor in doctors
        ])


        system_prompt = f"""
You are MediCare Hospital's AI assistant.

Your responsibilities:
1. Answer general questions about hospital departments and services.
2. Help users understand how to book appointments.
3. Provide available doctor names and their specializations.
4. Answer general questions about hospital procedures.
5. Be polite, clear, and concise.

Hospital departments:
{department_info}

Available doctors:
{doctor_info}

Important safety rules:
- Do not diagnose diseases.
- Do not prescribe medicines or recommend dosages.
- Do not replace a qualified doctor.
- For medical concerns, advise the user to consult a qualified doctor.
- For emergencies, advise the user to seek immediate emergency medical care.
- Never invent doctor names, hospital services, or hospital information.
"""


        # Connect to Ollama
        response = requests.post(
            'http://127.0.0.1:11434/api/chat',
            json={
                'model': 'llama3.2:1b',
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_message
                    }
                ],
                'stream': False
            },
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        reply = result.get(
            'message', {}
        ).get(
            'content',
            'Sorry, I could not generate a response.'
        )

        return JsonResponse({
            'reply': reply
        })


    except requests.exceptions.ConnectionError:

        return JsonResponse({
            'reply': (
                'The AI assistant is currently unavailable. '
                'Please make sure Ollama is running.'
            )
        }, status=503)


    except requests.exceptions.Timeout:

        return JsonResponse({
            'reply': (
                'The AI assistant is taking too long to respond. '
                'Please try again.'
            )
        }, status=504)


    except (json.JSONDecodeError, ValueError):

        return JsonResponse({
            'reply': 'Invalid request. Please try again.'
        }, status=400)


    except requests.exceptions.RequestException:

        return JsonResponse({
            'reply': 'There was a problem connecting to the AI service.'
        }, status=502)

# ==================================================
# DOCTOR - CREATE PRESCRIPTION FROM AN APPOINTMENT
# ==================================================

@login_required
def prescribe_for_appointment(request, appointment_id):
    """Allow only the doctor assigned to this appointment to prescribe."""
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        messages.error(request, "Only registered doctors can create prescriptions.")
        return redirect("home")

    appointment = get_object_or_404(
        Appointment.objects.select_related("patient__user", "doctor__user"),
        pk=appointment_id,
        doctor=doctor,
    )

    if appointment.status == "Cancelled":
        messages.error(request, "A cancelled appointment cannot be prescribed.")
        return redirect("doctor_dashboard")
    if appointment.status != "Confirmed":
        messages.warning(request, "Confirm this appointment before prescribing.")
        return redirect("doctor_dashboard")

    if request.method == "POST":
        diagnosis = request.POST.get("diagnosis", "").strip()
        consultation_notes = request.POST.get("consultation_notes", "").strip()
        medicines = []

        # Each medicine is submitted in parallel arrays, one entry per row.
        names = request.POST.getlist("medicine_name")
        dosages = request.POST.getlist("dosage")
        frequencies = request.POST.getlist("frequency")
        durations = request.POST.getlist("duration")
        instructions = request.POST.getlist("instructions")

        for i, name in enumerate(names):
            name = name.strip()
            if not name:
                continue
            medicines.append({
                "medicine_name": name,
                "dosage": dosages[i].strip() if i < len(dosages) else "",
                "frequency": frequencies[i].strip() if i < len(frequencies) else "",
                "duration": durations[i].strip() if i < len(durations) else "",
                "instructions": instructions[i].strip() if i < len(instructions) else "",
            })

        if not diagnosis:
            messages.error(request, "Please enter a diagnosis.")
        elif not medicines:
            messages.error(request, "Add at least one medicine.")
        elif any(not m["dosage"] or not m["frequency"] or not m["duration"] for m in medicines):
            messages.error(request, "Please complete dosage, frequency and duration for each medicine.")
        else:
            with transaction.atomic():
                record = MedicalRecord.objects.create(
                    patient=appointment.patient,
                    doctor=doctor,
                    appointment=appointment,
                    diagnosis=diagnosis,
                    consultation_notes=consultation_notes,
                    released_to_patient=True,
                )
                Prescription.objects.bulk_create([
                    Prescription(medical_record=record, **medicine)
                    for medicine in medicines
                ])
                appointment.status = "Completed"
                appointment.save(update_fields=["status"])

            messages.success(request, "Prescription saved and released to the patient.")
            return redirect("doctor_dashboard")

    return render(request, "doctor_prescribe.html", {
        "appointment": appointment,
    })
