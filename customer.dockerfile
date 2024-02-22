FROM python:3

RUN mkdir -p /opt/src/customer
WORKDIR /opt/src/customer

COPY customer/application.py ./application.py
COPY customer/configuration.py ./configuration.py
COPY customer/kupac.py ./kupac.py
COPY customer/models.py ./models.py
COPY customer/requirements.txt ./requirements.txt
COPY blockchain/solidity ./solidity

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]