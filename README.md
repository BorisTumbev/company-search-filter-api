# 🚀 Django Company Search, Filter, and Sort API

A scalable Django REST API for searching, filtering, and sorting company-related data — built with custom, efficient Python logic.

---

## 🛠️ Setup Instructions

1. **Clone the repository and navigate to your project root**

    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2. **Copy environment variables**

    ```bash
    cp .env.example .env
    ```

3. **Build and start the services (requires Docker + Docker Compose):**

    ```bash
    docker compose up --build
    ```

4. **Load sample data (fixture):**

    ```bash
    docker compose run --rm web python manage.py loaddata company/fixtures/test_companies.json
    ```

5. **Run the test suite (including logic and endpoint tests):**

    ```bash
    docker compose run --rm test
    # or manually, for a specific test module:
    docker compose run --rm test python manage.py test company.tests.test_filtering
    ```

6. **Visit the API at:**  
    ```
    http://localhost:8000/api/v1/companies/
    ```
    Use query parameters like `?search=industry:Tech`, `?filter=name="Alpha Corp" AND revenue>1000000`, `?sort=-founded_year`.

---

## 🧠 How Filtering and Sorting Work

### **Custom Filtering**
- **No use of Django ORM `.filter()`!**
- Query parameters (`filter=...`) are parsed into structured conditions.
- AND/OR logic is supported:  
  - e.g. `industry=Tech AND revenue>500000 OR name="Alpha Corp"`
- Quoted and unquoted values supported for multi-word fields.
- Nested and related fields are supported (`details__size=Large`, `revenue>1000000`).
- Filtering is implemented fully in Python, with robust utilities for nested field and related object lookup.

### **Custom Sorting**
- Query parameter `sort=industry,-founded_year` sorts results by one or more fields.
- **No use of Django ORM `.order_by()` or built-in `sorted()`!**
- Implements an efficient, stable **merge sort** algorithm.
- Supports multi-field, ascending/descending sorting, even on related/nested fields.

---

## 🧩 Algorithm Choices Explained

- **Filtering:**  
  Iterates through in-memory company objects. Each object is matched against all filter conditions using custom field/nested attribute access logic and a safe comparison map (never using `eval`). Supports AND/OR and quoted multi-word values.

- **Sorting:**  
  Utilizes a pure Python **merge sort** (O(n log n)) to guarantee stable, predictable performance.  
  Multi-field sorting is handled by generating a tuple key for each object based on the sort fields, with descending/ascending handled via key inversion — all in one pass.

---

## ⚠️ Limitations & Assumptions

- **In-memory only:** All filtering and sorting happen in Python, on data loaded into memory. For huge datasets, you may hit memory limits. This approach is chosen **by assignment design** (no `.filter()`/`.order_by()`).
- **No parentheses grouping** in filter queries yet (e.g. no support for `A AND (B OR C)`).
- **No NOT/negation support** in filter expressions.
- **Assumes all required fields and relations are loaded in the queryset** before filtering/sorting.
- **API is read-only** (GET/search/filter/sort only).
- **Performance:** Designed for moderate data volumes. For millions of records, consider an approach using database-backed filtering/sorting.

---

## 📝 Example API Queries

```http
GET /api/v1/companies/?filter=industry=Tech AND founded_year>=2000&sort=-founded_year
