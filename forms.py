from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, SelectField, DateField, RadioField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import IntegerField

class LoginForm(FlaskForm):
    email = StringField("username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField()

class RegisterForm(FlaskForm):
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField()

class LimitsForm(FlaskForm):
    limit_type = SelectField(choices=['entertainment', 'dine out', 'transportation', 'grocery shopping', 'others'])
    daily = DecimalField()
    weekly = DecimalField()
    monthly = DecimalField()
    submit1 = SubmitField("submit")

class CurrentWalletForm(FlaskForm):
    debit = DecimalField()
    cash = DecimalField()
    submit2 = SubmitField("submit")

class AddExpenseForm(FlaskForm):
    expense_type = SelectField(choices=['entertainment', 'dine out', 'transportation', 'grocery shopping', 'others'])
    amount = DecimalField()
    date = DateField()
    payment = SelectField(choices=['debit card', 'cash'])
    submit1 = SubmitField("submit")

class PersonalInfoForm(FlaskForm):
    name = StringField()
    phone = StringField()
    account_type = SelectField(choices=['personal', 'corporate'])
    sure = RadioField(choices=['yes', 'no'])
    submit = SubmitField()

class InOutComesForm(FlaskForm):
    salary = DecimalField()
    salary_day = IntegerField()
    scholarship = DecimalField()
    scholarship_day = IntegerField()
    others1 = DecimalField()
    others1_day = IntegerField()
    

    rent = DecimalField()
    rent_day = IntegerField()
    bills = DecimalField()
    bills_day = IntegerField()
    others2 = DecimalField()
    others2_day = IntegerField()
    
    submit1 = SubmitField("submit")

class ChooseCategoryForm(FlaskForm):
    category = SelectField(choices=['entertainment', 'dine out', 'transportation', 'grocery shopping', 'others'])
    submit = SubmitField()

class DeleteAccount(FlaskForm):
    permission = StringField()
    submit3 = SubmitField("Delete my account")

