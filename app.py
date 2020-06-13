from flask import Flask, render_template, flash, request, session, redirect, url_for, Markup
from datetime import *
app = Flask(__name__)
import pymysql
app.secret_key = "98"
db = pymysql.connect("127.0.0.1","root","","fyp")

@app.route("/")
def homepage():
    return render_template('client/home.html', title='Home Page')

@app.route("/register", methods=['POST'])
def registerpage():
    UserName = request.form["register_input_username"]
    Password = request.form["register_input_password"]
    DOB = request.form["register_input_dateofbirth"]
    Email = request.form["register_input_email"]
    Phonenumber = request.form["register_input_phonenumber"]
    cursor = db.cursor()
    if cursor.execute("""SELECT * FROM users WHERE User_Name = (%s)""",(UserName)):
        flash('Username has been taken by others, Please try another one!')
        return render_template('client/register.html', title='Register Page')
    else:
        cursor.execute("""INSERT INTO users (User_Name, User_Password, Dateofbirth, Email, Phonenumber) VALUES (%s, %s, %s, %s, %s)""",
        (UserName, Password, DOB, Email, Phonenumber))
        db.commit()
        flash('Registerd')
    return render_template('client/login.html', title='Login Page')

@app.route("/register")
def registerpage2():    
    return render_template('client/register.html', title='Register Page')

@app.route("/login", methods=['POST'])
def loginpage():
    UserName = request.form["login_input_username"]
    Password = request.form["login_input_password"]
    cursor = db.cursor()
    if cursor.execute("""SELECT * FROM users WHERE (User_Name, User_Password) = (%s, %s)""",(UserName, Password)):
        cursor = db.cursor()
        cursor.execute("""SELECT User_ID FROM users WHERE (User_Name, User_Password) = (%s, %s)""",(UserName, Password))
        userid = cursor.fetchone()
        session['currentuserid'] = userid[0]
        session['logged_in'] = True
        session['currentuser'] = UserName
        flash('Logged in')
        return render_template('client/Home.html', title='Home Page')
    else:
        flash('Wrong User Name or Password')
    return render_template('client/login.html', title='Login Page')

@app.route("/login")
def loginpage2():
    return render_template('client/login.html', title='Login Page')

@app.route("/dashboard")
def dashboard():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Users WHERE (User_ID) = (%s)",(session['currentuserid']))
    userinfo = cursor.fetchall()
    return render_template('client/dashboard.html', title='Dashboard', userinfo = userinfo)

@app.route("/orderhistory")
def orderhistory():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Orders WHERE (User_ID) = (%s)",(session['currentuserid']))
    realorderinfo = list(cursor.fetchall())
    orderinfo = []
    cursor = db.cursor()
    for i in realorderinfo:
        if cursor.execute("SELECT * FROM Coupon WHERE (Coupon_code) = (%s)",(i[10])):
            i = list(i)
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Coupon WHERE (Coupon_code) = (%s)",(i[10]))
            couponinfo = cursor.fetchone()
            i.append(couponinfo[1])
            orderinfo.append(i)
        else:
            orderinfo.append(i)
    orderitemlist = []
    realorderitemlist = []
    actuallist = []
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT Order_ID FROM Orders WHERE (User_ID) = (%s)",(session['currentuserid']))
    distinctorderid = cursor.fetchall()
    for i in distinctorderid:
        i = list(i)
        orderitemlist.append(i[0])
    for i in orderitemlist:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Order_item WHERE (Order_ID) = (%s)",(i))
        this = cursor.fetchall()
        this = list(this)
        for i in this:
            i = list(i)
            summary = i[2]*i[3]
            i.append(summary)
            realorderitemlist.append(i)
    for i in realorderitemlist:
        i = list(i)
        cursor = db.cursor()
        cursor.execute("SELECT Product_Name, Product_Image FROM Product WHERE (Product_ID) = (%s)",(i[1]))
        that = cursor.fetchall()
        that = list(that)
        for a in that:
            i.append(a[0])
            i.append(a[1])
            actuallist.append(i)
    return render_template('client/orderhistory.html', title='Order History', orderinfo = orderinfo,actuallist=actuallist)

@app.route("/updateuserinfo", methods=["POST","GET"])
def updateuser():
    password = request.form["password"]
    dob = request.form["dob"]
    email = request.form["email"]
    phonenumber = request.form["phonenumber"]
    cursor = db.cursor()
    cursor.execute("UPDATE Users SET User_Password = (%s), Dateofbirth = (%s) , Email = (%s) , Phonenumber = (%s) WHERE User_ID = (%s)",(password,dob,email,phonenumber,session['currentuserid']))
    db.commit()
    flash('Your informatino had been update!')
    return redirect(request.referrer)

@app.route("/logout")
def logoutpage():
    session['logged_in'] = False
    session['currentuser'] = False
    session['currentuserid'] = False
    flash ('Logged out')
    return render_template('client/Home.html', title='Home Page')

@app.route("/product_list")
def productpage():
    if "shoppingcart" not in session:
        session['shoppingcart'] = []
        session['totalprice'] = 0
    cursor = db.cursor()
    cursor.execute("SELECT * FROM product")
    results = list(cursor.fetchall())
    product_results= []
    for i in results:
        i = list(i)
        actualprice = round(float(i[3])*float(i[5]),2)
        i.append(actualprice)
        product_results.append(i)

    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT Product_Type FROM product")
    product_type_results = cursor.fetchall()

    return render_template('client/product_list.html', title='Product List', product_results = product_results, product_type_results = product_type_results)

@app.route("/addtofavourite", methods=['POST'])
def addtofa():
    try:
        if session['logged_in'] == True:
            productid = request.form['productid']
            cursor = db.cursor()
            if cursor.execute("SELECT * FROM user_favourite WHERE User_ID = (%s) AND Product_ID = (%s)",(session['currentuserid'],productid)):
                flash('This product already in your favourite list!')
                return redirect(request.referrer)
            else:
                cursor = db.cursor()
                cursor.execute("INSERT INTO user_favourite (User_ID, Product_ID) VALUES (%s,%s)",(session['currentuserid'],productid))
                db.commit()
                flash('Added to your favourite list!')
                return redirect(request.referrer)
        else:
            flash('Log in to checkout!')
            return redirect(request.referrer)
    except:
        flash('Log in to use favourite functions!')
        return redirect(request.referrer)
@app.route("/myfavourite")
def myfavourite():
    product_results = []
    results = []
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_favourite WHERE User_ID = (%s)",(session['currentuserid']))
    itemlist = list(cursor.fetchall())
    
    for i in itemlist:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Product WHERE Product_ID = (%s)", (i[1]))
        items = list(cursor.fetchone())
        product_results.append(items)
    for i in product_results:
        i = list(i)
        actualprice = round(float(i[3])*float(i[5]),2)
        i.append(actualprice)
        results.append(i)
    return render_template('client/myfavourite.html', results=results)

@app.route("/buy", methods=['POST','GET'])
def addtoshoppingcart():
    if "shoppingcart" not in session:
        session['shoppingcart'] = []
    added = False
    targetPid = request.form["productid"]
    targetpName = request.form["productname"]
    targetpPrice = request.form["productprice"]
    targetpQuantity = request.form["productquantity"]
    if session['shoppingcart'] == []:
        session['shoppingcart'].append([targetPid,targetpName,targetpPrice,targetpQuantity])
        session.modified = True
    else:
        for i in session['shoppingcart']:
            if targetPid == i[0]:
                a=float(i[3])
                b=float(targetpQuantity)
                newq = a+b
                i[3]=newq
                session.modified = True
                added = True
                break
        if not added:
            session['shoppingcart'].append([targetPid,targetpName,targetpPrice,targetpQuantity])
            session.modified = True
    session['totalprice'] = 0    
    for i in session['shoppingcart']:
        session['totalprice'] += round(float(i[2])*float(i[3]),2)
        session.modified = True
    flash('Added '+targetpQuantity+' '+targetpName+' '+'to shopping cart.' )
    return redirect(request.referrer)

@app.route('/updatequantity', methods=['POST','GET'])
def updateqty():
    updateitem= request.form["itemid"]
    updatequantity = request.form["itemquantity"]
    for i in session['shoppingcart']:
        if updateitem == i[0]:
            i[3] = updatequantity
            session.modified = True
            break
    session['totalprice'] = 0    
    for i in session['shoppingcart']:
        session['totalprice'] += round(float(i[2])*float(i[3]),2)
        session.modified = True
    flash('Updated item quantity.')
    return redirect(request.referrer)

@app.route('/deleteitem', methods=['POST','GET'])
def deleteitem():
    deleteitem = request.form["itemid"]
    for i in session['shoppingcart']:
        if deleteitem == i[0]:
            session['shoppingcart'].remove(i)
            session.modified = True
            break
    session['totalprice'] = 0    
    for i in session['shoppingcart']:
        session['totalprice'] += round(float(i[2])*float(i[3]),2)
        session.modified = True
    flash('Deleted item.')
    return redirect(request.referrer)

@app.route('/checkout', methods=['POST','GET'])
def checkout():
    try:
        if session['logged_in'] == True:
            if len(session['shoppingcart']) >0:
                return render_template('client/checkout.html', title = 'Check out')
            else:
                flash('Shopping Cart is Empty')
                return redirect(request.referrer)
        else:
            flash('Log in to checkout!')
            return redirect(request.referrer)
    except:
        flash('Log in to checkout!')
        return redirect(request.referrer)

@app.route('/submitcheckout', methods=['POST','GET'])
def submitcheckout():
    receivername = request.form["receivername"]
    addressline1 = request.form["addressline1"]
    addressline2 = request.form["addressline2"]
    paymentmethod = request.form["paymentmethod"]
    contact = request.form["contact"]
    timeslot = request.form["timeslot"]
    otherrequirement = request.form["otherrequirement"]
    coupon = request.form['coupon']
    if len(coupon) == 0:
        if len(session['shoppingcart']) > 0:
            cursor = db.cursor()
            cursor.execute("SELECT User_ID FROM Users WHERE (User_Name) = (%s)", (session['currentuser']))
            userid = cursor.fetchone()
            cursor = db.cursor()
            cursor.execute("INSERT INTO Orders (User_ID,Order_Date,Total_Price,Address_Line1,Address_Line2,Payment_Method,Delivery_time_slot,Other_requirement,Contact) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(userid[0],date.today(),session['totalprice'],addressline1,addressline2,paymentmethod,timeslot,otherrequirement,contact))
            cursor=db.cursor()
            cursor.execute("SELECT Order_ID FROM ORDERS ORDER BY Order_ID DESC LIMIT 1")
            orderid = cursor.fetchone()
            for i in session['shoppingcart']:
                cursor=db.cursor()
                cursor.execute("INSERT INTO Order_Item (Order_ID,Product_ID,Item_Quantity,Price,Remark) VALUES (%s,%s,%s,%s,%s)",(orderid[0],i[0],i[3],i[2],'Null'))
            db.commit()
            session['shoppingcart'] = []
            session.modified = True
            session['totalprice'] = 0
            session.modified = True
            flash('Order Completed!')
            return render_template('client/home.html', title = 'Home')
        else:
            flash('Shopping Cart is Empty!')
            return redirect(request.referrer)
    else:
        cursor = db.cursor()
        if cursor.execute("""SELECT * FROM Coupon WHERE Coupon_code = (%s)""",(coupon)):
            if len(session['shoppingcart']) > 0:
                cursor = db.cursor()
                cursor.execute("SELECT User_ID FROM Users WHERE (User_Name) = (%s)", (session['currentuser']))
                userid = cursor.fetchone()
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Coupon WHERE (Coupon_code) = (%s)",(coupon))
                curesults = cursor.fetchone()
                session['totalprice'] = session['totalprice']*curesults[2]
                session.modified = True
                cursor = db.cursor()
                cursor.execute("INSERT INTO Orders (User_ID,Order_Date,Total_Price,Address_Line1,Address_Line2,Payment_Method,Delivery_time_slot,Other_requirement,Contact,Coupon_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(userid[0],date.today(),session['totalprice'],addressline1,addressline2,paymentmethod,timeslot,otherrequirement,contact,coupon))
                cursor=db.cursor()
                cursor.execute("SELECT Order_ID FROM ORDERS ORDER BY Order_ID DESC LIMIT 1")
                orderid = cursor.fetchone()
                for i in session['shoppingcart']:
                    cursor=db.cursor()
                    cursor.execute("INSERT INTO Order_Item (Order_ID,Product_ID,Item_Quantity,Price,Remark) VALUES (%s,%s,%s,%s,%s)",(orderid[0],i[0],i[3],i[2],'Null'))
                db.commit()
                session['shoppingcart'] = []
                session.modified = True
                session['totalprice'] = 0
                session.modified = True
                flash('Order Completed with coupon:'+' '+coupon+' '+curesults[1])
                return render_template('client/home.html', title = 'Home')
            else:
                flash('Shopping Cart is Empty!')
                return redirect(request.referrer)
        else:
            flash('Wrong coupon code!')
            return redirect(request.referrer)

@app.route('/admin')
def adminlogin():
    try:
        if session['adminloggedin'] == True:
            return redirect('/adminhome')
        else:
            return render_template('admin/adminlogin.html', title = 'Admin Panel')
    except:
        return render_template('admin/adminlogin.html', title = 'Admin Panel')

@app.route('/admin', methods=['POST'])
def adminlogin2():
    login_input_adminusername = request.form['login_input_adminusername']
    login_input_adminpassword = request.form['login_input_adminpassword']
    if login_input_adminusername == '123' and login_input_adminpassword == '123':
        session['adminloggedin'] = True
        flash('Logged in as Admin')
        return redirect('/adminhome')
    else:
        flash('Wrong User Name or Password')
        return redirect(request.referrer)

@app.route('/adminlogout')
def adminlogin3():
    session['adminloggedin'] = False
    session.modified = True
    flash('Logged out')
    return redirect('/admin')

@app.route('/adminhome')
def adminlogin4():
        if session['adminloggedin'] == True:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(User_ID) FROM Users")
            users = cursor.fetchone()
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(Order_ID) FROM Orders")
            orders = cursor.fetchone()
            cursor = db.cursor()
            cursor.execute("SELECT SUM(Item_Quantity) FROM Order_item")
            items = cursor.fetchone()
            cursor = db.cursor()
            cursor.execute("SELECT SUM(Total_Price) FROM Orders")
            earns = list(cursor.fetchone())
            earns[0] = round(earns[0],2)
            cursor = db.cursor()
            cursor.execute("SELECT Product_ID, SUM(Item_Quantity) TotalSum FROM Order_item GROUP BY Product_ID ORDER BY TotalSum DESC LIMIT 5")
            soldproduct = list(cursor.fetchall())
            soldproduct1 = []
            for i in soldproduct:
                i = list(i)
                cursor = db.cursor()
                cursor.execute("SELECT Product_Name, Product_Type, Product_Price FROM Product WHERE Product_ID = (%s)",(i[0]))
                detail = list(cursor.fetchone())
                i.append(detail[0])
                i.append(detail[1])
                i.append(detail[2])
                soldproduct1.append(i)
            label=[]
            values=[]
            for i in soldproduct1:
                label.append(i[2])
                values.append(float(i[1]))


            cursor = db.cursor()
            cursor.execute("SELECT Product_ID, SUM(Item_Quantity) TotalSum FROM Order_item GROUP BY Product_ID ORDER BY TotalSum")
            soldproductv2 = list(cursor.fetchall())
            soldproduct1v2 = []
            for i in soldproductv2:
                i = list(i)
                cursor = db.cursor()
                cursor.execute("SELECT Product_Name, Product_Type, Product_Price FROM Product WHERE Product_ID = (%s)",(i[0]))
                detail = list(cursor.fetchone())
                i.append(detail[0])
                i.append(detail[1])
                i.append(detail[2])
                soldproduct1v2.append(i)


            subtotal = 0
            values1=[]
            cursor = db.cursor()
            cursor.execute("SELECT DISTINCT Product_Type FROM Product")
            label1 = list(cursor.fetchall())
            label2 = []
            for i in label1:
                label2.append(i[0])
            for i in label1:
                for a in soldproduct1v2:
                    if a[3] == i[0]:
                        subtotal += a[1]
                values1.append(subtotal)
                subtotal = 0

            print(label1)
            print(values1)
            
            return render_template('admin/adminhome.html', title = 'Admin Panel', users=users,orders=orders,items=items,earns=earns,label=label,values=values,label2=label2,values1=values1)

@app.route('/admineditproduct')
def admineditproduct():
    try:
        if session['adminloggedin'] == True:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM PRODUCT")
            product_results = cursor.fetchall()
            return render_template('admin/admineditproduct.html', title = 'Admin Panel', product_results=product_results)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)
        
@app.route('/admineditproduct', methods=['POST'])
def admineditproduct2():
    try:
        if session['adminloggedin'] == True:
            productid = request.form["productid"]
            productname = request.form["productname"]
            producttype = request.form["producttype"]
            productprice = request.form["productprice"]
            productimage = request.form["productimage"]
            productdiscount = request.form["productdiscount"]
            cursor = db.cursor()
            cursor.execute("UPDATE Product SET Product_Name = (%s), Product_Type = (%s), Product_Price = (%s), Product_Image = (%s), Discount = (%s) WHERE Product_ID = (%s)",(productname,producttype,productprice,productimage,productdiscount,productid))
            db.commit()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM PRODUCT")
            product_results = cursor.fetchall()
            flash('Updated Product #'+productid)
            return render_template('admin/admineditproduct.html', title = 'Admin Panel', product_results=product_results)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)
@app.route('/adminnewproduct')
def adminnewproduct():
    try:
        if session['adminloggedin'] == True:
            return render_template('admin/adminnewproduct.html', title = 'Admin Panel')
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/adminnewproduct', methods=['POST'])
def adminnewproduct1():
    try:
        if session['adminloggedin'] == True:
            productname = request.form["productname"]
            producttype = request.form["producttype"]
            productprice = request.form["productprice"]
            productimage = request.form["productimage"]
            productdiscount = request.form["productdiscount"]
            cursor = db.cursor()
            cursor.execute("INSERT INTO Product (Product_Name, Product_Type, Product_Price, Product_Image, Discount) VALUES (%s,%s,%s,%s,%s)",(productname, producttype, productprice, productimage, productdiscount))
            db.commit()
            cursor = db.cursor()
            cursor.execute("SELECT Product_ID, Product_Name FROM Product ORDER BY Product_ID DESC LIMIT 1")
            target = cursor.fetchall()
            flash("Add product #"+str(target[0][0])+','+str(target[0][1]))
            return render_template('admin/adminnewproduct.html', title = 'Admin Panel')
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/admindeleteproduct')
def admindeleteproduct():
    try:
        if session['adminloggedin'] == True:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM PRODUCT")
            product_results = cursor.fetchall()
            return render_template('admin/admindeleteproduct.html', title = 'Admin Panel', product_results=product_results)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/admindeleteproduct', methods=["POST"])
def admindeleteproduct1():
    try:
        if session['adminloggedin'] == True:
            productid = request.form["productid"]
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Product WHERE Product_ID = (%s)",(productid))
            target = cursor.fetchone()
            cursor = db.cursor()
            cursor.execute("DELETE FROM Product WHERE Product_ID = (%s)",(productid))
            db.commit()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM PRODUCT")
            product_results = cursor.fetchall()
            flash("Deleted product #"+productid+' '+str(target[1]))
            return render_template('admin/admindeleteproduct.html', title = 'Admin Panel', product_results=product_results)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)
@app.route('/adminedituser')
def adminedituser():
    try:
        if session['adminloggedin'] == True:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users")
            userresults = cursor.fetchall()
            return render_template('admin/adminedituser.html', title='Admin Panel', userresults=userresults)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/adminedituser', methods=["POST"])
def adminedituser1():
    try:
        if session['adminloggedin'] == True:
            userid = request.form["userid"]
            username = request.form["username"]
            userpassword = request.form["userpassword"]
            dob = request.form['dob']
            email = request.form['email']
            phonenumber = request.form['phonenumber']
            cursor = db.cursor()
            cursor.execute('UPDATE Users SET User_Name = (%s), User_Password = (%s), DateofBirth = (%s), Email = (%s), Phonenumber = (%s) WHERE User_ID = (%s)',(username,userpassword,dob,email,phonenumber,userid))
            db.commit()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users")
            userresults = cursor.fetchall()
            flash('Updated User#'+userid)
            return render_template('admin/adminedituser.html', title='Admin Panel', userresults=userresults)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/admindeleteuser')
def admindeleteuser():
    try:
        if session['adminloggedin'] == True:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users")
            userresults = cursor.fetchall()
            return render_template('admin/admindeleteuser.html', title='Admin Panel', userresults=userresults)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/admindeleteuser', methods=['POST'])
def admindeleteuser1():
    try:
        if session['adminloggedin'] == True:
            userid = request.form["userid"]
            cursor = db.cursor()
            cursor.execute("SELECT Order_ID FROM Orders WHERE User_ID = (%s)",(userid))
            orderlist = list(cursor.fetchall())
            print (orderlist)
            for i in orderlist:
                cursor = db.cursor()
                cursor.execute("DELETE FROM Order_item WHERE Order_ID = (%s)",(i[0]))
            cursor = db.cursor()
            cursor.execute("DELETE FROM Orders WHERE User_ID = (%s)",(userid))
            cursor = db.cursor()
            cursor.execute("DELETE FROM user_favourite WHERE User_ID = (%s)",(userid))
            cursor = db.cursor()
            cursor.execute("DELETE FROM Users WHERE User_ID = (%s)",(userid))
            db.commit()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Users")
            userresults = cursor.fetchall()
            flash ('Deleted User#'+userid)
            return render_template('admin/admindeleteuser.html', title='Admin Panel', userresults=userresults)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/admineditorder')
def admineditorder():
    try:
        if session['adminloggedin'] == True:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Orders")
            realorderinfo = list(cursor.fetchall())
            orderinfo = []
            cursor = db.cursor()
            for i in realorderinfo:
                if cursor.execute("SELECT * FROM Coupon WHERE (Coupon_code) = (%s)",(i[10])):
                    i = list(i)
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM Coupon WHERE (Coupon_code) = (%s)",(i[10]))
                    couponinfo = cursor.fetchone()
                    i.append(couponinfo[1])
                    orderinfo.append(i)
                else:
                    orderinfo.append(i)
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Order_Item")
            itemlist = list(cursor.fetchall())
            actuallist = []
            for i in itemlist:
                i = list(i)
                summary = round(i[2]*i[3],2)
                i.append(summary)
                cursor = db.cursor()
                cursor.execute("SELECT Product_Name, Product_Image FROM Product WHERE (Product_ID) = (%s)",(i[1]))
                that = cursor.fetchall()
                that = list(that)
                for a in that:
                    i.append(a[0])
                    i.append(a[1])
                    actuallist.append(i)
            return render_template('admin/admineditorder.html', title = 'Admin Panel', orderinfo=orderinfo, actuallist=actuallist)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/admineditorder', methods=['POST'])
def admineditorder1():
    try:
        if session['adminloggedin'] == True:
            orderid = request.form['orderid']
            date = request.form['date']
            addressline1 = request.form['addressline1']
            addressline2 = request.form['addressline2']
            paymentmethod = request.form['paymentmethod']
            timeslot = request.form['timeslot']
            otherrequirement = request.form['otherrequirement']
            contact = request.form['contact']
            cursor = db.cursor()
            cursor.execute("UPDATE Orders SET Order_Date = (%s), Address_Line1 = (%s), Address_Line2 = (%s), Payment_method = (%s), Delivery_time_slot = (%s), Other_requirement = (%s), contact = (%s) WHERE Order_ID = (%s)",(date,addressline1,addressline2,paymentmethod,timeslot,otherrequirement,contact,orderid))
            db.commit()
            flash('Updated Order #'+orderid)
            return redirect(request.referrer)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/adminupdateorderitem', methods=["POST"])
def adminupdateorderitem():
    if session['adminloggedin'] == True:
        orderid = request.form['orderid']
        productid = request.form['productid']
        quantity = request.form['quantity']
        newtotalprice = 0
        cursor = db.cursor()
        cursor.execute("UPDATE Order_Item SET Item_Quantity = (%s) WHERE Order_ID = (%s) AND Product_ID = (%s)",(quantity,orderid,productid))
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Order_Item WHERE Order_ID = (%s)",(orderid))
        items = cursor.fetchall()
        for i in items:
            newtotalprice += round(float(i[2])*float(i[3]),2)
        cursor =db.cursor()
        if cursor.execute("SELECT Coupon_code FROM Orders WHERE Order_ID = (%s)",(orderid)):
            cursor =db.cursor()
            cursor.execute("SELECT Coupon_code FROM Orders WHERE Order_ID = (%s)",(orderid))
            tcc = cursor.fetchone()
            if len(tcc[0]) > 0: 
                cursor = db.cursor()
                cursor.execute("SELECT Coupon_discount FROM Coupon WHERE Coupon_code = (%s)",(tcc[0]))
                dis = cursor.fetchone()
                newtotalprice = newtotalprice*dis[0]
        cursor = db.cursor()
        cursor.execute("UPDATE Orders SET Total_Price = (%s) WHERE Order_ID = (%s)",(newtotalprice,orderid))
        db.commit()
        flash ('Updated Order #'+orderid)
        return redirect(request.referrer)

@app.route('/admindeleteorderitem', methods=["POST"])
def admindeleteorderitem():
    try:
        if session['adminloggedin'] == True:
            orderid = request.form['orderid']
            productid = request.form['productid']
            newtotalprice = 0
            cursor = db.cursor()
            cursor.execute("DELETE FROM Order_Item WHERE Order_ID = (%s) AND Product_ID = (%s)",(orderid,productid))
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Order_Item WHERE Order_ID = (%s)",(orderid))
            items = cursor.fetchall()
            for i in items:
                newtotalprice += round(float(i[2])*float(i[3]),2)
            cursor = db.cursor()
            cursor.execute("UPDATE Orders SET Total_Price = (%s) WHERE Order_ID = (%s)",(newtotalprice,orderid))
            db.commit()
            flash ('Updated Order #'+orderid)
            return redirect(request.referrer)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/admindeleteorder', methods=["POST"])
def admindelteorder():
    try:
        if session['adminloggedin'] == True:
            orderid = request.form['orderid']
            cursor = db.cursor()
            cursor.execute("DELETE FROM Order_Item WHERE Order_ID = (%s)",(orderid))
            cursor = db.cursor()
            cursor.execute("DELETE FROM Orders WHERE Order_ID = (%s)",(orderid))
            db.commit()
            flash('Deleted Order #'+orderid)
            return redirect(request.referrer)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/adminsearchorder')
def adminsearchorder():
    try:
        if session['adminloggedin'] == True:
            return render_template('admin/adminsearchorder.html', title = 'Admin Panel')
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/adminsearchorder', methods=['POST'])
def adminsearchorder1():
    try:
        if session['adminloggedin'] == True:
            method = request.form['method']
            idvalue = request.form['idvalue']
            if method == 'Order':
                print(1)
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Orders WHERE Order_ID = (%s)",(idvalue))
                realorderinfo = list(cursor.fetchall())
                orderinfo = []
                cursor = db.cursor()
                for i in realorderinfo:
                    if cursor.execute("SELECT * FROM Coupon WHERE (Coupon_code) = (%s)",(i[10])):
                        i = list(i)
                        cursor = db.cursor()
                        cursor.execute("SELECT * FROM Coupon WHERE (Coupon_code) = (%s)",(i[10]))
                        couponinfo = cursor.fetchone()
                        i.append(couponinfo[1])
                        orderinfo.append(i)
                    else:
                        orderinfo.append(i)
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Order_Item WHERE Order_ID = (%s)",(idvalue))
                itemlist = list(cursor.fetchall())
                actuallist = []
                for i in itemlist:
                    i = list(i)
                    summary = round(float(i[2])*float(i[3]),2)
                    i.append(summary)
                    cursor = db.cursor()
                    cursor.execute("SELECT Product_Name, Product_Image FROM Product WHERE (Product_ID) = (%s)",(i[1]))
                    that = cursor.fetchall()
                    that = list(that)
                    for a in that:
                        i.append(a[0])
                        i.append(a[1])
                        actuallist.append(i)
            else:
                print(2)
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Orders WHERE (User_ID) = (%s)",(idvalue))
                realorderinfo = list(cursor.fetchall())
                orderinfo = []
                cursor = db.cursor()
                for i in realorderinfo:
                    if cursor.execute("SELECT * FROM Coupon WHERE (Coupon_code) = (%s)",(i[10])):
                        i = list(i)
                        cursor = db.cursor()
                        cursor.execute("SELECT * FROM Coupon WHERE (Coupon_code) = (%s)",(i[10]))
                        couponinfo = cursor.fetchone()
                        i.append(couponinfo[1])
                        orderinfo.append(i)
                    else:
                        orderinfo.append(i)
                orderitemlist = []
                realorderitemlist = []
                actuallist = []
                cursor = db.cursor()
                cursor.execute("SELECT DISTINCT Order_ID FROM Orders WHERE (User_ID) = (%s)",(idvalue))
                distinctorderid = cursor.fetchall()
                for i in distinctorderid:
                    i = list(i)
                    orderitemlist.append(i[0])
                for i in orderitemlist:
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM Order_item WHERE (Order_ID) = (%s)",(i))
                    this = cursor.fetchall()
                    this = list(this)
                    for i in this:
                        i = list(i)
                        summary = round(float(i[2])*float(i[3]),2)
                        i.append(summary)
                        realorderitemlist.append(i)
                for i in realorderitemlist:
                    i = list(i)
                    cursor = db.cursor()
                    cursor.execute("SELECT Product_Name, Product_Image FROM Product WHERE (Product_ID) = (%s)",(i[1]))
                    that = cursor.fetchall()
                    that = list(that)
                    for a in that:
                        i.append(a[0])
                        i.append(a[1])
                        actuallist.append(i)
            print (len(orderinfo))
            if len(orderinfo) == 0:
                flash ('No Results')
            return render_template('admin/adminsearchorder.html', title = 'Admin Panel',orderinfo=orderinfo, actuallist=actuallist)
        else:
            flash('Login in to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)

@app.route('/productdetail/<int:id>')
def productdetail(id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Product WHERE Product_ID = (%s)",(id))
    results = list(cursor.fetchone())
    price = round(float(results[3])*float(results[5]),2)
    results.append(price)
    print(results)
    return render_template('client/productdetail.html',results=results)

@app.route('/removefa', methods=['POST'])
def removefa():
    pid = request.form['productid']
    cursor = db.cursor()
    cursor.execute("DELETE FROM user_favourite WHERE User_ID = (%s) AND Product_ID = (%s)",(session['currentuserid'],pid))
    db.commit()
    flash('Removed from favourite list!')
    return redirect(request.referrer)

@app.route('/adminnewcoupon')
def adminnc():
    try:
        if session['adminloggedin'] == True:
            return render_template('admin/adminnewcoupon.html')
        else:
            flash('Login in to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login in to use this function!')
        return redirect(request.referrer)

@app.route('/adminnewcoupon', methods=['POST'])
def adminnc1():
    cdesc = request.form['cdesc']
    cdiscount = request.form['cdiscount']
    ccode = request.form['ccode']
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO Coupon (Coupon_Description, Coupon_discount, Coupon_code) VALUE (%s,%s,%s)",(cdesc,cdiscount,ccode))
        db.commit()
        flash('Added coupon'+' '+ccode+' '+'!')
        return redirect(request.referrer)
    except:
        flash('Coupon already taken, try another one!')
        return redirect(request.referrer)


@app.route('/admineditcoupon')
def admineditcoupon():
    try:
        if session['adminloggedin'] == True:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM coupon")
            coupon_results = cursor.fetchall()
            return render_template('admin/admineditcoupon.html', title = 'Admin Panel', coupon_results=coupon_results)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)
        
@app.route('/admineditcoupon', methods=['POST'])
def admineditcoupon2():
    try:
        if session['adminloggedin'] == True:
            couponid = request.form["couponid"]
            cdesc = request.form["cdesc"]
            cdis = request.form["cdis"]
            ccode = request.form["ccode"]
            cursor = db.cursor()
            cursor.execute("UPDATE Coupon SET Coupon_Description = (%s), Coupon_discount = (%s), Coupon_code = (%s) WHERE Coupon_ID = (%s)",(cdesc,cdis,ccode,couponid))
            db.commit()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Coupon")
            coupon_results = cursor.fetchall()
            flash('Updated Coupon #'+couponid)
            return render_template('admin/admineditcoupon.html', title = 'Admin Panel', coupon_results=coupon_results)
        else:
            flash('Login to use this function!')
            return redirect(request.referrer)
    except:
        flash('Login to use this function!')
        return redirect(request.referrer)



if __name__ == '__main__':
    app.run(debug=True)