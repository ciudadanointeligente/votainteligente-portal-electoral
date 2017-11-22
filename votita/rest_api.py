from rest_framework.serializers import (HyperlinkedModelSerializer,
                                        JSONField,
                                        StringRelatedField,
                                        HyperlinkedRelatedField)
from rest_framework.viewsets import ReadOnlyModelViewSet
from votita.models import KidsGathering, KidsProposal


class KidsGatheringSerializer(HyperlinkedModelSerializer):
    proposer = StringRelatedField()
    class Meta:
      model = KidsGathering
      fields = ['proposer','name','school']

class KidsGatheringViewSet(ReadOnlyModelViewSet):
    queryset = KidsGathering.objects.all()
    serializer_class = KidsGatheringSerializer

class KidsProposalSerializer(HyperlinkedModelSerializer):
    data = JSONField()
    proposer = StringRelatedField()
    class Meta:
        model = KidsProposal
        fields = ('id','title', 'slug', 'get_absolute_url', 'data', 'proposer', 'created', 'clasification','is_local_meeting','nro_supports')

class KidsProposalViewSet(ReadOnlyModelViewSet):
    queryset = KidsProposal.objects.all()
    serializer_class = KidsProposalSerializer
