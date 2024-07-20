#import libraries
from flask import Flask, redirect, render_template, flash, request, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import uuid
from werkzeug.utils import secure_filename
import os
import shutil

app = Flask(__name__)

app.secret_key = "apartment_rental"
#code for connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Roshan@22'
app.config['MYSQL_DB'] = 'apartmentRental'
# Intialize MySQL
mysql = MySQL(app)
           
@app.route('/')
def home() :
    return render_template('welcome.html')
    
    
@app.route('/AdminLogin', methods=['GET', 'POST'])
def AdminLogin() :
    error = None
    if request.method == 'POST' and 'adminUsername' in request.form and 'adminPass' in request.form and 'securityPass' in request.form:
        if request.form['adminUsername'] != 'admin' or \
                request.form['adminPass'] != '123' or \
                request.form['securityPass'] != '123':
            error = 'Invalid credentials'
        else:
            flash('You have logged in successfully!!')
            return redirect(url_for('AdminDashboard'))
    return render_template('AdminLogin.html', error=error)


@app.route('/AdminLogout')
def AdminLogout() :
    log2 = ''
    log2 = 'You have logged out successfully!!'
    return render_template('AdminLogin.html', log2=log2)


@app.route('/TenantLogin', methods=['GET', 'POST'])
def TenantLogin() :
    error = None
    if request.method == 'POST' and 'username' in request.form and 'pswd1' in request.form :
        username = request.form['username']
        password = request.form['pswd1']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM TENANT WHERE EMAIL = % s AND PSWD = % s', (username, password, ))
        account = cursor.fetchone()
        # If account exists in TENANT table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['T_ID']
            session['username'] = account['EMAIL']
            # Redirect to home page
            flash('You have logged in successfully!!')
            return redirect(url_for('TenantDashboard'))
        else:
            # Account doesnt exist or username/password incorrect
            error = ' Invalid Username or Password !!'
    return render_template('TenantLogin.html', error=error)


@app.route('/Logout')
def Logout() :
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    log = ''
    log = 'You have logged out successfully!!'
    return render_template('TenantLogin.html', log=log)


# User Registration
@app.route('/Register', methods=['GET','POST'])
def Register():
    msg1 = ''
    log = ''
    #applying empty validation
    if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'phNo' in request.form and 'dob' in request.form and 'occupation' in request.form and 'gender' in request.form and 'email' in request.form and 'pswd' in request.form:
        #passing HTML form data into python variable
        fname = request.form['firstname']
        lname = request.form['lastname']
        ph = request.form['phNo']
        dob = request.form['dob']
        gender = request.form['gender']
        occupation = request.form['occupation']
        email = request.form['email']
        pswd = request.form['pswd']
        if len(ph) != 10 :
            msg1 = 'Phone No. must be of 10 digits!!'
            return render_template('TenantRegister.html', msg1=msg1)
        #creating variable for connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM TENANT WHERE EMAIL = % s', (email,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            msg1 = 'Email already exists !'
        else:
            #executing query to insert new data into MySQL
            cursor.execute('INSERT INTO TENANT VALUES (% s, % s, NULL , % s, % s, % s , % s , % s , NULL, % s)', (fname, lname, ph, email, gender ,dob, occupation,pswd))
            mysql.connection.commit()
            #displaying message
            log = 'You have successfully registered !'
            return render_template('TenantLogin.html', log=log)

@app.route('/TenantRegister')
def tregister() :
    return render_template('TenantRegister.html')


#----------- ADMIN DASHBOARD----------------


@app.route('/AdminDashboard')
def AdminDashboard() :
    t_users=''
    return render_template('AdminDashboard.html', t_users=t_users)

@app.route('/TotalUsers')
def TotalUsers() :
    msg5=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT FNAME, LNAME, GENDER, PH_NO, EMAIL FROM TENANT')
    mysql.connection.commit()
    msg5=cursor.fetchall()
    return render_template('TotalUsers.html', msg5=msg5)


@app.route('/tenantReport', methods=['GET', 'POST'])
def tenantReport():
    tenantReport = ''
    msg6 = ''
    # creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT Uname, aptNo, TFatherName, PAddress FROM booking')
    msg6 = cursor.fetchall()
    return render_template('tenantReport.html', msg6=msg6, tenantReport=tenantReport)


# apartment rooms and add it
@app.route('/ApartmentRooms', methods=['POST','GET'])
def ApartmentRooms() :
    msg2=''
    msg3=''
    aptTitle = ''
    description = ''
    area = ''
    Rent=0
    Room = 0
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'room' in request.form and 'block' in request.form and 'status' in request.form and 'rentPerMonth' in request.form:
        #passing HTML form data into python variable
        Room = request.form['room']
        Block = request.form['block']
        Status = request.form['status']
        Rent = request.form['rentPerMonth']
        aptTitle = request.form['apartmentTitle'] 
        description = request.form.get('desc')
        area = request.form['area']
        file1 = request.files['hall']
        file2 = request.files['kitchen']
        file3 = request.files['bedroom']
        file4 = request.files['extra']
        path = 'static/images/apartment'+Room
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
                                # concatenate the directory path and the filename securely
        file1.save(os.path.join('static/images/apartment'+Room, secure_filename(file1.filename)))
        file2.save(os.path.join('static/images/apartment'+Room, secure_filename(file2.filename)))
        file3.save(os.path.join('static/images/apartment'+Room, secure_filename(file3.filename)))
        file4.save(os.path.join('static/images/apartment'+Room, secure_filename(file4.filename)))
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM APARTMENT WHERE ROOM_NO = % s', (Room,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            msg2 = 'Apartment already exists !'
        else:
            #executing query to insert new data into MySQL
            cursor.execute('INSERT INTO APARTMENT VALUES (% s, % s, % s, % s)', (Room, Block, Rent, Status))
            mysql.connection.commit()
            cursor.execute('INSERT INTO APARTMENT_DETAILS VALUES (% s, % s, % s, % s)', (Room, aptTitle, area, description))
            mysql.connection.commit()
            Image_url = 'images/apartment'+Room
            cursor.execute('INSERT INTO APARTMENT_PHOTOS VALUES (% s, % s, %s, %s, %s, %s)', (Room, Image_url, file1.filename, file2.filename, file3.filename, file4.filename))
            mysql.connection.commit()
            #displaying message
            msg2 = 'You have successfully added an Apartment !'

    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    msg3=cursor.fetchall()
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('ApartmentRooms.html',msg2=msg2,msg3=msg3,img_url=img_url)


@app.route('/UpdateApartment', methods=['GET','POST'])
def UpdateApartment():
    msg2=''
    msg3=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'room1' in request.form and 'status1' in request.form and 'rentPerMonth1' in request.form :
        #passing HTML form data into python variable
        Room1 = request.form['room1']
        Status1 = request.form['status1']
        Rent1 = request.form['rentPerMonth1']
        area1 = request.form['up_area']
        title1 = request.form['up_title']
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM APARTMENT WHERE ROOM_NO = % s', (Room1,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            #executing query to insert new data into MySQL
            cursor.execute('UPDATE APARTMENT SET RENT_PER_MONTH = % s, APT_STATUS = % s WHERE ROOM_NO = % s',(Rent1,Status1,Room1))
            mysql.connection.commit()
            cursor.execute('UPDATE APARTMENT_DETAILS SET AREA = % s, APT_TITLE = % s WHERE ROOM_NO = % s',(area1,title1,Room1))
            mysql.connection.commit()
        else:
            msg2 = 'Apartment doesn\'t exists !'

    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    msg3=cursor.fetchall() 
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('ApartmentRooms.html', msg2=msg2,msg3=msg3,img_url=img_url)


@app.route('/DeleteApartment', methods=['GET','POST'])
def DeleteApartment() :
    msg2=''
    msg3=''
    #creating variable for connection
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #applying empty validation
    if request.method == 'POST' and 'room2' in request.form :
        #passing HTML form data into python variable
        Room2 = request.form['room2']
        #query to check given data is present in database or no
        cursor.execute('SELECT * FROM APARTMENT WHERE ROOM_NO = % s', (Room2,))
        #fetching data from MySQL
        result = cursor.fetchone()
        if result:
            #executing query to insert new data into MySQL
            cursor.execute('SELECT PATHNAME FROM APARTMENT_PHOTOS WHERE ROOM_NO = % s',(Room2,))
            mysql.connection.commit()
            path = cursor.fetchone()
            pathname = 'static/'+path['PATHNAME']
            shutil.rmtree(pathname, ignore_errors=False, onerror=None)
            cursor.execute('DELETE FROM APARTMENT WHERE ROOM_NO = % s',(Room2,))
            mysql.connection.commit()
        else:
            msg2 = 'Apartment doesn\'t exists !'

    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    msg3=cursor.fetchall() 
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('ApartmentRooms.html', msg2=msg2,msg3=msg3,img_url=img_url)


#---------------------------------------------- TENANT DASHBOARD---------------------------------------------


@app.route('/TenantDashboard')
def TenantDashboard() :
    if 'loggedin' in session:
        return render_template('TenantDashboard.html')
    return render_template('TenantLogin.html')


@app.route('/RentApartment')
def rentApartment() :
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT APT_TITLE, A.ROOM_NO, AREA, RENT_PER_MONTH, APARTMENT_DESC FROM APARTMENT AS A, APARTMENT_DETAILS AS AD WHERE A.ROOM_NO = AD.ROOM_NO AND A.APT_STATUS = "Unoccupied"')
    mysql.connection.commit()
    apartment=cursor.fetchall()
    cursor.execute('SELECT * FROM APARTMENT_PHOTOS')
    mysql.connection.commit()
    img_url = cursor.fetchall()
    return render_template('RentApartment.html',apartment=apartment, img_url=img_url)



@app.route('/Details', methods=['GET', 'POST'])
def Details():
    Error = ''
    Uname = ''
    Tname = ''
    PAddress = ''
    aptNo = ''
    TFatherName = ''
    Date = date.today()
    rentAmt = 0
    Deposit = 0
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST' and 'Username' in request.form and 'aptNo' in request.form and 'TFatherName' in request.form and 'PerAddr' in request.form:
        Uname = request.form['Username']
        aptNo = request.form['aptNo']
        TFatherName = request.form['TFatherName']
        PAddress = request.form['PerAddr']
        insert_query = "INSERT INTO booking (Uname, aptNo, TFatherName, PAddress) VALUES (%s, %s, %s, %s)"
        data = (Uname, aptNo, TFatherName, PAddress)
        cursor.execute(insert_query, data)
        mysql.connection.commit()
        return redirect(url_for('thanks'))

    return render_template('Details.html', Error=Error)


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')



if __name__ == '__main__':
    app.run(port=5000,debug=True)
