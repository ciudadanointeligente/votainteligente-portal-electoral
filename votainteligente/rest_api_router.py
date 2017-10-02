from popular_proposal.rest_api import ProposalViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'propuestas', ProposalViewSet)
