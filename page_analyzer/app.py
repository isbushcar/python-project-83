import os

import bs4
import psycopg2
import requests
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


def get_conn():
    return psycopg2.connect(DATABASE_URL)


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
        ), 422

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'SELECT id FROM public.urls WHERE urls.name = %s LIMIT 1',
        (url,),
    )
    result = cur.fetchall()
    if not result:
        cur.execute('INSERT INTO public.urls (name) VALUES (%s)', (url,))
        conn.commit()
        flash('Страница успешно добавлена', 'success')

        cur.execute(
            'SELECT id FROM public.urls WHERE urls.name = %s LIMIT 1',
            (url,),
        )
        url_id = cur.fetchall()[0][0]
        conn.close()
    else:
        flash('Страница уже существует', 'info')
        conn.close()
        url_id = result[0][0]
    return redirect(url_for('show_url_details', url_id=url_id))


@app.get('/urls/<int:url_id>')
def show_url_details(url_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
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
        conn.close()
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
    conn.close()

    return render_template(
        '/url_details.html',
        url=result[0],
        checks=checks,
        messages=get_flashed_messages(with_categories=True),
    )


@app.get('/urls')
def show_all_urls():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM public.urls_with_last_checks')
    urls = cur.fetchall()
    conn.close()
    return render_template(
        '/urls.html',
        urls=urls,
        messages=get_flashed_messages(with_categories=True),
    )


@app.post('/urls/<int:url_id>/checks')
def check_url(url_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT name FROM urls WHERE id = %s LIMIT 1', (url_id,))
    url_to_check = cur.fetchall()[0][0]
    try:
        response = requests.get(url_to_check)
    except requests.exceptions.RequestException:
        conn.close()
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('show_url_details', url_id=url_id))

    status_code = response.status_code
    parsed_page = bs4.BeautifulSoup(response.text, 'html.parser')
    title = parsed_page.title.text if parsed_page.find('title') else ''
    h1 = parsed_page.h1.text if parsed_page.find('h1') else ''
    description = parsed_page.find("meta", attrs={"name": "description"})
    description = description.get("content") if description else ''

    cur.execute("""
        INSERT INTO public.url_checks
            (url_id, status_code, title, h1, description)
        VALUES (%s, %s, %s, %s, %s)
        """,
                (url_id, status_code, title, h1, description),
                )
    conn.commit()
    conn.close()
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url_details', url_id=url_id))
