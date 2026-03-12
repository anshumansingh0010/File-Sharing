import socket
import random
import string
import time
import os
from backend.sender import req

class Authenticate:
    
    def __init__(self,exp_time=120,token_exp=600):
        self.exp_time=exp_time
        self.otp=self.generate_otp()
        self.created_at=time.time()
        self.token_exp=token_exp
        
    
    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))  
    
    def generate_token(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=20))  
     
    def isValid(self, client_otp):
        if time.time()-self.created_at > self.exp_time :
            return False, "OTP expired"
        if client_otp!=self.otp:
            return False, "Invalid OTP"
        self.token:str=self.generate_token()
        return True, "Access granted"
    
    
class Sender:
    def __init__(self,port=2121,*filenames):
        self.receiver_ip=req.get_ip()
        self.receiver_port=port
        self.sender=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.files=[]
        for name in filenames:
            self.files.append(name)
        
    def start(self):
        try:
            self.sender.connect((self.receiver_ip, self.receiver_port))
            self.sender.sendall(b"Want to receive file")
            msg = self.sender.recv(1024).decode()
            if msg != "Yes":
                return False
            
            auth = Authenticate()
            print(f"DEBUG: OTP for {self.receiver_ip} is {auth.otp}")
            self.sender.sendall(b"Enter OTP")
            self.receiver_otp = self.sender.recv(1024).decode().strip()
            
            success, message = auth.isValid(self.receiver_otp)
            self.sender.sendall(message.encode())
            time.sleep(0.1)
            
            if success:
                self.send_all()
        finally:
            self.sender.close()
            print("Connection closed.")
    
    def send_all(self):
        self.sender.sendall(f"COUNT:{len(self.files)}".encode())
        time.sleep(0.1)
        for name in self.files:
            time.sleep(0.1)
            self.send_file(name)
        
    def send_file(self,filename):
        filesize = os.path.getsize(filename)
        header = f"{os.path.basename(filename)}|{filesize}"
        self.sender.sendall(header.encode())
        
        # to receive acknowledgemnet
        self.sender.recv(1024)
        
        with open(filename, "rb") as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                self.sender.sendall(data)
        print(f"Sent {filename}")
        