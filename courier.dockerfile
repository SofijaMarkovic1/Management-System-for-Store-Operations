FROM python:3

RUN mkdir -p /opt/src/courier
WORKDIR /opt/src/customer

COPY courier/application.py ./application.py
COPY courier/configuration.py ./configuration.py
COPY courier/kurir.py ./kurir.py
COPY courier/models.py ./models.py
COPY courier/requirements.txt ./requirements.txt
COPY blockchain/solidity ./solidity

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]