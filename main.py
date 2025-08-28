from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Date
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)

class Exp(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(Date)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(50))
    amount: Mapped[int] = mapped_column(Integer)

class Category(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

@app.route('/')
def home():
    month = request.args.get("month")
    category_filter = request.args.get("category")
    query = Exp.query.order_by(Exp.date.desc())

    if month:
        year, m = map(int, month.split("-"))
        query = query.filter(
            db.extract("year", Exp.date) == year,
            db.extract("month", Exp.date) == m
        )

    if category_filter and category_filter != "all":
        query = query.filter_by(category=category_filter)

    expenses = query.all()
    categories = [c.name for c in Category.query.all()]

    total_income = sum(e.amount for e in expenses if e.type == "income")
    total_expense = sum(e.amount for e in expenses if e.type == "expense")
    balance = total_income - total_expense

    return render_template(
        'index.html',
        expenses=expenses,
        categories=categories,
        datetime=datetime,
        selected_month=month,
        selected_category=category_filter or "all",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )

@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form['date']
    name = request.form['name']
    type_ = request.form['type']
    category = request.form['category']
    amount = request.form['amount']

    new_exp = Exp(
        date=datetime.strptime(date, "%Y-%m-%d").date(),
        name=name,
        type=type_,
        category=category,
        amount=int(amount)
    )
    db.session.add(new_exp)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_expense(id):
    exp = Exp.query.get_or_404(id)
    exp.date = request.form['date']
    exp.name = request.form['name']
    exp.type = request.form['type']
    exp.category = request.form['category']
    exp.amount = int(request.form['amount'])
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_expense(id):
    exp = Exp.query.get_or_404(id)
    db.session.delete(exp)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['name']
    if not Category.query.filter_by(name=name).first():
        db.session.add(Category(name=name))
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        defaults = ["Food", "Transport", "Shopping", "Bills", "Salary"]
        for d in defaults:
            if not Category.query.filter_by(name=d).first():
                db.session.add(Category(name=d))
        db.session.commit()
    app.run(debug=True, host="0.0.0.0")