# coding=utf-8
from popular_proposal.filters import ProposalFilterBase
from proposals_for_votainteligente.filters import (filterable_areas,
                                                   ProposalWithAreaFilter,
                                                   ProposalGeneratedAtFilter)
from proposals_for_votainteligente.tests import VIProposingCycleTestCaseBase
from popular_proposal.models import PopularProposal
from elections.models import Area
from popular_proposal.forms.form_texts import TOPIC_CHOICES
from django.core.management import call_command
import haystack
from datetime import timedelta
from django.utils import timezone
from django.test import override_settings
from django.core.urlresolvers import reverse


one_day_ago = timezone.now() - timedelta(days=1)
two_days_ago = timezone.now() - timedelta(days=2)
three_days_ago = timezone.now() - timedelta(days=3)



@override_settings(FILTERABLE_AREAS_TYPE=['Comuna'])
class PopularProposalFilterTestCase(VIProposingCycleTestCaseBase):
    def setUp(self):
        super(PopularProposalFilterTestCase, self).setUp()
        self.algarrobo = Area.objects.get(id='algarrobo-5602')
        self.p1 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=self.data,
                                                 title=u'P1',
                                                 clasification=TOPIC_CHOICES[1][0]
                                                 )
        self.p2 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=self.data,
                                                 title=u'P2',
                                                 clasification=TOPIC_CHOICES[2][0]
                                                 )
        self.p3 = PopularProposal.objects.create(proposer=self.fiera,
                                                 area=self.algarrobo,
                                                 data=self.data,
                                                 title=u'P3',
                                                 clasification=TOPIC_CHOICES[3][0]
                                                 )

    def test_filter_with_area(self):

        data = {'clasification': TOPIC_CHOICES[1][0],
                'area': self.algarrobo.id}
        f = ProposalWithAreaFilter(data=data)
        self.assertIn(self.p1, f.qs)
        self.assertNotIn(self.p2, f.qs)
        self.assertNotIn(self.p2, f.qs)

        data = {'area': self.algarrobo.id}
        f = ProposalWithAreaFilter(data=data)
        self.assertIn(self.p1, f.qs)
        self.assertIn(self.p2, f.qs)
        self.assertIn(self.p2, f.qs)

    def test_filter_where_generated_area(self):
        chonchi = Area.objects.create(name="Chonchi", classification="Comuna")
        p = PopularProposal.objects.create(proposer=self.fiera,
                                           data=self.data,
                                           title=u'P2',
                                           generated_at=chonchi,
                                           clasification=TOPIC_CHOICES[2][0]
                                           )
        data = {'generated_at': chonchi.id}
        f = ProposalGeneratedAtFilter(data=data)
        self.assertIn(p, f.qs)
        self.assertNotIn(self.p1, f.qs)
        self.assertNotIn(self.p2, f.qs)
        self.assertNotIn(self.p2, f.qs)

    def test_filterable_areas(self):
        laja = Area.objects.create(name="Laja", classification="Comuna")
        rm = Area.objects.create(name="region metropolitana",
                                 classification=u"Región")
        osorno = Area.objects.create(name="Osorno", classification="Comuna")
        areas = filterable_areas("This is a request")
        p = PopularProposal.objects.create(proposer=self.fiera,
                                           data=self.data,
                                           title=u'P2',
                                           generated_at=rm,
                                           clasification=TOPIC_CHOICES[2][0]
                                           )
        p2 = PopularProposal.objects.create(proposer=self.fiera,
                                           data=self.data,
                                           title=u'P2',
                                           generated_at=laja,
                                           clasification=TOPIC_CHOICES[2][0]
                                           )
        self.assertIn(laja, areas)
        self.assertNotIn(osorno, areas)
        self.assertNotIn(rm, areas)


@override_settings(FILTERABLE_AREAS_TYPE=['Comuna'])
class OrderingFormTestCase(VIProposingCycleTestCaseBase):
    def setUp(self):
        super(OrderingFormTestCase, self).setUp()
        self.algarrobo = Area.objects.get(id='algarrobo-5602')

    def test_order_by_in_form(self):
        url = reverse('popular_proposals:home')
        response = self.client.get(url)
        form = response.context['form']
        self.assertIn('order_by', form.fields.keys())

    def test_filtered_by_area(self):
        peru = Area.objects.create(name=u"Perú")
        p1 = PopularProposal.objects.create(proposer=self.fiera,
                                            area=peru,
                                            data=self.data,
                                            title=u'P1',
                                            clasification=TOPIC_CHOICES[1][0]
                                            )
        p1.created = two_days_ago
        p1.save()
        p2 = PopularProposal.objects.create(proposer=self.fiera,
                                            area=self.algarrobo,
                                            data=self.data,
                                            title=u'P2',
                                            clasification=TOPIC_CHOICES[2][0]
                                            )
        p2.created = three_days_ago
        p2.save()
        p3 = PopularProposal.objects.create(proposer=self.fiera,
                                            area=self.algarrobo,
                                            data=self.data,
                                            title=u'P3',
                                            clasification=TOPIC_CHOICES[3][0]
                                            )
        p3.created = one_day_ago
        p3.save()

        data = {'area': self.algarrobo.id}

        url = reverse('popular_proposals:home')
        response = self.client.get(url, data)
        qs = response.context['popular_proposals']
        self.assertIn(p2, qs)
        self.assertIn(p3, qs)
        self.assertNotIn(p1, qs)

        data = {'area': "non-existing"}

        url = reverse('popular_proposals:home')
        response = self.client.get(url, data)
        qs = response.context['popular_proposals']
        self.assertIn(p2, qs)
        self.assertIn(p3, qs)
        self.assertIn(p1, qs)
