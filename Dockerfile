FROM python:2.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /vota
WORKDIR /vota
# ADD requirements.txt /vota/
ADD . /vota/
RUN pip install -r requirements.txt
CMD python manage.py compilescss && python manage.py runserver
