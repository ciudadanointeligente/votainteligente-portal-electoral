SCRIPTS PARA CHILE 2017
========================
Estos son scripts de carga, modificación de datos para la elección parlamentaria y presidencial de Chile:

* areas.yaml: 
Tiene las municipalidades de Chile en formato de popolo y se peude cargar como ```./manage.py loaddata areas.yaml```

* circunscripciones_y_otros.csv:
Tiene las Circunscripciones, distritos y municipalidades de Chile

* collector.py:
Es un script que va al servel.cl y obtiene quienes fueron los ganadoresde la elección. Se corre con un simple ```python collector.py```

* division_electoral_chile.csv: 
División electoral d eChile, honestamente no tengo callampa idea por qué sería mejor que el archivo ```circunscripciones_y_otros.csv```


* division_electoral_chile.yaml: 
Lo mismo de arriba pero en otro formato

* division_electoral_chile.yml:
Lo mismo de arriba pero con otra extensión, creo que a veces el ```pyhthon manage.py loaddata division_electoral_chile.yml``` funcionaba con una extensión y con otra no.


* load_lupa.py:
Script que le asignaba a cada candidato un link donde se podría ver los gastos electorales de lupaelectoral.cl, un proyecto de espacio publico.

* load_photo_into_disk.py:
Creo que este script toma desde el campo image de cada candidato la url y la obtiene, guardandola localmente para luego ser accesada. (Esto es importante por que cuando una url no podía ser accesada con una foto, la página de ese candidato se moría terriblemente).

* nuevas_preguntas_12naranja.csv:
Este archivo le trae las preguntas y respuestas de la media naranja electoral para la primera vuelta electoral, pero eran preguntas nuevas.

* preguntas_media_naranja_2017.csv:
Este archivo le trae las preguntas y respuestas de la media naranja electoral para la primera vuelta electoral.

* preguntas_media_naranja_segunda_vuelta_2017.csv
Este archivo le trae las preguntas y respuestas de la media naranja electoral para la primera vuelta electoral.

* preguntas_media_naranja.yaml:
Le traelas preguntas para las elecciones municipales del 2016. (Laspreguntas eran medias malenas y además las respuestas eran gigantescas).

* stats_compromisos_por_eleccion.py: 
Script que imprime en pantalla la cantidad de compromisos por elección, la gracia era llenar un google spreadsheet con esta info.
* stats_compromisos_por_pacto.py:
Script que imprime en pantalla la cantidad de compromisos por pacto, la gracia era llenar un google spreadsheet con esta info.
* stats_per_pacto.py:
Script que imprime en pantalla las propuestas aceptadas por pacto(no la cantidad), la gracia era llenar un google spreadsheet con esta info.

* stats_pp_por_regiones.py:
Script que imprime en pantalla las propuestas ciudadanas que venían por cada una de las regiones, la gracia era llenar un google spreadsheet con esta info.

* stats_propuestas_con_compromisos.py:
Script que imprime en pantalla las propuestas ciudadanas y sus compromisos, la gracia era llenar un google spreadsheet con esta info.

* importer.py
Tiene muchas funcioncitas escritas para cargar datos que están arriba.
