from popular_proposal.rest_api import ProposalViewSet, CommitmentViewSet, CandidateViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'propuestas', ProposalViewSet)
router.register(r'compromisos', CommitmentViewSet)
router.register(r'candidatos', CandidateViewSet)
