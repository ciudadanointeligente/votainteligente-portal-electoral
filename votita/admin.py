from django.contrib import admin
from votita.models import KidsGathering, KidsProposal


class KidsProposalInline(admin.TabularInline):
    model = KidsProposal
    extra = 0
    can_delete = False
    fields = ['title', 'clasification']

@admin.register(KidsGathering)
class KidsGatheringAdmin(admin.ModelAdmin):
    list_display = ('proposer', 'name', 'created')
    inlines = [KidsProposalInline, ]


@admin.register(KidsProposal)
class KidsProposalAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'area',
                    'title',
                    'data',
                    'proposer',
                    )
    exclude = ('organization',)
