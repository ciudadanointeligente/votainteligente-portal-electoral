from rest_framework.serializers import (HyperlinkedModelSerializer,
                                        JSONField,
                                        StringRelatedField)
from rest_framework.viewsets import ReadOnlyModelViewSet
from popular_proposal.models import PopularProposal

class ProposalSerializer(HyperlinkedModelSerializer):
    data = JSONField()
    proposer = StringRelatedField()
    class Meta:
        model = PopularProposal
        fields = ('id','title', 'slug', 'get_absolute_url', 'data', 'proposer')

class ProposalViewSet(ReadOnlyModelViewSet):
    queryset = PopularProposal.objects.all()
    serializer_class = ProposalSerializer


    def get_queryset(self):
        queryset = super(ProposalViewSet, self).get_queryset()
        username = self.request.query_params.get('proposer', None)
        if username is not None:
            queryset = queryset.filter(proposer__username=username)
        return queryset
