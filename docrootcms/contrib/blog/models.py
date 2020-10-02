from django.core import serializers
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from tagulous.models import TagField, TagModel, TagTreeModel
from docrootcms.models import ContentMarkdownField


# BLOG MODELS
# Different categories, tags, classifications (tagulous)
class BlogTag(TagModel):
    """
    Blog Tags are public keywords that content people can use as metadata for the content.  They are visible
    to customers usually in the form of a tag cloud or keywords at the bottom to find related content.
    Ex: content has been tagged with 'technology' and shown at the bottom of the post to show other posts tagged
        with technology.
    """
    class TagMeta:
        force_lowercase = True


class BlogCategory(TagTreeModel):
    """
    Blog Categories are like tags but they are more structured and can have a hiearchy in the form of paths.  This
    has also been described as a content taxonomy.  This is often used as fixed headings and or to organize blogs for
    different website areas to display.
    Ex: content has been tagged with 'sports/NHL', 'sports/MLB' and 'tech/software/linux'
    This can be used on the main blog page to show 'sports', 'tech' etc
    Then each can have a blog with top posts for each sport type.
    NOTE: unlike tags which can be random, categories / taxonomy should be well thought out and defined beforehand
    """
    class TagMeta:
        force_lowercase = True

    class Meta:
        verbose_name_plural = "Blog categories"


class BlogProperty(TagModel):
    """
    Blog Properties are like tags for internal use.
    Ex: content has been tagged with 'homepage' and or 'hidden'
    Plugin properties = ['homepage',]
    Plugin exclude properties = ['hidden']
    Plugin will show all posts tagged 'homepage' but not any tagged 'hidden'
    Furthermore, homepage or hidden will not show up as a category or tagged as related content customers can use
    """
    class TagMeta:
        force_lowercase = True

    class Meta:
        verbose_name_plural = "Blog properties"


class MarkdownPost(models.Model):
    title = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250,
                            unique=True,
                            help_text='SEO Friendly name that is unique for use in URL')
    teaser = ContentMarkdownField(null=True, blank=True, field_image_prefix='post/teaser', help_text=mark_safe(
        'Markdown Reference: <a href="https://commonmark.org/help/">https://commonmark.org/help/</a>'))
    content = ContentMarkdownField(field_image_prefix='post/content', help_text=mark_safe(
        'Markdown Reference: <a href="https://commonmark.org/help/">https://commonmark.org/help/</a>'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    # image = FilerImageField(null=True, blank=True)
    publish_date = models.DateTimeField(default=timezone.now)
    expire_date = models.DateTimeField(null=True, blank=True)
    categories = TagField(
        to=BlogCategory,
        blank=True,
        help_text="Splits on commas and spaces;  hierarchy is defined by paths.  "
                  "Collectively known as a 'content taxonomy'.  This is often used as headings or to organize"
                  "different blog content."
                  "Ex: 'sports/nfl' 'sports/mlb' 'tech/sofware/linux'"
                  "NOTE: unlike tags, categories should be well thought out beforehand and not change often"
    )
    tags = TagField(
        to=BlogTag,
        blank=True,
        help_text="Splits on commas and spaces; tags will be displayed to the public and used to "
                  "pull a set of posts to show.  For example, you could tag posts with 'docker' "
                  "'zfs' then the plugin will show these at the bottom for visitors to use if there"
                  "are more posts with that tag."
    )
    properties = TagField(
        to=BlogProperty,
        blank=True,
        help_text="Splits on commas and spaces; like tags but not displayed to the public."
                  "For example, you could tag posts with 'homepage' and or "
                  "'hidden' then pull all posts tagged 'homepage' but not 'hidden'"
    )
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    modified_date = models.DateTimeField(auto_now=True, editable=False)
    modified_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-publish_date', 'title']

    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})

    def as_json(self):
        return serializers.serialize('json', [self])[0]

# SIMPLE POST IS JUST TEXT WITH NO CATEGORIES OR CLASSIFICATIONS
# class SimplePost(models.Model):
#     title = models.CharField(max_length=250, unique=True)
#     slug = models.SlugField(max_length=250,
#                             unique=True,
#                             help_text='SEO Friendly name that is unique for use in URL')
#     content = models.TextField()
#     author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     publish_date = models.DateTimeField(default=timezone.now)
#     expire_date = models.DateTimeField(null=True, blank=True)
#     created_date = models.DateTimeField(auto_now_add=True, editable=False)
#     modified_date = models.DateTimeField(auto_now=True, editable=False)
#     modified_by = models.CharField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         ordering = ['-publish_date', 'title']
#
#     def __str__(self):
#         return str(self.title)
#
#     def get_absolute_url(self):
#         return reverse("blog_detail", kwargs={"slug": self.slug})
#
# HTML POST MAY BE SOMETHING I LOOK AT IN THE FUTURE TO HAVE CKEDITOR INSTEAD OF MARKDOWN
#   but...  maybe not...
# class HTMLPost(models.Model):
#     title = models.CharField(max_length=250, unique=True)
#     slug = models.SlugField(max_length=250,
#                             unique=True,
#                             help_text='SEO Friendly name that is unique for use in URL')
#     # teaser = HTMLField(
#     #     max_length=300,
#     #     configuration='CKEDITOR_SETTINGS_SIMPLE',
#     #     help_text=u'Full text of the TD post.',
#     #     )
#     # content = HTMLField(
#     #     max_length=20000,
#     #     configuration='CKEDITOR_SETTINGS_SIMPLE',
#     #     help_text=u'Full text of the blog post.'
#     # )
#     teaser = MarkdownxField()
#     content = MarkdownxField()
#     author = models.ForeignKey(User, on_delete= models.CASCADE, null=True, blank=True)
#     # image = FilerImageField(null=True, blank=True)
#     publish_date = models.DateTimeField(default=timezone.now)
#     expire_date = models.DateTimeField(null=True, blank=True)
#     # categories = TagField(
#     #     to=BlogCategory,
#     #     blank=True,
#     #     help_text="Splits on commas and spaces;  hierarchy is defined by paths.  "
#     #               "Collectively known as a 'content taxonomy'.  This is often used as headings or to organize"
#     #               "different blog content."
#     #               "Ex: 'sports/nfl' 'sports/mlb' 'tech/sofware/linux'"
#     #               "NOTE: unlike tags, categories should be well thought out beforehand and not change often"
#     # )
#     # tags = TagField(
#     #     to=BlogTag,
#     #     blank=True,
#     #     help_text="Splits on commas and spaces; tags will be displayed to the public and used to "
#     #               "pull a set of posts to show.  For example, you could tag posts with 'docker' "
#     #               "'zfs' then the plugin will show these at the bottom for visitors to use if there"
#     #               "are more posts with that tag."
#     # )
#     # properties = TagField(
#     #     to=BlogProperty,
#     #     blank=True,
#     #     help_text="Splits on commas and spaces; like tags but not displayed to the public."
#     #               "For example, you could tag posts with 'homepage' and or "
#     #               "'hidden' then pull all posts tagged 'homepage' but not 'hidden'"
#     # )
#     created_date = models.DateTimeField(auto_now_add=True, editable=False)
#     modified_date = models.DateTimeField(auto_now=True, editable=False)
#     modified_by = models.CharField(max_length=255, null=True, blank=True)
#
#     class Meta:
#         ordering = ['-publish_date', 'title']
#
#     def __str__(self):
#         return str(self.title)
#
#     def get_absolute_url(self):
#         return reverse("blog_detail", kwargs={"slug": self.slug})
#
#     def as_json(self):
#         return serializers.serialize('json', [self])[0]
#
#     def as_html(self):
#         return markdownify(self.content)
