import datetime
import json
from flask import Blueprint, request, Response
from models import database, Proizvod, KategorijaProizvoda, Narudzbina, PripadaNarudzbini, PripadaKategoriji
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from web3 import Web3, HTTPProvider, Account

kupacBlueprint = Blueprint("kupac", __name__)


def vratiProizvod(kolicina, idProizvoda):
    proizvod = Proizvod.query.get(idProizvoda)
    kat = []
    for c in proizvod.kategorije:
        kateg = KategorijaProizvoda.query.get(c.kategorija_id)
        kat.append(kateg.naziv)
    p = {
        "categories": kat,
        "name": proizvod.ime,
        "price": proizvod.cena,
        "quantity": kolicina
    }
    return p


def read_file(path):
    with open(path, "r") as file:
        return file.read()


@kupacBlueprint.route('/search', methods=["GET"])
@jwt_required()
def pretraga():
    """if get_jwt().get("roles")[0] != "customer":
        message = {
            "msg": "Missing Authorization Header"
        }
        return Response(json.dumps(message), 401)
    product_name = request.args.get('name')
    category_name = request.args.get('category')
    if product_name is None:
        product_name = ""
    if category_name is None:
        category_name = ""
    proizvodi = Proizvod.query.all()
    proizvodi_rez = []
    kategorije_rez = []
    nazivi_kategorija = []
    for p in proizvodi:
        if p.ime.find(product_name) != -1:
            flag = False
            nazivi_kat = []
            for k in p.kategorije:
                kat = KategorijaProizvoda.query.get(k.kategorija_id)
                if kat.naziv.find(category_name) != -1:
                    flag = True
                    if kat.naziv not in nazivi_kategorija:
                        nazivi_kategorija.append(kat.naziv)
                nazivi_kat.append(kat.naziv)
            if flag:
                proizvod = {
                    "categories": nazivi_kat,
                    "id": p.id,
                    "name": p.ime,
                    "price": p.cena
                }
                proizvodi_rez.append(proizvod)
            flag = False
    if len(nazivi_kategorija) == 0 or len(proizvodi_rez) == 0:
        Response(None, status=200)
    rezultat = {
        "categories": nazivi_kategorija,
        "products": proizvodi_rez
    }
    return Response(json.dumps(rezultat), status=200)"""
    if get_jwt().get("roles")[0] != "customer":
        message = {
            "msg": "Missing Authorization Header"
        }
        return Response(json.dumps(message), 401)

    product_name = request.args.get('name', '')
    category_name = request.args.get('category', '')

    #proizvodi = Proizvod.query.filter(Proizvod.ime.like(f"%{product_name}%"))
    #if category_name != '':
    proizvodi = Proizvod.query.join(PripadaKategoriji, Proizvod.id == PripadaKategoriji.proizvod_id).join(
        KategorijaProizvoda, PripadaKategoriji.kategorija_id == KategorijaProizvoda.id).filter(Proizvod.ime.like(f"%{product_name}%"), KategorijaProizvoda.naziv.like(f"%{category_name}%"))

    proizvodi_rez = []
    nazivi_kategorija = []

    for p in proizvodi:
        kategorije = [KategorijaProizvoda.query.get(k.kategorija_id) for k in p.kategorije]
        nazivi_kat = [k.naziv for k in kategorije]
        nazivi_kategorija.extend(nazivi_kat)
        proizvod = {
            "categories": nazivi_kat,
            "id": p.id,
            "name": p.ime,
            "price": p.cena
        }
        proizvodi_rez.append(proizvod)

    nazivi_kategorija = list(set(nazivi_kategorija))  # Remove duplicate categories


    rezultat = {
        "categories": nazivi_kategorija,
        "products": proizvodi_rez
    }
    return Response(json.dumps(rezultat), status=200)


@kupacBlueprint.route('/order', methods=["POST"])
@jwt_required()
def naruci():
    if get_jwt().get("roles")[0] != "customer":
        message = {
            "msg": "Missing Authorization Header"
        }
        return Response(json.dumps(message), 401)
    requests = request.json.get("requests", None)
    if requests is None:
        message = {
            "message": "Field requests is missing."
        }
        return Response(json.dumps(message), 400)
    i = 0
    ids = []
    quantities = []
    cena = 0
    for req in requests:
        id = -1
        quantity = -1
        try:
            id = req["id"]
        except KeyError:
            message = {
                "message": "Product id is missing for request number " + str(i) + "."
            }
            return Response(json.dumps(message), 400)
        try:
            quantity = req["quantity"]
        except KeyError:
            message = {
                "message": "Product quantity is missing for request number " + str(i) + "."
            }
            return Response(json.dumps(message), 400)
        if not isinstance(id, int) or id <= 0:
            message = {
                "message": "Invalid product id for request number " + str(i) + "."
            }
            return Response(json.dumps(message), 400)
        if not isinstance(quantity, int) or quantity <= 0:
            message = {
                "message": "Invalid product quantity for request number " + str(i) + "."
            }
            return Response(json.dumps(message), 400)
        p = Proizvod.query.get(id)
        if p is None:
            message = {
                "message": "Invalid product for request number " + str(i) + "."
            }
            return Response(json.dumps(message), 400)
        ids.append(id)
        quantities.append(quantity)
        cena += p.cena * quantity
        i += 1

    address = request.json.get("address", None)
    if address is None or len(address) == 0:
        message = {
            "message": "Field address is missing."
        }
        return Response(json.dumps(message), 400)
    if not Web3.is_address(address):
        message = {
            "message": "Invalid address."
        }
        return Response(json.dumps(message), 400)
    # blockchain
    web3 = Web3(HTTPProvider("http://blockchain:8545"))
    bytecode = read_file("solidity/output/PaymentContract.bin")
    abi = read_file("solidity/output/PaymentContract.abi")
    contract = web3.eth.contract(bytecode=bytecode, abi=abi)
    transaction_hash = contract.constructor(address).transact({
        "from": web3.eth.accounts[0],
        "nonce": web3.eth.get_transaction_count(web3.eth.accounts[0]),
        "gasPrice": web3.eth.gas_price
    })
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    contractAddress = receipt.contractAddress

    n = Narudzbina(cena, 0, datetime.datetime.now(), get_jwt_identity(), contractAddress)
    database.session.add(n)
    database.session.commit()
    print(len(ids))
    for i in range(0, len(ids)):
        x = PripadaNarudzbini(n.id, ids[i], quantities[i])
        database.session.add(x)
        database.session.commit()
    message = {
        "id": n.id
    }
    return Response(json.dumps(message), 200)


@kupacBlueprint.route('/status', methods=["GET"])
@jwt_required()
def dohvatiNarudzbine():
    if get_jwt().get("roles")[0] != "customer":
        message = {
            "msg": "Missing Authorization Header"
        }
        return Response(json.dumps(message), 401)
    narudzbine = Narudzbina.query.filter(Narudzbina.porucilac == get_jwt_identity())
    rezultat = []
    for narudzbina in narudzbine:
        products = []
        for p in narudzbina.proizvodi:
            products.append(vratiProizvod(p.kolicina, p.proizvod_id))
        status = ""
        if narudzbina.status == 0:
            status = "CREATED"
        elif narudzbina.status == 1:
            status = "PENDING"
        elif narudzbina.status == 2:
            status = "COMPLETE"

        d = narudzbina.datum
        rounded_seconds = round(d.second)
        datum = narudzbina.datum.replace(second=int(rounded_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")

        n = {
            "products": products,
            "price": narudzbina.cena,
            "status": status,
            "timestamp": datum
        }
        rezultat.append(n)
    message = {
        "orders": rezultat
    }
    return Response(json.dumps(message), 200)


@kupacBlueprint.route('/delivered', methods=["POST"])
@jwt_required()
def dostavljeno():
    if get_jwt().get("roles")[0] != "customer":
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
    if narudzbina is None or narudzbina.status != 1:
        message = {
            "message": "Invalid order id."
        }
        return Response(json.dumps(message), 400)
    keys = request.json.get("keys", None)
    if keys is None or len(keys) == 0:
        message = {
            "message": "Missing keys."
        }
        return Response(json.dumps(message), 400)
    keys = keys.replace("'", '"')
    passphrase = request.json.get("passphrase", None)
    if passphrase is None or len(passphrase) == 0:
        message = {
            "message": "Missing passphrase."
        }
        return Response(json.dumps(message), 400)
    web3 = Web3(HTTPProvider("http://blockchain:8545"))
    bytecode = read_file("solidity/output/PaymentContract.bin")
    abi = read_file("solidity/output/PaymentContract.abi")
    try:
        keys = json.loads(keys)
        address = web3.to_checksum_address(keys["address"])
        private_key = Account.decrypt(keys, passphrase).hex()
    except ValueError:
        message = {
            "message": "Invalid credentials."
        }
        return Response(json.dumps(message), 400)
    contract = web3.eth.contract(address=narudzbina.ugovor, abi=abi)
    if address != contract.functions.getCustomer().call():
        message = {
            "message": "Invalid customer account."
        }
        return Response(json.dumps(message), 400)
    if contract.functions.getValue().call() == 0:
        message = {
            "message": "Transfer not complete."
        }
        return Response(json.dumps(message), 400)
    if narudzbina.status != 1:
        message = {
            "message": "Delivery not complete."
        }
        return Response(json.dumps(message), 400)
    narudzbina.status = 2
    database.session.add(narudzbina)
    database.session.commit()
    transaction = contract.functions.payout().build_transaction({
        "from": address,
        "nonce": web3.eth.get_transaction_count(address),
        "gasPrice": web3.eth.gas_price
    })
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    return Response(status=200)


@kupacBlueprint.route('/pay', methods=["POST"])
@jwt_required()
def placanje():
    if get_jwt().get("roles")[0] != "customer":
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
    # or narudzbina.status != 1
    if narudzbina is None:
        message = {
            "message": "Invalid order id."
        }
        return Response(json.dumps(message), 400)
    keys = request.json.get("keys", None)
    if keys is None or len(keys) == 0:
        message = {
            "message": "Missing keys."
        }
        return Response(json.dumps(message), 400)
    keys = keys.replace("'", '"')
    passphrase = request.json.get("passphrase", None)
    if passphrase is None or len(passphrase) == 0:
        message = {
            "message": "Missing passphrase."
        }
        return Response(json.dumps(message), 400)
    web3 = Web3(HTTPProvider("http://blockchain:8545"))
    bytecode = read_file("solidity/output/PaymentContract.bin")
    abi = read_file("solidity/output/PaymentContract.abi")
    try:
        keys = json.loads(keys)
        address = web3.to_checksum_address(keys["address"])
        private_key = Account.decrypt(keys, passphrase).hex()
    except (ValueError, json.decoder.JSONDecodeError):
        message = {
            "message": "Invalid credentials."
        }
        return Response(json.dumps(message), 400)
    if web3.eth.get_balance(address) < narudzbina.cena:
        message = {
            "message": "Insufficient funds."
        }
        return Response(json.dumps(message), 400)
    contract = web3.eth.contract(address=narudzbina.ugovor, abi=abi)
    if contract.functions.getValue().call() > 0:
        message = {
            "message": "Transfer already complete."
        }
        return Response(json.dumps(message), 400)
    transaction = contract.functions.sendMoney().build_transaction({
        "from": address,
        "nonce": web3.eth.get_transaction_count(address),
        "gasPrice": web3.eth.gas_price,
        "value": int(narudzbina.cena)
    })
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    return Response(status=200)
