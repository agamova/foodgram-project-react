from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField('E-mail', max_length=50, unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('user', 'following'),
                                    name='already subscribed'),
        )

    def __str__(self):
        return f'{self.user.username} followed {self.following.username}'
