from django.contrib import admin

from .models import EducationPlan, PendingStudent

admin.site.register(EducationPlan)
admin.site.register(PendingStudent)
