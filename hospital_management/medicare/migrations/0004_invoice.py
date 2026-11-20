# Generated for patient billing and payment tracking.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicare', '0003_department_logo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20)),
                ('payment_reference', models.CharField(blank=True, max_length=100)),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='medicare.appointment')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='medicare.patient')),
            ],
        ),
    ]
