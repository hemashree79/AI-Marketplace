from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = "codefury_secret_key_123" # remember to change this later lol

# TODO: hook up the database here later

@app.route('/')
def home():
    # homepage goes here
    return "Homepage working! Grid coming soon..."

@app.route('/login')
def login():
    # unified login page for everyone
    return "Login page - HTML needed"

@app.route('/dev')
def dev_dashboard():
    # where devs upload models
    return "Dev dashboard"

@app.route('/admin')
def admin_dashboard():
    # where admin approves stuff
    return "Admin dashboard"

@app.route('/buy/<int:model_id>')
def buy_model(model_id):
    # todo: figure out how the cart works
    return f"Buying model number {model_id}"

if __name__ == '__main__':
    # run the server
    app.run(debug=True)