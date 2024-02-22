FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY owner/application.py ./application.py
COPY owner/configuration.py ./configuration.py
COPY owner/vlasnik.py ./vlasnik.py
COPY owner/models.py ./models.py
COPY owner/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]