# Django Blog API

A RESTful blog API built with Django without Django REST Framework.

## Features

- User registration and authentication
- Create, read, update, delete blog posts
- Comment system
- Like functionality
- Pagination

## Setup

1. Clone the repository
2. Run migrations: `python manage.py migrate`
3. Create superuser: `python manage.py createsuperuser`
4. Start server: `python manage.py runserver`

## API Endpoints

- POST /api/register/ - Register user
- POST /api/login/ - Login user
- POST /api/create-post/ - Create post
- GET /api/posts/ - Get all posts
- GET /api/post/<id>/ - Get post detail
- POST /api/post/<id>/comment/ - Add comment
