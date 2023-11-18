from django.contrib import admin

from .models import Invitations, Module, Card, Label

admin.site.register(Invitations)
admin.site.register(Card)
admin.site.register(Label)
admin.site.register(Module)
