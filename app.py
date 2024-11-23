from flask import Flask, request, render_template, redirect, url_for, jsonify, session
import mysql.connector
import requests
import random
import time
from mysql.connector import Error
import pymysql

from itertools import zip_longest

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session handling

API_SERVER = "http://localhost:3000"
'''
# Database connection
connection = pymysql.connect(
    host = 'riku.shoshin.uwaterloo.ca',
    user = 'a498wang',
    password ='dbz4SLMtIM0bdgn8Q0%0',
    database= 'db101_a498wang'
)
=======
MYSQL_SERVER = "http://localhost:3000"


@app.template_global()
def zip(*args):
    """Add zip function to templates"""
    return zip_longest(*args)

# Countdown timer routes
@app.route('/start_countdown', methods=['GET'])
def start_countdown():
    session['countdown'] = 5
    return render_template('photo.html', 
                           countdown_active=True, 
                           seconds=session['countdown'])

@app.route('/update_countdown', methods=['POST'])
def update_countdown():
    if 'countdown' in session:
        if session['countdown'] > 0:
            session['countdown'] -= 1
            return jsonify({'countdown': session['countdown'], 'active': True})
        else:
            session.pop('countdown', None)  # Clear countdown from session
            return jsonify({'countdown': 0, 'active': False})
    return jsonify({'countdown': 0, 'active': False})

# Random caption generation
'''


# Routes for views
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Render the login page
        return render_template('login.html')

    if request.method == 'POST':
        # Extract username and password from the form
        username = request.form.get('username')
        password = request.form.get('password')

        # Prepare payload for the Node.js login API
        payload = {"username": username, "password": password}

        try:
            print(f"[LOGIN] Attempting login for user: {username}")
            # Send login request to Node.js
            response = requests.post(f"{API_SERVER}/wamUserLogin", json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"[LOGIN] Response from Node.js: {response.status_code} - {data}")

                # Check for errors in the Node.js response
                if "error" in data:
                    print(f"[LOGIN] Error from Node.js: {data['error']}")
                    return render_template('login.html', error=data["error"])

                # Handle successful login
                elif "redirect" in data:
                    print(f"[LOGIN] Login successful for user: {username}")
                    # Save session in Flask
                    session['username'] = username
                    print("[LOGIN] Flask session updated.")

                    # Sync session with Node.js
                    node_payload = {"username": username}
                    try:
                        sync_response = requests.post(f"{API_SERVER}/sync-session", json=node_payload, timeout=5)
                        if sync_response.status_code == 200:
                            print(f"[LOGIN] Session synced with Node.js: {sync_response.text}")
                        else:
                            print(f"[LOGIN] Failed to sync session with Node.js: {sync_response.status_code} - {sync_response.text}")
                    except Exception as e:
                        print(f"[LOGIN] Error syncing session with Node.js: {e}")

                    # Redirect to dashboard or appropriate page
                    return redirect(data["redirect"])
                else:
                    print("[LOGIN] Unexpected response from Node.js.")
                    return render_template('login.html', error="Unexpected response from server.")
            else:
                # Handle invalid credentials
                print(f"[LOGIN] Invalid credentials: {response.status_code}")
                return render_template('login.html', error="Invalid username or password.")

        except requests.exceptions.RequestException as e:
            # Handle connection issues
            print(f"[LOGIN] Error connecting to Node.js server: {e}")
            return render_template('login.html', error="Unable to connect to the server.")
        except Exception as e:
            # Catch any other errors
            print(f"[LOGIN] Unexpected error: {e}")
            return render_template('login.html', error="An unexpected error occurred.")
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        payload = {"username": username, "password": password}
        try:
            #print(f"Attempting login with payload: {payload}")
            response = requests.post(f"{API_SERVER}/wamUserLogin", json=payload, timeout=10)
            #print(f"Response from backend: {response.status_code} - {response.text}")
            
            if response.status_code == 200: #if app.js returns a successful HTTP status code 
                data = response.json() #parses json response of app.js
                if "error" in data: #if there is word "error" in json response
                    return render_template('login.html', error=data["error"]) #return to user with error
                elif "redirect" in data:
                    session['username'] = username  # Save user session
                    node_payload = {"username": username}
                    try:
                        sync_response = requests.post(f"{API_SERVER}/sync-session", json=node_payload)
                        print(f"Sync session response: {sync_response.status_code} - {sync_response.text}")
                    except Exception as e:
                        print(f"Error syncing session with Node.js: {e}")
                    return redirect(data["redirect"])
                #else:
                    #return render_template('login.html', error="Unexpected response from server.")
            else:
                return render_template('login.html', error="Invalid user or password.") #technically status code 401
        except Exception as e:
            #print(f"Error during login: {e}")
            return render_template('login.html', error="Unable to connect to the server.") #tecnically status code 500
'''
'''
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        payload = {"username": username, "password": password}
        try:
            print(f"Attempting login with payload: {payload}")
            response = requests.post(f"{API_SERVER}/wamUserLogin", json=payload)
            print(f"Response from backend: {response.status_code} - {response.text}")
            if response.status_code == 200:
                if response.text == "Incorrect Username and/or Password":
                    return render_template('login.html', errors="Incorrect Username and/or Password!")
                else:
                    return redirect('/dashboard')
            else:
                return render_template('login.html', error="Error: Unable to authenticate user.")
        except Exception as e:
            print(f"Error during login: {e}")
            return render_template('login.html', error="Unable to connect to the server.")
'''
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        classCode = request.form.get('classCode')
        firstName = request.form.get('fname')
        lastName = request.form.get('lname')

        if classCode != 'SE101':
            return render_template('signup.html', message="Invalid class code!")

        payload = {
            "username": username, 
            "password": password, 
            "classCode": classCode, 
            "firstName": firstName, 
            "lastName": lastName
        }
        try:
            # Check if the user already exists
            response = requests.get(f"{API_SERVER}/getWamUser/{username}")
            if response.status_code == 200 and response.json().get("success"):
                return render_template('signup.html', message="Username is already taken.")
            
            # Create a new user
            response = requests.post(f"{API_SERVER}/createWamUser", json=payload)
            if response.status_code == 200 and response.json().get("success"):
                session['username'] = username  # Log the user in immediately
                return redirect(url_for('dashboard'))
            return render_template('signup.html', message="Unable to create account.")
        except Exception as e:
            print(f"Signup error: {e}")
            return render_template('signup.html', message="Unable to connect to the server.")
            
'''
            response = requests.post(f"{API_SERVER}/getWamUser/:{username}", json=payload)
            data = response.json()
            if data.get("success"): #if value of success is true
                return render_template('signup.html', message="Username taken")
        
            response = requests.post(f"{API_SERVER}/createWamUser", json=payload)
            data = response.json()
            if data.get("success"): #if value of success is true
                return redirect('/dashboard')
        except Exception:
            return render_template('signup.html', message="Unable to connect to the server.")
        
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        class_code = request.form.get('classCode')
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')

        if class_code != 'SE101':
            message = "Invalid class code!"
            return render_template('signup.html', message=message)

        payload = {
            "username": username, 
            "password": password, 
            "classCode": class_code, 
            "firstName": first_name, 
            "lastName": last_name
        }
        try:
            response = requests.post(f"{API_SERVER}/wamUserSignup", json=payload)
            if response.status_code == 200:
                return redirect('/dashboard')
        except Exception:
            return render_template('signup.html', error="Unable to connect to the server.")
'''
@app.route('/logout', methods=['POST'])
def logout():
    print("Logout route hit")
    try:
        print(f"Sending logout request to {API_SERVER}/logout")
        response = requests.post(f"{API_SERVER}/logout", timeout=5)
        print(f"Received response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            session.clear()  # Clear Flask session
            print("Flask session cleared")
            return redirect('/')  # Redirect to the homepage
        else:
            print("Failed to log out on Node.js side")
            return render_template('dashboard.html', message="Failed to log out. Please try again.")
    except Exception as e:
        print(f"Error during logout: {e}")
        return render_template('dashboard.html', message="Unable to connect to the server.")
'''
@app.route('/logout', methods=['POST'])
def logout():
    print("Logout route hit")
    try:
        response = requests.post(f"{API_SERVER}/logout")
        if response.status_code == 200:
            session.clear()  # Clear Flask session
            return redirect('/')  # Redirect to the homepage
        else:
            return render_template('dashboard.html', message="Failed to log out. Please try again.")
    except Exception as e:
        print(f"Error during logout: {e}")
        return render_template('dashboard.html', message="Unable to connect to the server.")
'''
'''
        response = requests.post(f"{API_SERVER}/logout")
        if response.status_code == 200:
            session.pop('username', None)  # Clear the session
            return redirect(url_for('index'))  # Redirect to the homepage after logout
        else:
            return render_template('dashboard.html', message="Failed to log out. Please try again.")
    except Exception as e:
        print(f"Error during logout: {e}")
        return render_template('dashboard.html', message="Unable to connect to the server.")
    '''
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/photo')
def photo():
    return render_template('photo.html')

@app.route('/classphotos')
def viewclassphotos():
    return render_template('viewclassphotos.html')


@app.route('/yourphotos')
def viewyourphotos():
    return render_template('viewyourphotos.html')

@app.route('/viewyourphotos')
def view_your_photos():
    if 'username' not in session:
        return redirect('/login')
    try:
        #get user photos
        response = requests.get(f"{MYSQL_SERVER}/getPrivatePhotos/{session['username']}")
        if response.status_code == 200:
            photos = response.json()
            #get random comments for each photos
            # Generate a random comment for each photo from your comments list
            photo_comments = [random.choice(comments) for _ in range(len(photos))]
            return render_template('viewyourphotos.html', photos=photos, comments = photo_comments, total_photos=len(photos))
        else:
            return render_template('viewyourphotos.html', error="Couldn't fetch your photos", photos=[])
    except Exception as e:
        # Handle any other errors that might occur
        return render_template('viewyourphotos.html', 
                             error=f"Error: {str(e)}",
                             photos=[])

@app.route('/dashboard')
def dash_board():
    return render_template('dashboard.html')

@app.route('/scroll')
def scroll():
    return render_template('scroll.html')

@app.route('/viewclassphotos')
def view_class_photos():
    if 'username' not in session:
        return redirect('/login')
    try:
        #get class code assuming its se101 or stored in session
        class_code = "SE101" #or session.get('class code')
        
        response = requests.get(f"{MYSQL_SERVER}/getPublicPhotos/{class_code}")
        if response.status_code == 200:
            photos = response.json()
            photo_comments = [random.choice(comments) for _ in range(len(photos))]
            return render_template('viewclassphotos.html', 
                                photos=photos,
                                comments=photo_comments,
                                total_photos=len(photos))
        else:
            return render_template('viewclassphotos.html', 
                                error="Couldn't fetch class photos",
                                photos=[])
    except Exception as e:
        return render_template('viewclassphotos.html', 
                             error=f"Error: {str(e)}",
                             photos=[])

comments = [
        "cutie!", "stunner!", "looking gorgeous!", "amazing!", 
        "absolutely glowing!", "love this look!", "fantastic!", 
        "queen behavior!", "iconic!", "serving looks!", "perfect!", 
        "goals!!!", "oh not your best eh", "obsessed!", "slaying!", 
        "beautiful!"
    ]


@app.route('/postphoto')
def postphoto():
   # photo_captions = get_random_captions()
    #numbered_captions = [f"{caption} (Photo {i + 1} of 4)" for i, caption in enumerate(photo_captions)]
    captions=random.sample(comments,4)
    return render_template('postphoto.html', captions=captions)

# Countdown timer routes
@app.route('/start_countdown', methods=['GET'])
def start_countdown():
    session['countdown'] = 5
    return render_template('photo.html', 
                           countdown_active=True, 
                           seconds=session['countdown'])

@app.route('/update_countdown', methods=['POST'])
def update_countdown():
    if 'countdown' in session:
        if session['countdown'] > 0:
            session['countdown'] -= 1
            return jsonify({'countdown': session['countdown'], 'active': True})
        else:
            session.pop('countdown', None)  # Clear countdown from session
            return jsonify({'countdown': 0, 'active': False})
    return jsonify({'countdown': 0, 'active': False})

# Random caption generation
'''
def get_random_captions(num_captions=4):
    captions = [
        "cutie!", "stunner!", "looking gorgeous!", "amazing!", 
        "absolutely glowing!", "love this look!", "fantastic!", 
        "queen behavior!", "iconic!", "serving looks!", "perfect!", 
        "goals!!!", "oh not your best eh", "obsessed!", "slaying!", 
        "beautiful!"
    ]
    return random.sample(captions, num_captions)
    '''

if __name__ == '__main__':
    app.run(debug=True)
