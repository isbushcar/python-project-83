import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, flash, url_for, redirect, \
    get_flashed_messages, render_template
from psycopg2.extras import RealDictCursor
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
    return render_template(
        'index.html',
        messages=get_flashed_messages(with_categories=True),
        url={},
    )


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
    cur.execute(
        'SELECT * FROM public.urls WHERE urls.name = %s LIMIT 1',
        (url,),
    )
    if not cur.fetchall():
        cur.execute('INSERT INTO public.urls (name) VALUES (%s)', (url,))
        CONN.commit()
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')
    return redirect(url_for('index'))


@app.get('/urls/<int:url_id>')
def show_url_details(url_id):
    cur = CONN.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
                    SELECT
                        id, name, created_at::date
                    FROM public.urls
                    WHERE urls.id = %s
                    LIMIT 1""",
                (url_id,)
                )
    result = cur.fetchall()
    if not result:
        return render_template('/404.html'), 404

    cur.execute("""
                    SELECT
                        id, status_code, h1, title,
                        description, created_at::date
                    FROM public.url_checks
                    WHERE url_checks.url_id = %s
                    """,
                (url_id,)
                )
    checks = cur.fetchall()

    return render_template(
        '/url_details.html',
        url=result[0],
        checks=checks,
        messages=get_flashed_messages(with_categories=True),
    )


@app.get('/urls')
def show_all_urls():
    cur = CONN.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT
               urls.id,
               urls.name,
               uc.last_checked
        FROM public.urls
        LEFT JOIN (
            SELECT DISTINCT
               url_id,
               max(created_at::date) OVER (PARTITION BY url_id) AS last_checked
            FROM public.url_checks
            ) uc
            ON urls.id = uc.url_id
        ORDER BY urls.created_at DESC
        """,
                )
    urls = cur.fetchall()
    return render_template(
        '/urls.html',
        urls=urls,
        messages=get_flashed_messages(with_categories=True),
    )


@app.post('/urls/<int:url_id>/checks')
def check_url(url_id):
    cur = CONN.cursor()
    cur.execute("""
        INSERT INTO public.url_checks (url_id)
        VALUES (%s)
        """,
                (url_id,),
                )
    CONN.commit()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url_details', url_id=url_id))
