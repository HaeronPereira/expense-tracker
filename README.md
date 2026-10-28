# 💰 Personal Expense Tracker

A modern personal finance web application built with **Python, Flask and SQLite** for tracking expenses, managing bills, organising spending categories and analysing monthly expenditure.

The application provides a simple dashboard for understanding where money is being spent while keeping expense and bill management straightforward.

---

## ✨ Features

### 📊 Dashboard

The dashboard provides an overview of your finances, including:

- Monthly spending
- Outstanding bills
- Paid bills
- Total expense categories
- Recent expenses
- Spending breakdown by category

---

### 💳 Expense Management

Create and manage everyday expenses.

Features include:

- Add expenses
- View all expenses
- Edit existing expenses
- Delete expenses
- Assign categories
- Record payment methods
- Add notes
- Track expense dates
- Automatically calculate expense totals

---

### 🔍 Expense Search & Filtering

Expenses can be filtered using:

- Description search
- Category
- Month

Multiple filters can be combined to quickly locate specific transactions.

---

### 🧾 Bill Management

Keep track of recurring and one-off bills.

Features include:

- Add bills
- Edit bills
- Delete bills
- Set due dates
- Assign categories
- Add notes
- Mark bills as **Paid**
- Mark bills as **Unpaid**
- Calculate paid and outstanding bill totals

---

### 🗂️ Category Management

Create your own spending categories.

Examples:

- Groceries
- Transport
- Utilities
- Entertainment
- Shopping
- Subscriptions
- Eating Out

Categories can be:

- Created
- Edited
- Deleted
- Assigned to expenses
- Assigned to bills

The application prevents categories that are currently associated with expenses or bills from being deleted accidentally.

---

### 📈 Reports

The Reports page provides monthly spending analysis.

You can:

- Select a month
- View total monthly spending
- View transaction count
- View expenses for the selected month
- Analyse spending by category

---

## 🛠️ Technology Stack

### Backend

- Python
- Flask

### Frontend

- HTML5
- CSS3
- Jinja templates

### Database

- SQLite

### Development & Version Control

- Visual Studio Code
- Git
- GitHub

---

## 🏗️ Project Structure

```text
expense-tracker/
│
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
│
├── templates/
│   ├── index.html
│   ├── expenses.html
│   ├── add_expense.html
│   ├── edit_expense.html
│   ├── bills.html
│   ├── add_bill.html
│   ├── edit_bill.html
│   ├── categories.html
│   ├── edit_category.html
│   └── reports.html
│
└── static/
    └── css/
        └── style.css
```

---

## 🚀 Running the Project Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Move into the project:

```bash
cd expense-tracker
```

---

### 2. Create a virtual environment

On macOS/Linux:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create the database

```bash
python database.py
```

This creates the local SQLite database and the required tables.

---

### 5. Start the Flask application

```bash
python app.py
```

Flask will display the local application address in the terminal.

Open that address in your browser.

---

## 🗄️ Database Structure

The application uses three main entities:

### Expenses

Stores:

- Description
- Amount
- Expense date
- Category
- Payment method
- Notes
- Created date

### Bills

Stores:

- Bill name
- Amount
- Due date
- Category
- Payment status
- Notes
- Created date

### Categories

Stores user-defined expense and bill categories.

Relationships are maintained using category IDs rather than copying category names into individual transactions.

---

## 🔐 Security & Privacy

The local SQLite database should not be committed to the public repository.

The `.gitignore` file should contain:

```text
.venv/
__pycache__/
.DS_Store
.env
expense_tracker.db
```

This helps prevent local financial information, environment files and development artefacts from being uploaded to GitHub.

> **Important:** The current project is intended as a personal/portfolio application. Authentication should be added before storing real personal financial information on a publicly accessible deployment.

---

## 🌐 Deployment

The application is designed as a Flask web application and can be deployed to a Python-compatible hosting service.

The development workflow is:

```text
VS Code
   ↓
Git
   ↓
GitHub
   ↓
Python Hosting
   ↓
Public Web Application
```

---

## 🔮 Future Improvements

Potential future features include:

- 🔐 User authentication
- 👤 Multiple user accounts
- 📊 Interactive charts
- 💰 Monthly budgets
- ⚠️ Budget alerts
- 🔁 Recurring expenses and bills
- 📤 CSV export
- 📥 CSV import
- 📱 Improved mobile experience
- 🌙 Dark mode
- 📅 Custom date-range reports
- 💾 PostgreSQL support
- ☁️ Cloud deployment
- 🤖 AI-powered spending insights

---

## 💡 Example Workflow

```text
Create Category
      ↓
Add Expense
      ↓
Assign Category
      ↓
Store in SQLite
      ↓
View Dashboard
      ↓
Search / Filter Expenses
      ↓
Analyse Monthly Report
```

---

## 🎯 Project Purpose

This project was created to practise building an end-to-end web application covering:

- Frontend development
- Python backend development
- Flask routing
- CRUD operations
- Relational data
- SQLite database operations
- Filtering and reporting
- Git/GitHub version control
- Web application deployment

It demonstrates how a complete application can evolve from a simple Flask page into a functional personal finance management system.

---

## 👨‍💻 Author

**Haeron Pereira**

AI Engineer / Software Engineer

Areas of interest:

- Generative AI
- Large Language Models
- Retrieval-Augmented Generation (RAG)
- Agentic AI
- Python
- APIs
- Azure AI
- Full-stack application development

---

## 📄 Licence

This project is intended for personal learning and portfolio purposes.
