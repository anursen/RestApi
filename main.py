from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=True)
    has_toilet = db.Column(db.Boolean, nullable=True)
    has_wifi = db.Column(db.Boolean, nullable=True)
    has_sockets = db.Column(db.Boolean, nullable=True)
    can_take_calls = db.Column(db.Boolean, nullable=True)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route('/index')
@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(random_cafe.to_dict())


@app.route("/all")
def get_all_cafe():
    cafes = db.session.query(Cafe).all()
    # Simply convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafes=[i.to_dict() for i in cafes])


@app.route("/search")
def search():
    location = request.args.get('loc')
    result = Cafe.query.filter_by(location=location).all()
    if result:
        return ([i.to_dict() for i in result])
    else:
        return jsonify(error={'Not Found': 'Can"t find a match to your location'})

## HTTP POST - Create Record
@app.route('/add/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        new_cafe = Cafe(
            name=request.args.get("name"),
            map_url=request.args.get("map_url"),
            img_url=request.args.get("img_url"),
            location=request.args.get("location"),
            has_sockets=bool(request.args.get("has_sockets")),
            has_toilet=bool(request.args.get("has_toilet")),
            has_wifi=bool(request.args.get("has_wifi")),
            can_take_calls=bool(request.args.get("can_take_calls")),
            seats=request.args.get("seats"),
            coffee_price=request.args.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('index.html')


## HTTP PUT/PATCH - Update Record
@app.route('/update/<cafe_id>', methods=['PATCH'])
def update(cafe_id):
    new_price = request.args.get('new_price')
    cafe_to_update = Cafe.query.filter_by(id=cafe_id).first()
    cafe_to_update.coffee_price = new_price
    db.session.commit()
    return f"Coffee price of {cafe_to_update.name} Cafe has been updated to =>{new_price}. Have a great day."

## HTTP DELETE - Delete Record
@app.route('/report_closed/<int:cafe_id>/', methods=['DELETE'])
def delete(cafe_id):
    key = request.args.get('api')
    if cafe_id not in [i.id for i in db.session.query(Cafe).all()]:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the databas."})
    elif key != "TopSecretAPIKey":
        return jsonify({"error": "Sorry, That's not allowed. You don't have the correct api key."})
    else:
        cafe_to_delete = Cafe.query.get_or_404(cafe_id)
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return f"{cafe_to_delete.name} is successfully DELETED from the database"


if __name__ == '__main__':
    app.run(debug=True)
