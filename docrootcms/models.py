from django.db import models
from markdownx.models import MarkdownxField
from markdownx.models import MarkdownxFormField


# Markdownx Model overrides to use our new properties without importing all the code
class ContentMarkdownField(MarkdownxField):
    def __init__(self, *args, **kwargs):
        """
        sas 2020-09-15 : we want to add the ability to prefix our images based on the model/field via a new
            attribute 'field_image_prefix' which will be appended to the prefix defined in the settings file if given;
            this will allow us to categorize our images better based on model/field.
            EX: /media/markdownx/blog/content/me.jpg -or- /media/markdownx/blog/teaser/me.jpg
            NOTE: if not provided, will follow the same original rules as before
        """
        # pop the custom kwarg for the optional field image prefix so super does not error
        self.field_image_prefix = kwargs.pop('field_image_prefix', None)
        super(MarkdownxField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Customising the ``form_class``.

        :return: TextField with a custom ``form_class``.
        :rtype: django.db.models.TextField
        """
        defaults = {'form_class': MarkdownxFormField}
        defaults.update(kwargs)
        frmfield = super(MarkdownxField, self).formfield(**defaults)
        # sas 2020-09-15 : adding attrs if not there and then adding the image_prefix from the model or empty string
        if not frmfield.widget.attrs:
            frmfield.widget.attrs = {}
        frmfield.widget.attrs['data-field-image-prefix'] = self.field_image_prefix or ""
        return frmfield


# cms models
class Content(models.Model):
    uri = models.CharField(max_length=2000, blank=True)
    element_id = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ['uri', 'element_id']

    def __str__(self):
        return self.uri + " " + str(self.element_id)


