from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect, generate_csrf
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
csrf = CSRFProtect(app) #da ba3ml csrf protection lel app

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

#page el home
@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('search'))


#page el register
@csrf.exempt #da 3shan el register page mesh 3ayz a3mlha csrf protection 3shan el vulnerability bt3t el registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, 'user')",
                (username, email, password)
            )
            conn.commit()
            return redirect(url_for('login'))
        except:
            error = 'Username or email already exists.'
        finally:
            conn.close()
    return render_template('register.html', error=error)

#login
@csrf.exempt
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()
        if user:
            session['username'] = user['username']
            session['role']     = user['role']
            session['user_id']  = user['id']
            return redirect(url_for('search'))
        else:
            error = 'Invalid credentials.'
    return render_template('login.html', error=error)


#logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#Part el search

@app.route('/search')
def search():
    if 'username' not in session:
        return redirect(url_for('login'))

    query   = request.args.get('q', '')
    results = []
    error   = None

#vunrablity bt3t el search el hya sql injection
    if query:
        try:
            conn = get_db()
            # hena b2a bad5olo as data mesh sql command 3la b3d
            results = conn.execute(
                "SELECT id, username, email, role FROM users WHERE username LIKE ?",
                ('%' + query + '%',)).fetchall()
            conn.close()
        except Exception as e:
            error = str(e)

    return render_template('search.html',
                           query=query,
                           results=results,
                           error=error,
                           username=session['username'],
                           role=session['role'])

#page el profile
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    msg = request.args.get('msg', '')
    return render_template('profile.html',
                           username=session['username'],
                           role=session['role'],
                           msg= msg)



#admin page
@app.route('/admin')
def admin():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    conn = get_db()
    users = conn.execute("SELECT id, username, email, role FROM users").fetchall()
    conn.close()
    return render_template('admin.html',
                           username=session['username'],
                           users=users)


#da lma ba promote el user to admin
@app.route('/promote', methods=['POST'])
def promote():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    #hena b2a haykon fe el csrf token validation automatically
    target_id = request.form.get('user_id')
    conn = get_db()
    conn.execute("UPDATE users SET role = 'admin' WHERE id = ?", (target_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))



if __name__ == '__main__':
    from database import init_db
    init_db()
    app.run(debug=True)