from flask import Flask, request, render_template, redirect, url_for, jsonify, session
import mysql.connector
import requests
import random
import time
from mysql.connector import Error

from itertools import zip_longest

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session handling

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

# Routes for views
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        payload = {"wamUserId": username, "password": password}
        try:
            response = requests.post(f"{MYSQL_SERVER}/wamUserLogin", json=payload)
            if response.status_code == 200:
                if response.text == "Incorrect Username and/or Password":
                    return render_template('login.html', errors="Incorrect Username and/or Password!")
                else:
                    return redirect('/dashboard')
        except Exception:
            return render_template('login.html', error="Unable to connect to the server.")

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
            response = requests.post(f"{MYSQL_SERVER}/wamUserSignup", json=payload)
            if response.status_code == 200:
                return redirect('/dashboard')
        except Exception:
            return render_template('signup.html', error="Unable to connect to the server.")


@app.route('/photo')
def photo():
    return render_template('photo.html')


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
def post_photo():
   # photo_captions = get_random_captions()
    #numbered_captions = [f"{caption} (Photo {i + 1} of 4)" for i, caption in enumerate(photo_captions)]
    captions=random.sample(comments,4)
    return render_template('postphoto.html', captions=captions)

if __name__ == '__main__':
    app.run(debug=True)
