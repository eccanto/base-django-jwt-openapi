# Overview

Basic project about an e-commerce REST API using:
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](http://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
- [OpenAPI Schema](https://www.django-rest-framework.org/api-guide/schemas/#generating-an-openapi-schema)

# Get Started

## Installation

### Dependencies

```bash
cd service/
python3 -m pip instasll -r requirements.txt
```

### Deploying

**`TODO`**

## How to use this API Rest

Here are some examples of how to use the Rest API ([jq](https://stedolan.github.io/jq/) is required)

get authentication token:
```bash
JWT_TOKEN=$(
    curl -s -X POST \
        'http://localhost:8083/api/token/' \
        -H 'Content-Type: application/json' \
        -d '{
            "username": "admin",
            "password": "admin"
        }' \
    | jq -r '.access'
) && echo "JWT token: ${JWT_TOKEN}"
```

### Register a product

```bash
PRODUCT_ID=$(
    curl -s -X POST \
        'http://localhost:8083/api/v1/product/' \
        -H 'Content-Type: application/json' \
        -H "Authorization: Bearer ${JWT_TOKEN}" \
        -d '{
            "name": "test 1.1",
            "price": "1200.99",
            "stock": 10
        }' \
    | jq -r '.id'
) && echo "product ID: ${PRODUCT_ID}"
```

### Edit a product

**PUT**
```bash
curl -s -X PUT \
    "http://localhost:8083/api/v1/product/${PRODUCT_ID}/" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${JWT_TOKEN}" \
    -d '{
        "name": "test 1.2",
        "price": "1500",
        "stock": 10
    }' | jq
```

**PATCH**
```bash
curl -s -X PATCH \
    "http://localhost:8083/api/v1/product/${PRODUCT_ID}/" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${JWT_TOKEN}" \
    -d '{
        "price": 1700
    }' | jq
```

### Get a product
```bash
curl -s -X GET \
    "http://localhost:8083/api/v1/product/${PRODUCT_ID}/" \
    -H "Authorization: Bearer ${JWT_TOKEN}" | jq
```

### Delete a product
```bash
curl -s -X DELETE \
    "http://localhost:8083/api/v1/product/${PRODUCT_ID}/" \
    -H "Authorization: Bearer ${JWT_TOKEN}"
```

### Get product list

```bash
curl -s -X GET \
  'http://localhost:8083/api/v1/product/' \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  | jq
```

### Edit stock of a product

```bash
curl -s -X PATCH \
    "http://localhost:8083/api/v1/product/${PRODUCT_ID}/" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${JWT_TOKEN}" \
    -d '{
        "stock": 5
    }' | jq
```

### Register an order

**`TODO`**
