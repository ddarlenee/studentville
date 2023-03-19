from flask import Flask, redirect, render_template, request, url_for, session 
import hashlib
import pandas as pd

# Download the file from Google Drive and save it locally
file_id = '1FpZ9OKNtS63JXgn4Akr9eDLnrqvwPehr'
url = f'https://drive.google.com/uc?id={file_id}&export=download'
filename = 'students.xlsx'
df = pd.read_excel(url, engine='openpyxl')
df.to_excel(filename, index=False)

# Read the password data from the file
students = df.set_index('User ID')['Password'].to_dict()

app = Flask(__name__)
app.secret_key = 'mysecretkey'

salt = 'mysalt'
hashed_passwords = {u: hashlib.sha256((p + salt).encode('utf-8')).hexdigest() for u, p in students.items()}

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'userid' in session:
        return redirect(url_for('homepage'))

    error = None
    if request.method == 'POST':
        # Check if the user id and password are valid
        userid = request.form['userid']
        password = request.form['password']
        if userid in students and hashed_passwords[userid] == hashlib.sha256((password + salt).encode('utf-8')).hexdigest():
            session['userid'] = userid
            return redirect(url_for('homepage'))
        else:
            if userid in students:
                error = "Incorrect password"
            else:
                error = "Invalid User ID and Password"
    return render_template('login.html', error=error)

@app.route('/homepage')
def homepage():
    if 'userid' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', userid=session['userid'])

@app.route('/success')
def success():
    return render_template('success.html')
  
@app.route('/perks')
def perks():
    if 'userid' not in session:
        return redirect(url_for('login'))
    return render_template('perks.html')
  
@app.route('/suggestions', methods=['GET', 'POST'])
def suggestions():
    if request.method == 'POST':
        suggestion = request.form['box']
        with open('suggestions.txt', 'a') as f:
            f.write(suggestion + '\n')
        return 'Thanks for your suggestion!'
    else:
        return render_template('suggestions.html')

@app.route('/proj')
def proj():
    if 'userid' not in session:
        return redirect(url_for('login'))
    return render_template('proj.html')

@app.route('/logout')
def logout():
    session.pop('userid', None)
    return redirect(url_for('login'))
  
app.run(host='0.0.0.0', port=81)
