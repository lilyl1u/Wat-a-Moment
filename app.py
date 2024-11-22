from flask import Flask, request, render_template, redirect, url_for, jsonify
import mysql.connector
import requests
from mysql.connector import Error
app = Flask(__name__)

MYSQL_SERVER = "http://localhost:3000"
# change to js server's address

@app.route('./')
def homepage():
    return render_template('index.html')

@app.route('./signup')
def signup():
    # replace this later
    return render_template('index.html')
    #call function is user exists
    # if true -> return message "choose a new username"-> return  template
    #       else-> call createWamUser and return dashboard 


@app.route('./login')
def login():
    if request.method== 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        # get form data
        username = request.form.get('username')
        password = request.form.get('password')

        #make post reqest to js server
        #creates JSON object that backend will expect
        payload = {"wamUserId": username, "password": password}
        try: 
            #sneds post request to wamUserLogin on backend
            response = requests.post(f"{MYSQL_SERVER}/wamUserLogin", json=payload)
            if response.status_code == 200:
                if response.text == "Incorrect Username and/or Password":
                    return render_template('login.html', errors="Incorrect Username and/or Passowrd!")
            else:
                # user entered corect stuff
                # after completing succesfull action, redirect to new page 
                # this is convention to use after post
                return redirect('/dashboard')
        except Exception as e:
            #handle connection errors
            return render_template('login.html', error="Unable to connect to the server.")




    #call WamUser-> already redirects to dashboard 
    # if error message then send to html "error" + return login
    # angies function already returns true/false


    

















if __name__ == '__main__':
    app.run(debug=True)