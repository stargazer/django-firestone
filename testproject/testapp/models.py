from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import admin
from django.contrib.auth.models import User


class Contact(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True, blank=False)

    def clean_fields(self, exclude=None):
        try:
            validate_email(self.email)
        except ValidationError, e:
            raise ValidationError({'email': e.messages})

        super(Contact, self).clean_fields(exclude)

admin.site.register(Contact)        
