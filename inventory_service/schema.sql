CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    price       NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE stock (
    product_id  INTEGER PRIMARY KEY REFERENCES products(id),
    quantity    INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    warehouse   VARCHAR(100) DEFAULT 'main'
);
