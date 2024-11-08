from django.contrib.auth import get_user_model

from django.urls import reverse

from django.db import models

MAX_LENGTH_TITLE = 256  # Максимальная длина полей
LIMIT_TEXT = 15  # Максимальная длина текста для __str__

User = get_user_model()


class PublishModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено')

    class Meta:
        abstract = True


class Category(PublishModel):
    title = models.CharField(
        max_length=MAX_LENGTH_TITLE,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:LIMIT_TEXT]


class Location(PublishModel):
    name = models.CharField(
        default='Планета земля',
        max_length=MAX_LENGTH_TITLE,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class Post(PublishModel):
    title = models.CharField(
        max_length=MAX_LENGTH_TITLE,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    image = models.ImageField('Фото', upload_to='post_image', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title[:LIMIT_TEXT]

    def get_absolute_url(self):
        return reverse('blog:profile', kwargs={'slug': self.author})


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created_at',)
