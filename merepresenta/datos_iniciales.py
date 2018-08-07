QuestionCategory.objects.all().delete()
Topic.objects.all().delete()
Position.objects.all().delete()
cat = QuestionCategory.objects.create(name=u"#Gênero")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Legalização do aborto")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Pergunta sobre violência de gênero")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Paridade de gênero e raça nos cargos públicos ( ou cota de 50%)")

cat = QuestionCategory.objects.create(name=u"#Raça")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Criminalização do sacrifício de animais em rituais de matriz africana")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Cotas raciais nas universidades")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Prioridade de acesso de mulheres negras a exames de mamografia")

cat = QuestionCategory.objects.create(name=u"#LGBTs")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Discriminar LGBTs deve ser crime")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Trans e travestis poderem usar o banheiro que quiser")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Projeto “Escola sem partido”")

cat = QuestionCategory.objects.create(name=u"#Povos tradicionais")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Marco temporal")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Guarda florestal indígena")

cat = QuestionCategory.objects.create(name=u"#Direitos sociais")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Reforma trabalhista")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Teto de gastos públicos")



cat = QuestionCategory.objects.create(name=u"#Segurança")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Autos de resistência")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Redução de maioridade penal ")

cat = QuestionCategory.objects.create(name=u"#Corrupção")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Políticos serem donos de emissoras de rádio e TV")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Transparência nos gastos dos partidos políticos")

cat = QuestionCategory.objects.create(name=u"#Drogas")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Legalização da maconha")

cat = QuestionCategory.objects.create(name=u"#Migrantes")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Acesso de migrantes venezuelanos")
Topic.objects.create(category=cat, description="In publishing and graphic design, lorem ipsum is a placeholder text commonly used<br/>to demonstrate the visual form of a document without<br />relying on meaningful content. Replacing the actual content with placeholder text allows designers to design the form of the content before the content itself has been produced.", label=u"Direito a voto de migrantes")


for t in Topic.objects.all():
    label_yes = u"Sou a <strong>FAVOR</strong> da %s" % t.label
    yes = Position.objects.create(topic=t, label=label_yes)
    label_no = u"Sou <strong>CONTRA</strong> a %s" % t.label
    no = Position.objects.create(topic=t, label=label_no)
