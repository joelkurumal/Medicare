
# from django import forms
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
# from django.utils import timezone
# from .models import Appointment, Department, Doctor, Patient
# from .models import Appointment, Department, Doctor
# User = get_user_model()


# class AppointmentBookingForm(forms.ModelForm):

#     department = forms.ModelChoiceField(
#         queryset=Department.objects.all(),
#         empty_label="Select Department",
#         required=True
#     )

#     class Meta:
#         model = Appointment
#         fields = [
#             'doctor',
#             'appointment_date',
#             'appointment_time',
#             'reason'
#         ]

#         widgets = {
#             'doctor': forms.Select(attrs={
#                 'class': 'form-control',
#                 'id': 'id_doctor'
#             }),
#             'appointment_date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control',
#                 'id': 'id_appointment_date'
#             }),
#             'appointment_time': forms.TimeInput(attrs={
#                 'type': 'time',
#                 'class': 'form-control'
#             }),
#             'reason': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 4,
#                 'placeholder': 'Describe your reason for consultation'
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields['doctor'].queryset = (
#             Doctor.objects.filter(available=True)
#             .select_related('user', 'department')
#         )

#         self.fields['doctor'].empty_label = "Select Doctor"

#         self.fields['appointment_date'].widget.attrs['min'] = (
#             timezone.localdate().isoformat()
#         )

#     def clean(self):
#         cleaned_data = super().clean()

#         doctor = cleaned_data.get('doctor')
#         appointment_date = cleaned_data.get('appointment_date')
#         appointment_time = cleaned_data.get('appointment_time')
#         department = cleaned_data.get('department')

#         if doctor and department:
#             if doctor.department_id != department.id:
#                 self.add_error(
#                     'doctor',
#                     'Please select a doctor from the chosen department.'
#                 )

#         if appointment_date and appointment_date < timezone.localdate():
#             self.add_error(
#                 'appointment_date',
#                 'You cannot book an appointment for a past date.'
#             )

#         if (
#             doctor and appointment_date and appointment_time
#             and appointment_date >= timezone.localdate()
#         ):
#             if appointment_date == timezone.localdate():
#                 selected_datetime = timezone.datetime.combine(
#                     appointment_date,
#                     appointment_time
#                 )
#                 if timezone.is_naive(selected_datetime):
#                     selected_datetime = timezone.make_aware(
#                         selected_datetime,
#                         timezone.get_current_timezone()
#                     )

#                 if selected_datetime <= timezone.localtime():
#                     self.add_error(
#                         'appointment_time',
#                         'Please select a future time.'
#                     )

#             already_booked = Appointment.objects.filter(
#                 doctor=doctor,
#                 appointment_date=appointment_date,
#                 appointment_time=appointment_time,
#                 status__in=['Pending', 'Confirmed']
#             ).exists()

#             if already_booked:
#                 self.add_error(
#                     'appointment_time',
#                     'This time slot is already booked. Please select another time.'
#                 )

#         return cleaned_data


# class PatientSignupForm(forms.Form):
#     username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username', 'autocomplete': 'username'}))
#     first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
#     last_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
#     email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com', 'autocomplete': 'email'}))
#     date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
#     gender = forms.ChoiceField(required=False, choices=[('', 'Select gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'), ('Prefer not to say', 'Prefer not to say')], widget=forms.Select(attrs={'class': 'form-select'}))
#     phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number', 'autocomplete': 'tel'}))
#     address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}))
#     blood_group = forms.ChoiceField(required=False, choices=[('', 'Select blood group'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], widget=forms.Select(attrs={'class': 'form-select'}))
#     password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password', 'autocomplete': 'new-password'}))
#     password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password again', 'autocomplete': 'new-password'}))

#     def clean_username(self):
#         username = self.cleaned_data['username']
#         if User.objects.filter(username__iexact=username).exists():
#             raise forms.ValidationError('This username is already taken.')
#         return username

#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if User.objects.filter(email__iexact=email).exists():
#             raise forms.ValidationError('An account with this email already exists.')
#         return email

#     def clean(self):
#         cleaned = super().clean()
#         password1, password2 = cleaned.get('password1'), cleaned.get('password2')
#         if password1 and password2 and password1 != password2:
#             self.add_error('password2', 'The passwords do not match.')
#         if password1:
#             try:
#                 validate_password(password1)
#             except ValidationError as exc:
#                 self.add_error('password1', exc)
#         return cleaned

#     def save(self):
#         user = User.objects.create_user(username=self.cleaned_data['username'], first_name=self.cleaned_data['first_name'], last_name=self.cleaned_data['last_name'], email=self.cleaned_data['email'], password=self.cleaned_data['password1'])
#         Patient.objects.create(user=user, date_of_birth=self.cleaned_data.get('date_of_birth'), gender=self.cleaned_data.get('gender', ''), phone=self.cleaned_data['phone'], address=self.cleaned_data.get('address', ''), blood_group=self.cleaned_data.get('blood_group', ''))
#         return user

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import Appointment, Department, Doctor


class PatientSignUpForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
    )

    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    gender = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select Gender'),
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Enter your address'
        })
    )

    blood_group = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select Blood Group'),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username',
                'autocomplete': 'username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email already exists.'
            )

        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        if not phone:
            raise forms.ValidationError(
                'Phone number is required.'
            )

        return phone

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class AppointmentBookingForm(forms.ModelForm):

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        required=True
    )

    class Meta:
        model = Appointment
        fields = [
            'doctor',
            'appointment_date',
            'appointment_time',
            'reason'
        ]

        widgets = {
            'doctor': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_doctor'
            }),
            'appointment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_appointment_date'
            }),
            'appointment_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your reason for consultation'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['doctor'].queryset = (
            Doctor.objects.filter(available=True)
            .select_related('user', 'department')
        )

        self.fields['doctor'].empty_label = "Select Doctor"

        self.fields['appointment_date'].widget.attrs['min'] = (
            timezone.localdate().isoformat()
        )

    def clean(self):
        cleaned_data = super().clean()

        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')
        department = cleaned_data.get('department')

        if doctor and department:
            if doctor.department_id != department.id:
                self.add_error(
                    'doctor',
                    'Please select a doctor from the chosen department.'
                )

        if appointment_date and appointment_date < timezone.localdate():
            self.add_error(
                'appointment_date',
                'You cannot book an appointment for a past date.'
            )

        if (
            doctor and appointment_date and appointment_time
            and appointment_date >= timezone.localdate()
        ):
            if appointment_date == timezone.localdate():
                selected_datetime = timezone.datetime.combine(
                    appointment_date,
                    appointment_time
                )

                if timezone.is_naive(selected_datetime):
                    selected_datetime = timezone.make_aware(
                        selected_datetime,
                        timezone.get_current_timezone()
                    )

                if selected_datetime <= timezone.localtime():
                    self.add_error(
                        'appointment_time',
                        'Please select a future time.'
                    )

            already_booked = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['Pending', 'Confirmed']
            ).exists()

            if already_booked:
                self.add_error(
                    'appointment_time',
                    'This time slot is already booked. Please select another time.'
                )

        return cleaned_data
