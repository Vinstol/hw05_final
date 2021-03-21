from django.contrib.auth import get_user_model

from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст сообщения',
        help_text='Напишите здесь текст своего сообщения',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор сообщения'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу, в которую Вы хотите написать сообщение'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Вставьте картинку для своего сообщения'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Присвойте новой группе название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор группы'
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Дайте краткое опишисание новой группы'
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемое сообщение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Напишите здесь свой комментарий',
    )
    created = models.DateTimeField(
        verbose_name='Дата и время публикации комментария',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:5]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на которого подписываются'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unigue_subscriber'
            ),
        ]
        ordering = ['-author']

    def __str__(self):
        return self.author[:15]
