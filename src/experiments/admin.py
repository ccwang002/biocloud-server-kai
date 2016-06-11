from django.contrib import admin

from .models import Experiment, Condition


class ConditionInline(admin.TabularInline):
    model = Experiment.data_sources.through


@admin.register(Experiment)
class Experiment(admin.ModelAdmin):
    inlines = [
        ConditionInline,
    ]
    exclude = ('data_sources',)

