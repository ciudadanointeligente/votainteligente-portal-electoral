# coding=utf-8
DEFAULT_CANDIDATE_EXTRA_INFO = {
    "portrait_photo": "/static/img/candidate-default.jpg",
    'custom_ribbon': 'ribbon text'
}
DEFAULT_ELECTION_EXTRA_INFO = {
    "extra": "Extra extra extra"
}
NAV_BAR = ('profiles', 'questionary', 'soulmate', 'facetoface', 'ask', 'ranking')
THEME = None
WHEN_TO_NOTIFY = [25, 50, 100, 150, 200]
NOTIFY_CANDIDATES = True
NOTIFY_CANDIDATES_OF_NEW_PROPOSAL = True
MAX_AMOUNT_OF_MAILS_TO_CANDIDATE = 3
FILTERABLE_AREAS_TYPE = ['Comuna']
DEFAULT_EXTRAPAGES_FOR_ORGANIZATIONS=[{'title':u'Agenda', 'content':'''* **19 DE NOVIEMBRE**\r\nPrimera vuelta de Elecciones Presidenciales y Parlamentarias
* **17 DE DICIEMBRE**   *Segunda vuelta de Elecciones Presidenciales'''},
                                                           {'title':u'Documentos', 'content':''}]

MODERATION_ENABLED = False
MARKED_AREAS = []
POSSIBLE_GENERATING_AREAS_FILTER = []
EXCLUDED_PROPOSALS_APPS = []
AREAS_THAT_SHOULD_BE_REDIRECTING_TO_THEIR_PARENTS = ['comuna']
SECOND_ROUND_ELECTION = None
PRIORITY_CANDIDATES = []

# Popular Proposals adaptation
AUTHORITY_MODEL = "elections.models.Candidate"
PROPOSALS_ADAPTER = "proposals_for_votainteligente.models.ProposalsAdapter"
MAIL_SENDER_FUNCTION = 'votainteligente.send_mails.send_mail'
MAIL_TO_STAFF_SENDER_FUNCTION = 'votainteligente.send_mails.send_mails_to_staff'
DEFAULT_FITERSET_CLASS = 'proposals_for_votainteligente.filters.ProposalGeneratedAtFilter'
WIZARD_PREVIOUS_CLASSES = ['proposals_for_votainteligente.forms.AreaForm',]
PROPOSAL_UPDATE_FORM  = 'proposals_for_votainteligente.forms.UpdateProposalForm'
WIZARD_FORM_MODIFIER = 'proposals_for_votainteligente.forms.wizard_forms_field_modifier'
NUMERICAL_NOTIFICATION_CLASSES = ['popular_proposal.subscriptions.YouAreAHeroNotification',
                                  # 'proposals_for_votainteligente.subscriptions.ManyCitizensSupportingNotification'
                                  ]
IS_AUTHORITY_DETERMINER = "backend_candidate.models.is_candidate"