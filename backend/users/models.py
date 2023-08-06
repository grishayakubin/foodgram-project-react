from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        help_text='Логин',
        error_messages={'unique': 'username не уникален'},
    )

    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Имя',
        help_text='Укажите имя'
    )

    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Фамилия',
        help_text='Укажите фамилию'
    )

    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name='email',
        help_text='Укажите email'
    )

    password = models.CharField(
        max_length=150,
        help_text='Пароль',
        blank=False,
        null=False
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} {self.email}'


class Follow(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='no_self_follow'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
