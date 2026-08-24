"""Generate a small Odoo-like SQLite database for P3 structured queries.

Creates ``data/mock_odoo.sqlite`` with five tables:
``res_partner``, ``product_product``, ``sale_order``, ``sale_order_line``, ``stock_quant``.

Run from repo root::

    uv run python scripts/generate_mock_odoo.py
"""

from __future__ import annotations

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "data" / "mock_odoo.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS res_partner (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    is_company INTEGER NOT NULL DEFAULT 0,
    customer_rank INTEGER NOT NULL DEFAULT 0,
    supplier_rank INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    create_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS product_product (
    id INTEGER PRIMARY KEY,
    default_code TEXT,
    barcode TEXT,
    name TEXT NOT NULL,
    list_price REAL NOT NULL DEFAULT 0,
    standard_price REAL NOT NULL DEFAULT 0,
    type TEXT NOT NULL DEFAULT 'product',
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS sale_order (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    partner_id INTEGER NOT NULL REFERENCES res_partner(id),
    date_order TEXT NOT NULL,
    state TEXT NOT NULL,
    amount_total REAL NOT NULL DEFAULT 0,
    user_id INTEGER,
    company_id INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS sale_order_line (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES sale_order(id),
    product_id INTEGER NOT NULL REFERENCES product_product(id),
    name TEXT NOT NULL,
    product_uom_qty REAL NOT NULL DEFAULT 1,
    price_unit REAL NOT NULL DEFAULT 0,
    price_subtotal REAL NOT NULL DEFAULT 0,
    discount REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS stock_quant (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES product_product(id),
    location_id INTEGER NOT NULL,
    location_name TEXT NOT NULL DEFAULT 'WH/Stock',
    quantity REAL NOT NULL DEFAULT 0,
    reserved_quantity REAL NOT NULL DEFAULT 0,
    in_date TEXT
);

CREATE INDEX IF NOT EXISTS idx_sale_order_partner ON sale_order(partner_id);
CREATE INDEX IF NOT EXISTS idx_sale_order_state_date ON sale_order(state, date_order);
CREATE INDEX IF NOT EXISTS idx_sol_order ON sale_order_line(order_id);
CREATE INDEX IF NOT EXISTS idx_sol_product ON sale_order_line(product_id);
CREATE INDEX IF NOT EXISTS idx_quant_product ON stock_quant(product_id);
"""

PARTNER_NAMES = [
    "Acme Trading Co.",
    "Blue Ocean Retail",
    "Công ty TNHH Minh Phát",
    "Delta Supplies",
    "Eastwind Logistics",
    "FreshMart Vietnam",
    "Greenfield Partners",
    "Hoàng Gia Electronics",
    "IndoPac Wholesale",
    "Jade Commerce",
    "Kim Long Distribution",
    "Lumen Tech Store",
    "Metro Home Goods",
    "Nova Brands",
    "Orchid Fashion",
    "Pacific Tools",
    "Quốc Anh Furniture",
    "Riverstone Market",
    "Sunrise Office",
    "Terra Agro",
    "Urban Style",
    "VietFresh Foods",
    "Westgate Industrial",
    "Xpress Mobile",
    "Yellow Brick Toys",
]

PRODUCTS = [
    ("DESK-001", "Executive Desk Oak", 450.0, 280.0),
    ("CHAIR-002", "Ergonomic Office Chair", 220.0, 130.0),
    ("LAMP-003", "LED Desk Lamp Pro", 45.0, 22.0),
    ("MON-004", "27in Monitor 4K", 380.0, 260.0),
    ("KEY-005", "Mechanical Keyboard", 95.0, 55.0),
    ("MOU-006", "Wireless Mouse", 35.0, 18.0),
    ("PAP-007", "A4 Copy Paper (500)", 6.5, 3.2),
    ("PEN-008", "Ballpoint Pen Box", 12.0, 5.0),
    ("CAB-009", "Filing Cabinet 4-Drawer", 310.0, 190.0),
    ("SHE-010", "Bookshelf 5-Tier", 180.0, 110.0),
    ("TAB-011", "Tablet 10in WiFi", 290.0, 210.0),
    ("PHN-012", "Smartphone Mid-Range", 420.0, 320.0),
    ("HD-013", "External HDD 2TB", 75.0, 52.0),
    ("USB-014", "USB-C Hub 7-in-1", 48.0, 26.0),
    ("BAG-015", "Laptop Backpack", 55.0, 28.0),
    ("BOT-016", "Stainless Water Bottle", 18.0, 8.0),
    ("MUG-017", "Ceramic Coffee Mug", 9.0, 4.0),
    ("CLN-018", "Screen Cleaning Kit", 14.0, 6.0),
    ("CAB-019", "Cable Organizer Set", 11.0, 5.0),
    ("PAD-020", "Mouse Pad XL", 8.0, 3.5),
    ("WEB-021", "HD Webcam", 65.0, 38.0),
    ("MIC-022", "USB Microphone", 88.0, 48.0),
    ("SPK-023", "Bluetooth Speaker", 72.0, 40.0),
    ("PRT-024", "Label Printer", 160.0, 95.0),
    ("SCN-025", "Document Scanner", 210.0, 140.0),
    ("SHR-026", "Paper Shredder", 125.0, 78.0),
    ("FAN-027", "Desk Fan Quiet", 42.0, 24.0),
    ("HUM-028", "Mini Humidifier", 36.0, 19.0),
    ("PLT-029", "Standing Desk Mat", 28.0, 14.0),
    ("RUG-030", "Office Floor Mat", 52.0, 30.0),
]

STATES_WEIGHTED = [
    ("sale", 45),
    ("done", 35),
    ("draft", 10),
    ("sent", 5),
    ("cancel", 5),
]


def _weighted_choice(rng: random.Random, pairs: list[tuple[str, int]]) -> str:
    items, weights = zip(*pairs, strict=True)
    return rng.choices(items, weights=weights, k=1)[0]


def generate(*, seed: int = 42) -> Path:
    rng = random.Random(seed)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)

        partners: list[tuple] = []
        for idx, name in enumerate(PARTNER_NAMES, start=1):
            is_company = 1 if idx % 3 != 0 else 0
            partners.append(
                (
                    idx,
                    name,
                    f"contact{idx}@example.com",
                    f"+84-9{idx:02d}-{rng.randint(100, 999):03d}-{rng.randint(1000, 9999):04d}",
                    is_company,
                    rng.randint(0, 5),
                    rng.randint(0, 2),
                    1,
                    (date.today() - timedelta(days=rng.randint(30, 400))).isoformat(),
                )
            )
        conn.executemany(
            """INSERT INTO res_partner
               (id, name, email, phone, is_company, customer_rank, supplier_rank, active, create_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            partners,
        )

        products: list[tuple] = []
        for idx, (code, name, price, cost) in enumerate(PRODUCTS, start=1):
            products.append(
                (
                    idx,
                    code,
                    f"890{idx:04d}",
                    name,
                    price,
                    cost,
                    "product",
                    1,
                )
            )
        conn.executemany(
            """INSERT INTO product_product
               (id, default_code, barcode, name, list_price, standard_price, type, active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            products,
        )

        base_date = date.today() - timedelta(days=180)
        orders: list[tuple] = []
        lines: list[tuple] = []
        line_id = 1
        for order_id in range(1, 71):
            partner_id = rng.randint(1, len(PARTNER_NAMES))
            days_offset = rng.randint(0, 180)
            order_date = (base_date + timedelta(days=days_offset)).isoformat()
            state = _weighted_choice(rng, STATES_WEIGHTED)
            order_name = f"S{order_id:05d}"
            n_lines = rng.randint(1, 4)
            amount_total = 0.0
            for _ in range(n_lines):
                product_id = rng.randint(1, len(PRODUCTS))
                qty = rng.choice([1, 1, 2, 3, 5, 10])
                _, _, list_price, _ = PRODUCTS[product_id - 1]
                discount = rng.choice([0.0, 0.0, 0.0, 5.0, 10.0])
                price_unit = round(list_price * (1 - discount / 100), 2)
                subtotal = round(price_unit * qty, 2)
                amount_total += subtotal
                prod_name = PRODUCTS[product_id - 1][1]
                lines.append(
                    (
                        line_id,
                        order_id,
                        product_id,
                        prod_name,
                        qty,
                        price_unit,
                        subtotal,
                        discount,
                    )
                )
                line_id += 1
            orders.append(
                (
                    order_id,
                    order_name,
                    partner_id,
                    order_date,
                    state,
                    round(amount_total, 2),
                    rng.randint(1, 3),
                    1,
                )
            )

        conn.executemany(
            """INSERT INTO sale_order
               (id, name, partner_id, date_order, state, amount_total, user_id, company_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            orders,
        )
        conn.executemany(
            """INSERT INTO sale_order_line
               (id, order_id, product_id, name, product_uom_qty, price_unit, price_subtotal, discount)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            lines,
        )

        quants: list[tuple] = []
        quant_id = 1
        for product_id in range(1, len(PRODUCTS) + 1):
            qty = round(rng.uniform(0, 120), 2)
            reserved = round(min(qty, rng.uniform(0, qty * 0.4)), 2)
            quants.append(
                (
                    quant_id,
                    product_id,
                    1,
                    "WH/Stock",
                    qty,
                    reserved,
                    date.today().isoformat(),
                )
            )
            quant_id += 1
            if rng.random() < 0.3:
                input_qty = round(rng.uniform(0, 40), 2)
                quants.append(
                    (
                        quant_id,
                        product_id,
                        2,
                        "WH/Input",
                        input_qty,
                        0.0,
                        date.today().isoformat(),
                    )
                )
                quant_id += 1

        conn.executemany(
            """INSERT INTO stock_quant
               (id, product_id, location_id, location_name, quantity, reserved_quantity, in_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            quants,
        )
        conn.commit()
    finally:
        conn.close()

    return DB_PATH


def main() -> None:
    path = generate()
    conn = sqlite3.connect(path)
    try:
        counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in (
                "res_partner",
                "product_product",
                "sale_order",
                "sale_order_line",
                "stock_quant",
            )
        }
    finally:
        conn.close()
    print(f"Wrote {path}")
    for table, n in counts.items():
        print(f"  {table}: {n} rows")


if __name__ == "__main__":
    main()
