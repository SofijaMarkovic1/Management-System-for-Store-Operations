from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class PripadaKategoriji(database.Model):
    __tablename__ = "pripada_kategoriji"
    id = database.Column(database.Integer, primary_key=True)
    proizvod_id = database.Column(database.Integer, database.ForeignKey('proizvod.id'), nullable=False)
    kategorija_id = database.Column(database.Integer, database.ForeignKey('kategorija_proizvoda.id'), nullable=False)

    def __repr__(self):
        return "({}, {}, {})".format(self.id, self.proizvod_id, self.kategorija_id)

    def __init__(self, proizvod, kategorija):
        self.proizvod_id = proizvod
        self.kategorija_id = kategorija


class KategorijaProizvoda(database.Model):
    __tablename__ = "kategorija_proizvoda"
    id = database.Column(database.Integer, primary_key=True)
    naziv = database.Column(database.String(256), nullable=False)
    proizvodi = database.relationship('PripadaKategoriji', backref='kategorija_proizvoda')

    def __repr__(self):
        return "({}, {})".format(self.id, self.naziv)

    def __init__(self, naziv):
        self.naziv = naziv


class PripadaNarudzbini(database.Model):
    __tablename__ = "pripada_narudzbini"
    id = database.Column(database.Integer, primary_key=True)
    proizvod_id = database.Column(database.Integer, database.ForeignKey('proizvod.id'), nullable=False)
    narudzbina_id = database.Column(database.Integer, database.ForeignKey('narudzbina.id'), nullable=False)
    kolicina = database.Column(database.Integer, nullable=False)
    def __repr__(self):
        return "({}, {}, {})".format(self.id, self.proizvod_id, self.narudzbina_id)


class Proizvod(database.Model):
    __tablename__ = "proizvod"
    id = database.Column(database.Integer, primary_key=True)
    ime = database.Column(database.String(256), nullable=False)
    cena = database.Column(database.REAL, nullable=False)
    kategorije = database.relationship('PripadaKategoriji', backref='proizvod')

    def __repr__(self):
        return "({}, {}, {})".format(self.id, self.ime, self.cena)

    def __init__(self, ime, cena):
        self.ime = ime
        self.cena = cena


class Narudzbina(database.Model):
    __tablename__ = "narudzbina"
    id = database.Column(database.Integer, primary_key=True)
    cena = database.Column(database.REAL, nullable=False)
    status = database.Column(database.Integer, nullable=False)
    datum = database.Column(database.DATETIME, nullable=False)
    porucilac = database.Column(database.String(256), nullable=False)
    ugovor = database.Column(database.String(256), nullable=False)
    proizvodi = database.relationship('PripadaNarudzbini', backref='narudzbina')

    def __repr__(self):
        return "({}, {}, {}, {}, {})".format(self.id, self.cena, self.status, self.datum, self.porucilac)

    def __init__(self, cena, status, datum, porucilac, ugovor):
        self.cena = cena
        self.status = status
        self.datum = datum
        self.porucilac = porucilac
        self.ugovor = ugovor
