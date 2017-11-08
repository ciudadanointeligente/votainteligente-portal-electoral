from elections.models import Candidate
from popular_proposal.models import Commitment

class CommitmentsExporter(object):
    def __init__(self, area, position=None):
        super(CommitmentsExporter, self).__init__()
        self.candidates = []
        candidates = Candidate.objects.filter(elections__area=area)
        if position:
            candidates = candidates.filter(elections__position=position)
        for c in candidates:
            self.candidates.append(c)
        self.proposals = []
        for p in area.proposals.all():
            self.proposals.append(p)

    def has_commited(self, candidate, proposal):
        return Commitment.objects.filter(proposal=proposal, candidate=candidate).exists()

    def get_line_for(self, candidate):
        result = [candidate.election.position, candidate.name]
        for p in self.proposals:
            if self.has_commited(candidate, p):
                result.append(u'\u2713')
            else:
                result.append(u'')
        return result

    def get_header(self):
        line_0 = ['','']
        line_1 = ['','']
        line_2 = [u'Postulando a', u'Candidato']
        for p in self.proposals:
            line_0.append('https://votainteligente.cl' + p.get_absolute_url())
            line_1.append(p.data['clasification'])
            line_2.append(p.title)
        result =  [line_0, line_1, line_2]
        return result

    def get_lines(self):
        header = self.get_header()
        lines = header
        for c in self.candidates:
            lines.append(self.get_line_for(c))
        return lines
