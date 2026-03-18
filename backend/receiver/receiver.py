import socket
import os
from backend.receiver import res

class FileStore:
    
    def __init__(self):
        self.downloads_path = os.path.join(os.path.expanduser("~"), "Downloads/Received")
        os.makedirs(self.downloads_path,exist_ok=True)

    def receive_file(self,conn,filename:str,filesize):
        save_path = os.path.join(self.downloads_path, f"received_{filename}")
        with open(save_path,"wb") as f:
            remaining = filesize
            while remaining > 0:
                data=conn.recv(min(remaining,4096))
                if not data:
                    break
                f.write(data)
                remaining-=len(data)
        print(f"Successfully received: {filename}")


class SessionManager:
    
    def __init__(self):
        self.file_store=FileStore()
     
    def start_session(self,conn:socket.socket,addr,getOtp):
        print(f"Connected by {addr}")
        if conn.recv(1024).decode()== "Want to receive file":
            conn.sendall(f"Yes{socket.gethostname()}".encode())
        
        print(conn.recv(1024).decode())
        otp=getOtp()
        conn.sendall(otp.encode())
        
        auth_res=conn.recv(1024).decode()
        print(f"Auth Status : {auth_res}")
        
        if auth_res=="Access granted":
            count_data=conn.recv(1024).decode()
            num_files=int(count_data.split(":")[1])
            for _ in range(num_files):
                header=conn.recv(1024).decode()
                filename,filesize=header.split("|")
                filesize=int(filesize)
                
                conn.sendall(b"ACK")
                self.file_store.receive_file(conn,filename,filesize)
                
          
class Receiver:
    def __init__(self,port=2121):
        self.host=socket.gethostname()
        self.port=port
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manager = SessionManager()
        res.find_sender()
        
    def start(self,getOtp):
        self.receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.receiver.bind((self.host, self.port))
        self.receiver.listen(5)
        print(f"Listening on {self.host}:{self.port}")
        try:
            # while True: 
                conn, addr = self.receiver.accept()
                try:
                    self.manager.start_session(conn, addr,getOtp)
                except Exception as e:
                    print(f"Session Error: {e}")
                finally:
                    print("Connection closed.")
                    conn.close() 
        finally:
            self.receiver.close()
            print("Receiver Stopped")
