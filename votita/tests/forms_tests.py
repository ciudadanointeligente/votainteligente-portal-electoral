# coding=utf-8
from popular_proposal.tests import ProposingCycleTestCaseBase
from backend_citizen.models import Organization, Enrollment
from elections.models import Area
from django.contrib.auth.models import User
from popular_proposal.models import ProposalTemporaryData, PopularProposal, ProposalLike
from popular_proposal.tests.wizard_tests import WizardDataMixin
from django.core import mail
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.test import override_settings
from votita.models import KidsProposal, KidsGathering
from django.core.urlresolvers import reverse
from votita.forms.forms import CreateGatheringForm, UpdateGatheringForm
from constance.test import override_config
from elections.models import Area


USER_PASSWORD = 'secr3t'


class CreateGatheringFormTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(CreateGatheringFormTestCase, self).setUp()
        self.a_comuna = Area.objects.filter(classification='Comuna').first()

    def test_create_a_gathering(self):
        data = {"name": "Segundo medio C",
                "presidents_features": "inteligente,honesto",
                "generated_at": self.a_comuna.id}
        form = CreateGatheringForm(data, proposer=self.feli)
        self.assertTrue(form.is_valid())
        gathering = form.save()
        self.assertEquals(gathering.name, data['name'])
        self.assertTrue(gathering.presidents_features.all())
        self.assertEquals(gathering.generated_at, self.a_comuna)

    def test_update_gathering(self):
        gathering = KidsGathering.objects.create(proposer=self.feli,
                                                 name=u"Título",
                                                 presidents_features=['ingeligente',
                                                                      'honesto'])
        photo = self.get_image()
        data = {
            'male': 10,
            'female': 10,
            'others': 10,
            'comments': "Muy buena actividad, esto es lindo",
        }
        file_data = {'image': photo}
        form = UpdateGatheringForm(data=data,
                                   files=file_data,
                                   instance=gathering)
        self.assertTrue(form.is_valid())
        g = form.save()
        g = KidsGathering.objects.get(id=g.id)
        self.assertTrue(g.stats_data)
        self.assertTrue(g.image)
        self.assertTrue(g.comments)
