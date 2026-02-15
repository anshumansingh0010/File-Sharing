import socket
import os
def client():
    host="127.0.0.1"
    port=2121
    client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host,port))
    msg=client.recv(1024).decode()
    if msg=="required otp for verification":
        otp=input("Enter otp :")
        client.sendall(otp.encode())
        auth_status=client.recv(1024).decode()
        if auth_status!="ACCESS_GRANTED":
            return
    # client.sendall(os.path.basename(filename).encode())
    # with open(filename,"rb") as f:
    #     print("sending...")
    #     while True:
    #         data=f.read(4096)
    #         if not data:
    #             break
    #         client.sendall(data)
    print("sent successfully")
    client.close()
    
if __name__ == "__main__":
    # file = input("Enter filename to transfer: ")
    # client(file)
    client()
        