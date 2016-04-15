from django.contrib import admin
from popular_proposal.models import PopularProposal, ProposalTemporaryData


@admin.register(PopularProposal)
class PopularProposalAdmin(admin.ModelAdmin):
    list_display = ('id','area', 'title', 'data', 'proposer')


@admin.register(ProposalTemporaryData)
class ProposalTemporaryDataAdmin(admin.ModelAdmin):
    list_display = ('id','area', 'data', 'proposer')
