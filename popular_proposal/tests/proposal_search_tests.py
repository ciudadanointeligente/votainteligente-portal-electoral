# coding=utf-8
from popular_proposal.models import PopularProposal
from popular_proposal.tests import ProposingCycleTestCaseBase
from popular_proposal.search_indexes import ProposalIndex
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from django.core.management import call_command
from elections.models import Area
from popular_proposal.forms.form_texts import TOPIC_CHOICES
import haystack
from haystack.query import SearchQuerySet


class PopularProposalSearchIndexTestCase(ProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalSearchIndexTestCase, self).setUp()
        self.algarrobo = Area.objects.get(id=1)
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
        call_command('rebuild_index', interactive=False, verbosity=0)

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)

    def test_index_template(self):
        r = SearchQuerySet().all()
        self.assertTrue(r.count())
        self.assertEquals(r.filter(text="bicicletas").count(), 1)

    def test_index_getProposals(self):
        r = SearchQuerySet().models(PopularProposal).auto_query("bicicletas")
        self.assertEquals(r[0].object, self.p2)

    def test_what_texts_it_searchs(self):
        data_with_texts = {'title': u'Que solucionen los problemas',
                           'terms_and_conditions': True,
                           'solution_at_the_end': u'Pericos',
                           'when': u'3_year',
                           'solution': u'Gatos',
                           'problem': u'Bicicletas',
                           'clasification': TOPIC_CHOICES[1][0],
                           'causes': u'Perros'}
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=data_with_texts,
                                                 title=u'Que solucionen los problemas',
                                                 clasification=TOPIC_CHOICES[1][0]
                                                 )
       	index = ProposalIndex()
        self.assertTrue(index.text.use_template)
        indexed_proposal = index.text.prepare_template(p1)
        self.assertIn(p1.title, indexed_proposal)
        self.assertIn(data_with_texts['solution'], p1.data_as_text)
        self.assertIn(data_with_texts['problem'],  p1.data_as_text)
        self.assertIn(data_with_texts['causes'],  p1.data_as_text)

        self.assertIn(data_with_texts['solution'], indexed_proposal)
        self.assertIn(data_with_texts['problem'], indexed_proposal)
        self.assertIn(data_with_texts['causes'], indexed_proposal)
