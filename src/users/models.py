import datetime
import random
import logging
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin,
)
from django.core import signing
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _

logger = logging.getLogger(__name__)


def random_auth_number():
    return random.randint(0, 1e4)


class EmailUserManager(BaseUserManager):
    """Custom manager for EmailUser"""

    def _create_user(self, email, password, **extra_fields):
        """Create and save a EmailUser with the given email and password.

        Args:
            email (str): User email
            password (str): User password
            is_staff (bool): Whether user is staff or not
            is_superuser (bool): Whether user is admin or not
            **extra_fields: Unnecessary fields during user creation

        Returns:
            users.models.EmailUser: a new EmailUser

        Raises:
            ValueError: if email is not set

        """
        now = timezone.now()    # we set timezone as UTC so it is a utcnow
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        last_login = extra_fields.pop('last_login', now)
        date_joined = extra_fields.pop('date_joined', now)
        user = self.model(
            email=email, last_login=last_login, date_joined=date_joined,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular EmailUser given email and password.

        Args:
            email (str): User email
            password (optional[str]): User password
            **extra_fields: Rest of fields passed for user creation

        Returns:
            users.models.EmailUser: A regular EmailUser
        """
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save an admin EmailUser given email and password.

        Args:
            email (str): User email
            password (optional[str]): User password
            **extra_fields: Rest of fields passed for user creation

        Returns:
            users.models.EmailUser: An admin EmailUser
        """
        return self._create_user(
            email, password,
            verified=True,  # skip the email verification
            is_staff=True, is_superuser=True,
            **extra_fields
        )

    def get_with_verification_key(self, verification_key):
        """Get a user from verification key.

        Args:
            verification_key: Hash-like string for email verification

        Raises:
            self.model.DoesNotExist:
                When the verification failed, such as bad verification key
        """
        try:
            username = signing.loads(
                verification_key,
                salt=settings.SECRET_KEY,
            )
        except signing.BadSignature:
            raise self.model.DoesNotExist
        return self.get(**{self.model.USERNAME_FIELD: username})


class EmailUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        verbose_name=_('email address'),
        max_length=255, unique=True, db_index=True,
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        blank=True,
    )
    auth_number = models.IntegerField(
        default=random_auth_number,
        verbose_name=_('auth number'),
        help_text=_(
            "Access key seed for your reports and results. <strong>Warning! "
            "Changing this integer will invalidate all previously generated "
            "report and result links.</strong>"
        ),
    )
    verified = models.BooleanField(
        verbose_name=_('verified'),
        default=False,
        help_text=_(
            "Designates whether the user has verified email ownership."
        ),
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now,
    )

    objects = EmailUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        if self.name:
            return '{name:s} <{email:s}> ({pk!s})'.format(
                name=self.name,
                email=self.email,
                pk=self.pk
            )
        else:
            return '{email:s} ({pk!s})'.format(
                email=self.email,
                pk=self.pk
            )

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def get_verification_key(self):
        key = signing.dumps(
            obj=getattr(self, self.USERNAME_FIELD),
            salt=settings.SECRET_KEY,
        )
        return key

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_verification_email(self, request):
        """Send verification email to this user.
        """
        verification_key = self.get_verification_key()
        verification_url = request.build_absolute_uri(
            reverse('user_verify', kwargs={
                'verification_key': verification_key,
            }),
        )
        context = {
            'user': self,
            'host': request.get_host(),
            'verification_key': verification_key,
            'verification_url': verification_url,
        }
        message = render_to_string(
            'registration/verification_email.txt', context,
        )
        self.email_user(
            subject=ugettext('Verify your email address on {host}').format(
                **context
            ),
            message=message, fail_silently=False,
        )

    def create_biocloud_folders(self):
        """
        Setup BioCloud related folders, including data sources,
        results, and report.
        """
        logger.info('Create BioCloud folders for {}'.format(self))
        for biocloud_root_folder in [
            settings.BIOCLOUD_DATA_SOURCES_DIR,
            # settings.BIOCLOUD_RESULTS_DIR,
            # settings.BIOCLOUD_REPORTS_DIR,
        ]:
            user_folder = Path(biocloud_root_folder, str(self.pk))
            if user_folder.exists():
                logger.warning("User {} specific folder {} is existed. Skipped."
                               .format(self, user_folder))
            else:
                user_folder.mkdir()
