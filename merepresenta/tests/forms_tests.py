# coding=utf-8
from medianaranja2.tests.adapter_tests import MediaNaranjaAdaptersBase
from merepresenta.forms import MeRepresentaProposalsForm
from elections.models import Area
from popular_proposal.models import PopularProposal
from django.conf import settings
from merepresenta.models import MeRepresentaPopularProposal


class ProposalsFormsTestCase(MediaNaranjaAdaptersBase):
    popular_proposal_class = MeRepresentaPopularProposal
    def setUp(self):
        super(ProposalsFormsTestCase, self).setUp()
        self.setUpProposals()
        self.area = Area.objects.create(name=u"children",
                                        classification=settings.FILTERABLE_AREAS_TYPE[0])
        self.election.area = self.area
        self.election.save()

    def test_proposals_form_instanciate(self):
        argentina = Area.objects.create(name=u'Argentina', id=u'argentina')
        proposals = MeRepresentaPopularProposal.objects.filter(id__in=[self.p1.id, self.p2.id, self.p3.id])
        kwargs = {'proposals': proposals} 
        form = MeRepresentaProposalsForm(**kwargs)
        proposals_choices = list(form.fields['proposals'].choices)
        possible_labels = {}
        for t in proposals_choices:
            if type(t) == tuple:
                possible_labels[t[0]] = t[1]
        self.assertIn(unicode(self.p1), possible_labels[self.p1.id])
        self.assertIn(unicode(self.p2), possible_labels[self.p2.id])
        self.assertIn(unicode(self.p3), possible_labels[self.p3.id])
        areas = form.fields['area'].queryset.all()
        for a in areas:
            self.assertEquals(a.classification, settings.FILTERABLE_AREAS_TYPE[0])