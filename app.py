from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm
from flask_login import UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = '25e01a84c93d97366d83e08cbf23aa2c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://limjinyung:990114@5432/attendance_database'
db = SQLAlchemy(app)


class Student(db.Model, UserMixin):
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), unique=True, nullable=False)
    last_name = db.Column(db.String(20), unique=True, nullable=False)
    DOB = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    # def __repr__(self):
    #     return f"Student('{self.student_id}', '{self.email}', '{self.image_file}')"

class Staff(db.Model, UserMixin):
    staff_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), unique=True, nullable=False)
    last_name = db.Column(db.String(20), unique=True, nullable=False)
    DOB = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    # def __repr__(self):
    #     return f"Staff('{self.first_name + self.last_name}', '{self.email}','{self.image_file}')"


class Unit(db.Model):
    unit_code = db.Column(db.String(20), primary_key=True)
    unit_name = db.Column(db.String(20), unique=True, nullable=False)
    unit_offer = db.Column(db.Boolean, nullable=False)

    # def __repr__(self):
    #     return f"Unit('{self.unit_code}', '{self.unit_name}','{self.unit_offer}')"


class Room(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)

    # def __repr__(self):
    #     return f"Room('{self.room_id}')"

# Association tables



@app.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == "__main__":
    app.run(debug=True)