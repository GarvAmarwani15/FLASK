from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Event, Participant, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = "secret123"

db.init_app(app)


# ---------------- DATABASE ----------------

with app.app_context():
    db.create_all()

    # Default Admin
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="admin123", role="admin")
        db.session.add(admin)
        db.session.commit()


# ---------------- HELPERS ----------------

def is_logged_in():
    return session.get("user") is not None


def is_admin():
    return session.get("role") == "admin"


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():

    if session.get("user"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:

            session["user"] = user.username
            session["role"] = user.role

            return redirect(url_for("dashboard"))

        else:
            return render_template(
                "login.html",
                error="Invalid credentials"
            )

    return render_template("login.html")
# ---------------- DASHBOARD REDIRECT ----------------
@app.route("/dashboard")
def dashboard():

    if not session.get("user"):
        return redirect(url_for("login"))

    if session.get("role") == "admin":
        return redirect(url_for("admin"))
    else:
        return redirect(url_for("events"))


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- STUDENT AREA ----------------
@app.route("/events")
def events():

    if not session.get("user"):
        return redirect(url_for("login"))

    events = Event.query.all()
    return render_template("index.html", events=events)

# ---------------- ADMIN AREA ----------------

@app.route("/admin")
def admin():

    if not is_logged_in() or not is_admin():
        return redirect(url_for("login"))

    events = Event.query.all()
    return render_template("admin.html", events=events)


@app.route("/add_event", methods=["GET", "POST"])
def add_event():

    if not is_logged_in() or not is_admin():
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        date = request.form["date"]

        event = Event(name=name, description=description, date=date)

        db.session.add(event)
        db.session.commit()

        return redirect(url_for("admin"))

    return render_template("add_event.html")


@app.route("/participants/<int:event_id>")
def participants(event_id):

    if not is_logged_in() or not is_admin():
        return redirect(url_for("login"))

    event = Event.query.get(event_id)
    participants = Participant.query.filter_by(
        event_id=event_id
    ).all()

    return render_template(
        "participants.html",
        participants=participants,
        event=event
    )


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)