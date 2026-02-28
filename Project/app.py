from flask import Flask, request, redirect, url_for, session, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret123'

db = SQLAlchemy(app)

# -------------------- DATABASE MODELS --------------------

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(300))
    date = db.Column(db.String(50))
    location = db.Column(db.String(100))


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))


# Create DB
with app.app_context():
    db.create_all()

    # Create default admin if not exists
    if not Admin.query.first():
        admin = Admin(username="admin", password="1234")
        db.session.add(admin)
        db.session.commit()


# -------------------- HOME PAGE --------------------

@app.route('/')
def home():
    events = Event.query.all()

    html = """
    <h1>College Event Management</h1>
    <a href="/admin">Admin Login</a>
    <hr>

    {% for event in events %}
        <h3>{{ event.title }}</h3>
        <p>{{ event.description }}</p>
        <p>{{ event.date }} | {{ event.location }}</p>

        <a href="/register/{{ event.id }}">Register</a>
        <hr>
    {% endfor %}
    """

    return render_template_string(html, events=events)


# -------------------- REGISTER --------------------

@app.route('/register/<int:event_id>', methods=['GET', 'POST'])
def register(event_id):

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        participant = Participant(
            name=name,
            email=email,
            phone=phone,
            event_id=event_id
        )

        db.session.add(participant)
        db.session.commit()

        return redirect(url_for('success'))

    html = """
    <h2>Event Registration</h2>

    <form method="POST">
        Name: <input type="text" name="name"><br><br>
        Email: <input type="email" name="email"><br><br>
        Phone: <input type="text" name="phone"><br><br>

        <button type="submit">Register</button>
    </form>
    """

    return render_template_string(html)


# -------------------- SUCCESS --------------------

@app.route('/success')
def success():
    return "<h2>Registration Successful!</h2><a href='/'>Go Home</a>"


# -------------------- ADMIN LOGIN --------------------

@app.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username, password=password).first()

        if admin:
            session['admin'] = username
            return redirect(url_for('dashboard'))

    html = """
    <h2>Admin Login</h2>

    <form method="POST">
        Username: <input type="text" name="username"><br><br>
        Password: <input type="password" name="password"><br><br>

        <button type="submit">Login</button>
    </form>
    """

    return render_template_string(html)


# -------------------- DASHBOARD --------------------

@app.route('/dashboard')
def dashboard():

    if 'admin' not in session:
        return redirect(url_for('admin'))

    events = Event.query.all()

    html = """
    <h2>Admin Dashboard</h2>

    <a href="/add_event">Add Event</a> |
    <a href="/logout">Logout</a>

    <hr>

    {% for event in events %}
        <h3>{{ event.title }}</h3>

        <a href="/participants/{{ event.id }}">Participants</a> |
        <a href="/delete/{{ event.id }}">Delete</a>

        <hr>
    {% endfor %}
    """

    return render_template_string(html, events=events)


# -------------------- ADD EVENT --------------------

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():

    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        date = request.form['date']
        location = request.form['location']

        event = Event(
            title=title,
            description=desc,
            date=date,
            location=location
        )

        db.session.add(event)
        db.session.commit()

        return redirect(url_for('dashboard'))

    html = """
    <h2>Add Event</h2>

    <form method="POST">
        Title: <input type="text" name="title"><br><br>
        Description: <input type="text" name="description"><br><br>
        Date: <input type="text" name="date"><br><br>
        Location: <input type="text" name="location"><br><br>

        <button type="submit">Add</button>
    </form>
    """

    return render_template_string(html)


# -------------------- DELETE EVENT --------------------

@app.route('/delete/<int:id>')
def delete(id):

    event = Event.query.get(id)

    if event:
        db.session.delete(event)
        db.session.commit()

    return redirect(url_for('dashboard'))


# -------------------- PARTICIPANTS --------------------

@app.route('/participants/<int:event_id>')
def participants(event_id):

    data = Participant.query.filter_by(event_id=event_id).all()

    html = """
    <h2>Participants</h2>

    {% for p in participants %}
        <p>{{ p.name }} | {{ p.email }} | {{ p.phone }}</p>
    {% endfor %}

    <br>
    <a href="/dashboard">Back</a>
    """

    return render_template_string(html, participants=data)


# -------------------- LOGOUT --------------------

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))


# -------------------- RUN APP --------------------

if __name__ == '__main__':
    app.run(debug=True)