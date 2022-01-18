from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == 'POST':
        # purchase logic
        item_id = request.form.get('purchased_item')
        item = Item.query.filter_by(id=item_id).first()
        # assign item to user
        if item:
            if current_user.can_purchase(item.price):
                item.buy(current_user)
                flash(f"Congratulations! Item {item.name} purchased successfully", category='success')
            else:
                flash(f"Not enough budget to purchase {item.name}", category='danger')

        # sell logic
        sold_item_id = request.form.get('sold_item')
        sold_item = Item.query.filter_by(id=sold_item_id).first()
        if sold_item:
            if current_user.can_sell(sold_item):
                sold_item.sell(current_user)
                flash(f"Congratulations! Item {sold_item.name} sold successfully", category='success')
            else:
                flash(f"Item {sold_item.name} cannot be sold", category='danger')
        # redirect to market page
        return redirect(url_for('market'))

    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, owned_items=owned_items, purchase_form=purchase_form, selling_form=selling_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        # login user
        login_user(user)
        flash(f'Account created successfully', category='success')
        return redirect(url_for('market'))
    # if errors dict is present
    if form.errors != {}:
        for error in form.errors.values():
            flash(f'There was an error creating user: {error}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'User logged in successfully', category='success')
            return redirect(url_for('market'))
        else:
            flash(f'Incorrect user name or password, Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("User logged out", category="info")
    return redirect(url_for('home'))
