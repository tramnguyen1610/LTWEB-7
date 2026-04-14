from django.contrib import admin
from .models import RewardPenalty

@admin.register(RewardPenalty)
class RewardPenaltyAdmin(admin.ModelAdmin):
    list_display = ('employee', 'type', 'amount', 'date_applied')
    list_filter = ('type', 'date_applied')
    search_fields = ('employee__full_name', 'reason')