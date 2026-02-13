from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

@app.route('/')
def index():
    return "Hello, World!"


@app.route('/add')
def add():
    kanha = User(name = "Garv", role = "admin")
    db.session.add(kanha)
    db.session.commit()
    return "<p>data added!</p>"

@app.route('/show')
def show():
    users = User.query.filter_by(id=1)
    for user in users:
        print(f"{user.name} - {user.role}")
    print(User)
    return "<p>data fetching!</p>"

@app.route('/update')
def update():
    user = User.query.filter_by(name="Admin").first()
    user.name = "Garv"
    db.session.commit()
    return f"Updated user: {user.name}"

@app.route('/delete')
def delete():
    user = User.query.get(6)
    db.session.delete(user)
    db.session.commit()
    return f"Deleted user: {user.name}"


@app.route('/show_all')
def show_all():
    users = User.query.all()

    return render_template("index.html",users =  users)

@app.route('/show_f')
def show_f():
    users = User.query.filter(User.email.like("%gmail.com")).all()

    return render_template("index.html",users =  users)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)