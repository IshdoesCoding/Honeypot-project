# Libraries
import logging # logs files
from logging.handlers import RotatingFileHandler #rotates log files
from flask import Flask, request, render_template

# Logging format
logging_format = logging.Formatter("%(asctime)s - %(message)s") #format of the log file

# HTTP logger
http_logger = logging.getLogger("http_logger") #captures username, password, IP
http_logger.setLevel(logging.INFO) #provides the info logger
http_handler = RotatingFileHandler("http_audits.log", maxBytes=2000, backupCount=5) ##file we are going to log to
http_handler.setFormatter(logging_format) #sets the format of the log file
http_logger.addHandler(http_handler) #adds the handler to the logger

# Baseline honeypot

def web_honeypot(input_username="admin", input_password="password"):

    app = Flask(__name__)

    @app.route('/')

    def index():
        return render_template('wp-admin.html')

    @app.route('/wp-admin-login', methods=['POST'])

    def login():
        username = request.form['username']
        password = request.form['password']

        ip_address = request.remote_addr

        #logs the login attempt in the http_audits.log file
        http_logger.info(f'Login attempt with username: {username}, password: {password}, IP: {ip_address}') #logging the login attempt

        if username == input_username and password == input_password:
            return "Welcome to the admin panel!"
        else:
            return "Invalid credentials. Please try again."

    return app

def run_web_honeypot(port=8080, input_username="admin", input_password="password"):
    run_wb_honeypot_app = web_honeypot(input_username, input_password)
    run_wb_honeypot_app.run(debug=True, port=port, host='0.0.0.0')

    return run_wb_honeypot_app


