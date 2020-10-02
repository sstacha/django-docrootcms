from django import forms
from os import path
from collections import namedtuple
from django.core.files.storage import default_storage

from markdownx.forms import ImageForm
from markdownx.exceptions import MarkdownxImageUploadError
from markdownx.settings import _mdx

from markdownx.settings import (
    MARKDOWNX_MEDIA_PATH,
    MARKDOWNX_UPLOAD_CONTENT_TYPES,
    MARKDOWNX_UPLOAD_MAX_SIZE,
    # MARKDOWNX_USE_ORIGINAL_IMAGE_NAME,
)
# sas 2020-09-27 : should place in markdownx.settings above but placing here so there are fewer changes
MARKDOWNX_USE_ORIGINAL_IMAGE_NAME = _mdx('USE_ORIGINAL_IMAGE_NAME', False)


# markdownx overrides for forms
class MarkdownImageUploadForm(ImageForm):

    # sas 2020-09-15 : adding field to sanitize the input for the field image prefix if given
    field_image_prefix = forms.CharField(required=False)

    def _save(self, image, file_name, commit):
        """
        Final saving process, called internally after processing tasks are complete.

        :param image: Prepared image
        :type image: django.core.files.uploadedfile.InMemoryUploadedFile
        :param file_name: Name of the file using which the image is to be saved.
        :type file_name: str
        :param commit: If ``True``, the image is saved onto the disk.
        :type commit: bool
        :return: URL of the uploaded image ``commit=True``, otherwise a namedtuple
                 of ``(path, image)`` where ``path`` is the absolute path generated
                 for saving the file, and ``image`` is the prepared image.
        :rtype: str, namedtuple

        NOTE: copied from original form with 2 modifications below
            1) we do not store a unique file name; if the filename exists we skip and just return the url
            2) we will inject the new field_image_prefix path if it is provided
                NOTE: provided by model and passed via ajax javascript to view

        """
        # Defining a universally unique name for the file
        # to be saved on the disk.

        # NOTE: this takes away the ability for content creators to control the file name
        #   or quickly return an existing image link.  Altering to give better control and functionality over file names
        #   add MARKDOWNX_USE_ORIGINAL_IMAGE_NAME = True to change the default functionality
        # sas 2020-09-27 : added functionality to use the original file name and just return link if exists
        if MARKDOWNX_USE_ORIGINAL_IMAGE_NAME:
            unique_file_name = file_name
        else:
            unique_file_name = self.get_unique_file_name(file_name)

        # sas 2020-09-15 : reading the sanitized image prefix or empty string and appending to path
        field_image_prefix = self.cleaned_data['field_image_prefix'] or ''
        full_path = path.join(MARKDOWNX_MEDIA_PATH, field_image_prefix, unique_file_name)

        if commit:
            # sas 2020-09-27 : we only want to save if the image doesn't already exist; otherwise we just return the url
            if MARKDOWNX_USE_ORIGINAL_IMAGE_NAME and default_storage.exists(full_path):
                pass
            else:
                default_storage.save(full_path, image)
            return default_storage.url(full_path)

        # If `commit is False`, return the path and in-memory image.
        image_data = namedtuple('image_data', ['path', 'image'])
        return image_data(path=full_path, image=image)

    def clean(self):
        """
        Checks the upload against allowed extensions and maximum size.

        :return: Upload

        NOTE: copied from original form with 1 modification below
            1) commented setting to just image so we can keep the clean_data for our new field override too
        """
        upload = self.cleaned_data.get('image')

        # -----------------------------------------------
        # See comments in `self._error_templates` for
        # additional information on each error.
        # -----------------------------------------------
        if not upload:
            raise MarkdownxImageUploadError.not_uploaded()

        content_type = upload.content_type
        file_size = upload.size

        if content_type not in MARKDOWNX_UPLOAD_CONTENT_TYPES:

            raise MarkdownxImageUploadError.unsupported_format()

        elif file_size > MARKDOWNX_UPLOAD_MAX_SIZE:

            raise MarkdownxImageUploadError.invalid_size(
                current=file_size,
                expected=MARKDOWNX_UPLOAD_MAX_SIZE
            )
        # sas 2020-09-15 : removing the upload return which strips other vars like the new field image prefix
        # return upload


class LoginForm(forms.Form):

    login = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())
    target = forms.CharField()
