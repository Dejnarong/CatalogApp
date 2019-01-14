#!/usr/bin/python

from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker, joinedload, scoped_session
from database_setup import Base, Categories, CategoriesItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Hypebeast Catalog"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitems.db?check_same_thread=False')
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# This gconnect I taken from lesson 6
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ " style = "width: 150px; height: 150px;border-radius: 150px;
        -webkit-border-radius: 150px;-moz-border-radius: 150px;"> """
    flash("you are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Home Page
@app.route('/')
@app.route('/catalog')
def showCatalog():
    # Get all categories to display
    categories = session.query(Categories).order_by(asc(Categories.name))
    # Get only latest 5 row to show
    categorieslastestitems = session.query(CategoriesItem).order_by(
        desc(CategoriesItem.id)).limit(5).all()
    # if not log in user can just view data
    if 'username' not in login_session:
        return render_template(
            'publiccatalog.html', categories=categories,
            categorieslastestitems=categorieslastestitems)
    # if log in user can add own item
    else:
        return render_template(
            'catalog.html', categories=categories,
            categorieslastestitems=categorieslastestitems)


# View item by category
@app.route('/catalog/<string:catalog_name>/items')
def showAllItem(catalog_name):
    # Just select for list all categories
    categories = session.query(Categories).order_by(asc(Categories.name))
    categories_id = session.query(
        Categories).filter_by(name=catalog_name).one()
    # Get all item in category
    categoriesitem = session.query(CategoriesItem).filter_by(
        categories_id=categories_id.id).order_by(asc(CategoriesItem.title))
    return render_template(
        'catalogitem.html', categories=categories,
        categoriesitems=categoriesitem, catalogname=catalog_name)


# Show category item detail
@app.route('/catalog/<string:catalog_name>/<string:item_name>')
def showItemDetail(catalog_name, item_name):
    # get category id to find item
    categories_id = session.query(
        Categories).filter_by(name=catalog_name).one()
    # get item
    categoriesitem = session.query(CategoriesItem).filter_by(
        categories_id=categories_id.id, title=item_name).one()
    # get user who create item
    creator = getUserInfo(categoriesitem.user_id)
    # if log in user not create item can't be edit and delete
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template(
            'publiccatalogitemdetail.html',
            itemdetail=categoriesitem)
    # if log in user create item can be edit and delete
    else:
        return render_template(
            'catalogitemdetail.html',
            itemdetail=categoriesitem)


# Add Category Item
@app.route('/add')
@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    # if not login user will go to login page
    if 'username' not in login_session:
        return redirect('/login')
    # if user click create item will insert item to db
    if request.method == 'POST':
        categories_id = session.query(Categories).filter_by(
            name=request.form['category_name']).one()
        newItem = CategoriesItem(
            title=request.form['title'],
            description=request.form['description'],
            categories_id=categories_id.id,
            user_id=login_session['user_id'])
        session.add(newItem)
        flash('New Item %s Successfully Created' % newItem.title)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        # Get all categories for selectbox
        categories = session.query(Categories).all()
        return render_template('newcatalogitem.html', categories=categories)


# Edit Category Item
@app.route(
    '/catalog/<string:catalog_name>/<string:item_name>/edit',
    methods=['GET', 'POST'])
def editItem(catalog_name, item_name):
    categories_id = session.query(
        Categories).filter_by(name=catalog_name).one()
    edititem_id = session.query(CategoriesItem).filter_by(
        categories_id=categories_id.id, title=item_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if edititem_id.user_id != login_session['user_id']:
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        if request.form['title']:
            edititem_id.title = request.form['title']
        if request.form['description']:
            edititem_id.description = request.form['description']
        if request.form['category_name']:
            newCategories_id = session.query(Categories).filter_by(
                name=request.form['category_name']).one()
            edititem_id.categories_id = newCategories_id.id
        session.add(edititem_id)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showCatalog'))
    else:
        categories = session.query(Categories).all()
        return render_template(
            'editcatalogitem.html',
            categories=categories, item=edititem_id)


# Delete Category item
@app.route(
    '/catalog/<string:catalog_name>/<string:item_name>/delete',
    methods=['GET', 'POST'])
def deleteItem(catalog_name, item_name):
    categories_id = session.query(
        Categories).filter_by(name=catalog_name).one()
    deleteitem_id = session.query(CategoriesItem).filter_by(
        categories_id=categories_id.id, title=item_name).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deleteitem_id.user_id != login_session['user_id']:
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        session.delete(deleteitem_id)
        flash('%s Successfully Deleted' % deleteitem_id.title)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deletecatalogitem.html', item=deleteitem_id)


# JSON API
# Get all data to json file
@app.route('/catalog/JSON')
def catalogJSON():
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Categories).options(
        joinedload(Categories.item)).all()
    return jsonify(
            Category=[dict(
                c.serialize,
                Item=[i.serialize for i in c.item]) for c in categories])


@app.route('/catalog/<string:catalog_name>/items/JSON')
def showAllItemJSON(catalog_name):
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Categories).options(
        joinedload(Categories.item)).filter_by(name=catalog_name).all()
    return jsonify(
            Category=[dict(
                c.serialize,
                Item=[i.serialize for i in c.item]) for c in categories])


@app.route('/catalog/<string:catalog_name>/<string:item_name>/JSON')
def showItemDetailJSON(catalog_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    categories_id = session.query(
        Categories).filter_by(name=catalog_name).one()
    # get item
    categoriesitem = session.query(CategoriesItem).filter_by(
        categories_id=categories_id.id, title=item_name).all()
    return jsonify(CatagoryItems=[i.serialize for i in categoriesitem])


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
