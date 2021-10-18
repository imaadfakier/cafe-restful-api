from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random as random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route('/random', methods=['GET', ])
def random_cafe():
    all_db_cafes = db.session.query(Cafe).all()
    random_db_cafe = random.choice(seq=all_db_cafes)
    random_db_dict = random_db_cafe.__dict__
    print(random_db_dict)
    print(type(random_db_dict))
    del random_db_dict['_sa_instance_state']
    return jsonify(cafe=random_db_dict)


@app.route('/all', methods=['GET', ])
def all_cafes():
    all_db_cafes_as_dicts = []
    all_db_cafes = db.session.query(Cafe).all()
    for db_cafe in all_db_cafes:
        db_cafe_dict = db_cafe.__dict__
        db_cafe_dict.pop('_sa_instance_state', None)
        all_db_cafes_as_dicts.append(db_cafe_dict)
    return jsonify(cafes=all_db_cafes_as_dicts)


@app.route(rule='/search', methods=['GET', ])
def search_for_cafe():
    cafe_location_search = request.args.get('loc')
    location_cafe_results = []
    cafes_at_location = db.session.query(Cafe).filter(Cafe.location == cafe_location_search).all()
    if cafes_at_location:
        for cafe_at_location in cafes_at_location:
            cafe_at_location_dict = vars(cafe_at_location)
            del cafe_at_location_dict['_sa_instance_state']
            location_cafe_results.append(cafe_at_location_dict)
    else:
        location_cafe_results = {
            'Not Found': 'Sorry, we don\'t have a cafe at that location.',
        }
        return jsonify(error=location_cafe_results)
    return jsonify(cafes=location_cafe_results)


# HTTP POST - Create Record
@app.route('/add', methods=['POST', ])
def add_new_cafe():
    new_cafe_to_add = Cafe(
        name=request.form.get('name'),
        map_url=request.form.get('map_url'),
        img_url=request.form.get('img_url'),
        location=request.form.get('loc'),
        has_sockets=bool(request.form.get('sockets')),
        has_toilet=bool(request.form.get('toilet')),
        has_wifi=bool(request.form.get('wifi')),
        can_take_calls=bool(request.form.get('calls')),
        seats=request.form.get('seats'),
        coffee_price=request.form.get('coffee_price'),
    )
    db.session.add(new_cafe_to_add)
    db.session.commit()
    return jsonify(response={
        'success': 'Successfully added the new cafe.'
    })


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<string:cafe_id>', methods=['PATCH', ])
def update_coffee_price(cafe_id):
    new_coffee_price = request.args.get('new_price')
    cafe_to_update = Cafe.query.get(cafe_id)
    if not cafe_to_update:
        return jsonify(error={
            'Not Found': 'Sorry a cafe with that id was not found in the database.'
        }), 404
    cafe_to_update.coffee_price = new_coffee_price
    db.session.commit()
    return jsonify(success='Successfully updated the price.')


# HTTP DELETE - Delete Record
@app.route('/report-closed/<string:cafe_id>')
def delete_cafe(cafe_id):
    secret_api_key = request.args.get(key='api-key')
    if secret_api_key:
        if secret_api_key == 'TopSecretAPIKey':
            cafe_to_delete = Cafe.query.get(cafe_id)
            if cafe_to_delete:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                return jsonify(success='Cafe successfully deleted.'), 200
            return jsonify(error={
                'Not Found': 'Sorry a cafe with that id was not found in the database.'
            }), 404
        else:
            return jsonify(error={
                'error': 'Sorry, that\'s not allowed. Make sure you have the correct API key.'
            }), 403
    else:
        return jsonify(error={
            'error': 'Sorry, that\'s not allowed. Make sure you have provided your secret API key.'
        }), 403


if __name__ == '__main__':
    app.run(debug=True)
