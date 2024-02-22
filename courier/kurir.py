import json
from flask import Blueprint, request, Response
from models import database, Narudzbina
from flask_jwt_extended import jwt_required, get_jwt
from web3 import Web3, HTTPProvider
kurirBlueprint = Blueprint("kurir", __name__)


def read_file(path):
    with open(path, "r") as file:
        return file.read()


@kurirBlueprint.route("/orders_to_deliver", methods=["GET"])
@jwt_required()
def narudzbine_za_dostavu():
    if get_jwt().get("roles")[0] != "courier":
        message = {
                "msg": "Missing Authorization Header"
                }
        return Response(json.dumps(message), 401)
    rezultat = []
    narudzbine = Narudzbina.query.filter(Narudzbina.status == 0)
    for n in narudzbine:
        x = {
            "id": n.id,
            "email": n.porucilac
        }
        rezultat.append(x)
    message = {
        "orders": rezultat
    }
    return Response(json.dumps(message), status=200)


@kurirBlueprint.route("/pick_up_order", methods=["POST"])
@jwt_required()
def preuzmi():
    if get_jwt().get("roles")[0] != "courier":
        message = {
                "msg": "Missing Authorization Header"
                }
        return Response(json.dumps(message), 401)
    id = request.json.get("id", None)
    if id is None:
        message = {
                    "message": "Missing order id."
                }
        return Response(json.dumps(message), 400)
    if not isinstance(id, int) or id <= 0:
        message = {
            "message": "Invalid order id."
        }
        return Response(json.dumps(message), 400)
    narudzbina = Narudzbina.query.get(id)
    if narudzbina is None or narudzbina.status != 0:
        message = {
            "message": "Invalid order id."
        }
        return Response(json.dumps(message), 400)
    address = request.json.get("address", None)
    if address is None or len(address) == 0:
        message = {
            "message": "Missing address."
        }
        return Response(json.dumps(message), 400)
    if not Web3.is_address(address):
        message = {
            "message": "Invalid address."
        }
        return Response(json.dumps(message), 400)
    web3 = Web3(HTTPProvider("http://blockchain:8545"))
    bytecode = read_file("solidity/output/PaymentContract.bin")
    abi = read_file("solidity/output/PaymentContract.abi")
    contract = web3.eth.contract(address=narudzbina.ugovor, abi=abi)
    if contract.functions.getValue().call() == 0:
        message = {
            "message": "Transfer not complete."
        }
        return Response(json.dumps(message), 400)
    narudzbina.status = 1
    database.session.add(narudzbina)
    database.session.commit()
    contract.functions.setCourier(address).transact({
        "from": web3.eth.accounts[0],
        "nonce": web3.eth.get_transaction_count(web3.eth.accounts[0]),
        "gasPrice": web3.eth.gas_price
    })
    return Response(status=200)