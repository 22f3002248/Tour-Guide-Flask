import csv
import os
from datetime import datetime, timedelta, timezone

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, login_required, login_user,
                         logout_user)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>

app = Flask(__name__)

app.instance_path = os.path.join(app.root_path, 'instance')
os.makedirs(app.instance_path, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "travelAGENCY"

db = SQLAlchemy()
db.init_app(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

app.app_context().push()


def current_time(IST=timezone(timedelta(hours=5, minutes=30))):
    return datetime.now(IST)


# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<User: {self.id} | {self.username} | {self.email}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "role": self.role
        }


class Destination(db.Model):
    destination_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    destination_name = db.Column(db.String, nullable=False)
    destination_district = db.Column(db.String)
    destination_description = db.Column(db.Text)
    image_url = db.Column(db.String(100))

    def __repr__(self):
        return f"<Destination: {self.destination_id} | {self.destination_name}>"

    def to_dict(self):
        return {
            "destination_id": self.destination_id,
            "destination_name": self.destination_name,
            "destination_district": self.destination_district,
            "destination_description": self.destination_description,
            "image_url": self.image_url
        }


class DestinationPlanning(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination_id = db.Column(
        'destination_id', db.Integer, db.ForeignKey(Destination.destination_id))
    day1 = db.Column(db.Text)
    day2 = db.Column(db.Text)
    day3 = db.Column(db.Text)
    day4 = db.Column(db.Text)
    day5 = db.Column(db.Text)
    day6 = db.Column(db.Text)

    def __repr__(self):
        return f"<DestinationPlanning: {self.id} | {self.destination_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "day1": self.day1,
            "day2": self.day2,
            "day3": self.day3,
            "day4": self.day4,
            "day5": self.day5,
            "day6": self.day6
        }


class EnquiryDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination_id = db.Column(
        'destination_id', db.Integer, db.ForeignKey(Destination.destination_id))
    user_name = db.Column(db.String)
    email = db.Column(db.String)
    message = db.Column(db.Text)

    def __repr__(self):
        return f"<EnquiryDetail: {self.id} | {self.destination_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "user_name": self.user_name,
            "email": self.email,
            "message": self.message
        }


class ReplyDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination_id = db.Column(
        'destination_id', db.Integer, db.ForeignKey(Destination.destination_id))
    user_name = db.Column(db.String)
    email = db.Column(db.String)
    original_message = db.Column(db.Text)
    reply_message = db.Column(db.Text)
    enquiry_id = db.Column(db.Integer, db.ForeignKey(EnquiryDetail.id))

    def __repr__(self):
        return f"<ReplyDetail: {self.id} | {self.destination_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "destination_id": self.destination_id,
            "user_name": self.user_name,
            "email": self.email,
            "original_message": self.original_message,
            "reply_message": self.reply_message,
            "enquiry_id": self.enquiry_id
        }


with app.app_context():
    db.create_all()


# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>


@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        destinations = Destination.query.all()
        return render_template('index.html', destinations=destinations)
    elif request.method == 'POST':
        try:
            destination_name = request.form.get('destination')
            destination = Destination.query.filter_by(
                destination_name=destination_name).first()
            return redirect(url_for('destination',
                                    destination_id=destination.destination_id))
        except:
            return redirect(url_for('destination', destination_id=1))


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if Users.query.filter_by(username=username).first():
            return render_template("index.html", alert_type="danger",
                                   error_type="Register Failed",
                                   error_message="Username already taken!")
        hashed_password = generate_password_hash(
            password, method="pbkdf2:sha256")
        new_user = Users(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == "admin":
                return redirect(url_for("admin_home"))
            else:
                return redirect(url_for("user_home"))
        else:
            return render_template("index.html", alert_type="danger",
                                   error_type="Login Failed",
                                   error_message="Incorrect Username/Password!")
    return render_template("index.html")


@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


@app.route('/destination/<string:destination_id>')
def destination(destination_id):
    destination = Destination.query.filter_by(
        destination_id=destination_id).first()
    planning = DestinationPlanning.query.filter_by(
        destination_id=destination_id).first()
    return render_template('destination.html',
                           destination=destination, planning=planning)


@app.route('/enquiry/<string:destination_id>', methods=['GET', 'POST'])
@login_required
def enquiry(destination_id):
    destination = Destination.query.filter_by(
        destination_id=destination_id).first()
    planning = DestinationPlanning.query.filter_by(
        destination_id=destination_id).first()
    if request.method == 'GET':
        flash(f"Fill the form to enquire about {destination.destination_name}",
              category='warning')
        return render_template('enquiry.html',
                               destination=destination, planning=planning)
    elif request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        enq = EnquiryDetail(destination_id=destination_id,
                            user_name=name, email=email, message=message)
        db.session.add(enq)
        db.session.commit()
        flash("We wil get back to you soon !", category='success')
        return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        return render_template('search.html', result='')
    elif request.method == 'POST':
        searchterm = request.form.get('search')
        if searchterm:
            result = Destination.query.filter(
                Destination.destination_name.like('%'+searchterm+'%'))
            return render_template('search.html',
                                   result=result, searchterm=searchterm)
    return render_template('search.html', result='')


@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    destinations = Destination.query.all()
    if request.method == 'GET':
        return render_template('contact.html', destinations=destinations)
    elif request.method == 'POST':
        destination_id = request.form.get('destination')
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        destination = Destination.query.filter_by(
            destination_id=destination_id).first()
        req = EnquiryDetail(destination_id=destination.destination_id,
                            user_name=name, email=email, message=message)
        db.session.add(req)
        db.session.commit()
        flash("We wil get back to you soon !", category='success')
        return redirect(url_for('index'))
    return render_template('contact.html', destinations=destinations)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>


def data_gen():
    u = Users.query.all()
    if not u:
        user1 = Users(username="admin", email="admin@gmail.com", name="Admin",
                      password=generate_password_hash(
                          "password", method="pbkdf2:sha256"), role="admin")
        db.session.add(user1)
        user2 = Users(username="user", email="user@gmail.com", name="User",
                      password=generate_password_hash(
                          "password", method="pbkdf2:sha256"), role="user")
        db.session.add(user2)
        db.session.commit()
    d = Destination.query.all()
    if not d:
        with open('./static/destination.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                des = Destination(
                    destination_name=row[0], destination_district=row[1],
                    destination_description=row[2],
                    image_url=f'images/{row[0]}.jpg')
                db.session.add(des)
            db.session.commit()
            with open('./static/planning.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    des = DestinationPlanning(
                        destination_id=row[0],
                        day1=row[1],
                        day2=row[2],
                        day3=row[3],
                        day4=row[4],
                        day5=row[5],
                        day6=row[6],)
                    db.session.add(des)
            db.session.commit()


data_gen()


# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>


if __name__ == '__main__':
    app.run(debug=True)
