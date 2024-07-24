from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import csv
import os

# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>


app = Flask(__name__)
app.instance_path = os.path.join(app.root_path, 'instance')
os.makedirs(app.instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'travel'

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>


class Destination(db.Model):
    destination_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    destination_name = db.Column(db.String, nullable=False)
    destination_district = db.Column(db.String)
    destination_description = db.Column(db.Text)
    image_url = db.Column(db.String(100))


class DestinationPlanning(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination_id = db.Column(
        'destination_id', db.Integer, db.ForeignKey(Destination.destination_id))
    day1 = db.Column(db.Text)
    day2 = db.Column(db.Text)
    day3 = db.Column(db.Text)
    day4 = db.Column(db.Text)
    day5 = db.Column(db.Text)


class EnquiryDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination_id = db.Column(
        'destination_id', db.Integer, db.ForeignKey(Destination.destination_id))
    user_name = db.Column(db.String)
    email = db.Column(db.String)
    message = db.Column(db.Text)


with app.app_context():
    db.create_all()


# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>


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


# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>


def data_gen():
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
                        day5=row[5],)
                    db.session.add(des)
            db.session.commit()


data_gen()


# ->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>->=>


if __name__ == '__main__':
    app.run(debug=True)
