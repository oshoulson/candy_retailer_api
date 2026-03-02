# Candy Retailer Training API

A FastAPI-based demo service for managing candy retailer accounts and orders. Designed for training, testing, and integration demos on Render.com.

## Features

- **Account Management**: Lookup customer accounts by email or phone
- **Order Tracking**: Retrieve orders by email, phone, account ID, or order ID
- **Order Cancellation**: Cancel pending and processing orders
- **Fake Data**: Pre-seeded with realistic customer and order data
- **Dynamic Dates**: Dates automatically adjust relative to current date

## Getting Started

### Installation

```bash
pip install -r requirements.txt
```

### Running Locally

```bash
uvicorn server:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Data Schema

### Account
- `account_id`: Unique identifier (e.g., CUST-2001)
- `name`: Customer name
- `email`: Email address
- `phone`: Phone number (optional)
- `loyalty_points`: Accumulated loyalty points
- `tier`: Membership tier (Bronze, Silver, Gold, Platinum)

### Order
- `order_id`: Unique identifier (e.g., ORD-5001)
- `account_id`: Associated customer (optional, for guest orders)
- `status`: Order status (pending, processing, shipped, delivered, cancelled)
- `eta`: Estimated time of arrival
- `items`: List of order items with quantity and unit price
- `total_amount`: Total order value

## Endpoints

### GET /account
Lookup a customer account by phone.

**Parameters:**
- `phone` (required): Customer phone (any format)

**Example:**
```bash
curl "http://localhost:8000/account?phone=415-555-0101"
```

### GET /orders
Retrieve orders by various criteria.

**Parameters (choose one):**
- `phone`: Customer phone
- `account_id`: Customer account ID
- `order_id`: Specific order ID

**Example:**
```bash
curl "http://localhost:8000/orders?phone=415-555-0101"
curl "http://localhost:8000/orders?order_id=ORD-5001"
```

### POST /orders/{order_id}/cancel
Cancel an order (only for pending/processing orders).

**Parameters:**
- `order_id` (path): Order ID to cancel

**Request Body (optional):**
```json
{
  "reason": "Changed my mind"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/orders/ORD-5005/cancel" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Changed my mind"}'
```

## Sample Data

### Accounts
- Sarah Chen (CUST-2001) - Gold, 450 points, multiple orders
- Marcus Johnson (CUST-2002) - Silver, 120 points
- Elena Rodriguez (CUST-2003) - Bronze, 80 points
- David Park (CUST-2004) - Platinum, 250 points
- Lisa Wong (CUST-2005) - Bronze, no phone, no orders
- James Miller (CUST-2006) - Bronze, 10 points

### Orders
- 9 accounts-associated orders (various statuses)
- 3 guest orders (no account)
- Total: 12 orders with various items and statuses
