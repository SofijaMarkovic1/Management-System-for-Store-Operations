import codecs
import csv
import json
from flask import Blueprint, request, Response
from models import database, Proizvod, KategorijaProizvoda, PripadaKategoriji
from flask_jwt_extended import jwt_required, get_jwt
import requests

vlasnikBlueprint = Blueprint("vlasnik", __name__)


@vlasnikBlueprint.route('/update', methods=["POST"])
@jwt_required()
def kreirajProizvod():
    if get_jwt().get("roles")[0] != "owner":
        message = {
            "msg": "Missing Authorization Header"
        }
        return Response(json.dumps(message), 401)

    if 'file' not in request.files:
        message = {
            "message": "Field file is missing."
        }
        return Response(json.dumps(message), 400)

    file = request.files['file']
    i = 0
    names = []
    categories = []
    prices = []
    if file:
        file_text = codecs.iterdecode(file, 'latin1')

        csv_reader = csv.reader(file_text)

        for row in csv_reader:
            print(row)

            if len(row) < 3:
                message = {
                    "message": "Incorrect number of values on line " + str(i) + "."
                }
                return Response(json.dumps(message), 400)

            k = row[0].split('|')

            categories.append(k)

            p = row[2]
            try:
                p = float(p)
                if p <= 0:
                    message = {
                        "message": "Incorrect price on line " + str(i) + "."
                    }
                    return Response(json.dumps(message), 400)
                prices.append(p)
            except ValueError:
                message = {
                    "message": "Incorrect price on line " + str(i) + "."
                }
                return Response(json.dumps(message), 400)

            n = row[1]
            if n in names or Proizvod.query.filter(Proizvod.ime == n).first() is not None:
                message = {
                    "message": "Product " + n + " already exists."
                }
                return Response(json.dumps(message), 400)

            names.append(n)
            i += 1

        for i in range(0, len(categories)):
            kategorije = []
            for x in categories[i]:
                y = KategorijaProizvoda.query.filter(KategorijaProizvoda.naziv == x).first()
                if y is None:
                    k = KategorijaProizvoda(x)
                    database.session.add(k)
                    database.session.commit()
                    kategorije.append(k)
                else:
                    kategorije.append(y)
            cena = prices[i]
            ime = names[i]
            p = Proizvod(ime, cena)
            database.session.add(p)
            database.session.commit()
            for k in kategorije:
                pk = PripadaKategoriji(p.id, k.id)
                database.session.add(pk)
                database.session.commit()
        return Response(None, status=200)
    else:
        message = {
            "message": "Field file missing."
        }
        return Response(json.dumps(message), 400)


@vlasnikBlueprint.route('/product_statistics', methods=["get"])
@jwt_required()
def product_statistics():
    if get_jwt().get("roles")[0] != "owner":
        message = {
            "msg": "Missing Authorization Header"
        }
        return Response(json.dumps(message), 401)
    url = "http://sparkapp:5006/database"
    response = requests.get(url)
    return response.json()


@vlasnikBlueprint.route('/category_statistics', methods=["get"])
@jwt_required()
def category_statistics():
    if get_jwt().get("roles")[0] != "owner":
        message = {
            "msg": "Missing Authorization Header"
        }
        return Response(json.dumps(message), 401)
    url = "http://sparkapp:5006/database1"
    response = requests.get(url)
    return response.json()
