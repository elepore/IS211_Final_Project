from flask import Flask, session, redirect, url_for, request, render_template, flash, jsonify
import hashlib
import sqlite3
import requests
from datetime import timedelta
import os 
import re

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=30)
app.secret_key = os.urandom(16)  

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form['new_username']
    password = request.form['new_password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        flash('User registered successfully')
    except sqlite3.Error as e:
        flash('Error registering user')
    finally:
        conn.close()
    return redirect(url_for('login'))

@app.route('/impersonate', methods=['POST'])
def impersonate():
    user_id = request.form['user_id']
    try:
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = user[0]
            session['user_id'] = user_id
            return redirect(url_for('view_books'))
        else:
            flash('User not found')
    except sqlite3.Error as e:
        flash(str(e))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            conn = sqlite3.connect('books.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user = c.fetchone()
            conn.close()
            if user and user[2] == hashed_password:  
                session['username'] = username
                session['user_id'] = user[0]
                return redirect(url_for('view_books'))
            else:
                flash('Invalid username or password', 'login_error')
        except sqlite3.Error as e:
            flash(str(e), 'login_error')
    elif request.method == 'GET':
        try:
            conn = sqlite3.connect('books.db')
            c = conn.cursor()
            c.execute("SELECT id, username FROM users")
            users = c.fetchall()
            conn.close()
        except sqlite3.Error:
            users = []
        return render_template('login.html', users=users)
    return render_template('login.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        isbn = request.form['isbn']
        if not re.match(r'^\d{10,13}$', isbn):
            flash('Invalid ISBN format', 'add_book_error')
            return render_template('add_book.html')    
        book_details = get_book_details(isbn)
        if book_details:
            try:
                conn = sqlite3.connect('books.db')
                c = conn.cursor()
                c.execute("INSERT INTO books (user_id, isbn_10, isbn_13, title, author, page_count, average_rating, thumbnail) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (session['user_id'], book_details['isbn_10'], book_details['isbn_13'], book_details['title'], book_details['authors'], book_details['page_count'], book_details['average_rating'], book_details['thumbnail']))
                conn.commit()
                flash('Book added successfully', 'add_book_success')
            except Exception as e:
                flash('Failed to add book: ' + str(e), 'add_book_error')
            finally:
                conn.close()
        else:
            flash('Failed to retrieve book details', 'add_book_error')
    return render_template('add_book.html')


@app.route('/view_books')
def view_books():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE user_id=?", (session['user_id'],))
    books = c.fetchall()
    conn.close()

    return render_template('view_catalogue.html', books=books, username=session.get('username'))

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        c.execute("DELETE FROM books WHERE id=? AND user_id=?", (book_id, session['user_id']))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('view_books'))  

@app.route('/delete_selected_books', methods=['POST'])
def delete_selected_books():
    if 'username' not in session:
        return jsonify({'success': False})
    data = request.json
    book_ids = data.get('book_ids', [])
    try:
        conn = sqlite3.connect('books.db')
        c = conn.cursor()
        for book_id in book_ids:
            c.execute("DELETE FROM books WHERE id=? AND user_id=?", (book_id, session['user_id']))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)})

    conn.close()
    return jsonify({'success': True})

def parse_book_data(data):
    if 'items' in data and data['items']:
        print('yes')
        book = data['items'][0]['volumeInfo']
        title = book.get('title', 'No Title')
        authors = ', '.join(book.get('authors', ['Unknown']))
        page_count = book.get('pageCount', 0)
        average_rating = book.get('averageRating', 0)
        thumbnail = book.get('imageLinks', {}).get('thumbnail', '')
        industry_identifiers = book.get('industryIdentifiers', [])
        isbn_10 = isbn_13 = ''
        for identifier in industry_identifiers:
            if identifier['type'] == 'ISBN_10':
                isbn_10 = identifier['identifier']
            elif identifier['type'] == 'ISBN_13':
                isbn_13 = identifier['identifier']
        return {
            'title': title,
            'authors': authors,
            'page_count': page_count,
            'average_rating': average_rating,
            'thumbnail': thumbnail,
            'isbn_10': isbn_10,
            'isbn_13': isbn_13
        }
    else:
        return None
    
def get_book_details(isbn):
    try:
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}')
        response.raise_for_status()  
        data = response.json()
        return parse_book_data(data)
    except requests.exceptions.HTTPError as err:
        flash(f"HTTP error: {err}")
    except requests.exceptions.RequestException as err:
        flash(f"Error: {err}")
    except Exception as err:
        flash(f"An error occurred: {err}")
    return None

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)
