from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import MarkdownPost


@admin.register(MarkdownPost)
class PostAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'slug', 'created_date')
    list_filter = ('modified_by',)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('modified_by',)

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.modified_by = str(request.user)[:255]
        instance.save()
        form.save_m2m()
        return instance
