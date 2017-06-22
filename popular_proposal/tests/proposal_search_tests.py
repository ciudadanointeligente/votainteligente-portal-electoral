# coding=utf-8
from popular_proposal.models import PopularProposal
from popular_proposal.tests import ProposingCycleTestCaseBase
# from popular_proposal.search_indexes import ProposalIndex
from django.core.management import call_command
from elections.models import Area
from popular_proposal.forms.form_texts import TOPIC_CHOICES
import haystack
from haystack.query import SearchQuerySet


class PopularProposalSearchIndexTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalSearchIndexTestCase, self).setUp()
        self.algarrobo = Area.objects.get(id='algarrobo-5602')
        self.p1 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=self.data,
                                                 title=u'Que solucionen los problemas',
                                                 clasification=TOPIC_CHOICES[1][0]
                                                 )
        self.p2 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=self.data,
                                                 title=u'Bicicletas para todas',
                                                 clasification=TOPIC_CHOICES[2][0]
                                                 )
        self.p3 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=self.data,
                                                 title=u'Educación de caludad',
                                                 clasification=TOPIC_CHOICES[3][0]
                                                 )
        for key, opts in haystack.connections.connections_info.items():
            haystack.connections.reload(key)
        call_command('update_index', interactive=False, verbosity=0)

    def test_index_template(self):
        r = SearchQuerySet().all()
        self.assertTrue(r.count())
        self.assertEquals(r.filter(text="bicicletas").count(), 1)
