from flask import session
from datetime import date, timedelta

def register(email, password, mycursor, mydb):

    #create incomes
    sql = "INSERT INTO fixed_income (salary, scholarship, in_other) VALUES(%s, %s, %s)"
    mycursor.execute(sql, (0, 0, 0))
    
    #create outcomes
    sql = "INSERT INTO fixed_outcome (rent, bills, out_other) VALUES(%s, %s, %s)"
    mycursor.execute(sql, (0, 0, 0))

    #create wallet
    sql = "INSERT INTO wallet (debit_card, cash, total) VALUES(%s, %s, %s)"
    mycursor.execute(sql, (0, 0, 0))
    
    mydb.commit()

    sql = "SELECT income_id FROM fixed_income ORDER BY income_id DESC LIMIT 1"
    mycursor.execute(sql)
    fi = mycursor.fetchone()

    sql = "SELECT outcome_id FROM fixed_outcome ORDER BY outcome_id DESC LIMIT 1"
    mycursor.execute(sql)
    fo = mycursor.fetchone()

    sql = "SELECT wallet_id FROM wallet ORDER BY wallet_id DESC LIMIT 1"
    mycursor.execute(sql)
    w = mycursor.fetchone()

    sql = "INSERT INTO user (email, password, income_id, outcome_id, wallet_id) VALUES(%s, %s, %s, %s, %s)"
    val = (email, password, fi['income_id'], fo['outcome_id'], w['wallet_id'])
    mycursor.execute(sql, val)
    mydb.commit()

    sql = "SELECT user_id FROM user ORDER BY user_id DESC LIMIT 1"
    mycursor.execute(sql)
    user = mycursor.fetchone()
    
    return user['user_id']

def update_wallet(form, mycursor, mydb):
    sql = "SELECT wallet_id FROM user WHERE user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    w = mycursor.fetchone()

    sql = "UPDATE wallet SET debit_card=%s, cash=%s, total=%s WHERE wallet_id=%s"
    val = (form.debit.data, form.cash.data, form.debit.data + form.cash.data, w['wallet_id'])
    mycursor.execute(sql, val)
    mydb.commit()

def update_limit(form, mycursor, mydb):
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], form.limit_type.data))
    limit = mycursor.fetchone()

    if limit == None:
        sql = "INSERT INTO limits (expense_type, daily, weekly, monthly, user_id) VALUES(%s, %s, %s, %s, %s)"
        val = (form.limit_type.data, form.daily.data, form.weekly.data, form.monthly.data, session['user_id'])
        mycursor.execute(sql, val)
        mydb.commit()

    else:
        sql = "UPDATE limits SET daily=%s, weekly=%s, monthly=%s WHERE user_id=%s AND expense_type=%s"
        val = (form.daily.data, form.weekly.data, form.monthly.data, session['user_id'], form.limit_type.data)
        mycursor.execute(sql,val)
        mydb.commit()

def add_expense(form, mycursor, mydb):
    sql = "INSERT INTO expense (expense_type, payment, amount, date, user_id) VALUES(%s, %s, %s, %s, %s)"
    val = (form.expense_type.data, form.payment.data, form.amount.data, form.date.data, session['user_id'])
    mycursor.execute(sql, val)
    mydb.commit()

    sql = "SELECT wallet_id FROM user WHERE user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    wid = mycursor.fetchone()

    sql = "SELECT * FROM wallet WHERE wallet_id=%s"
    mycursor.execute(sql, (wid['wallet_id'], ))
    the_wallet = mycursor.fetchone()
    
    if form.payment.data == 'cash':
        sql = "UPDATE wallet SET cash=%s, total=%s WHERE wallet_id=%s"
        val = (the_wallet['cash'] - float(form.amount.data), the_wallet['total'] - float(form.amount.data), wid['wallet_id'])
    
    else:
        sql = "UPDATE wallet SET debit_card=%s, total=%s WHERE wallet_id=%s "
        val = (the_wallet['debit_card'] - float(form.amount.data), the_wallet['total'] - float(form.amount.data), wid['wallet_id'])

    mycursor.execute(sql, val)
    mydb.commit()

def check_daily_limit(mycursor):
    sql = "SELECT * FROM user WHERE user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    user = mycursor.fetchone()

    # find daily_limit for entertainment
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'entertainment'))
    entertainment_limit = mycursor.fetchone()

    # find daily_limit for dine_out
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'dine out'))
    dine_out_limit = mycursor.fetchone()

    # find daily_limit for transportation
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'transportation'))
    transportation_limit = mycursor.fetchone()

    # find daily_limit for grocery_shopping
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'grocery shopping'))
    grocery_shopping_limit = mycursor.fetchone()

    # find daily_limit for others
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'others'))
    others_limit = mycursor.fetchone()


    #find expenses

    today = date.today()
    state = []
    
    # for entertainment

    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'entertainment'))
    entertainment_expense = mycursor.fetchall()
    
    if len(entertainment_expense) != 0 and entertainment_limit != None:
        total_entertainment_expense = 0
        for x in entertainment_expense:
            if x['date'] == today:
                total_entertainment_expense += x['amount']
        
        if entertainment_limit['daily'] != None:
            if total_entertainment_expense > entertainment_limit['daily']:
                state.append("entertainment")


    # for dine_out
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'dine out'))
    dine_out_expense = mycursor.fetchall()

    if len(dine_out_expense) != 0 and dine_out_limit != None: 
        total_dine_out_expense = 0
        for x in dine_out_expense:
            if x['date'] == today:
                total_dine_out_expense += x['amount']

        if dine_out_limit['daily'] != None:
            if total_dine_out_expense > dine_out_limit['daily']:
                state.append("dine out")

    # for transportation
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'transportation'))
    transportation_expense = mycursor.fetchall()


    if len(transportation_expense) != 0 and transportation_limit != None:
        total_transportation_expense = 0
        for x in transportation_expense:
            if x['date'] == today:
                total_transportation_expense += x['amount']

        if transportation_limit['daily'] != None:
            if total_transportation_expense > transportation_limit['daily']:
                state.append("transportation")

    # for grocery_shopping
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'grocery shopping'))
    grocery_shopping_expense = mycursor.fetchall()

    if len(grocery_shopping_expense) != 0 and grocery_shopping_limit != None:
        total_grocery_shopping_expense = 0
        for x in grocery_shopping_expense:
            if x['date'] == today:
                total_grocery_shopping_expense += x['amount']

        if grocery_shopping_limit['daily'] != None:
            if total_grocery_shopping_expense > grocery_shopping_limit['daily']:
                state.append("grocery shopping")

    # for others
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'others'))
    others_expense = mycursor.fetchall()

    if len(others_expense) != 0 and others_limit != None:
        total_others_expense = 0
        for x in others_expense:
            if x['date'] == today:
                total_others_expense += x['amount']

        if others_limit['daily'] != None:
            if total_others_expense > others_limit['daily']:
                state.append("others")

    return state
    
def check_weekly_limit(mycursor):
    sql = "SELECT * FROM user WHERE user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    user = mycursor.fetchone()

    # find weekly_limit for entertainment
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'entertainment'))
    entertainment_limit = mycursor.fetchone()

    # find weekly_limit for dine_out
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'dine out'))
    dine_out_limit = mycursor.fetchone()

    # find weekly_limit for transportation
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'transportation'))
    transportation_limit = mycursor.fetchone()

    # find weekly_limit for grocery_shopping
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'grocery shopping'))
    grocery_shopping_limit = mycursor.fetchone()

    # find weekly_limit for others
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'others'))
    others_limit = mycursor.fetchone()


    #find expenses

    today = date.today()
    today += timedelta(days=-7)
    state = []
    
    # for entertainment

    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'entertainment'))
    entertainment_expense = mycursor.fetchall()
    
    if len(entertainment_expense) != 0 and entertainment_limit != None:
        total_entertainment_expense = 0
        for x in entertainment_expense:
            if x['date'] > today:
                total_entertainment_expense += x['amount']
        
        if entertainment_limit['weekly'] != None:
            if total_entertainment_expense > entertainment_limit['weekly']:
                state.append("entertainment")


    # for dine_out
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'dine out'))
    dine_out_expense = mycursor.fetchall()

    if len(dine_out_expense) != 0 and dine_out_limit != None: 
        total_dine_out_expense = 0
        for x in dine_out_expense:
            if x['date'] > today:
                total_dine_out_expense += x['amount']

        if dine_out_limit['weekly'] != None:
            if total_dine_out_expense > dine_out_limit['weekly']:
                state.append("dine out")

    # for transportation
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'transportation'))
    transportation_expense = mycursor.fetchall()


    if len(transportation_expense) != 0 and transportation_limit != None:
        total_transportation_expense = 0
        for x in transportation_expense:
            if x['date'] > today:
                total_transportation_expense += x['amount']

        if transportation_limit['weekly'] != None:
            if total_transportation_expense > transportation_limit['weekly']:
                state.append("transportation")

    # for grocery_shopping
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'grocery shopping'))
    grocery_shopping_expense = mycursor.fetchall()

    if len(grocery_shopping_expense) != 0 and grocery_shopping_limit != None:
        total_grocery_shopping_expense = 0
        for x in grocery_shopping_expense:
            if x['date'] > today:
                total_grocery_shopping_expense += x['amount']

        if grocery_shopping_limit['weekly'] != None:
            if total_grocery_shopping_expense > grocery_shopping_limit['weekly']:
                state.append("grocery shopping")

    # for others
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'others'))
    others_expense = mycursor.fetchall()

    if len(others_expense) != 0 and others_limit != None:
        total_others_expense = 0
        for x in others_expense:
            if x['date'] > today:
                total_others_expense += x['amount']

        if others_limit['weekly'] != None:
            if total_others_expense > others_limit['weekly']:
                state.append("others")

    return state

def check_monthy_limit(mycursor):
    sql = "SELECT * FROM user WHERE user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    user = mycursor.fetchone()

    # find monthly_limit for entertainment
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'entertainment'))
    entertainment_limit = mycursor.fetchone()

    # find monthly_limit for dine_out
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'dine out'))
    dine_out_limit = mycursor.fetchone()

    # find monthly_limit for transportation
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'transportation'))
    transportation_limit = mycursor.fetchone()

    # find monthly_limit for grocery_shopping
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'grocery shopping'))
    grocery_shopping_limit = mycursor.fetchone()

    # find monthly_limit for others
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'others'))
    others_limit = mycursor.fetchone()


    #find expenses

    today = date.today()
    today += timedelta(days=-30)
    state = []
    
    # for entertainment

    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'entertainment'))
    entertainment_expense = mycursor.fetchall()
    
    if len(entertainment_expense) != 0 and entertainment_limit != None:
        total_entertainment_expense = 0
        for x in entertainment_expense:
            if x['date'] > today:
                total_entertainment_expense += x['amount']
        
        if entertainment_limit['monthly'] != None:
            if total_entertainment_expense > entertainment_limit['monthly']:
                state.append("entertainment")

    # for dine_out
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'dine out'))
    dine_out_expense = mycursor.fetchall()

    if len(dine_out_expense) != 0 and dine_out_limit != None: 
        total_dine_out_expense = 0
        for x in dine_out_expense:
            if x['date'] > today:
                total_dine_out_expense += x['amount']

        if dine_out_limit['monthly'] != None:
            if total_dine_out_expense > dine_out_limit['monthly']:
                state.append("dine out")


    # for transportation
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'transportation'))
    transportation_expense = mycursor.fetchall()


    if len(transportation_expense) != 0 and transportation_limit != None:
        total_transportation_expense = 0
        for x in transportation_expense:
            if x['date'] > today:
                total_transportation_expense += x['amount']

        if transportation_limit['monthly'] != None:
            if total_transportation_expense > transportation_limit['monthly']:
                state.append("transportation")

    # for grocery_shopping
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'grocery shopping'))
    grocery_shopping_expense = mycursor.fetchall()

    if len(grocery_shopping_expense) != 0 and grocery_shopping_limit != None:
        total_grocery_shopping_expense = 0
        for x in grocery_shopping_expense:
            if x['date'] > today:
                total_grocery_shopping_expense += x['amount']

        if grocery_shopping_limit['monthly'] != None:
            if total_grocery_shopping_expense > grocery_shopping_limit['monthly']:
                state.append("grocery shopping")

    # for others
    sql = "SELECT * FROM expense WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'others'))
    others_expense = mycursor.fetchall()

    if len(others_expense) != 0 and others_limit != None:
        total_others_expense = 0
        for x in others_expense:
            if x['date'] > today:
                total_others_expense += x['amount']

        if others_limit['monthly'] != None:
            if total_others_expense > others_limit['monthly']:
                state.append("others")

    return state

def update_profile(form, mycursor, mydb):

    if form.sure.data == 'yes':
        sql = "UPDATE user SET name=%s, phone=%s, acc_type=%s WHERE user_id=%s"
        val = (form.name.data, form.phone.data, form.account_type.data, session['user_id'])
        mycursor.execute(sql, val)
        mydb.commit()

def update_comes(form, mycursor, mydb):
    sql = "SELECT income_id, outcome_id, wallet_id FROM user WHERE user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    user = mycursor.fetchone()
    
    sql = "UPDATE fixed_income SET salary=%s, salary_day=%s, scholarship=%s, scholarship_day=%s, in_other=%s, in_other_day=%s WHERE income_id=%s"
    val = (form.salary.data, form.salary_day.data, form.scholarship.data, form.scholarship_day.data, form.others1.data, form.others1_day.data, user['income_id'])
    mycursor.execute(sql, val)
    mydb.commit()

    sql = "UPDATE fixed_outcome SET rent=%s, rent_day=%s, bills=%s, bills_day=%s, out_other=%s, out_other_day=%s WHERE outcome_id=%s"
    val = (form.rent.data, form.rent_day.data, form.bills.data, form.bills_day.data, form.others2.data, form.others2_day.data, user['outcome_id'])
    mycursor.execute(sql, val)
    mydb.commit()

def site_info(mycursor):
    sql = "SELECT count(user_id) as num_of_user FROM user"
    mycursor.execute(sql)
    num_of_user = mycursor.fetchone()

    num_of_user = num_of_user['num_of_user']
    
    sql = "SELECT avg(salary+scholarship+in_other) as av_income FROM fixed_income"
    mycursor.execute(sql)
    av_income = mycursor.fetchone()
    
    if av_income['av_income'] != None:
        av_income = round(av_income['av_income'],2)
    else :
        av_income = 0.0

    sql = "SELECT avg(rent+bills+out_other) as av_outcome FROM fixed_outcome"
    mycursor.execute(sql)
    av_outcome = mycursor.fetchone()
    
    if av_outcome['av_outcome'] != None:
        av_outcome = round(av_outcome['av_outcome'],2)
    else:
        av_outcome = 0.0


    sql = "select expense_type, count(*) from expense group by expense_type"
    mycursor.execute(sql)
    categorised = mycursor.fetchall()

    return [av_income, av_outcome, categorised]
        
def categorised_expenses(mycursor):
    sql = "select expense_type, count(*) from expense where user_id=%s group by expense_type"
    mycursor.execute(sql, (session['user_id'], ))
    expenses= mycursor.fetchall()

    return expenses

def update_salary_vs(mycursor, mydb):
    sql = "SELECT income_id, outcome_id, wallet_id FROM user WHERE user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    user = mycursor.fetchone()

    today = date.today()
    day = today.strftime("%d")

    sql = "SELECT * FROM wallet WHERE wallet_id=%s"
    mycursor.execute(sql, (user['wallet_id'], ))
    wallet = mycursor.fetchone()

    sql = "SELECT * FROM fixed_income WHERE income_id=%s"
    mycursor.execute(sql, (user['income_id'], ))
    income = mycursor.fetchone()

    
    if day == income['salary_day']:

        sql = "UPDATE wallet SET total=%s, debit_card=%s WHERE wallet_id=%s"
        mycursor.execute(sql, (wallet['total'] + income['salary'], wallet['debit_card'] + income['salary'] , user['wallet_id']))
        mydb.commit()

    if day == income['scholarship_day']:
    
        sql = "UPDATE wallet SET total=%s, debit_card=%s WHERE wallet_id=%s"
        mycursor.execute(sql, (wallet['total'] + income['scholarship'], wallet['debit_card'] + income['scholarship'] , user['wallet_id']))
        mydb.commit()

    if day == income['in_other_day']:
    
        sql = "UPDATE wallet SET total=%s, debit_card=%s WHERE wallet_id=%s"
        mycursor.execute(sql, (wallet['total'] + income['in_other'], wallet['debit_card'] + income['in_other'] , user['wallet_id']))
        mydb.commit()

    sql = "SELECT * FROM fixed_outcome WHERE outcome_id=%s"
    mycursor.execute(sql, (user['outcome_id'], ))
    outcome = mycursor.fetchone()

    if day == outcome['rent_day']:

        sql = "UPDATE wallet SET total=%s, debit_card=%s WHERE wallet_id=%s"
        mycursor.execute(sql, (wallet['total'] - outcome['rent'], wallet['debit_card'] - outcome['rent'] , user['wallet_id']))
        mydb.commit()

    if day == outcome['bills_day']:

        sql = "UPDATE wallet SET total=%s, debit_card=%s WHERE wallet_id=%s"
        mycursor.execute(sql, (wallet['total'] - outcome['bills'], wallet['debit_card'] - outcome['bills'] , user['wallet_id']))
        mydb.commit()

    if day == outcome['out_other_day']:

        sql = "UPDATE wallet SET total=%s, debit_card=%s WHERE wallet_id=%s"
        mycursor.execute(sql, (wallet['total'] - outcome['out_other'], wallet['debit_card'] - outcome['out_other'] , user['wallet_id']))
        mydb.commit()

def money_left(mycursor):
    sql = "SELECT wallet_id FROM user WHERE user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    wallet_id = mycursor.fetchone()
    wallet_id = wallet_id['wallet_id']

    sql = "SELECT * FROM wallet WHERE wallet_id=%s"
    mycursor.execute(sql, (wallet_id, ))
    wallet = mycursor.fetchone()

    s = ""
    r = []

    s = str(wallet['debit_card']) + " money in your debit card." 
    r.append(s) 
    s = str(wallet['cash']) + " money as cash." 
    r.append(s) 
    s = str(wallet['total']) + " money in total" 
    r.append(s) 
    return r

def delete_expense(mycursor, mydb, exp):
    for e in exp:
       sql = "DELETE FROM expense WHERE expense_id=%s"
       mycursor.execute(sql, (e, ))
       mydb.commit()
     
def get_limits(mycursor):

    total = []
    #for entertainment 
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'entertainment'))
    entertainment = mycursor.fetchone()

    if entertainment != None:
        total.append(['entertainment', entertainment['daily'], entertainment['weekly'], entertainment['monthly']])

    #
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'dine out'))
    entertainment = mycursor.fetchone()

    if entertainment != None:
        total.append(['dine out', entertainment['daily'], entertainment['weekly'], entertainment['monthly']])

    #
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'transportation'))
    entertainment = mycursor.fetchone()

    if entertainment != None:
        total.append(['transportation', entertainment['daily'], entertainment['weekly'], entertainment['monthly']])

    #
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'grocery shopping'))
    entertainment = mycursor.fetchone()

    if entertainment != None:
        total.append(['grocery shopping', entertainment['daily'], entertainment['weekly'], entertainment['monthly']])

    #
    sql = "SELECT * FROM limits WHERE user_id=%s AND expense_type=%s"
    mycursor.execute(sql, (session['user_id'], 'others'))
    entertainment = mycursor.fetchone()

    if entertainment != None:
        total.append(['others', entertainment['daily'], entertainment['weekly'], entertainment['monthly']])

    return total

def delete_account(mycursor, mydb):
    sql = "select * from user where user_id=%s"
    mycursor.execute(sql, (session['user_id'], ))
    user = mycursor.fetchone()

    #delete income and outcome
    sql = "delete from fixed_outcome where outcome_id=%s"
    mycursor.execute(sql, (user['outcome_id'], ))

    sql = "delete from fixed_income where income_id=%s"
    mycursor.execute(sql, (user['income_id'], ))

    #delete wallet
    sql = "delete from wallet where wallet_id=%s"
    mycursor.execute(sql, (user['wallet_id'], ))

    #delete limits
    sql = "delete from limits where user_id=%s"
    mycursor.execute(sql, (user['user_id'], ))

    #delete expenses
    sql = "delete from expense where user_id=%s"
    mycursor.execute(sql, (user['user_id'], ))

    mydb.commit()
    
    #delete user
    sql = "delete from user where user_id=%s"
    mycursor.execute(sql, (user['user_id'], ))
    mydb.commit()

    session.pop('user_id')


