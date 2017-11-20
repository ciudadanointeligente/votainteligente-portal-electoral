from rest_framework.serializers import (HyperlinkedModelSerializer,
                                        JSONField,
                                        StringRelatedField)
from rest_framework.viewsets import ReadOnlyModelViewSet
from popular_proposal.models import PopularProposal, Commitment
from elections.models import Candidate

class ProposalSerializer(HyperlinkedModelSerializer):
    data = JSONField()
    proposer = StringRelatedField()
    class Meta:
        model = PopularProposal
        fields = ('id','title', 'slug', 'get_absolute_url', 'data', 'proposer','created', 'clasification','is_local_meeting','nro_supports')

class ProposalViewSet(ReadOnlyModelViewSet):
    queryset = PopularProposal.objects.all()
    serializer_class = ProposalSerializer


    def get_queryset(self):
        queryset = super(ProposalViewSet, self).get_queryset()
        username = self.request.query_params.get('proposer', None)
        if username is not None:
            queryset = queryset.filter(proposer__username=username)
        clasification = self.request.query_params.get('clasification', None)
        if clasification is not None:
            queryset = queryset.filter(clasification=clasification)
        return queryset


class CommitmentsSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Commitment
        fields = ('id','proposal','candidate', 'detail', 'commited', 'get_absolute_url')


class CommitmentViewSet(ReadOnlyModelViewSet):
    queryset = Commitment.objects.all()
    serializer_class = CommitmentsSerializer


class CandidateSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Candidate
        fields = ('id','name', 'get_absolute_url', 'commitments')


class CandidateViewSet(ReadOnlyModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    pagination_class = None