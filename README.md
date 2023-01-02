# Page analyzer
[![Actions Status](https://github.com/isbushcar/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/isbushcar/python-project-83/actions)
![Flake8](https://github.com/isbushcar/python-project-83/workflows/flake8/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/06b57373133c22603d79/maintainability)](https://codeclimate.com/github/isbushcar/python-project-83/maintainability)
## Description
Page analyzer is a simple web-application to get web-site base SEO characteristics.  
[You can take look at deployed app here.](https://python-project-83-production-3e95.up.railway.app)
## Local deployment (requires Poetry)
1. Clone repository: `git clone https://github.com/isbushcar/python-project-83.git`
2. Go to directory python-project-lvl4 `cd python-project-lvl4`
3. Install dependencies by `poetry install`
4. Add `.env` file with `DATABASE_URL` and `SECRET_KEY` variables
5. Now application can be started by `make dev` (dev) or `make start` (gunicorn)