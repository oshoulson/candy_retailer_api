from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import re

app = FastAPI(title="Candy Retailer Training API", version="1.0.0")

# ---------- Models ----------
class ErrorPayload(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

class OrderItem(BaseModel):
    item_name: str
    quantity: int
    unit_price: float

class Account(BaseModel):
    account_id: str
    name: str
    email: str
    phone: Optional[str] = None
    loyalty_points: int
    tier: Optional[str] = "Bronze"

class Order(BaseModel):
    order_id: str
    account_id: Optional[str] = None
    status: str  # pending | processing | shipped | delivered | cancelled
    eta: datetime
    items: List[OrderItem]
    total_amount: float

# ---------- Fake Data Store ----------
ACCOUNTS: Dict[str, Account] = {}
ORDERS: Dict[str, Order] = {}

PHONE_INDEX: Dict[str, str] = {}  # last10 digits -> account_id


def normalize_phone(p: str) -> str:
    digits = re.sub(r"\D", "", p or "")
    return digits[-10:] if len(digits) >= 10 else digits


def create_dynamic_date(base_date: datetime, reference_date: datetime = datetime(2025, 10, 16)) -> datetime:
    """
    Create a dynamic date by adjusting the base_date relative to the current date.
    The reference_date (Oct 16, 2025) is used as the original reference point.
    """
    time_diff = base_date - reference_date
    current_date = datetime.now()
    return current_date + time_diff


# ---------- Seed Functions ----------
def add_account(account_id: str, name: str, email: str, phone: Optional[str] = None, loyalty_points: int = 0, tier: str = "Bronze") -> Account:
    acc = Account(account_id=account_id, name=name, email=email, phone=phone, loyalty_points=loyalty_points, tier=tier)
    ACCOUNTS[account_id] = acc
    if phone:
        PHONE_INDEX[normalize_phone(phone)] = account_id
    return acc


def add_order(
    order_id: str,
    status: str,
    eta: datetime,
    items: List[OrderItem],
    account_id: Optional[str] = None,
) -> Order:
    total_amount = sum(item.quantity * item.unit_price for item in items)
    order = Order(
        order_id=order_id,
        account_id=account_id,
        status=status,
        eta=eta,
        items=items,
        total_amount=total_amount,
    )
    ORDERS[order_id] = order
    return order


def seed_data():
    """Seed fixtures with various account and order scenarios.
    Scenarios covered:
      - Accounts with multiple orders
      - Accounts with no orders
      - Orders without accounts (anonymous)
      - Different order statuses
      - Various items in orders
    """
    ACCOUNTS.clear()
    ORDERS.clear()
    PHONE_INDEX.clear()

    # ---- Accounts ----
    a1 = add_account("CUST-2001", "Sarah Chen", "sarah.chen@email.com", "+1 (415) 555-0101", loyalty_points=450, tier="Gold")
    a2 = add_account("CUST-2002", "Marcus Johnson", "marcus.j@email.com", "(212) 555-0199", loyalty_points=120, tier="Silver")
    a3 = add_account("CUST-2003", "Elena Rodriguez", "+1-617-555-0112", loyalty_points=80)
    a4 = add_account("CUST-2004", "David Park", "d.park@email.com", "+1 (206) 555-0133", loyalty_points=250, tier="Platinum")
    a5 = add_account("CUST-2005", "Lisa Wong", "lisa.w@email.com", loyalty_points=0)  # No phone
    a6 = add_account("CUST-2006", "James Miller", "james.m@email.com", "+1 (702) 555-0166", loyalty_points=10)

    # Helper for UTC-naive datetimes
    def dt(y, m, d, hh, mm=0):
        return datetime(y, m, d, hh, mm)

    # ---- Orders with accounts ----
    # Sarah Chen (a1) - Gold member with multiple orders
    add_order(
        "ORD-5001",
        status="delivered",
        eta=create_dynamic_date(dt(2025, 10, 8, 14)),
        items=[
            OrderItem(item_name="Gummy Bears", quantity=2, unit_price=4.99),
            OrderItem(item_name="Dark Chocolate Bar", quantity=1, unit_price=8.99),
        ],
        account_id=a1.account_id,
    )
    add_order(
        "ORD-5002",
        status="shipped",
        eta=create_dynamic_date(dt(2025, 10, 20, 10)),
        items=[
            OrderItem(item_name="Lollipops Assorted", quantity=3, unit_price=2.49),
            OrderItem(item_name="Taffy Pull", quantity=1, unit_price=5.99),
        ],
        account_id=a1.account_id,
    )
    add_order(
        "ORD-5003",
        status="processing",
        eta=create_dynamic_date(dt(2025, 11, 1, 15)),
        items=[
            OrderItem(item_name="Sour Gummies", quantity=5, unit_price=3.99),
        ],
        account_id=a1.account_id,
    )

    # Marcus Johnson (a2) - Silver member
    add_order(
        "ORD-5004",
        status="delivered",
        eta=create_dynamic_date(dt(2025, 10, 12, 11)),
        items=[
            OrderItem(item_name="Chocolate Truffles", quantity=1, unit_price=14.99),
            OrderItem(item_name="Peppermint Bark", quantity=2, unit_price=6.99),
        ],
        account_id=a2.account_id,
    )
    add_order(
        "ORD-5005",
        status="pending",
        eta=create_dynamic_date(dt(2025, 10, 25, 16)),
        items=[
            OrderItem(item_name="Swedish Fish", quantity=2, unit_price=3.49),
        ],
        account_id=a2.account_id,
    )

    # Elena Rodriguez (a3) - Bronze member, single order
    add_order(
        "ORD-5006",
        status="shipped",
        eta=create_dynamic_date(dt(2025, 10, 18, 13)),
        items=[
            OrderItem(item_name="Caramel Candies", quantity=1, unit_price=7.99),
            OrderItem(item_name="Gummy Worms", quantity=2, unit_price=2.99),
            OrderItem(item_name="Chocolate Chips", quantity=3, unit_price=4.49),
        ],
        account_id=a3.account_id,
    )

    # David Park (a4) - Platinum member
    add_order(
        "ORD-5007",
        status="delivered",
        eta=create_dynamic_date(dt(2025, 10, 9, 10)),
        items=[
            OrderItem(item_name="Premium Chocolate Box", quantity=1, unit_price=24.99),
        ],
        account_id=a4.account_id,
    )
    add_order(
        "ORD-5008",
        status="processing",
        eta=create_dynamic_date(dt(2025, 10, 22, 14)),
        items=[
            OrderItem(item_name="Candy Assortment Mix", quantity=4, unit_price=9.99),
            OrderItem(item_name="Licorice Twists", quantity=1, unit_price=3.99),
        ],
        account_id=a4.account_id,
    )

    # Lisa Wong (a5) - No phone, no orders (account exists but empty)

    # James Miller (a6) - Single order
    add_order(
        "ORD-5009",
        status="cancelled",
        eta=create_dynamic_date(dt(2025, 10, 15, 12)),
        items=[
            OrderItem(item_name="Rainbow Gummies", quantity=1, unit_price=5.99),
        ],
        account_id=a6.account_id,
    )

    # ---- Unassigned orders (no account) ----
    add_order(
        "ORD-U6001",
        status="pending",
        eta=create_dynamic_date(dt(2025, 10, 17, 11)),
        items=[
            OrderItem(item_name="Chocolate Covered Almonds", quantity=1, unit_price=11.99),
        ],
    )
    add_order(
        "ORD-U6002",
        status="shipped",
        eta=create_dynamic_date(dt(2025, 10, 23, 15)),
        items=[
            OrderItem(item_name="Jellybean Mix", quantity=3, unit_price=4.99),
            OrderItem(item_name="Marshmallows", quantity=2, unit_price=3.49),
        ],
    )
    add_order(
        "ORD-U6003",
        status="delivered",
        eta=create_dynamic_date(dt(2025, 10, 11, 9)),
        items=[
            OrderItem(item_name="Mint Chocolate Chips", quantity=1, unit_price=6.99),
        ],
    )


seed_data()


# ---------- Helpers ----------
def err(status: int, code: str, message: str, details: Optional[dict] = None):
    raise HTTPException(
        status_code=status,
        detail={"error": ErrorPayload(code=code, message=message, details=details).dict()},
    )


def find_account_by_phone(phone: str) -> Account:
    if not phone:
        err(400, "BAD_REQUEST", "Query parameter 'phone' is required")
    key = normalize_phone(phone)
    if len(key) < 10:
        err(400, "INVALID_PHONE", "Provide at least 10 digits for phone")
    account_id = PHONE_INDEX.get(key)
    if not account_id:
        err(404, "ACCOUNT_NOT_FOUND", f"No account for phone ending {key}")
    return ACCOUNTS[account_id]


# ---------- Endpoints ----------
@app.get("/account", response_model=Account)
async def get_account(phone: str = Query(..., description="Phone number")):
    return find_account_by_phone(phone)


@app.get("/orders")
async def get_orders(
    phone: Optional[str] = None,
    account_id: Optional[str] = None,
    order_id: Optional[str] = None,
) -> Dict[str, Any]:
    provided_params = sum([bool(phone), bool(account_id), bool(order_id)])

    if provided_params == 0:
        err(400, "BAD_REQUEST", "Provide one of: 'phone', 'account_id', or 'order_id'")
    elif provided_params > 1:
        err(400, "BAD_REQUEST", "Provide only one of: 'phone', 'account_id', or 'order_id'")

    # Handle order_id lookup
    if order_id:
        order = ORDERS.get(order_id)
        if not order:
            err(404, "ORDER_NOT_FOUND", f"No order_id {order_id}")
        return {"orders": [order.__dict__]}

    # Handle phone or account_id lookup
    if phone:
        account = find_account_by_phone(phone)
        acct_id = account.account_id
    else:
        acct_id = account_id
        if acct_id not in ACCOUNTS:
            err(404, "ACCOUNT_NOT_FOUND", f"No account_id {acct_id}")

    items = [o for o in ORDERS.values() if o.account_id == acct_id]
    return {"orders": [o.__dict__ for o in items]}


class CancelBody(BaseModel):
    reason: Optional[str] = None


@app.post("/orders/{order_id}/cancel", response_model=Order)
async def cancel_order(order_id: str, body: Optional[CancelBody] = None):
    order = ORDERS.get(order_id)
    if not order:
        err(404, "ORDER_NOT_FOUND", f"No order_id {order_id}")
    if order.status == "cancelled":
        err(409, "ALREADY_CANCELLED", "Order already cancelled")
    if order.status == "delivered":
        err(409, "ALREADY_DELIVERED", "Cannot cancel delivered orders")

    order.status = "cancelled"
    ORDERS[order_id] = order
    return order


# Optional: root route
@app.get("/")
async def root():
    return {"service": "candy_retailer", "version": "1.0.0"}
