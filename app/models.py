from app import db
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression):
        ids, total = query_index(cls.__tablename__, expression)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class Oggetto(SearchableMixin, db.Model):
    __searchable__ = ['object_name', 'object_notes']
    id = db.Column(db.Integer, primary_key=True)
    object_name = db.Column(db.String(64), index=True, unique=True)
    object_notes = db.Column(db.String(300), index=True, unique=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    def __repr__(self):
        return "<Oggetto: {}>".format(self.object_name)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(64), index=True, unique=True)
    objects = db.relationship('Oggetto', backref='objects', lazy='dynamic')

    def __repr__(self):
        # This representation is so simple because we use this string to print all possible location
        # options in the add_location form
        return "{}".format(self.location_name)
