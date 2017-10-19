from numpy import matrix, concatenate


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


class Calculator(object):
	def __init__(self, adapter):
		self.adapter = adapter
	

	def _get_vector_result(self):
		P = matrix(self.adapter.get_responses_matrix())
		R = matrix(self.adapter.get_responses_vector()).transpose()
		_r = P * R
		return _r

	def get_result(self):
		candidates_vector = matrix(self.adapter.candidates).transpose().tolist()
		_result = self._get_vector_result().tolist()
		concatenated = []
		for index in range(len(_result)):
			concatenated.append({'candidate': candidates_vector[index][0], 'value': _result[index][0]})
		concatenated = sorted(concatenated, key=lambda t: -t['value'])
		return concatenated