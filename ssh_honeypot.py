# Libraries
import logging # logs files
import socket
import threading #socket library
import paramiko 
from logging.handlers import RotatingFileHandler #rotates log files

#Constants
logging_format = logging.Formatter("%(message)s") #format of the log file
SSH_BANNER = "SSH-2.0-OpenSSH_7.4" #custom banner

host_key = paramiko.RSAKey(filename='server.key') #private key file

#----loggers & logging files-----
data_logger = logging.getLogger("data_logger") #captures username, password, IP
data_logger.setLevel(logging.INFO) #provides the info logger
data_handler = RotatingFileHandler("audits.log", maxBytes=2000, backupCount=5) ##file we are going to log to
data_handler.setFormatter(logging_format) #sets the format of the log file
data_logger.addHandler(data_handler) #adds the handler to the logger

creds_logger = logging.getLogger("creds_logger") #captures username, password, IP
creds_logger.setLevel(logging.INFO) #provides the info logger
creds_handler = RotatingFileHandler("cmd_audits.log", maxBytes=2000, backupCount=5) ##file we are going to log to
creds_handler.setFormatter(logging_format) #sets the format of the log file
creds_logger.addHandler(creds_handler) #adds the handler to the logger

#-----Emulated Shell-----

def emulated_shell(channel, client_ip): 
    channel.send(b'corporate-jumpbox2$')
    command = b""
    #loop thorugh the terminal session
    while True:
        char = channel.recv(1) #listening to user input
        channel.send(char) #sends the user input into char
        if not char:
            channel.close()

        command += char

        #evaluating logic
        if char == b'\r':
            if command.strip() == b"exit": #.strip gives the raw input
                response = b'Goodbye!\r\n'
                channel.close()
            elif command.strip() == b'pwd':
                response = b'\\usr\\local' + b'\r\n'
                creds_logger.info(f'Command {command.strip()} executed by {client_ip}') #logging the command executed
            elif command.strip() == b'whoami':
                response = b'usr\r\n'
                creds_logger.info(f'Command {command.strip()} executed by {client_ip}')
            elif command.strip() == b'ls':
                response = b'jumpbox1.conf\r\n'
                creds_logger.info(f'Command {command.strip()} executed by {client_ip}')
            elif command.strip() == b'cat jumpbox1.conf':
                response = b'\n' + b"Go to ishy.com" + b"\r\n"
                creds_logger.info(f'Command {command.strip()} executed by {client_ip}')
            else:
                response = b"\n" + bytes(command.strip()) + b"\r\n"

        
        channel.send(response)
        channel.send(b'corporate-jumpbox2$')
        command = b""

#-----SSH Server + Sockets-----

# server config -- boiler plate
class Server(paramiko.ServerInterface):

    #constructor
    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind:str, chanid: int) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def get_allowed_auths(self):
        return "password"
    
    def check_auth_password(self, username, password):
        funnel_logger.info(f'Client IP: {self.client_ip} attempted connection with Username: {username} | Password: {password}') #logging the username and password
        creds_logger.info(f'Client IP: {self.client_ip} | Username: {username} | Password: {password}') #logging the username and password
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL # if username is username and password is password then success and logged into shell env
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL # if no username and password is provided then success and logged into shell env

    #checks if I have a request
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    #handles the commands that are being input
    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True

def client_handle(client, addr, username, password):

    client_ip = addr[0]
    print(f"(client_ip) has connected to the server")


    #creating a SSH session
    try:
        transport = paramiko.Transport(client) # initializing the transport object
        transport.local_version = SSH_BANNER #constant custom banner

        #creating instance of a server
        server = Server(client_ip=client_ip, input_username=username, input_password=password)

        transport.add_server_key(HOST_KEY) #adding the host key to the transport object (public/private key pair to verify the auth of server)
        transport.start_server(server=server) #starting the server

        channel = transport.accept(100) #accepting the connection from the client
        if channel is None:
            print(f"[-] No channel for {client_ip}")

        standard_banner = "Welcome to the Ubuntu 22.04 LTS\r\n"
        channel.send(standard_banner) #sending the banner to the client
        emulated_shell(channel, client_ip=client_ip) #calling the emulated shell function
    except Exception as error:
        print(error)
        print(f"[-] Error handling client {client_ip}")
    finally: #closing client session
        try:
            transport.close()
        except Exception as error:
            print(error)
            print(f"[-] Error closing transport for {client_ip}")
        client.close()

#-----Provision SSH-based honeypot----

def honeypot(address, port, username=None, password=None):
    #creating a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4 addresses, listening using TCP socket port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #reusing the address
    sock.bind((address, port)) #binding the socket to the address and port
    sock.listen(100) #listening for connections

    print(f"[*] Listening for connections on {address}:{port}")

    while True:
        try:
            client, addr = sock.accept() #accepting the connection from the client
            print(f"[*] Connection from {addr[0]}:{addr[1]}")

            #creating a new thread for each client
            client_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            client_thread.start()
        except Exception as error:
            print(error)
            print(f"[-] Error accepting connection from {addr[0]}:{addr[1]}")

honeypot('127.0.0.1', 2223, username=None, password=None) #starting the honeypot on localhost and port 2223 with username and password





