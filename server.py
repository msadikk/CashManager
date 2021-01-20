from flask import Flask, render_template, session, redirect, request, url_for
from flask_login import LoginManager
from forms import LoginForm, RegisterForm, LimitsForm, CurrentWalletForm, AddExpenseForm, PersonalInfoForm, InOutComesForm
from forms import ChooseCategoryForm, DeleteAccount
import mysql.connector
from functions import register, update_wallet, update_limit, add_expense, check_daily_limit, check_weekly_limit, check_monthy_limit
from functions import update_profile, update_comes, site_info, categorised_expenses, update_salary_vs, money_left, delete_expense
from functions import get_limits, delete_account
from passlib.hash import pbkdf2_sha256 as hasher
import database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecretkey'


mydb=mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="password",
    database="CashManager")

mycursor = mydb.cursor(dictionary=True)

for table in database.tables:
    mycursor.execute(table)
    mydb.commit()


@app.route('/')
def home_page():
    info = site_info(mycursor)
    return render_template("home.html", info=info)

@app.route('/settings', methods=['POST', 'GET'])
def settings_page():
    wallet_form = CurrentWalletForm()
    limit_form = LimitsForm()

    if wallet_form.validate_on_submit() and wallet_form.submit2.data == True:
        update_wallet(wallet_form, mycursor, mydb)
        return redirect(url_for('settings_page'))
    
    if limit_form.is_submitted() and limit_form.submit1.data == True:
        update_limit(limit_form, mycursor, mydb)
        return redirect(url_for('settings_page'))

    sql = "select wallet_id from user where user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    wallet_id = mycursor.fetchone()
    id = wallet_id['wallet_id']

    sql = "select * from wallet where wallet_id=%s"
    mycursor.execute(sql, (id, ))
    wallet = mycursor.fetchone()
    
    return render_template("settings.html", wallet_form=wallet_form, limit_form=limit_form, wallet=wallet)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses_page():
    exp_form = AddExpenseForm(request.form)

    if exp_form.validate_on_submit() and exp_form.submit1.data == True:
        add_expense(exp_form, mycursor, mydb)
        return redirect(url_for('expenses_page'))

    if request.method == 'POST':
        exp = request.form.getlist('deletebox')
        delete_expense(mycursor, mydb, exp)
        return redirect(url_for('expenses_page'))
    
    categorised = categorised_expenses(mycursor)

    sql = "SELECT * FROM expense WHERE user_id=%s ORDER BY date ASC "
    mycursor.execute(sql, (session['user_id'], ))
    expenses = mycursor.fetchall()

    return render_template("expenses.html", exp_form=exp_form, expenses=expenses, categorised=categorised)

@app.route('/profile')
def profile_page():
    daily_state = check_daily_limit(mycursor)
    if len(daily_state) == 0:
        daily_state = None

    weekly_state = check_weekly_limit(mycursor)
    if len(weekly_state) == 0:
        weekly_state = None

    monthly_state = check_monthy_limit(mycursor)
    if len(monthly_state) == 0:
        monthly_state = None

    left = money_left(mycursor)
    limits = get_limits(mycursor)

    return render_template("profile.html", daily_state=daily_state, weekly_state=weekly_state, monthly_state=monthly_state, left=left, limits=limits )

@app.route('/profile_settings', methods=['GET', 'POST'])
def profile_settings_page():
    set_form = PersonalInfoForm(request.form)
    comes_form = InOutComesForm(request.form)
    delete_form = DeleteAccount(request.form)

    if set_form.validate_on_submit() and set_form.submit.data == True:

        update_profile(set_form, mycursor, mydb)
        return redirect(url_for('profile_settings_page'))
    
    if comes_form.is_submitted and comes_form.submit1.data == True:
        update_comes(comes_form, mycursor, mydb)
        return redirect(url_for('profile_settings_page'))

    if delete_form.is_submitted() and delete_form.submit3.data == True:
        if delete_form.permission.data == "DeLetE mY AcCounT":
            delete_account(mycursor, mydb)
    

    sql = "select * from user where user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    user = mycursor.fetchone()

    sql = "select * from fixed_income where income_id=%s"
    mycursor.execute(sql, (user['income_id'], ))
    ins = mycursor.fetchone()

    sql = "select * from fixed_outcome where outcome_id=%s"
    mycursor.execute(sql, (user['outcome_id'], ))
    outs = mycursor.fetchone()

    return render_template("profile_settings.html", set_form=set_form, comes_form=comes_form, user=user, ins=ins, outs=outs, delete_form=delete_form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm(request.form)

    if form.validate_on_submit():

    
        sql = "SELECT user_id, password from user WHERE email=%s"
        mycursor.execute(sql, (form.email.data, ))
        user = mycursor.fetchone()

        login = hasher.verify(form.password.data, user['password']) 

        if id != None and login == True:
            session['user_id'] = user['user_id']
            update_salary_vs(mycursor, mydb)
            return redirect('/profile')

    
    return render_template("login.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        
        sql = "SELECT email FROM user WHERE email=%s"
        mycursor.execute(sql, (form.email.data, ))
        match = mycursor.fetchone()

        if match != None:
            return redirect('/register')

        hashed = hasher.hash(form.password.data)
        session['user_id'] = register(form.email.data, hashed, mycursor, mydb)
        return redirect('/profile')

    return render_template("register.html", form=form)

@app.route('/logout')
def logout_page():
    if 'user_id' not in session:
        return redirect('/')

    session.pop('user_id')
    return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)