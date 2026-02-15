import socket
import random
import string
import time

otp_exp = 120
token_exp = 600

otp_store = {}
token_store = {}

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

def run_server():
    host = '127.0.0.1'
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
                        conn.sendall(b"ACCESS_GRANTED")
                        print(f"Access granted to {addr}")
                    else:
                        conn.sendall(b"Otp expired")
                        print(f"OTP expired for {addr}")
                else:
                    conn.sendall(b"Invalid Otp")
                    print(f"Invalid OTP attempt from {addr}")
                    
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        server.close()

if __name__ == "__main__":
    run_server()
