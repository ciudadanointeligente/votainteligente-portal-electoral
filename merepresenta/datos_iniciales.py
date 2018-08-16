QuestionCategory.objects.all().delete()
Topic.objects.all().delete()
Position.objects.all().delete()
cat = QuestionCategory.objects.create(name=u"#Gênero")
Topic.objects.create(category=cat, description="A prática de aborto é crime no Brasil: mulheres e médicos que praticam aborto ilegal podem ser presos. Uma em cada cinco mulheres já fez aborto no país e, por ano, cerca de 1 milhão de abortos são realizados. Metade das mulheres que praticam aborto ilegal acabam tendo complicações médicas e precisam ser internadas e muitas delas morrem. O Supremo Tribunal Federal fez recentemente uma audiência pública sobre o tema, com participação da sociedade civil e de pesquisadores, e vai decidir se mulheres com gravidez de até 12 semanas podem abortar (ADPF 442).",
    label=u"Legalização do aborto")
Topic.objects.create(category=cat, description="Cerca de 12 mulheres são assassinadas por dia no Brasil. O feminicídio (assassinato motivado pela vítima ser mulher) atinge principalmente mulheres negras e de baixa renda. Mesmo depois de três anos da lei do feminicídio ter sido aprovada no Brasil, os seus efeitos ainda não podem ser medidos. A falta de dados oficiais dificulta o combate a este tipo de violência contra mulheres. A aplicação efetiva da lei do feminicídio depende de seu monitoramento pelos órgãos públicos, responsáveis pela coleta e divulgação dos dados.",
    label=u"Monitoramento da Lei do feminicídio")

Topic.objects.create(category=cat, description="27% da população: essa é a porcentagem de mulheres negras no Brasil. Mas no Congresso Nacional, elas são apenas 2%. Mulheres brancas também são minoria na política, a diferença é que elas têm 3 vezes mais chances de ganhar uma eleição do que mulheres negras. Dentro dos partidos políticos, apenas 2,5% dos recursos são destinados para candidaturas de mulheres negras. Hoje está no Tribunal Superior Eleitoral uma consulta pública que exige um investimento mínimo de dinheiro dos partidos em candidatas negras.",
    label=u"Financiamento público de campanhas de mulheres negras")

cat = QuestionCategory.objects.create(name=u"#Raça")
Topic.objects.create(category=cat, description="A Constituição protege a liberdade religiosa e a Lei de Crimes Ambientais proíbe maus tratos contra animais. Abates religiosos são praticados por judeus, muçulmanos e fiéis de religiões afro-brasileiras de um jeito que provoca morte instantânea, com mínimo de dor. Tribunais do Rio Grande do Sul e São Paulo já decidiram que estes casos não são maus tratos. Agora o Supremo Tribunal Federal dará a palavra final sobre o assunto (RE 494601).",
    label=u"Tornar crime o abate religioso de animais")
Topic.objects.create(category=cat, description="Apenas <a src='https://www.cartacapital.com.br/sociedade/ibge-apenas-10-das-mulheres-negras-completam-o-ensino-superior' target='_blank'>10% das mulheres negras e 7% dos homens negros</a> têm acesso à universidade, mostrando que esse espaço ainda não é democrático e não representa a realidade da população brasileira. O valor médio do salário da população negra é quase metade do valor do salário da população branca (60%). As ações afirmativas, como cotas raciais nas universidades, servem para mudar esse cenário. Em 2012, o Supremo Tribunal Federal entendeu que as cotas raciais são um direito e ajudam a corrigir o histórico de racismo e escravidão no Brasil.",
    label=u"Cotas raciais nas universidades")
Topic.objects.create(category=cat, description="Mulheres negras sofrem com preconceito racial no atendimento de saúde no SUS. Em relação a mulheres brancas, recebem menos anestesia no parto, esperam mais tempo por atendimento, têm menos acesso a exames médicos, como mamografia, e 60% das vítimas de mortalidade materna no país são negras..",
    label=u"Prioridade no atendimento de mulheres negras no SUS ")

cat = QuestionCategory.objects.create(name=u"#LGBTs")
Topic.objects.create(category=cat, description="O Brasil é um dos países que mais mata LGBTs no mundo, em especial travestis e transexuais. Mas não há legislação que considere crime o preconceito contra lésbicas, transexuais e travestis, bissexuais, gays. Propostas para tornar crime o preconceito contra LGBTs estão sendo discutidas no Congresso Nacional (PL 134/2018, PL 515/2017 e 7582/2014).",
    label=u"O preconceito contra LGBTs deve ser crime")
Topic.objects.create(category=cat, description="A população transexual e travesti é frequentemente impedida de usar banheiros de acordo com sua identidade de gênero. Não existe uma legislação sobre o assunto. Porém, o Supremo Tribunal Federal iniciou essa discussão em 2015, dizendo que não permitir o uso de banheiros conforme identidade de gênero feriria a dignidade humana, mas o julgamento foi suspenso (RE 845779).",
    label=u"Trans e travestis podem usar o banheiro que quiserem")
Topic.objects.create(category=cat, description="“Escola sem partido” é nome dado a uma série de projetos lei que têm sido apresentados nos municípios, estados e também no Congresso Nacional (PL 7180/2014), que querem tirar o ensino sobre raça, classe social, gênero, identidade de gênero e orientação sexual nas escolas. 73% dos estudantes LGBTs já sofreu agressão verbal, 60% se sente inseguro e 36% já sofreu violência física nas escolas.",
    label=u"Projeto “Escola sem partido”")

cat = QuestionCategory.objects.create(name=u"#Povos tradicionais & Meio Ambiente")
Topic.objects.create(category=cat, description="A demarcação de terras é uma luta histórica dos povos indígenas e quilombolas, por conta de seus vínculos históricos, culturais e ancestrais com o território. Uma série de iniciativas quer impedir o direito à terra que esses povos têm, seja no Congresso Nacional (PEC 215/2000), seja no judiciário. É o caso do “marco temporal”, argumento usado por alguns juízes para limitar o direito à terra apenas para os povos tradicionais que estivessem vivendo nela em 5 de outubro de 1988. Mas isso ignora que esses povos tradicionais foram expulsos e impedidos de retornar a suas terras.",
    label=u"Marco temporal na demarcação de terra ")
Topic.objects.create(category=cat, description="Nos últimos 30 anos de democracia no Brasil, apenas um representante indígena foi eleito para o Congresso Nacional, apesar dos indígenas serem 0,4% da população brasileira. Para mudar esse cenário, recursos públicos para campanhas ou cadeiras no Congresso poderiam ser reservados a candidaturas de indígenas.",
    label=u"Cotas para indígenas no Congresso")
Topic.objects.create(category=cat, description="O Brasil é campeão mundial no consumo de agrotóxicos, mercado que gira bilhões de dólares todos os anos. Mais da metade dos alimentos consumidos pelos brasileiros está contaminado por agrotóxicos e milhares de pessoas são atendidas pelo SUS com sintomas de intoxicação. O tema está sendo discutido no Congresso (PL 6299/2002), para permitir ainda mais o uso de alimentos com agrotóxicos.",
    label=u"Facilitar uso de agrotóxico")


cat = QuestionCategory.objects.create(name=u"#Trabalho, Saúde e Educação")
Topic.objects.create(category=cat, description="A reforma trabalhista aprovada no atual governo criou algumas formas precárias de contratação, como o contrato intermitente, enfraqueceu os sindicatos ao retirar a contribuição sindical obrigatória, permitiu o trabalho insalubre da mulher gestante e retirou o acesso gratuito do trabalhador à justiça.",
    label=u"Reforma trabalhista")
Topic.objects.create(category=cat, description="O governo atual adotou uma política econômica conhecida por “teto de gastos públicos”, para limitar os gastos públicos federais. Essa política é formada por algumas medidas como: congelamento de gastos sociais com políticas para a saúde, educação e seguro desemprego pelos próximos 20 anos. A ONU condenou tais medidas, por afetarem a população mais pobre. Ainda assim, ela foi aprovada no Congresso Nacional pela Emenda Constitucional 95.",
    label=u"Teto de gastos públicos")



cat = QuestionCategory.objects.create(name=u"#Segurança e Direitos Humanos")
Topic.objects.create(category=cat, description="“Auto de resistência” era o nome dado pela polícia ao homicídio de pessoas que ofereceram “resistência à prisão”. Na prática, significava dizer que esses homicídios eram praticados por policiais em legítima defesa. O problema é que esses casos acabam não sendo investigados e, dos que são, 98% são arquivados. Hoje essa expressão foi proibida, mas outras parecidas, como 'mortes em decorrência de ação policial', continuam sendo usadas pela polícia.",
    label=u"Autos de resistência")
Topic.objects.create(category=cat, description="Nossa Constituição não permite que menores de 18 anos sejam processados e presos como adultos, mas permite que esses adolescentes sejam internados em Fundações Casa. Alguns membros do Congresso Nacional defendem a alteração da Constituição para reduzir a “maioridade penal” (PEC 171/93 e PEC 33/12), ou seja, que possam ser presos como adultos. Como não estão conseguindo, agora tentam outra estratégia: aumentar o tempo que os adolescentes passam internados (PL 7197/02). Estudos comprovam que a redução da maioridade penal em diferentes países não levou à redução da criminalidade.",
    label=u"Redução de maioridade penal")

cat = QuestionCategory.objects.create(name=u"#Corrupção")
Topic.objects.create(category=cat, description="Hoje existem 32 deputados federais e 8 senadores no Congresso Nacional que são donos de emissoras de rádio e TV. Assim eles podem influenciar o que a mídia fala sobre eles. Esses veículos de comunicação são concessões públicas que dependem de autorização do próprio Congresso Nacional, ou seja, dos próprios deputados federais e senadores. Duas ações no Supremo Tribunal Federal questionam se essa situação viola a nossa Constituição (ADPF 246 e ADPF 379).",
    label=u"Políticos serem donos de emissoras de rádio e TV")
Topic.objects.create(category=cat, description="Todos os partidos políticos recebem dinheiro público do chamado “Fundo Partidário”. Nas eleições de 2018, pela primeira vez, também receberão 1,7 bilhão de reais de dinheiro público para financiar suas campanhas eleitorais de um “Fundo Especial de Financiamento de Campanha”. As lideranças dos partidos têm liberdade para escolher como gastar esse dinheiro e não existe um controle da sociedade sobre esses gastos. A obrigação dos partidos divulgarem seus balanços financeiros e prestações de contas pode ajudar na fiscalização da utilização desses recursos públicos pela sociedade.",
    label=u"Transparência nos gastos dos partidos políticos")

cat = QuestionCategory.objects.create(name=u"#Drogas")
Topic.objects.create(category=cat, description="A maconha não seria mais um mercado ilegal se fossem aprovadas leis dizendo como ela deveria ser produzida e vendida, do mesmo jeito que já acontece com outras drogas, como álcool, tabaco e medicamentos. Isso significa que a maconha poderia ser produzida, vendida e utilizada de acordo com o direito. O mercado da maconha seria fiscalizado e não financiaria mais atividades criminosas. A legalização da maconha está sendo discutida no Congresso Nacional (Projetos de Lei 7.270/2014 e 10.549/2018).",
    label=u"Legalização da maconha")
Topic.objects.create(category=cat, description="A internação psiquiátrica compulsória ocorre quando uma pessoa é internada contra a sua vontade. Atualmente, ela pode ocorrer por decisão do Judiciário (sem precisar da autorização da família) em casos extremos, quando o paciente não tem mais controle sobre sua condição psicológica e física. Alguns políticos têm tentado combater o uso de drogas com a internação compulsória coletiva de usuários, ou seja, contra sua vontade e sem avaliação da condição psicológica e física de cada um. É o que ocorre atualmente na cidade de São Paulo, na região da Cracolândia.",
    label=u"Internação compulsória para usuários de drogas")

cat = QuestionCategory.objects.create(name=u"#Migrantes")
Topic.objects.create(category=cat, description="A Venezuela está passando por uma grave crise econômica e humanitária. O Brasil faz fronteira com a Venezuela, mas é um dos países da América do Sul que menos recebe migrantes de lá. Em Roraima, o governo restringiu o acesso de venezuelanos à saúde e o judiciário chegou a fechar as fronteiras para a entrada de novos migrantes. Casos de xenofobia (ódio e preconceito por causa da origem da pessoa) também têm acontecido.",
    label=u"Acolhimento de migrantes venezuelanos no Brasil")

Topic.objects.create(category=cat, description="Cerca de 3 milhões de migrantes residem, trabalham e estudam no Brasil. Porém, eles não podem votar, nem se candidatar. Esse cenário pode mudar caso a nossa Constituição seja alterada e garanta o direito à participação dos migrantes na política do país (PEC 25/2012). Diversos países já garantiram esse direito.",
    label=u"Direito a voto de migrantes")


for t in Topic.objects.all():
    label_yes = u"Sou a <strong>FAVOR</strong> da %s" % t.label
    yes = Position.objects.create(topic=t, label=label_yes)
    label_no = u"Sou <strong>CONTRA</strong> a %s" % t.label
    no = Position.objects.create(topic=t, label=label_no)
