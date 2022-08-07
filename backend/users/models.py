from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_username


class User(AbstractUser):
    email = models.EmailField('email', max_length=254, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS
    if 'email' in REQUIRED_FIELDS:
        REQUIRED_FIELDS.remove('email')
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[validate_username]
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    subscribed_to = models.ManyToManyField(
        'self',
        through='Subscription',
        related_name='subscribers',
        symmetrical=False
    )
    favorite_recipes = models.ManyToManyField('foodgram.Recipe', related_name='favorited_by')
    shopping_cart_recipes = models.ManyToManyField('foodgram.Recipe', related_name='added_to_shopping_cart_by')

    class Meta:
        ordering = ['-id']


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='+'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribed_to'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('subscribed_to')),
                name='subscribed_not_to_yourself'
            ),
        ]
