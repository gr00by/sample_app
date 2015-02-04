import sqlite3
import requests
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

DATABASE = 'db/test.db'
DEBUG = True
USERNAME = 'admin'
PASSWORD = 'default'
SECRET_KEY = 'secretkey'
KEY = 'AzlJX8fcBQ58xQaOLHrNXz'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select filename, url, mimetype, size, id from entries order by id desc')
    entries = [dict(filename=row[0], url=row[1], mimetype=row[2], size=row[3], id=row[4]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/_add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    if not request.form['filename']:
    	flash('Please enter a filename')
    else:
	    g.db.execute('insert into entries (url, filename, mimetype, size) values (?, ?, ?, ?)',
		[request.form['url'], request.form['filename'], request.form['mimetype'], request.form['size']])
	    g.db.commit()
	    flash('File sucessfully uploaded')
    return redirect(url_for('show_entries'))

@app.route('/_delete')
def delete_entry():
	if not session.get('logged_in'):
	    abort(401)
	g.db.execute('delete from entries where id = ?', [request.args['id']])
	g.db.commit()
	par = {'key': app.config['KEY']}
	r = requests.delete(request.args['url'], params=par)
	print r.url
	flash('Entry deleted')
	return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run(debug=True)