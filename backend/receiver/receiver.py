import socket
import random
import string
import time
import os
import res


class FileStore:
    def __init__(self):
        self.downloads_path = os.path.join(os.path.expanduser("~"), "Downloads/Received")
        os.makedirs(self.downloads_path,exist_ok=True)

    def receive_file(self,conn,filename:str):
        save_path = os.path.join(self.downloads_path, f"received_{filename}")
        with open(save_path, "wb") as f:
            while True:
                data=conn.recv(4096)
                if not data:
                    break
                f.write(data)
        return True


class SessionManager:
    def __int__(self):
        self.file_store=FileStore()
     
    def start_session(self,conn:socket.socket,addr):
        if conn.recv(1024).decode()== "Want to receive file":
            conn.sendall(b"Yes")
        
        print(conn.recv(1024).decode())
        otp=input()
        conn.sendall(otp.encode())
        
        auth_res=conn.recv(1024).decode()
        print(f"Auth Status : {auth_res}")
        
        if auth_res=="Access granted":
            
        
           
class Receiver:
    def __init__(self,port=2121):
        self.host=socket.gethostname()
        self.port=port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manager = SessionManager()
        
    def start(self):
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"Listening on {self.host}:{self.port}")
        while True:
            conn, addr = self.server.accept()
            try:
                self.manager.start_session(conn, addr)
            finally:
                conn.close()
                self.server.close()
    











otp_exp = 120
token_exp = 600

otp_store = {}
token_store = {}

def generate_otp():
        return ''.join(random.choices(string.digits, k=6)) 

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

def run_server():
    host = socket.gethostname()
    port = 2121
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server.bind((host, port))
    server.listen()
    
    print(f"Server is listening on {host}:{port}...")
    
    try:
        while True:
            conn, addr = server.accept()
            with conn:
                print(f"Connected by {addr}")
                otp = generate_otp()
                otp_store[otp] = time.time()
                
                print(f"Otp for {addr} is {otp}")
                
                conn.sendall(b"required otp for verification")
                
                data = conn.recv(1024)
                if not data:
                    continue
                    
                client_otp = data.decode().strip()
            
                if client_otp == otp:
                    if time.time() - otp_store[otp] <= otp_exp:
                        token = generate_token()
                        token_store[token] = time.time()
                        conn.sendall(b"access granted")
                        print(f"Access granted to {addr}")
                    else:
                        conn.sendall(b"Otp expired")
                        print(f"OTP expired for {addr}")
                else:
                    conn.sendall(b"Invalid Otp")
                    print(f"Invalid OTP attempt from {addr}")
                    
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                filename=conn.recv(1024).decode().strip()
                if not os.path.exists(downloads_path):
                    os.makedirs(downloads_path,exist_ok=True)
                save_path = os.path.join(downloads_path, f"received_{filename}")
                print(f"receiving {filename}")
                with open(save_path, "wb") as f:
                    while True:
                        data=conn.recv(4096)
                        if not data:
                            break
                        f.write(data)
                print("received successfully")
                
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        server.close()

if __name__ == "__main__":
    res.find_receiver()
    run_server()
