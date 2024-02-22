from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class Korisnik(database.Model):
    __tablename__ = "korisnik"
    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(256), nullable=False)
    sifra = database.Column(database.String(256), nullable=False)
    ime = database.Column(database.String(256), nullable=False)
    prezime = database.Column(database.String(256), nullable=False)
    uloga = database.Column(database.Integer, nullable=False)

    def __init__(self, email, sifra, ime, prezime, uloga):
        self.email = email
        self.sifra = sifra
        self.ime = ime
        self.prezime = prezime
        self.uloga = uloga

    def __repr__(self):
        return "({}, {}, {}, {}, {}, {})".format(self.id, self.email, self.sifra, self.ime, self.prezime, self.uloga)


