from django.contrib import admin
from .models import EducationPlan, Module, Card, Label, File

admin.site.register(EducationPlan)
admin.site.register(Card)
admin.site.register(Label)
admin.site.register(Module)
admin.site.register(File)
