from django.db import models
from django.core.validators import RegexValidator, EmailValidator


class Account(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone_regex = RegexValidator(
        regex=r'^\+?\d{10,12}$',
        message="Phone number must be in digits format '+999999999'. Up to 15 digits allowed."
    )
    mobile_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)

    # Payment Information
    card_holder_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    expiry_date = models.CharField(max_length=5, blank=True, null=True, help_text="Format: MM/YY")
    cvv = models.CharField(max_length=4, blank=True, null=True)

    # Account Status
    is_active = models.BooleanField(default=True)   # For deactivate account
    is_deleted = models.BooleanField(default=False) # For delete account (soft delete)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def deactivate(self):
        self.is_active = False
        self.save()

    def delete_account(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
