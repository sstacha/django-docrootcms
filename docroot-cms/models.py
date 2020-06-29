from django.db import models


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
