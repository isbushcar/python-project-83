import psycopg2
from psycopg2.extras import RealDictCursor
import os
from flask import render_template, Flask, request, flash, url_for, redirect, get_flashed_messages, render_template
from dotenv import load_dotenv
from validators.url import url as validate_url

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY')
)

DATABASE_URL = os.getenv('DATABASE_URL')
CONN = psycopg2.connect(DATABASE_URL)


@app.get('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages, url={})


@app.post('/urls')
def add_url():
    form_input = request.form.to_dict()
    url = form_input.get('url')
    if validate_url(url) is not True:
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            url=form_input,
            messages=get_flashed_messages(with_categories=True)
        )

    cur = CONN.cursor()
    cur.execute('SELECT * FROM urls WHERE urls.name = %s LIMIT 1', (url,))
    if not cur.fetchall():
        cur.execute('INSERT INTO urls (name) VALUES (%s)', (url,))
        CONN.commit()
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')
    return redirect(url_for('index'))


@app.get('/urls/<int:url_id>')
def show_url(url_id):
    cur = CONN.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
                    SELECT 
                        id, name, DATE_TRUNC('day', created_at) AS created_at 
                    FROM urls 
                    WHERE urls.id = %s 
                    LIMIT 1""",
                (url_id,)
                )
    result = cur.fetchall()
    if not result:
        return render_template('/404.html'), 404
    return render_template('/url_details.html', url=result[0])


@app.get('/urls')
def show_all_urls():
    cur = CONN.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id, name
        FROM urls
        ORDER BY created_at DESC
        """,
                )
    urls = cur.fetchall()
    return render_template('/urls.html', urls=urls)
