from flask import Flask
from flask_sqlalchemy import SQLAlchemy


builtin_list = list


db = SQLAlchemy()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data


class Layer(db.Model):
    __tablename__ = 'layers'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    # author = db.Column(db.String(255))
    # publishedDate = db.Column(db.String(255))
    # imageUrl = db.Column(db.String(255))
    description = db.Column(db.String(4096))
    createdBy = db.Column(db.String(255))
    groupFilter = db.Column(db.String(255))
    stateFilter = db.Column(db.String(255))
    createdById = db.Column(db.String(255))

    def __repr__(self):
        return "<Layer(title='%s', author=%s)" % (self.title, self.author)


def list(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (Layer.query
             .order_by(Layer.title)
             .limit(limit)
             .offset(cursor))
    layers = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(layers) == limit else None
    return (layers, next_page)


def read(id):
    result = Layer.query.get(id)
    if not result:
        return None
    return from_sql(result)


def create(data):
    layer = Layer(**data)
    db.session.add(layer)
    db.session.commit()
    return from_sql(layer)


def update(data, id):
    layer = Layer.query.get(id)
    for k, v in data.items():
        setattr(layer, k, v)
    db.session.commit()
    return from_sql(layer)


def delete(id):
    Layer.query.filter_by(id=id).delete()
    db.session.commit()


def _create_database():
    """
    If this script is run directly, create all the tables necessary to run the
    application.
    """
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")


if __name__ == '__main__':
    _create_database()
