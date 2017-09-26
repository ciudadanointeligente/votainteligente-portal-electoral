from rest_framework import routers, serializers, viewsets
from popular_proposal.models import PopularProposal

class ProposalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PopularProposal
        fields = ('id','title', 'slug', 'get_absolute_url')

class ProposalViewSet(viewsets.ModelViewSet):
    queryset = PopularProposal.objects.all()
    serializer_class = ProposalSerializer
