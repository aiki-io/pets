from app import db


class App(db.Document):
    app_id = db.StringField(db_field='ai', unique=True)
    app_secret = db.StringField(db_field='as')
    meta = {
        'indexes': [('app_id')]
    }


class Access(db.Document):
    app = db.ReferenceField(App, db_field='a')
    token = db.StringField(db_field='t')
    expires = db.DateTimeField(db_field='e')


class Store(db.Document):
    external_id = db.StringField(db_field='ei')
    neighborhood = db.StringField(db_field='n')
    street_adress = db.StringField(db_field='sa')
    city = db.StringField(db_field='c')
    state = db.StringField(db_field='st')
    zip = db.StringField(db_field='z')
    phone = db.StringField(db_field='p')
    live = db.BooleanField(db_field='l', default=True)

    meta = {
        'indexes': [('external_id', 'live')]
    }


class Pet(db.Document):
    external_id = db.StringField(db_field='ei')
    name = db.StringField(db_field='n')
    species = db.StringField(db_field='s')
    breed = db.StringField(db_field='b')
    age = db.IntField(db_field='a')
    store = db.ReferenceField(Store, db_field='st')
    price = db.DecimalField(
        db_field='p',
        precision=2,
        rounding='ROUND_HALF_UP'
    )
    sold = db.BooleanField(db_field='sl', default=False)
    received_date = db.DateTimeField(db_field='rd')
    sold_date = db.DateTimeField(db_field='sd')
    live = db.BooleanField(db_field='l', default=True)

    meta = {
        'indexes': [
            ('external_id', 'live'),
            ('species', 'breed',  'live'),
            ('store', 'live')
        ]
    }
