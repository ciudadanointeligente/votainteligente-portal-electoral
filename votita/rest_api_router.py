from votita.rest_api import KidsGatheringViewSet, KidsProposalViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'kidsencuentros', KidsGatheringViewSet)
router.register(r'kidspropuestas', KidsProposalViewSet)
