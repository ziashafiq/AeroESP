from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Core authentication model for AeroESP.
    Student- and teacher-specific data will be stored
    in separate profile models.
    """

    def __str__(self):
        return self.username