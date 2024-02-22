FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY owner/migrate.py ./migrate.py
COPY owner/configuration.py ./configuration.py
COPY owner/models.py ./models.py
COPY owner/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]