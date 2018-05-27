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
    state = db.StringField(db_field='s')
    zip = db.StringField(db_field='z')
    phone = db.StringField(db_field='p')

    meta = {
        'indexes': [('external_id')]
    }
