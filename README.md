# Country Data API

A RESTful API that fetches country data from external APIs, stores it in a database, and provides CRUD operations.

## Features

- Fetch country data from the REST Countries API
- Fetch exchange rates from an external API
- Calculate estimated GDP based on population and exchange rates
- Store all data in a database
- Provide RESTful endpoints for CRUD operations
- Generate and serve a summary image

## Endpoints

- `POST /api/countries/refresh` - Fetch all countries and exchange rates, then cache them in the database
- `GET /api/countries` - Get all countries from the DB (support filters and sorting)
  - Filter options: `?region=Africa | ?currency=NGN | ?sort=gdp_desc`
- `GET /api/countries/:name` - Get one country by name
- `DELETE /api/countries/:name` - Delete a country record
- `GET /api/status` - Show total countries and last refresh timestamp
- `GET /api/countries/image` - Serve summary image

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Modify the variables as needed

4. Run database migrations:
```bash
python manage.py makemigrations api
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Usage

### Refresh Country Data
```bash
curl -X POST http://localhost:8000/api/countries/refresh
```

### Get All Countries
```bash
curl http://localhost:8000/api/countries
```

### Get Countries with Filter
```bash
curl http://localhost:8000/api/countries?region=Africa
```

### Get Country by Name
```bash
curl http://localhost:8000/api/countries/Nigeria
```

### Get Status
```bash
curl http://localhost:8000/api/status
```

## Technical Details

- Uses Django and Django REST Framework
- Supports MySQL (configured in settings)
- Includes error handling and validation
- Generates data visualization with matplotlib

## Error Handling

The API provides consistent JSON responses for errors:
- 404 → `{ "error": "Country not found" }`
- 400 → `{ "error": "Validation failed" }`
- 500 → `{ "error": "Internal server error" }`
