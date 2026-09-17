# 📚 LibraSys — Library Management System

A complete, full-stack CRUD web application for managing a library's books,
members, and book issue/return transactions. Built with **Django + Django
REST Framework** on the backend and a clean **HTML/CSS/JavaScript** dashboard
on the frontend — no build tools, no Node.js required to run it.

---

## 1. Project Overview

LibraSys lets library staff:
- Maintain a catalogue of books (add, edit, delete, search, filter by category)
- Maintain a member registry (add, edit, delete, search, activate/deactivate)
- Issue books to members and record returns, with automatic overdue detection
  and fine calculation
- View a live dashboard with key stats and recent activity

## 2. Problem Statement

Manual library record-keeping (registers/spreadsheets) is error-prone and
hard to search. LibraSys digitizes the full lending lifecycle — cataloguing,
membership, issuing, returning, and fines — behind a simple, responsive web UI.

## 3. Objectives

- Implement full CRUD for Books and Members
- Implement Issue / Return workflows with business rules (copy availability,
  active-member checks, overdue + fine calculation)
- Expose a documented REST API
- Provide a professional, color-coded dashboard UI
- Persist data in a relational database (SQLite by default)

## 4. Technology Stack

| Layer              | Technology                          |
|---------------------|--------------------------------------|
| Backend framework   | Django 4.2                          |
| REST API            | Django REST Framework 3.15          |
| Database            | SQLite (default, zero-config)       |
| Frontend            | HTML5, CSS3, Vanilla JavaScript      |
| Fonts               | Google Fonts (Poppins, Inter)        |

No React/Node build step is required — the frontend is served directly by
Django as static templates that call the REST API with `fetch`.

## 5. System Architecture

```
Browser (HTML/CSS/JS)
        |
        v
Django Views (templates) ---- serves the dashboard pages
        |
        v
Django REST Framework API (/api/books, /api/members, /api/transactions)
        |
        v
Django ORM
        |
        v
SQLite Database (db.sqlite3)
```

## 6. Database / Entity Design

**Book**
| Field            | Type          | Notes                          |
|-------------------|---------------|----------------------------------|
| title             | CharField     | required                        |
| author            | CharField     | required                        |
| isbn              | CharField     | unique, 10 or 13 digits          |
| category          | CharField     | choice field                    |
| publisher         | CharField     | optional                        |
| publish_year      | Integer       | optional                        |
| total_copies      | PositiveInt   | ≥ 1                              |
| available_copies  | PositiveInt   | auto-managed                     |
| added_date        | DateTime      | auto                             |

**Member**
| Field            | Type      | Notes                    |
|-------------------|-----------|---------------------------|
| name              | CharField | required                 |
| email             | Email     | unique, required          |
| phone             | CharField | validated format          |
| address           | CharField | optional                 |
| membership_date   | Date      | auto                      |
| is_active         | Boolean   | default true              |

**Transaction** (issue/return record)
| Field         | Type            | Notes                                |
|----------------|-----------------|----------------------------------------|
| book           | ForeignKey→Book | required                              |
| member         | ForeignKey→Member | required                            |
| issue_date     | Date            | auto, on creation                     |
| due_date       | Date            | auto, issue_date + 14 days             |
| return_date    | Date            | set on return                          |
| status         | CharField       | ISSUED / OVERDUE / RETURNED             |
| fine_amount    | Decimal         | ₹5/day after due date, set on return   |

## 7. REST API Reference

Base URL: `/api/`

| Operation                | Method | Endpoint                              |
|---------------------------|--------|-----------------------------------------|
| List / search books       | GET    | `/api/books/?search=&category=`         |
| Create book                | POST   | `/api/books/`                          |
| Retrieve book              | GET    | `/api/books/{id}/`                     |
| Update book                 | PUT    | `/api/books/{id}/`                    |
| Delete book                 | DELETE | `/api/books/{id}/`                    |
| List / search members      | GET    | `/api/members/?search=`                |
| Create member               | POST   | `/api/members/`                       |
| Update member                | PUT    | `/api/members/{id}/`                 |
| Delete member                | DELETE | `/api/members/{id}/`                 |
| List transactions           | GET    | `/api/transactions/?status=`          |
| Issue a book                 | POST   | `/api/transactions/`                 |
| Return a book                 | POST   | `/api/transactions/{id}/return_book/` |
| Dashboard statistics           | GET    | `/api/dashboard/`                    |

A book cannot be deleted while it has copies currently issued; the same
applies to a member with active loans. Issuing fails if there are no
available copies or the member is inactive. Returns are date-stamped
automatically and a ₹5/day fine is applied for late returns.

## 8. Validation Rules

- ISBN: digits and hyphens only, 10 or 13 digits total
- Email: valid email format, unique per member
- Phone: 7–15 digits, optional leading `+`
- Total copies: minimum 1
- All server-side validation is enforced by DRF serializers, independent of
  the client-side HTML5 validation.

## 9. Installation & Setup

**Prerequisites:** Python 3.9+ installed on your machine.

```bash
# 1. Extract the zip and move into the project folder
cd library_management_system

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create the database tables
python manage.py makemigrations
python manage.py migrate

# 5. (Optional) Load sample books & members to explore the app
python manage.py seed_data

# 6. (Optional) Create an admin login for the Django admin panel
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser.

The Django admin panel (optional, for raw data management) is available at
**http://127.0.0.1:8000/admin/** once you've created a superuser.

> No frontend build step, no Node.js, and no extra configuration is
> required — the steps above are the only setup Django itself needs to run
> on any machine.

## 10. Testing the Application

1. Go to **Books** → add/edit/delete a few books; try duplicate ISBNs and
   short ISBNs to see validation errors.
2. Go to **Members** → add/edit/delete members; try an invalid phone number
   or duplicate email.
3. Go to **Issue / Return** → issue a book to a member, confirm the book's
   available copies drops by one, then return it and confirm the copy count
   is restored.
4. Check the **Dashboard** after each action to confirm the stats update.
5. Use Postman (or curl) against the endpoints in Section 7 to test the API
   directly, including error cases (missing fields, invalid IDs, issuing a
   book with zero copies left).

## 11. Security & Quality Notes

- No secrets are hard-coded beyond the development `SECRET_KEY`, which
  should be replaced with an environment variable before any real
  deployment (`DEBUG = False`, a proper `SECRET_KEY`, and a restricted
  `ALLOWED_HOSTS` list).
- All database access goes through the Django ORM (parameterized queries).
- Server-side validation is enforced independently of client-side checks.

## 12. Version Control

This project includes a `.gitignore` that excludes the virtual environment,
`db.sqlite3`, and other local artifacts, so the repository stays clean.
To publish it:

```bash
git init
git add .
git commit -m "Initial commit: Library Management System"
git branch -M main
git remote add origin <your-empty-github-repo-url>
git push -u origin main
```

## 13. Project Structure

```
library_management_system/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── config/                  # Django project settings & routing
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── library/                 # Main application
│   ├── models.py            # Book, Member, Transaction
│   ├── serializers.py       # DRF serializers + validation
│   ├── views.py             # API viewsets + dashboard endpoint
│   ├── urls.py               # API routing
│   ├── page_views.py          # Template rendering views
│   ├── admin.py              # Django admin registration
│   └── management/commands/seed_data.py
├── templates/                # Server-rendered HTML pages
│   ├── base.html
│   ├── index.html            # Dashboard
│   ├── books.html
│   ├── members.html
│   └── transactions.html
└── static/
    ├── css/style.css
    └── js/ (api.js, dashboard.js, books.js, members.js, transactions.js)
```

## 14. Future Enhancements

- User authentication & role-based access (librarian vs. admin)
- Email/SMS due-date reminders
- Barcode/QR scanning for faster issue/return
- Export reports (PDF/Excel) of overdue books and fines
- Pagination and bulk import of books via CSV

## 15. Completion Checklist

- [x] Create, Read, Update, Delete for Books
- [x] Create, Read, Update, Delete for Members
- [x] Issue and Return workflow with business rules
- [x] Server-side validation on all inputs
- [x] REST API with documented endpoints
- [x] Responsive, color-coded dashboard UI
- [x] SQLite database with Django ORM
- [x] Git-ready with `.gitignore`
