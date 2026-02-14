from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def home():
    return "<h1>Hello Test</h1>"

@app.route('/registration', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Store user data in session
        session['name'] = name
        session['email'] = email
        
        return f"Registration Successful! <br> Name: {name} <br> Email: {email}"
    
    return render_template("index.html")

@app.route('/profile')
def profile():
    # Access session data
    if 'name' in session:
        return f"<h1>Profile</h1><p>Name: {session['name']}</p><p>Email: {session['email']}</p>"
    return "<h1>No user logged in</h1>"

@app.route('/logout')
def logout():
    # Clear session data
    session.pop('name', None)
    session.pop('email', None)
    return redirect("registration")


if __name__ == '__main__':
    app.run(debug=True)