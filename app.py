import os
from datetime import date
import sqlite3
import re
from helpers import lookup
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["TEMPLATES_AUTO_RELOAD"] = True
Session(app)
#print(app.config)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    con = sqlite3.connect("finance.db")
    db = con.cursor()
    db.execute("SELECT cash FROM users WHERE username=?",(user_id,))
    rows = str(db.fetchone())
    rows = rows.replace("'", "")
    rows = rows.replace("(", "")
    rows = rows.replace(",", "")
    balance = rows.replace(")", "")
    return render_template("home.html", user_id=user_id, balance=balance)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method=="GET" :
        return render_template("buy.html")
    else:
        username = session["user_id"]
        s = request.form.get("sym")
        s = s.upper()
        con = sqlite3.connect("stock.db")
        db = con.cursor()
        table_name = 'data'
        column_name = s
        number = int(request.form.get("name"))
        # Check if the column exists
        db.execute(f"PRAGMA table_info({table_name})")
        columns = db.fetchall()
        column_names = [col[1] for col in columns]
        if column_name in column_names:
            ds = con.cursor()
            s = request.form.get("sym")
            s = s.upper()
            try:
                a = lookup(s)
                b = float(a["price"])
                q = sqlite3.connect("finance.db")
                w = q.cursor()
                w.execute("SELECT cash FROM users WHERE username=?",(username,))
                rows = w.fetchone()
                rows = str(rows[0])
                rows = rows.replace("'", "")
                rows = rows.replace("(", "")
                rows = rows.replace(")", "")
                n = float(rows)
                p = b * number
                if p > n:
                    x = n/b
                    x = round(x)
                    return render_template("failnb.html",n=n,x=x,s=s)
                else:
                    ds.execute(f"SELECT {s} FROM data WHERE username=?",(username,))
                    rows = ds.fetchone()
                    rows = str(rows[0])
                    rows = rows.replace("'", "")
                    rows = rows.replace("(", "")
                    rows = rows.replace(")", "")
                    try:
                        x = int(rows)
                    except ValueError:
                        x = 0
                    n = n - p
                    x = x + number
                    dm = con.cursor()
                    dm.execute(f"UPDATE data SET {s}={x} WHERE username=?",(username,))
                    con.commit()
                    ds = q.cursor()
                    ds.execute(f"UPDATE users SET cash={n} WHERE username=?",(username,))
                    q.commit()
                    k = sqlite3.connect("h.db")
                    q = k.cursor()
                    j = "buy"
                    r = date.today()
                    q.execute("INSERT INTO history (username, name, type, amount, value, date) VALUES(?,?,?,?,?,?)",(username, s, j, number, p, r))
                    k.commit()
                    return render_template("succesbuy.html", x=x,s=s)
            except sqlite3.OperationalError:
                x = 0
                q = sqlite3.connect("finance.db")
                w = q.cursor()
                w.execute("SELECT cash FROM users WHERE username=?",(username,))
                rows = w.fetchone()
                rows = str(rows[0])
                rows = rows.replace("'", "")
                rows = rows.replace("(", "")
                rows = rows.replace(")", "")
                n = float(rows)
                a = request.form.get("sym")
                a = lookup(a)
                a = float(a["price"])
                p = a * number
                if p > n:
                    x = n/a
                    x = round(x)
                    return render_template("failnb.html",n=n,x=x,s=s)
                else:
                    
                    x = x + number
                    n = n - p
                    dm = con.cursor()
                    h = request.form.get("sym")
                    dm.execute(f"UPDATE data SET {h}={x} WHERE username=?",(username,))
                    con.commit()
                    ds = q.cursor()
                    ds.execute(f"UPDATE users SET cash={n} WHERE username=?",(username,))
                    q.commit()
                    k = sqlite3.connect("h.db")
                    w = k.cursor()
                    j = "buy"
                    r = date.today()
                    w.execute("INSERT INTO history (username, name, type, amount, value, date) VALUES(?,?,?,?,?,?)",(username, s, j, number, p, r))
                    k.commit()
                    return render_template("succesbuy.html",x=x,s=s)
        else:
            s = request.form.get("sym")
            s = s.upper()
            a = lookup(s)
            try:
                a = float(a["price"])
                p = number * a
                q = sqlite3.connect("finance.db")
                w = q.cursor()
                w.execute("SELECT cash FROM users WHERE username=?",(username,))
                rows = w.fetchone()
                rows = str(rows[0])
                rows = rows.replace("'", "")
                rows = rows.replace("(", "")
                rows = rows.replace(")", "")
                n = float(rows)
                if p > n:
                    x = n/a
                    x = round(x)
                    return render_template("failnb.html",n=n,x=x,s=s)
                else:
                    k = con.cursor()
                    data_type = "INTERGER"
                    k.execute(f"ALTER TABLE data ADD COLUMN {s} {data_type}")
                    con.commit()
                    l = con.cursor()
                    l.execute(f"UPDATE data SET {s}={number} WHERE username=?",(username,))
                    con.commit()
                    n = n - p
                    e = q.cursor()
                    e.execute(f"UPDATE users SET cash={n} WHERE username=?",(username,))
                    q.commit()
                    x = number
                    k = sqlite3.connect("h.db")
                    q = k.cursor()
                    j = "buy"
                    r = date.today()
                    q.execute("INSERT INTO history (username, name, type, amount, value, date) VALUES(?,?,?,?,?,?)",(username, s, j, number, p, r))
                    k.commit()
                    return render_template("succesbuy.html",x=x,s=s)
            except TypeError:
                return render_template("std.html",s=s)



@app.route("/history")
@login_required
def history():
    username=session["user_id"]
    a = sqlite3.connect("h.db")
    b = a.cursor()
    rows = b.execute("SELECT * FROM history WHERE username=?",(username,))
    rows = rows.fetchall()
    return render_template("his.html", data = rows)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    con = sqlite3.connect("finance.db")
    db = con.cursor()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        us = request.form.get("username")
        # Query database for username
        pas = request.form.get("password")
        db.execute("SELECT hash FROM users WHERE username=?",(us,))
        rows = db.fetchone()
        if rows:
            rows = str(rows[0])
            rows = rows.replace("'", "")
            rows = rows.replace("(", "")
            rows = rows.replace(")", "")
            if rows == pas:
                session["user_id"] = us
                session["username"] = request.form.get("username")
                return redirect("/")
            else:
                return render_template("test.html")
        else:
            return render_template("us.html")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")
    else:
        x = lookup(request.form.get("sym"))
        name = request.form.get("sym")
        n = int(request.form.get("name"))
        p = float(x["price"])
        p = p * n
        return render_template("price.html", p=p, name=name, n=n)
    





@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        hash = request.form.get("password")
        con = sqlite3.connect("finance.db")
        db = con.cursor()
        db.execute("SELECT * FROM users WHERE username=?",(username,))
        result = db.fetchone()
        if result:
            return render_template("useuser.html")
        else:
            db.execute("INSERT INTO users (username, hash, cash) VALUES (?, ?, 10000)", (username, hash))
            con.commit()
            a = sqlite3.connect("stock.db")
            b = a.cursor()
            b.execute("INSERT INTO data (username, a, b, c) VALUES (?, 0, 0, 0)", (username,))
            a.commit()
            return render_template("succesre.html")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method=="GET":
        return render_template("sell.html")
    else:
        username = session["user_id"]
        s = request.form.get("sym")
        s = s.upper()
        con = sqlite3.connect("stock.db")
        db = con.cursor()
        table_name = 'data'
        column_name = s
        number = int(request.form.get("num"))
        # Check if the column exists
        db.execute(f"PRAGMA table_info({table_name})")
        columns = db.fetchall()
        column_names = [col[1] for col in columns]
        if column_name in column_names:
            a = con.cursor()
            a.execute(f"SELECT {s} FROM data WHERE username=?",(username,))
            rows = a.fetchone()
            if rows:
                rows = str(rows[0])
                rows = rows.replace("'", "")
                rows = rows.replace("(", "")
                rows = rows.replace(")", "")
                try:
                    n = int(rows)
                    if n < number:
                        return render_template("failsell.html", n=n,s=s)
                    else:
                        a = lookup(s)
                        a = float(a["price"])
                        a = a * number
                        n = n - number
                        q = con.cursor()
                        q.execute(f"UPDATE data SET {s}={n} WHERE username=?",(username,))
                        con.commit()
                        b = sqlite3.connect("finance.db")
                        c = b.cursor()
                        c.execute(f"SELECT cash FROM users WHERE username=?",(username,))
                        rows = c.fetchone()
                        rows = str(rows[0])
                        rows = rows.replace("'", "")
                        rows = rows.replace("(", "")
                        rows = float(rows.replace(")", ""))
                        rows = rows + a
                        d = b.cursor()
                        d.execute(f"UPDATE users SET cash={rows} WHERE username=?",(username,))
                        b.commit()
                        k = sqlite3.connect("h.db")
                        q = k.cursor()
                        j = "sell"
                        r = date.today()
                        q.execute("INSERT INTO history (username, name, type, amount, value, date) VALUES(?,?,?,?,?,?)",(username, s, j, number, a, r))
                        k.commit()
                        return render_template("succesel.html",number=number,s=s)
                except ValueError:
                    return render_template("failnst.html",s=s)
                except TypeError:
                    return render_template("std.html",s=s)
            else:
                return render_template("failnst.html",s=s)
        else:
            return render_template("failnst.html",s=s)

@app.route("/top",methods=["GET", "POST"])
@login_required
def top():
    if request.method=="GET":
        return render_template("top.html")
    else:
        a = request.form.get("amount")
        try:
            a = float(a)
        except ValueError:
            return render_template("failtop.html")
        s = sqlite3.connect("finance.db")
        q = s.cursor()
        username = session["user_id"]
        q.execute("SELECT cash from users WHERE username=?",(username,))
        m = q.fetchone()
        m = float(m[0])
        m = m + a
        j = s.cursor()
        j.execute(f"UPDATE users SET cash={m} WHERE username=?",(username,))
        s.commit()
        w = sqlite3.connect("h.db")
        r = w.cursor()
        h = date.today()
        r.execute("INSERT INTO history (username, name, type, amount, value, date) VALUES(?,?,?,?,?,?)",(username, "-", "Top up", "-", a, h))
        w.commit()
        return render_template("succestop.html", m=m)
        
@app.route("/Inventory")
@login_required
def invent():
    a = sqlite3.connect("stock.db")
    b = a.cursor()
    table_name = "data"
    rows = b.execute(f"PRAGMA table_info({table_name})")
    rows = rows.fetchall()
    username = session["user_id"]
    i = 1
    v= []
    while i < len(rows):
        c = a.cursor()
        q = rows[i]
        q = q[1]
        c.execute(f"SELECT {q} FROM data WHERE username=?",(username,))
        x = c.fetchone()
        x = x[0]
        if str(x)=="None":
            i = i + 1
            pass
        elif str(x)=="0":
            i = i + 1
            pass
        else:
            v.append([q,x])
            i = i + 1
            pass
    return render_template("store.html", rows=v)








    




