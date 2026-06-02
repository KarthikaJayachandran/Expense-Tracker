# 💰 PocketLens

A full-stack web application to track personal expenses by category, with monthly summaries and filters.

---

## ✨ Features

- **Add / Edit / Delete** expenses
- **Filter** by category, date range, and title search
- **Monthly Summary** with category-wise breakdown and visual progress bars
- **Export to CSV** to easily backup your current filtered view
- Expenses sorted by date (latest first)

---

## 🛠️ Tech Stack & Rationale

| Layer    | Technology                     | Why Chosen                                                 |
|----------|--------------------------------|------------------------------------------------------------|
| Frontend | React 18 + TypeScript          | Component model, type safety, great DX for rapid UI development |
| Bundler  | Vite                           | Near-instant dev server, minimal config compared to Webpack |
| Backend  | FastAPI                        | Auto Swagger docs, robust Pydantic validation, async-ready |
| ORM      | SQLAlchemy 2.0 (mapped_column) | Pythonic DB access, clean model definitions, secure against SQLi |
| Database | SQLite                         | Zero-config file-based DB, perfect for local single-user apps |

---

## 🚀 Setup Instructions

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10

---

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

API will be available at: `http://localhost:8000`  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App will be available at: `http://localhost:5173`

> **Note**: Start the backend first, then the frontend.

---

## 🏛️ Architecture Overview

The application follows a clean, decoupled client-server architecture:

1. **Frontend (Presentation Layer)**: Built with React and TypeScript. Uses Axios for API communication. State is managed locally via React hooks (useState, useEffect, useCallback) to keep the app lightweight. UI components are modular (Forms, Lists, Filters, Summary).
2. **Backend API (Application Layer)**: Built with FastAPI. Structured into distinct layers to separate concerns:
   - **Routers** (`routers/`): Handle HTTP requests and responses.
   - **Services** (`services/`): Handle complex business logic (e.g., summary aggregations).
   - **CRUD** (`crud.py`): Handle database transactions and queries.
3. **Database (Data Layer)**: SQLite accessed via SQLAlchemy ORM.

## 💾 Data Model Explanation

The application uses a single primary relational table `expenses` to store data:

- `id` (Integer, Primary Key): Unique identifier for the expense.
- `title` (String): Short text describing the expense.
- `amount` (Float): The cost of the expense (enforced positive).
- `category` (String): The category (restricted to: Food, Transport, Shopping, Bills, Entertainment, Other).
- `date` (Date): The date the expense occurred (defaults to today).
- `note` (String, Optional): Additional context for the expense.
- `created_at` (DateTime): Auto-generated timestamp of creation.
- `updated_at` (DateTime): Auto-updated timestamp on modification.

---

## 🔌 API Endpoint Summary

| Method | Route                        | Description                                      |
|--------|------------------------------|--------------------------------------------------|
| GET    | `/expenses`                  | List all expenses (supports query filters)       |
| POST   | `/expenses`                  | Create a new expense                             |
| PUT    | `/expenses/{id}`             | Update an existing expense entirely              |
| DELETE | `/expenses/{id}`             | Delete an expense                                |
| GET    | `/summary/current-month`     | Get total spent & category breakdown for a month |

---

## 🛡️ Validation & Edge Cases Handled

The application is built to be robust against bad input and edge cases:

- **Frontend Validation**: Forms prevent submission of empty titles, titles with only spaces, negative/zero amounts, and invalid dates. Displays real-time error messages.
- **Backend Validation**: Pydantic models strictly enforce data types, string lengths (e.g., max 500 chars for notes), and enum values for categories. Date defaults to today if omitted.
- **Invalid Date Ranges**: If a user filters with a `from_date` greater than `to_date`, the frontend immediately alerts the user, and the backend has a custom exception handler to return a clear 422 error.
- **Empty States**: The UI gracefully handles scenarios where no expenses exist (or none match filters) with user-friendly "No expenses found" empty states.
- **Graceful Error Handling**: Database transaction failures trigger rollbacks and return sanitized 500 errors to prevent leaking stack traces.

---

## 🎯 Prioritization Decisions

During implementation, prioritization focused on:
1. **Core E2E Functionality**: Ensuring a user can reliably add, view, edit, and delete an expense over everything else.
2. **Clean Architecture**: Structuring the backend with Routers/Services/CRUD to demonstrate maintainability and testability, rather than putting everything in one file.
3. **UX / Polish**: Implementing a responsive, clean CSS design with instant feedback (clearing filters automatically on save) to ensure the app feels premium.

---

## ⚖️ Tradeoffs & Skipped Features

### What was completed vs intentionally skipped
- **Completed**: Full CRUD, advanced filtering, robust validation, dynamic monthly summaries, dashboard statistics, CSV export, and a responsive custom UI.
- **Skipped**: Redux/Context API, React Router, Authentication, Pagination, and Database Migrations (Alembic).

### Reasons for skipping features
| Skipped Feature | Rationale |
|-----------------|-----------|
| **Redux / Global State** | Over-engineering. Local state (`useState`) passed as props is perfectly sufficient for a single-page app of this scope. |
| **React Router** | The app's requirements only dictate two main views (List and Summary), which fit well on a single scrolling dashboard. |
| **Authentication** | Explicitly out of scope for the challenge (single-user local app). |
| **Alembic Migrations** | `Base.metadata.create_all()` is used for simplicity. For a production app, Alembic would be required, but it adds unnecessary overhead for a rapid prototype. |
| **Pagination** | Assumed small dataset for a local personal tracker. Fetching all expenses at once simplifies the filtering implementation significantly. |

---

## ⚠️ Known Rough Edges / Limitations

- **Single user only** — no authentication or multi-user support.
- **Schema changes** require manually deleting `expenses.db` and restarting the backend due to lack of Alembic.
- **SQLite concurrency** — perfectly fine for local use, but not suitable for high-concurrency production deployments.

---

## 🔮 Future Improvements

- [ ] Add Alembic for seamless database schema migrations.
- [ ] Implement pagination on the `/expenses` endpoint for infinite scrolling on the frontend.
- [ ] Add PDF export functionality for expense reports.
- [ ] Implement budget limits per category with visual alerts in the summary.
- [ ] Write a comprehensive test suite (pytest for backend, vitest/RTL for frontend).
- [ ] Add offline support via PWA (Service Workers).
