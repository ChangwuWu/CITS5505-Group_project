from cs50 import SQL
import time
from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify, url_for, flash
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
import random
import string
import base64
import io

# # Instantiate Flask object named app
app = Flask(__name__)

# # Configure sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Creates a connection to the database
db = SQL( "sqlite:///data.db" )

@app.route("/")
def index():
    kind = request.args.get('gender')
    continent = request.args.get('category')

    if kind and continent:
        shoes = db.execute("SELECT * FROM shoes WHERE kind = :kind and continent = :continent ORDER BY team ASC",kind=kind, continent=continent )
    elif kind:
        shoes = db.execute("SELECT * FROM shoes WHERE kind = :kind ORDER BY team ASC", kind=kind )
    elif continent:
        shoes = db.execute("SELECT * FROM shoes WHERE continent = :continent ORDER BY team ASC", continent=continent )
    else:
        shoes = db.execute("SELECT * FROM shoes ORDER BY team ASC")
    shoesLen = len(shoes)
    # Initialize variables
    shoppingCart = []

    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = db.execute("SELECT team,shoesize, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team,shoesize")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # shoes = db.execute("SELECT * FROM shoes ORDER BY team ASC")
        # shoesLen = len(shoes)
        # return render_template ("index.html", shoppingCart=shoppingCart, shoes=shoes, shopLen=shopLen, shoesLen=shoesLen, total=total, totItems=totItems, display=display, session=session )
    return render_template ("index.html", shoes=shoes, shoppingCart=shoppingCart, shoesLen=shoesLen, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/buy/")
def buy():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    shoesize = request.args.get('shoesize')
    if session:
        # Store id of the selected shirt
        id = int(request.args.get('id'))
        # Select info of selected shirt from database
        goods = db.execute("SELECT * FROM shoes WHERE id = :id", id=id)
        # Extract values from selected shirt record
        # Check if shirt is on sale to determine price
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        team = goods[0]["team"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Insert selected shirt into shopping cart
        db.execute("INSERT INTO cart (id, qty, team, image, price, subTotal, shoesize) VALUES (:id, :qty, :team, :image, :price, :subTotal,:shoesize)", id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal,shoesize=shoesize)
        shoppingCart = db.execute("SELECT team, shoesize, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team, shoesize")
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Select all shoes for home page view
        shoes = db.execute("SELECT * FROM shoes ORDER BY team ASC")
        shoesLen = len(shoes)
        # Go back to home page
        # return render_template ("index.html", shoppingCart=shoppingCart, shoes=shoes, shopLen=shopLen, shoesLen=shoesLen, total=total, totItems=totItems, display=display, session=session )
        return redirect(url_for("index"))

@app.route("/update/")
def update():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    shoesize = request.args.get('shoesize')
    if session:
        # Store id of the selected shirt
        id = int(request.args.get('id'))
        db.execute("DELETE FROM cart WHERE id = :id", id=id)
        # Select info of selected shirt from database
        goods = db.execute("SELECT * FROM shoes WHERE id = :id", id=id)
        # Extract values from selected shirt record
        # Check if shirt is on sale to determine price
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        team = goods[0]["team"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Insert selected shirt into shopping cart
        db.execute("INSERT INTO cart (id, qty, team, image, price, subTotal,shoesize) VALUES (:id, :qty, :team, :image, :price, :subTotal,:shoesize)", id=id, qty=qty, team=team, image=image, price=price, subTotal=subTotal,shoesize=shoesize)
        shoppingCart = db.execute("SELECT team,shoesize, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team, shoesize")
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Go back to cart page
        return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/filter/")
def filter():
    if request.args.get('continent'):
        query = request.args.get('continent')
        shoes = db.execute("SELECT * FROM shoes WHERE continent = :query ORDER BY team ASC", query=query )
    if request.args.get('sale'):
        query = request.args.get('sale')
        shoes = db.execute("SELECT * FROM shoes WHERE onSale = :query ORDER BY team ASC", query=query)
    if request.args.get('id'):
        query = int(request.args.get('id'))
        shoes = db.execute("SELECT * FROM shoes WHERE id = :query ORDER BY team ASC", query=query)
    if request.args.get('kind'):
        query = request.args.get('kind')
        shoes = db.execute("SELECT * FROM shoes WHERE kind = :query ORDER BY team ASC", query=query)
    if request.args.get('price'):
        query = request.args.get('price')
        shoes = db.execute("SELECT * FROM shoes ORDER BY onSalePrice ASC")
    shoesLen = len(shoes)
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        # Rebuild shopping cart
        shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Render filtered view
        return render_template ("index.html", shoppingCart=shoppingCart, shoes=shoes, shopLen=shopLen, shoesLen=shoesLen, total=total, totItems=totItems, display=display, session=session )
    # Render filtered view
    return render_template ( "index.html", shoes=shoes, shoppingCart=shoppingCart, shoesLen=shoesLen, shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route("/checkout/")
def checkout():
    order = db.execute("SELECT * from cart")
    # Update purchase history of current customer
    for item in order:
        db.execute("INSERT INTO purchases (uid, id, team, image, quantity,shoesize) VALUES(:uid, :id, :team, :image, :quantity, :shoesize)", uid=session["uid"], id=item["id"], team=item["team"], image=item["image"], quantity=item["qty"], shoesize=item["shoesize"]  )
    # Clear shopping cart
    db.execute("DELETE from cart")
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Redirect to home page
    return redirect('/')


@app.route("/remove/", methods=["GET"])
def remove():
    # Get the id of shirt selected to be removed
    out = int(request.args.get("id"))
    # Remove shirt from shopping cart
    db.execute("DELETE from cart WHERE id=:id", id=out)
    # Initialize shopping cart variables
    totItems, total, display = 0, 0, 0
    # Rebuild shopping cart
    shoppingCart = db.execute("SELECT team, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team")
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Turn on "remove success" flag
    display = 1
    # Render shopping cart
    return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/new/", methods=["GET"])
def new():
    # Render log in page
    return render_template("new.html")


@app.route("/logged/", methods=["POST"] )
def logged():
    # Get log in info from log in form
    user = request.form["username"].lower()
    pwd = request.form["password"]
    captcha = request.form["captcha"].lower()
    #pwd = str(sha1(request.form["password"].encode('utf-8')).hexdigest())
    # Make sure form input is not blank and re-render log in page if blank
    print(session.get('captcha').lower())
    if captcha !=session.get('captcha').lower():
        flash('Catpcha incorrect!', 'danger')
        return redirect(url_for("index"))
    if user == "" or pwd == "":
        # return render_template ("login.html" )
        return redirect(url_for("index"))
    # Find out if info in form matches a record in user database
    query = "SELECT * FROM users WHERE username = :user"
    rows = db.execute (query, user=user)

    # If username and password match a record in database, set session variables
    if len(rows) == 1:
        if rows[0]['password'] != pwd:
            flash('Password incorrect!', 'danger')
            return redirect(url_for("index"))
        else:
            session['user'] = user
            session['time'] = datetime.now( )
            session['uid'] = rows[0]["id"]
    else:
        flash('Username not exists!', 'danger')
        return redirect(url_for("index"))
    # Redirect to Home Page
    if 'user' in session:
        return redirect ( "/" )
    # If username is not in the database return the log in page
    # return render_template ( "login.html", msg="Wrong username or password." )
    return redirect ( "/" )


@app.route("/history/")
def history():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Retrieve all shoes ever bought by current user
    myShoes = db.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myShoesLen = len(myShoes)
    # Render table with shopping history of current user
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myShoes=myShoes, myShoesLen=myShoesLen)


@app.route("/logout/")
def logout():
    # clear shopping cart
    db.execute("DELETE from cart")
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register/", methods=["POST"] )
def registration():
    # Get info from form
    username = request.form["username"]
    password = request.form["password"]
    confirm = request.form["confirm"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    if password != confirm:
        flash('Two password not matched!', 'danger')
        return redirect(url_for("index"))
    # See if username already in the database
    rows = db.execute( "SELECT * FROM users WHERE username = :username ", username = username )
    # If username already exists, alert user
    if len( rows ) > 0:
        flash('Username already exists!','danger')
        return redirect(url_for("index"))
    # If new user, upload his/her info into the users database
    new = db.execute ( "INSERT INTO users (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
                    username=username, password=password, fname=fname, lname=lname, email=email )
    # Render login template
    return redirect(url_for("index"))


@app.route("/cart/")
def cart():
    if 'user' in session:
        # Clear shopping cart variables
        totItems, total, display = 0, 0, 0
        # Grab info currently in database
        shoppingCart = db.execute("SELECT team,shoesize, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY team,shoesize")
        # Get variable values
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
    # Render shopping cart
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)

@app.route('/feedback',methods=["GET","POST"])
def feedback():
    if request.method == "GET":
        shoppingCart = []
        shopLen = len(shoppingCart)
        totItems, total, display = 0, 0, 0
        data=db.execute("SELECT * FROM feedbacks ")
        feedbacks = sorted(data,key=lambda x: x["addtime"],reverse=True)
        return render_template('feedback.html',shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session if "user" in session else {},feedbacks=feedbacks)
    uid = session["uid"]
    addtime = time.strftime("%Y-%m-%d %H:%M")
    nickname = session['user']
    comments = request.form.get('content')
    id = db.execute(
        "INSERT INTO feedbacks (uid,nickname,comments,addtime) values (:uid,:nickname,:comments,:addtime)",
       uid=uid, nickname=nickname, addtime=addtime, comments=comments)
    return redirect("/feedback")



def generate_captcha_image():
    image = Image.new('RGB', (120, 40), color=(73, 109, 137))
    d = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    font_size = 25
    font = font.font_variant(size=font_size)

    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    d.text((10, 5), captcha_text, spacing=20, fill=(255, 255, 0), font=font)

    for _ in range(random.randint(3, 5)):
        start = (random.randint(0, image.width), random.randint(0, image.height))
        end = (random.randint(0, image.width), random.randint(0, image.height))
        d.line([start, end], fill=(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
    return image, captcha_text

@app.route('/captcha')  
def captcha_image():  
    image, captcha = generate_captcha_image()  
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    session['captcha'] = captcha
    img_str = base64.b64encode(buffer.getvalue()).decode()
    # img_tag = '<img src="data:image/png;base64,{}">'.format(img_str)
    img_tag = 'data:image/png;base64,{}'.format(img_str)
    return img_tag


# Only needed if Flask run is not used to execute the server
if __name__ == "__main__":
   app.run( host='0.0.0.0', port=8080 ,debug=True)
