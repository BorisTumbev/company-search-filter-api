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
    # populate them with your local settings
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

## 🔎 How Searching Works

- **Free-form search** via the `search` query parameter:  
  - e.g. `?search=industry:Tech country:Ger`
- **Supports:**
  - Text fields (substring or exact match)
  - Numeric fields and comparisons (>, <, >=, <=)
  - Nested and related fields (`details__ceo_name:Alice`)
  - Multiple search criteria combined with AND (all must match)
  - Quoted values for multi-word search (e.g. `name="Beta Group"`)
- **Implementation:**  
  - Parses the `search` string into conditions using regex and custom parsing logic.
  - Each company is checked for all search conditions using a custom `match()` function.
  - All filtering is done in pure Python — no Django ORM `.filter()`!

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

## 🧩 Algorithm Choices & Complexity

- **Searching/Filtering:**  
  - Iterates through all company objects in memory.  
  - Each object is checked against all filter/search conditions.
  - **Time Complexity:**  
    - Filtering/searching: **O(n × m)** (n = number of companies, m = number of conditions)
    - Each company is inspected once per condition (includes nested/related lookups as needed).
- **Sorting:**  
  - Uses custom Python **merge sort** for all sorting (never `sorted()`).
  - Handles multi-field sorts via tuple keys, with all logic in one pass.
  - **Time Complexity:**  
    - Sorting: **O(n log n)** (where n is number of companies in the filtered result set)
    - Each comparison may involve field lookups, but done efficiently per tuple key.

---

## ⚠️ Limitations & Assumptions

- **In-memory only:** All filtering, searching, and sorting happen in Python, on data loaded into memory. For huge datasets, you may hit memory limits. This approach is chosen **by assignment design** (no `.filter()`/`.order_by()`).
- **No parentheses grouping** in filter queries yet (e.g. no support for `A AND (B OR C)`).
- **No NOT/negation support** in filter expressions.
- **Assumes all required fields and relations are loaded in the queryset** before filtering/sorting.
- **Performance:** Designed for moderate data volumes. For millions of records, consider an approach using database-backed filtering/sorting.

---

## 📝 Example API Queries

```http
GET http://127.0.0.1:8000/api/v1/companies/?filter=name=Beta Group OR founded_year=1999&sort=-name&search=country:Ger
