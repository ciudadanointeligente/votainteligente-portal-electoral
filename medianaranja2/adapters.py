from numpy import matrix, concatenate, ones


class Adapter(object):
	def __init__(self, election, positions):
		self.user_positions = positions
		self.user_questions = []
		for position in self.user_positions:
			if position.topic not in self.user_questions:
				self.user_questions.append(position.topic)
		self.candidates = list(election.candidates.order_by('id'))
		self.topics = []
		self.positions = []
		for category in election.categories.all().order_by('id'):
			for topic in category.topics.all().order_by('id'):
				self.topics.append(topic)
				for position in topic.positions.all().order_by('id'):
					self.positions.append(position)

	def get_responses_vector(self):
		response = []
		for position in self.user_positions:
			topic = position.topic
			for p in topic.positions.all().order_by('id'):
				if p == position:
					response.append(1)
				else:
					response.append(0)
		return response

	def get_positions_from_candidate(self, candidate):
		positions = []
		for question in self.user_questions:
			for position in question.positions.order_by('id'):
				if question.taken_positions.filter(person=candidate, position=position):
					positions.append(1)
				else:
					positions.append(0)
		return positions

	def get_responses_matrix(self):
		matrix = []
		for candidate in self.candidates:
			matrix.append(self.get_positions_from_candidate(candidate))
		return matrix


class CommitmentsAdapter(object):
	def __init__(self, election, proposals):
		self.candidates = []
		for candidate in election.candidates.order_by('id'):
			self.candidates.append(candidate)
		self.proposals = proposals
		self.ones = ones((len(self.proposals),1))

	def get_commitments_matrix(self):
		_C = []
		for candidate in self.candidates:
			vector = []
			for p in self.proposals:
				if candidate.commitments.filter(proposal=p, commited=True).exists():
					vector.append(1)
				else:
					vector.append(0)
			_C.append(vector)
		return matrix(_C)


class Calculator(object):

	def __init__(self,
				election,
				selected_positions=[],
				selected_proposals=[],
				questions_adapter_class=Adapter,
				commitments_adapter_class=CommitmentsAdapter):
		self.set_questions_adapter(questions_adapter_class(election, selected_positions))
		self.set_commitments_adapter(commitments_adapter_class(election, selected_proposals))


	def	set_questions_importance(self, importance):
		self.questions_importance = importance

	def	set_proposals_importance(self, importance):
		self.proposals_importance = importance

	def set_questions_adapter(self, adapter):
		self.questions_adapter = adapter
	
	def set_commitments_adapter(self, adapter):
		self.commitments_adapter = adapter

	def _get_questions_vector_result(self):
		P = matrix(self.questions_adapter.get_responses_matrix())
		R = matrix(self.questions_adapter.get_responses_vector()).transpose()
		_r = P * R
		return _r

	def get_questions_result(self):
		candidates_vector = matrix(self.questions_adapter.candidates).transpose().tolist()
		_result = self._get_questions_vector_result().tolist()
		concatenated = []
		for index in range(len(_result)):
			concatenated.append({'candidate': candidates_vector[index][0], 'value': _result[index][0]})
		concatenated = sorted(concatenated, key=lambda t: -t['value'])
		return concatenated

	def get_commitments_result(self):
		C = self.commitments_adapter.get_commitments_matrix()
		return C * self.commitments_adapter.ones

	def get_result(self):
		P_x_R = self._get_questions_vector_result()
		C = self.get_commitments_result()
		result = P_x_R * self.questions_importance + C * self.proposals_importance
		return result