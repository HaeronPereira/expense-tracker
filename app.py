from flask import Flask, render_template, request, redirect, url_for, Response, flash
from database import get_db_connection, create_tables
import csv
import io

app = Flask(__name__)

app.secret_key = "expense-tracker-development-key"


def safe_csv_value(value):

    if value is None:
        return ""

    text = str(value)

    dangerous_characters = (
        "=",
        "+",
        "-",
        "@"
    )

    if text.startswith(dangerous_characters):
        return "'" + text

    return text

create_tables()


@app.route("/")
def home():

    connection = get_db_connection()

    monthly_expenses = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE strftime('%Y-%m', expense_date)
            = strftime('%Y-%m', 'now', 'localtime')
        """
    ).fetchone()[0]

    unpaid_bills = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM bills
        WHERE status = 'Unpaid'
        """
    ).fetchone()[0]

    paid_bills = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM bills
        WHERE status = 'Paid'
        """
    ).fetchone()[0]

    category_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM categories
        """
    ).fetchone()[0]

    recent_expenses = connection.execute(
        """
        SELECT
            expenses.id,
            expenses.description,
            expenses.amount,
            expenses.expense_date,
            expenses.payment_method,
            categories.name AS category_name
        FROM expenses
        LEFT JOIN categories
            ON expenses.category_id = categories.id
        ORDER BY expenses.expense_date DESC,
                 expenses.id DESC
        LIMIT 5
        """
    ).fetchall()

    category_spending = connection.execute(
        """
        SELECT
            categories.name AS category_name,
            COALESCE(SUM(expenses.amount), 0) AS total_amount
        FROM expenses
        INNER JOIN categories
            ON expenses.category_id = categories.id
        WHERE strftime('%Y-%m', expenses.expense_date)
            = strftime('%Y-%m', 'now', 'localtime')
        GROUP BY categories.id, categories.name
        ORDER BY total_amount DESC
        """
    ).fetchall()


    connection.close()

    return render_template(
        "index.html",
        monthly_expenses=monthly_expenses,
        unpaid_bills=unpaid_bills,
        paid_bills=paid_bills,
        category_count=category_count,
        recent_expenses=recent_expenses,
        category_spending=category_spending
    )


@app.route("/categories", methods=["GET", "POST"])
def categories():

    connection = get_db_connection()

    if request.method == "POST":

        category_name = request.form["category_name"].strip()

        if not category_name:

            connection.close()

            flash(
                "Please enter a category name.",
                "warning"
            )

            return redirect(url_for("categories"))

        try:

            connection.execute(
                """
                INSERT INTO categories (name)
                VALUES (?)
                """,
                (category_name,)
            )

            connection.commit()
            connection.close()

            flash(
                "Category added successfully.",
                "success"
            )

            return redirect(url_for("categories"))

        except Exception:

            connection.close()

            flash(
                "That category already exists.",
                "error"
            )

            return redirect(url_for("categories"))

    categories = connection.execute(
        """
        SELECT *
        FROM categories
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "categories.html",
        categories=categories
    )


@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():

    connection = get_db_connection()

    if request.method == "POST":

        description = request.form["description"].strip()
        amount = request.form["amount"]
        expense_date = request.form["expense_date"]
        category_id = request.form["category_id"]
        payment_method = request.form["payment_method"]
        notes = request.form["notes"].strip()

        connection.execute(
            """
            INSERT INTO expenses
            (
                description,
                amount,
                expense_date,
                category_id,
                payment_method,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                description,
                amount,
                expense_date,
                category_id,
                payment_method,
                notes
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("expenses"))

    categories = connection.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()

    connection.close()

    return render_template(
        "add_expense.html",
        categories=categories
    )

@app.route("/expenses")
def expenses():

    connection = get_db_connection()

    search = request.args.get("search", "").strip()
    category_id = request.args.get("category", "")
    selected_month = request.args.get("month", "")

    query = """
        SELECT
            expenses.id,
            expenses.description,
            expenses.amount,
            expenses.expense_date,
            expenses.payment_method,
            expenses.notes,
            categories.name AS category_name
        FROM expenses
        LEFT JOIN categories
            ON expenses.category_id = categories.id
        WHERE 1 = 1
    """

    parameters = []

    if search:
        query += """
            AND expenses.description LIKE ?
        """

        parameters.append(f"%{search}%")

    if category_id:
        query += """
            AND expenses.category_id = ?
        """

        parameters.append(category_id)

    if selected_month:
        query += """
            AND strftime('%Y-%m', expenses.expense_date) = ?
        """

        parameters.append(selected_month)

    query += """
        ORDER BY expenses.expense_date DESC,
                 expenses.id DESC
    """

    expenses = connection.execute(
        query,
        parameters
    ).fetchall()

    total = sum(
        expense["amount"]
        for expense in expenses
    )

    categories = connection.execute(
        """
        SELECT *
        FROM categories
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "expenses.html",
        expenses=expenses,
        total=total,
        categories=categories,
        search=search,
        selected_category=category_id,
        selected_month=selected_month
    )

@app.route("/edit-expense/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):

    connection = get_db_connection()

    expense = connection.execute(
        """
        SELECT *
        FROM expenses
        WHERE id = ?
        """,
        (expense_id,)
    ).fetchone()

    if expense is None:
        connection.close()
        return "Expense not found", 404

    if request.method == "POST":

        description = request.form["description"].strip()
        amount = request.form["amount"]
        expense_date = request.form["expense_date"]
        category_id = request.form["category_id"]
        payment_method = request.form["payment_method"]
        notes = request.form["notes"].strip()

        connection.execute(
            """
            UPDATE expenses
            SET
                description = ?,
                amount = ?,
                expense_date = ?,
                category_id = ?,
                payment_method = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                description,
                amount,
                expense_date,
                category_id,
                payment_method,
                notes,
                expense_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("expenses"))

    categories = connection.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()

    connection.close()

    return render_template(
        "edit_expense.html",
        expense=expense,
        categories=categories
    )

@app.route("/delete-expense/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM expenses
        WHERE id = ?
        """,
        (expense_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("expenses"))

@app.route("/bills")
def bills():

    connection = get_db_connection()

    bills = connection.execute(
        """
        SELECT
            bills.id,
            bills.name,
            bills.amount,
            bills.due_date,
            bills.status,
            bills.notes,
            categories.name AS category_name
        FROM bills
        LEFT JOIN categories
            ON bills.category_id = categories.id
        ORDER BY bills.due_date ASC,
                 bills.id DESC
        """
    ).fetchall()

    unpaid_total = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM bills
        WHERE status = 'Unpaid'
        """
    ).fetchone()[0]

    paid_total = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM bills
        WHERE status = 'Paid'
        """
    ).fetchone()[0]

    connection.close()

    return render_template(
        "bills.html",
        bills=bills,
        unpaid_total=unpaid_total,
        paid_total=paid_total
    )


@app.route("/add-bill", methods=["GET", "POST"])
def add_bill():

    connection = get_db_connection()

    if request.method == "POST":

        name = request.form["name"].strip()
        amount = request.form["amount"]
        due_date = request.form["due_date"]
        category_id = request.form["category_id"]
        status = request.form["status"]
        notes = request.form["notes"].strip()

        connection.execute(
            """
            INSERT INTO bills
            (
                name,
                amount,
                due_date,
                category_id,
                status,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                amount,
                due_date,
                category_id,
                status,
                notes
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("bills"))

    categories = connection.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()

    connection.close()

    return render_template(
        "add_bill.html",
        categories=categories
    )

@app.route("/toggle-bill-status/<int:bill_id>", methods=["POST"])
def toggle_bill_status(bill_id):

    connection = get_db_connection()

    bill = connection.execute(
        """
        SELECT status
        FROM bills
        WHERE id = ?
        """,
        (bill_id,)
    ).fetchone()

    if bill is None:
        connection.close()
        return "Bill not found", 404

    if bill["status"] == "Paid":
        new_status = "Unpaid"
    else:
        new_status = "Paid"

    connection.execute(
        """
        UPDATE bills
        SET status = ?
        WHERE id = ?
        """,
        (new_status, bill_id)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("bills"))

@app.route("/edit-bill/<int:bill_id>", methods=["GET", "POST"])
def edit_bill(bill_id):

    connection = get_db_connection()

    bill = connection.execute(
        """
        SELECT *
        FROM bills
        WHERE id = ?
        """,
        (bill_id,)
    ).fetchone()

    if bill is None:
        connection.close()
        return "Bill not found", 404

    if request.method == "POST":

        name = request.form["name"].strip()
        amount = request.form["amount"]
        due_date = request.form["due_date"]
        category_id = request.form["category_id"]
        status = request.form["status"]
        notes = request.form["notes"].strip()

        connection.execute(
            """
            UPDATE bills
            SET
                name = ?,
                amount = ?,
                due_date = ?,
                category_id = ?,
                status = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                name,
                amount,
                due_date,
                category_id,
                status,
                notes,
                bill_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(url_for("bills"))

    categories = connection.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()

    connection.close()

    return render_template(
        "edit_bill.html",
        bill=bill,
        categories=categories
    )

@app.route("/delete-bill/<int:bill_id>", methods=["POST"])
def delete_bill(bill_id):

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM bills
        WHERE id = ?
        """,
        (bill_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("bills"))


@app.route("/reports")
def reports():

    connection = get_db_connection()

    selected_month = request.args.get("month")

    if not selected_month:
        selected_month = connection.execute(
            """
            SELECT strftime('%Y-%m', 'now', 'localtime')
            """
        ).fetchone()[0]

    expenses = connection.execute(
        """
        SELECT
            expenses.id,
            expenses.description,
            expenses.amount,
            expenses.expense_date,
            expenses.payment_method,
            categories.name AS category_name
        FROM expenses
        LEFT JOIN categories
            ON expenses.category_id = categories.id
        WHERE strftime('%Y-%m', expenses.expense_date) = ?
        ORDER BY expenses.expense_date DESC,
                 expenses.id DESC
        """,
        (selected_month,)
    ).fetchall()

    total_spending = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE strftime('%Y-%m', expense_date) = ?
        """,
        (selected_month,)
    ).fetchone()[0]

    category_spending = connection.execute(
        """
        SELECT
            categories.name AS category_name,
            SUM(expenses.amount) AS total_amount
        FROM expenses
        INNER JOIN categories
            ON expenses.category_id = categories.id
        WHERE strftime('%Y-%m', expenses.expense_date) = ?
        GROUP BY categories.id, categories.name
        ORDER BY total_amount DESC
        """,
        (selected_month,)
    ).fetchall()

    expense_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM expenses
        WHERE strftime('%Y-%m', expense_date) = ?
        """,
        (selected_month,)
    ).fetchone()[0]

    connection.close()

    return render_template(
        "reports.html",
        expenses=expenses,
        total_spending=total_spending,
        category_spending=category_spending,
        expense_count=expense_count,
        selected_month=selected_month
    )

@app.route("/export-expenses")
def export_expenses():

    connection = get_db_connection()

    search = request.args.get("search", "").strip()
    category_id = request.args.get("category", "")
    selected_month = request.args.get("month", "")

    query = """
        SELECT
            expenses.expense_date,
            expenses.description,
            categories.name AS category_name,
            expenses.payment_method,
            expenses.amount,
            expenses.notes
        FROM expenses
        LEFT JOIN categories
            ON expenses.category_id = categories.id
        WHERE 1 = 1
    """

    parameters = []

    if search:

        query += """
            AND expenses.description LIKE ?
        """

        parameters.append(f"%{search}%")

    if category_id:

        query += """
            AND expenses.category_id = ?
        """

        parameters.append(category_id)

    if selected_month:

        query += """
            AND strftime('%Y-%m', expenses.expense_date) = ?
        """

        parameters.append(selected_month)

    query += """
        ORDER BY expenses.expense_date DESC,
                 expenses.id DESC
    """

    expenses = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow(
        [
            "Date",
            "Description",
            "Category",
            "Payment Method",
            "Amount",
            "Notes"
        ]
    )

    for expense in expenses:

        writer.writerow(
            [
                expense["expense_date"],
                safe_csv_value(expense["description"]),
                safe_csv_value(expense["category_name"]),
                safe_csv_value(expense["payment_method"]),
                expense["amount"],
                safe_csv_value(expense["notes"])
            ]
        )

    csv_content = "\ufeff" + output.getvalue()

    filename = "expenses.csv"

    if selected_month:
        filename = f"expenses-{selected_month}.csv"

    return Response(
        csv_content,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition":
                f"attachment; filename={filename}"
        }
    )

@app.route("/edit-category/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):

    connection = get_db_connection()

    category = connection.execute(
        """
        SELECT *
        FROM categories
        WHERE id = ?
        """,
        (category_id,)
    ).fetchone()

    if category is None:

        connection.close()

        flash(
            "Category could not be found.",
            "error"
        )

        return redirect(url_for("categories"))

    if request.method == "POST":

        category_name = request.form["category_name"].strip()

        if not category_name:

            connection.close()

            flash(
                "Please enter a category name.",
                "warning"
            )

            return redirect(
                url_for(
                    "edit_category",
                    category_id=category_id
                )
            )

        try:

            connection.execute(
                """
                UPDATE categories
                SET name = ?
                WHERE id = ?
                """,
                (category_name, category_id)
            )

            connection.commit()
            connection.close()

            flash(
                "Category updated successfully.",
                "success"
            )

            return redirect(url_for("categories"))

        except Exception:

            connection.close()

            flash(
                "A category with that name already exists.",
                "error"
            )

            return redirect(
                url_for(
                    "edit_category",
                    category_id=category_id
                )
            )

    connection.close()

    return render_template(
        "edit_category.html",
        category=category
    )

@app.route("/delete-category/<int:category_id>", methods=["POST"])
def delete_category(category_id):

    connection = get_db_connection()

    category = connection.execute(
        """
        SELECT *
        FROM categories
        WHERE id = ?
        """,
        (category_id,)
    ).fetchone()

    if category is None:

        connection.close()

        flash(
            "Category could not be found.",
            "error"
        )

        return redirect(url_for("categories"))

    expense_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM expenses
        WHERE category_id = ?
        """,
        (category_id,)
    ).fetchone()[0]

    bill_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM bills
        WHERE category_id = ?
        """,
        (category_id,)
    ).fetchone()[0]

    if expense_count > 0 or bill_count > 0:

        connection.close()

        flash(
            "This category cannot be deleted because it is being used by an expense or bill.",
            "warning"
        )

        return redirect(url_for("categories"))

    connection.execute(
        """
        DELETE FROM categories
        WHERE id = ?
        """,
        (category_id,)
    )

    connection.commit()
    connection.close()

    flash(
        "Category deleted successfully.",
        "success"
    )

    return redirect(url_for("categories"))

if __name__ == "__main__":
    app.run(debug=True)