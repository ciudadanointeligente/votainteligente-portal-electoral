# coding=utf-8
from django.contrib import admin
from popular_proposal.models import (PopularProposal,
                                     ProposalTemporaryData,
                                     Commitment,
                                     PopularProposalSite,
                                     ProposalLike)
from popular_proposal.forms import ProposalTemporaryDataModelForm
from popular_proposal.forms.form_texts import TEXTS


@admin.register(PopularProposalSite)
class PopularProposalSiteAdmin(admin.ModelAdmin):
    pass

@admin.register(PopularProposal)
class PopularProposalAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'area',
                    'title',
                    'data',
                    'proposer',
                    )
    exclude = ('organization',)

    def get_queryset(self, *args, **kwargs):
        return PopularProposal.all_objects.all()


fieldset = []
for key in ProposalTemporaryDataModelForm.base_fields:
    fieldset.append(key)

for key in TEXTS.keys():
    if key not in fieldset:
        fieldset.append(key)


@admin.register(ProposalTemporaryData)
class ProposalTemporaryDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'area', 'data', 'proposer', 'status')
    form = ProposalTemporaryDataModelForm
    fieldsets = (
        (None, {
            'fields': fieldset,
        }),
    )

    def get_queryset(self, request):
        return ProposalTemporaryData.objects.all()

    def get_form(self, request, obj=None, **kwargs):
        return ProposalTemporaryDataModelForm


@admin.register(ProposalLike)
class ProposalLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_organization', 'proposal', 'created')
    def is_organization(self, obj):
        return obj.user.profile.is_organization
    is_organization.short_description = u'Es organización?'
    is_organization.admin_order_field = 'user__profile__is_organization'


@admin.register(Commitment)
class CommitmentAdmin(admin.ModelAdmin):
    list_display = ('id', "candidate", "proposal")
