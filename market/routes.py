from market import app, db
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, AddItemForm
from flask_login import login_user, logout_user, login_required, current_user


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/market", methods=['GET', 'POST'])
@login_required
def market():
    items = Item.query.filter_by(owner=None).all()
    if request.method == 'POST':
        purchase_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchase_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                current_user.buy(p_item_object)
                flash(f'Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$',
                      category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!",
                      category='danger')

        selled_item = request.form.get('selled_item')
        p_item_object = Item.query.filter_by(name=selled_item).first()
        if p_item_object:
            current_user.sell(p_item_object)
            flash(f'Congratulations! You selled {p_item_object.name} for {p_item_object.price}$',
                  category='success')
        add_item_form = AddItemForm()
        if add_item_form.validate_on_submit():
            item_to_add = Item(name=add_item_form.name.data,
                                price=add_item_form.price.data,
                                barcode=add_item_form.barcode.data,
                                description=add_item_form.description.data)

            db.session.add(item_to_add)
            db.session.commit()


        return redirect(url_for('market'))
    return render_template('market.html',
                           items=items,
                           purchase_item_form=PurchaseItemForm(),
                           current_user=current_user,
                           sell_item_form=SellItemForm(),
                           add_item_form=AddItemForm())


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_add = User(username=form.username.data,
                           email_address=form.email_address.data,
                           password=form.password1.data)
        db.session.add(user_to_add)
        db.session.commit()
        login_user(user_to_add)
        flash(f'Success! You are logged in as: {user_to_add.username}', category='success')
        return redirect(url_for('market'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('home'))
