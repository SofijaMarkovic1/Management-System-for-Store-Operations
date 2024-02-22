import json
import re
from flask import Blueprint, request, Response
from models import Korisnik, database
from sqlalchemy import and_
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

korisnikBlueprint = Blueprint("korisnik", __name__)


@korisnikBlueprint.route('/index', methods=["GET"])
def korisnici():
    return str(Korisnik.query.all())


@korisnikBlueprint.route('/register_customer', methods=["POST"])
def registracijaKupca():
    email = request.json.get("email", "")
    sifra = request.json.get("password", "")
    ime = request.json.get("forename", "")
    prezime = request.json.get("surname", "")
    uloga = 1

    # provere
    if len(ime) == 0:
        message = {
            "message": "Field forename is missing."
        }
        return Response(json.dumps(message), status=400)
    if len(prezime) == 0:
        message = {
            "message": "Field surname is missing."
        }
        return Response(json.dumps(message), 400)
    if len(email) == 0:
        message = {
            "message": "Field email is missing."
        }
        return Response(json.dumps(message), 400)
    if len(sifra) == 0:
        message = {
            "message": "Field password is missing."
        }
        return Response(json.dumps(message), 400)
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{3,}$'
    if not re.match(pattern, email):
        message = {
            "message": "Invalid email."
        }
        return Response(json.dumps(message), 400)
    if len(sifra) < 8:
        message = {
            "message": "Invalid password."
        }
        return Response(json.dumps(message), 400)
    if Korisnik.query.filter(Korisnik.email == email).first() is not None:
        message = {
            "message": "Email already exists."
        }
        return Response(json.dumps(message), 400)
    kupac = Korisnik(email=email, sifra=sifra, ime=ime, prezime=prezime, uloga=uloga)
    database.session.add(kupac)
    database.session.commit()
    return Response(None, status=200)


@korisnikBlueprint.route('/register_courier', methods=["POST"])
def registracijaKurira():
    email = request.json.get("email", "")
    sifra = request.json.get("password", "")
    ime = request.json.get("forename", "")
    prezime = request.json.get("surname", "")
    uloga = 2

    # provere
    if len(ime) == 0:
        message = {
            "message": "Field forename is missing."
        }
        return Response(json.dumps(message), status=400)
    if len(prezime) == 0:
        message = {
            "message": "Field surname is missing."
        }
        return Response(json.dumps(message), 400)
    if len(email) == 0:
        message = {
            "message": "Field email is missing."
        }
        return Response(json.dumps(message), 400)
    if len(sifra) == 0:
        message = {
            "message": "Field password is missing."
        }
        return Response(json.dumps(message), 400)
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{3,}$'
    if not re.match(pattern, email):
        message = {
            "message": "Invalid email."
        }
        return Response(json.dumps(message), 400)
    if len(sifra) < 8:
        message = {
            "message": "Invalid password."
        }
        return Response(json.dumps(message), 400)
    if Korisnik.query.filter_by(email=email).first() is not None:
        message = {
            "message": "Email already exists."
        }
        return Response(json.dumps(message), 400)
    kupac = Korisnik(email=email, sifra=sifra, ime=ime, prezime=prezime, uloga=uloga)
    database.session.add(kupac)
    database.session.commit()
    return Response(None, status=200)


@korisnikBlueprint.route('/login', methods=["POST"])
def login():
    email = request.json.get("email", "")
    sifra = request.json.get("password", "")

    # provere
    if len(email) == 0:
        message = {
            "message": "Field email is missing."
        }
        return Response(json.dumps(message), 400)
    if len(sifra) == 0:
        message = {
            "message": "Field password is missing."
        }
        return Response(json.dumps(message), 400)
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{3,}$'
    if not re.match(pattern, email):
        message = {
            "message": "Invalid email."
        }
        return Response(json.dumps(message), 400)
    korisnik = Korisnik.query.filter(and_(Korisnik.email == email, Korisnik.sifra == sifra)).first()
    if korisnik is None:
        message = {
            "message": "Invalid credentials."
        }
        return Response(json.dumps(message), 400)
    role = ""
    if korisnik.uloga == 0:
        role = "owner"
    elif korisnik.uloga == 1:
        role = "customer"
    else:
        role = "courier"
    aditionalClaims = {
        "forename": korisnik.ime,
        "surname": korisnik.prezime,
        "email": korisnik.email,
        "password": korisnik.sifra,
        "roles": [role]
    }
    accessToken = create_access_token(identity=korisnik.email, additional_claims=aditionalClaims)
    message = {
        "accessToken": accessToken
    }
    return Response(json.dumps(message), 200)


@korisnikBlueprint.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    email = get_jwt_identity()
    korisnik = Korisnik.query.filter(Korisnik.email == email).first()
    if korisnik is None:
        message = {
            "message": "Unknown user."
        }
        return Response(json.dumps(message), 400)
    database.session.delete(korisnik)
    database.session.commit()
    return Response(status=200)
