from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    UserManager,
)

class UserManager(UserManager):
    use_in_migrations = True

    def create_user(self, email, name):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name,  password):
        if not email:
            raise ValueError("The Email field must be set")
        if not password:            
           raise ValueError("The Password field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):

    objects = UserManager()

    email = models.EmailField(verbose_name="이메일", unique=True)
    name = models.CharField(verbose_name="이름", max_length=50, unique=True)
    joined_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    @property
    def is_staff(self):
        return self.is_admin
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]