from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True, null=True)
    email = models.EmailField(unique=True, validators=[EmailValidator()], blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?\d{10,12}$',
        message="Phone number must be in digits format '+999999999'. Up to 15 digits allowed."
    )
    mobile_number = models.CharField(validators=[phone_regex], max_length=17, unique=True, blank=True, null=True)

    card_holder_name = models.CharField(max_length=100, blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=True, null=True)
    expiry_date = models.CharField(max_length=5, blank=True, null=True, help_text="Format: MM/YY")
    cvv = models.CharField(max_length=4, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def deactivate(self):
        self.is_active = False
        self.save()

    def delete_account(self):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.user.username}"



@receiver(post_save, sender=User)
def create_account_for_new_user(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
