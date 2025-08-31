from flask import Flask, render_template, request, redirect
import csv, os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "transactions.csv"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "description", "category", "type", "amount"])

def read_transactions():
    transactions = []
    with open(DATA_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append(row)
    return transactions

def write_transaction(date, description, category, ttype, amount):
    transactions = read_transactions()
    new_id = len(transactions) + 1
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([new_id, date, description, category, ttype, amount])

def update_transaction(tid, date, description, category, ttype, amount):
    transactions = read_transactions()
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "description", "category", "type", "amount"])
        for row in transactions:
            if row["id"] == tid:
                writer.writerow([tid, date, description, category, ttype, amount])
            else:
                writer.writerow([row["id"], row["date"], row["description"], row["category"], row["type"], row["amount"]])

def delete_transaction(tid):
    transactions = read_transactions()
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "description", "category", "type", "amount"])
        for row in transactions:
            if row["id"] != tid:
                writer.writerow([row["id"], row["date"], row["description"], row["category"], row["type"], row["amount"]])

def format_amount(value, ttype=None):
    value = float(value)
    if ttype == "income":
        return f"+ ₹{value:,.2f}"
    elif ttype == "expense":
        return f"- ₹{value:,.2f}"
    else:
        if value > 0:
            return f"+ ₹{value:,.2f}"
        elif value < 0:
            return f"- ₹{abs(value):,.2f}"
        return "₹0.00"

def format_date(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%d %b, %Y")
    except:
        return date_str

@app.route("/")
def index():
    filter_category = request.args.get("category", "all")
    filter_type = request.args.get("type", "all")
    filter_year = request.args.get("year", "all")
    filter_month = request.args.get("month", "all")

    transactions = read_transactions()

    filtered = []
    for t in transactions:
        d = datetime.strptime(t["date"], "%Y-%m-%d")
        if filter_category != "all" and t["category"] != filter_category:
            continue
        if filter_type != "all" and t["type"] != filter_type:
            continue
        if filter_year != "all" and str(d.year) != filter_year:
            continue
        if filter_month != "all" and str(d.month) != filter_month:
            continue
        t["formatted_amount"] = format_amount(t["amount"], t["type"])
        t["formatted_date"] = format_date(t["date"])
        filtered.append(t)

    income = sum(float(t["amount"]) for t in filtered if t["type"] == "income")
    expenses = sum(float(t["amount"]) for t in filtered if t["type"] == "expense")
    balance = income - expenses

    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]

    return render_template("index.html",
                           transactions=filtered,
                           summary={
                               "income": format_amount(income, "income"),
                               "expenses": format_amount(expenses, "expense"),
                               "balance": format_amount(balance)
                           },
                           selected_category=filter_category,
                           selected_type=filter_type,
                           selected_year=filter_year,
                           selected_month=filter_month,
                           months=months)

@app.route("/add", methods=["POST"])
def add():
    date = request.form["date"]
    description = request.form["description"]
    category = request.form["category"]
    ttype = request.form["type"]
    amount = request.form["amount"]
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    write_transaction(date, description, category, ttype, amount)
    return redirect("/")

@app.route("/edit/<tid>", methods=["POST"])
def edit(tid):
    date = request.form["date"]
    description = request.form["description"]
    category = request.form["category"]
    ttype = request.form["type"]
    amount = request.form["amount"]
    update_transaction(tid, date, description, category, ttype, amount)
    return redirect("/")

@app.route("/delete/<tid>")
def delete(tid):
    delete_transaction(tid)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
