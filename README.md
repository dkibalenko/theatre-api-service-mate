# Theatre API

## Introduction
This project is an API service for theatre management written on DRF.

## Features
* Authentication with JWT
* Authorization with permissions
* Admin panel via /admin/
* Image upload via /upload-image/
* Swagger documentation via /api/doc/swagger/
* Managing reservations and tickets
* Creating plays with genres and actors
* Creating plays, theatre halls
* Creating performances
* Managing props for individual performances
* Filtering performances by date and play
* Filtering plays by title, genre and actor
* Pagination reservations

## Installing with GitHub
Install PostgreSQL and create a database.
There is env.example file to see how to set environment variables.

  ```bash
  git clone https://github.com/dkibalenko/theatre-api-service-mate.git
  cd theatre-api-service-mate
  python3 -m venv env
  source venv/Scripts/activate
  pip install -r requirements.txt
  set POSTGRES_DB
  set POSTGRES_USER
  set POSTGRES_HOST
  set POSTGRES_PORT
  set POSTGRES_PASSWORD
  set DJANGO_SECRET_KEY
  python manage.py migrate
  python manage.py runserver
  ```

### Run with Docker
  ```bash
  docker compose build
  docker compose up
  ```

## Getting access
  * Get access token via ```/api/user/token/```
  * Enter Test User credentials

## Test User
* Email: admin@admin.com
* Password: admin

## Contributing
* Fork the repository
* Create a new branch (`git checkout -b <new_branch_name>`)
* Commit your changes (`git commit -am 'message'`)
* Push the branch to GitHub (`git push origin <new_branch_name>`)
* Create a new Pull Request
