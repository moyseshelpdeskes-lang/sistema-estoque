# Modelo de dados

## Diagrama ER

```mermaid
erDiagram
    CATEGORY ||--o{ PRODUCT : "classifica"
    SUPPLIER ||--o{ PRODUCT : "fornece"
    PRODUCT  ||--o{ STOCK_MOVEMENT : "tem"
    USER     ||--o{ STOCK_MOVEMENT : "registra"

    CATEGORY {
        int id PK
        string name UK
        string description
        datetime created_at
    }

    SUPPLIER {
        int id PK
        string name
        string contact
        string cnpj UK
        datetime created_at
    }

    USER {
        int id PK
        string email UK
        string password_hash
        string role
        bool is_active
        datetime created_at
    }

    PRODUCT {
        int id PK
        string sku UK
        string name
        float unit_price
        int quantity
        int minimum_stock
        int category_id FK
        int supplier_id FK
        bool is_active
        datetime created_at
        datetime updated_at
    }

    STOCK_MOVEMENT {
        int id PK
        int product_id FK
        int user_id FK
        string type
        int quantity
        int resulting_balance
        string reason
        datetime created_at
    }
    