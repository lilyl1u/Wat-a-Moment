from flask import Flask, request, render_template, redirect, url_for, jsonify

app = Flask(__name__)

@app.route('/form', methods=['POST'])
def form():
    fname=request.form.get('fname')
    lname=request.form.get('lname')
    password=request.form.get('password')
    
    if len(password)<6:
        message="Your password is too short! Make sure it is 6 characters or more"
        return render_template('form.html', message=message)
  
    if not any(character.isupper() for character in password):
        message="Your password does not have a capital letter! Make sure it contains a capital letter."
        return render_template('form.html', message=message)
  
    if not any(character.islower() for character in password):
        message="Your password does not have a lower-case letter! Make sure it contains a lower-caseletter."
        return render_template('form.html', message=message)
    else:
      return redirect(url_for('submit', fname=fname, lname=lname))
        
if __name__ == '__main__':
  app.run(debug=True)
#flask / python for form
