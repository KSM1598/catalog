from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db import NailPolishBrands, Base, BrandItems, Users
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import random
import string
import requests
from flask import make_response
from functools import wraps
app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']


# APPLICATION_NAME = "Nail-Polish-Addicts-Store"
engine = create_engine('sqlite:///nailpolishesstore.db',
                       connect_args={'check_same_thread': False},
                       echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state)


# creating gconnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('''Invalid state
                                                parameter.'''), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        code = request.data
        try:
            ''' Upgrade the authorization code into a credentials object'''
            oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(json.dumps('''Failed to upgrade the
                                                authorization code.'''), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        ''' Check that the access token is valid.'''
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        ''' If there was an error in the access token info, abort.'''
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        ''' Verify that the access token is used for the intended user.'''
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(
                json.dumps("""Token's user ID doesn't
                           match given user ID."""), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        ''' Verify that the access token is valid for this app.'''
        if result['issued_to'] != CLIENT_ID:
            response = make_response(json.dumps("""Token's client ID does
                                                not match app's."""), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_access_token = login_session.get('access_token')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('''Current user is already
                                                connected.'''), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        ''' Store the access token in the session for later use.'''
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = gplus_id
        ''' Get user info'''
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']

        # see if user exists,if not create new user
        u_id = getUserID(login_session['email'])
        if not u_id:
            u_id = createUser(login_session)
        login_session['u_id'] = u_id

        output = ''
        output += '<h1>Welcome, '
        output += login_session['username']
        output += '!</h1>'
        output += '<img src="'
        output += login_session['picture']
        output += '''<"style="width:300px;
                       height:300px;
                       border-radius:150px;
                       -webkit-border-radius:150px;
                       -moz-border-radius:150px;">'''

        flash("You are now logged in as %s" % login_session['username'])
        print "Done!"
        return output


# disconnect from connected user
@app.route("/logout")
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('''Current user not
                                            connected.'''), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully logged out!.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully Logged Out!')
        return redirect(url_for('brandsMenu'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps('''Failed to revoke token for
                                            given user.'''), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Login Required function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect('/login')
    return decorated_function


@app.route('/nailpolishesbrands/menu/JSON')
def brandsMenuJSON():
    nailpolishbrands = session.query(NailPolishBrands)
    return jsonify(Brands=[i.serialize for i in nailpolishbrands])


@app.route('/nailpolishesbrands/<int:brand_id>/JSON')
def brandJSON(brand_id):
    brand = session.query(NailPolishBrands).filter_by(id=brand_id).one()
    return jsonify(Brand=brand.serialize)


@app.route('/nailpolishesbrands/<int:item_id>/menu/JSON')
def brandItemsMenuJSON(item_id):
    brands = session.query(NailPolishBrands).filter_by(id=item_id).one()
    nail_polish_brands = brands
    items = session.query(BrandItems).filter_by(item_id=nail_polish_brands.id)
    return jsonify(Brand_Itemss=[i.serialize for i in items])


@app.route('/nailpolishesbrands/<int:item_id>/menu/<int:brand_id>/JSON')
def brandItemJSON(item_id, brand_id):
    brandItem = session.query(BrandItems).filter_by(id=brand_id).one()
    return jsonify(BrandItem=brandItem.serialize)


@app.route('/')
@app.route('/nailpolishesbrands/')
def brandsMenu():
    brands = session.query(NailPolishBrands)
    if 'username' not in login_session:
        return render_template('publicbrands.html', brands=brands)
    return render_template('brands.html', brands=brands)


@app.route('/nailpolishesbrands/new/', methods=['GET', 'POST'])
@login_required
def newBrand():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBrand = NailPolishBrands(name=request.form['name'],
                                    u_id=login_session['u_id'])
        session.add(newBrand)
        session.commit()
        flash("NEW NAIL POLISH BRAND ADDED SUCCESSFULLY")
        return redirect(url_for('brandsMenu'))
    else:
        return render_template('newbrand.html')


@app.route('/nailpolishesbrands/<int:brand_id>/edit/', methods=['GET', 'POST'])
@login_required
def editBrand(brand_id):
    editedBrand = session.query(NailPolishBrands).filter_by(id=brand_id).one()
    active_user = getUserInfo(editedBrand.u_id)

    if 'username' in login_session:
        if login_session['u_id'] == editedBrand.u_id:
            if request.method == 'POST':
                if request.form['name']:
                    editedBrand.name = request.form['name']
                    session.add(editedBrand)
                    session.commit()
                    flash("BRAND EDITED SUCCESSFULLY")
                    return redirect(url_for('brandsMenu'))
            else:
                return render_template('editbrand.html',
                                       brand_id=brand_id, i=editedBrand)
        else:
            flash("Unauthorized access... This brand was created by %s"
                  % active_user.uname)
            return redirect(url_for('brandsMenu'))
    else:
        flash("""Unauthorized access... Please Login to
              make changes to the brand.""")
        return redirect('/login')


@app.route('/nailpolishesbrands/<int:brand_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteBrand(brand_id):
    bToDelete = session.query(NailPolishBrands).filter_by(id=brand_id).one()
    brandToDelete = bToDelete
    if 'username' not in login_session:
        flash("Unauthorized access.... Please Login to delete this brand.")
        return redirect('/login')
    if brandToDelete.u_id != login_session['u_id']:
        flash("Only the creator can make changes to their respective brands.")
        return render_template('delete.html')
    if request.method == 'POST':
        session.delete(brandToDelete)
        session.commit()
        flash("BRAND %s DELETED SUCCESSFULLY" % brandToDelete.name)
        return redirect(url_for('brandsMenu'))
    else:
        return render_template('deletebrand.html',
                               brand_id=brand_id, i=brandToDelete)


@app.route('/')
@app.route('/nailpolishesbrands/<int:brand_id>/', methods=['GET', 'POST'])
def brandItemsMenu(brand_id):
    brands = session.query(NailPolishBrands).filter_by(id=brand_id).one()
    nail_polish_brands = brands
    creator = getUserInfo(nail_polish_brands.u_id)
    items = session.query(BrandItems).filter_by(item_id=nail_polish_brands.id)
    if 'username' not in login_session or creator.id != login_session['u_id']:
        return render_template('publicbranditems.html',
                               nail_polish_brands=nail_polish_brands,
                               items=items)
    else:
        return render_template('branditems.html',
                               nail_polish_brands=nail_polish_brands,
                               items=items)


@app.route('/nailpolishesbrands/<int:brand_id>/new/', methods=['GET', 'POST'])
@login_required
def newBrandItem(brand_id):
    brands = session.query(NailPolishBrands).filter_by(id=brand_id).one()
    nail_polish_brands = brands
    creator = getUserInfo(nail_polish_brands.u_id)
    if 'username' in login_session:
        if login_session['u_id'] == nail_polish_brands.u_id:
            if request.method == 'POST':
                newItem = BrandItems(name=request.form['name'],
                                     description=request.form['description'],
                                     price=request.form['price'],
                                     item_id=nail_polish_brands.id,
                                     u_id=login_session['u_id'])
                session.add(newItem)
                session.commit()
                flash("NEW NAIL POLISH %s ADDED SUCCESSFULLY" % (newItem.name))
                return redirect(url_for('brandItemsMenu', brand_id=brand_id))
            else:
                return render_template('newbranditem.html', brand_id=brand_id)
        else:
            flash("Unauthorized access.... This brand belongs to %s"
                  % creator.name)
    else:
        flash("Unauthorized access.... Please Login to delete this brand.")
        return redirect('/login')


@app.route('/nailpolishesbrands/<int:brand_id>/<int:item_id>/edit/',
           methods=['GET', 'POST'])
@login_required
def editBrandItem(brand_id, item_id):
    editedItem = session.query(BrandItems).filter_by(id=brand_id).one()
    if 'username' in login_session:
        if login_session['u_id'] != editedItem.u_id:
            flash("""Unauthorized access... Only the creator of this brand
                  has the right to make changes.""")
            return redirect(url_for('brandItemsMenu', brand_id=brand_id))
        else:
            if request.method == 'POST':
                if request.form['name']:
                    editedItem.name = request.form['name']
                if request.form['description']:
                    editedItem.description = request.form['description']
                if request.form['price']:
                    editedItem.price = request.form['price']
                session.add(editedItem)
                session.commit()
                flash("NAIL POLISH EDITED SUCCESSFULLY")
                return redirect(url_for('brandItemsMenu', item_id=item_id))
            else:
                return render_template('editbranditems.html',
                                       brand_id=brand_id, item_id=item_id,
                                       i=editedItem)
    else:
        flash("""Unauthorized access... Please Login to make changes
        to the brand item.""")
        return redirect('/login')


@app.route('/nailpolishesbrands/<int:item_id>/<int:brand_id>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteBrandItem(brand_id, item_id):
    itemToDelete = session.query(BrandItems).filter_by(id=brand_id).one()
    if 'username' not in login_session:
        flash("Unauthorized access... Please Login to delete this brand item.")
        return redirect('/login')
    if itemToDelete.u_id != login_session['u_id']:
        flash("""Only the creator can make changes to their respective
              brand items.""")
        return redirect(url_for('brandItemsMenu', brand_id=brand_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("NAIL POLISH DELETED SUCCESSFULLY")
        return redirect(url_for('brandsMenu'))
    else:
        return render_template('deletebranditem.html',
                               brand_id=brand_id,
                               item_id=item_id, i=itemToDelete)


# creating new user
def createUser(login_session):
    newUser = Users(uname=login_session['username'],
                    email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


# getting user info
def getUserInfo(u_id):
    user = session.query(Users).filter_by(id=u_id).one()
    return user


# getting user ID
def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
