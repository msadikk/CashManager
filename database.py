tables = []

sql = """create table if not exists wallet(
    wallet_id int auto_increment, 
    debit_card double default 0,
    cash double default 0,
    total double default 0,
    primary key(wallet_id)
)
"""
tables.append(sql)

sql = """create table if not exists fixed_outcome(
    outcome_id int auto_increment, 
    rent double default 0,
    bills double default 0,
    out_other double default 0,
    rent_day int default 1,
    bills_day int default 1,
    out_other_day int default 1,
    primary key(outcome_id)
)
"""
tables.append(sql)

sql = """create table if not exists fixed_income(
    income_id int auto_increment,
    salary double default 0,
    scholarship double default 0,
    in_other double default 0,
    salary_day int default 1,
    scholarship_day int default 1,
    in_other_day int default 1,
    primary key(income_id)
)
"""
tables.append(sql)

sql = """create table if not exists user(
    user_id int auto_increment,
    email varchar(30) not null,
    password varchar(100) not null, 
    name varchar(30) default "",
    phone varchar(11) default "",
    acc_type varchar(10) default "personal",
    income_id int,
    outcome_id int, 
    wallet_id int,
    primary key(user_id),
    foreign key(income_id) references fixed_income(income_id) on delete cascade,
    foreign key(outcome_id) references fixed_outcome(outcome_id) on delete cascade,
    foreign key(wallet_id) references wallet(wallet_id) on delete cascade
)
"""
tables.append(sql)

sql = """create table if not exists expense(
    expense_id int auto_increment,
    expense_type varchar(25),
    payment varchar(25),
    amount double, 
    date date, 
    user_id int,
    primary key(expense_id),
    foreign key(user_id) references user(user_id) on delete cascade
)
"""
tables.append(sql)

sql = """create table if not exists limits(
    expense_type varchar(20),
    daily double, 
    weekly double, 
    monthly double, 
    user_id int,
    primary key(expense_type, user_id)
)
"""
tables.append(sql)
