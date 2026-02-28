from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event.db'
db = SQLAlchemy(app)

# ---------------- MODELS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))  # admin / participant

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    date = db.Column(db.String(50))

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    event_id = db.Column(db.Integer)

# ---------------- CREATE DB ----------------
with app.app_context():
    db.create_all()

# ---------------- HOME ----------------
@app.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']

        # Admin Code Check
        if role == "admin" and request.form['admin_code'] != "ADMIN123":
            return "❌ Invalid Admin Code"

        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=request.form['password'],
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            email=request.form['email'],
            password=request.form['password']
        ).first()

        if user:
            session['user_id'] = user.id
            session['role'] = user.role

            if user.role == "admin":
                return redirect('/admin')
            else:
                return redirect('/participant_dashboard')

    return render_template('login.html')

# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/')

    events = Event.query.all()
    return render_template('admin.html', events=events)

# ---------------- ADD EVENT ----------------
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if session.get('role') != 'admin':
        return redirect('/')

    if request.method == 'POST':
        event = Event(
            title=request.form['title'],
            description=request.form['description'],
            date=request.form['date']
        )
        db.session.add(event)
        db.session.commit()
        return redirect('/admin')

    return render_template('add_event.html')

# ---------------- EDIT EVENT ----------------
@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    if session.get('role') != 'admin':
        return redirect('/')

    event = Event.query.get(id)

    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        event.date = request.form['date']
        db.session.commit()
        return redirect('/admin')

    return render_template('edit_event.html', event=event)

# ---------------- DELETE EVENT ----------------
@app.route('/delete_event/<int:id>')
def delete_event(id):
    if session.get('role') != 'admin':
        return redirect('/')

    event = Event.query.get(id)
    db.session.delete(event)
    db.session.commit()
    return redirect('/admin')

# ---------------- ENROLL ----------------
@app.route('/enroll/<int:event_id>')
def enroll(event_id):
    if session.get('role') != 'participant':
        return redirect('/')

    user_id = session['user_id']

    existing = Registration.query.filter_by(
        user_id=user_id,
        event_id=event_id
    ).first()

    if not existing:
        reg = Registration(user_id=user_id, event_id=event_id)
        db.session.add(reg)
        db.session.commit()

    return redirect('/participant_dashboard')


# ---------------- PARTICIPANTS ----------------
@app.route('/participants/<int:event_id>')
def participants(event_id):
    if session.get('role') != 'admin':
        return redirect('/')

    regs = Registration.query.filter_by(event_id=event_id).all()
    users = [User.query.get(r.user_id) for r in regs]

    return render_template('participants.html', users=users)

@app.route('/participant_dashboard')
def participant_dashboard():
    if session.get('role') != 'participant':
        return redirect('/')

    user_id = session['user_id']

    # All events
    all_events = Event.query.all()

    # Registered events
    regs = Registration.query.filter_by(user_id=user_id).all()
    registered_event_ids = [r.event_id for r in regs]

    return render_template(
        'participant_dashboard.html',
        all_events=all_events,
        registered_event_ids=registered_event_ids
    )

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
