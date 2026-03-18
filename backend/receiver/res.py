import socket

def find_sender():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", 37020))
    response = socket.gethostname().encode()
    while True:
        data, addr = client.recvfrom(1024)
        print("received message: %s"%data)
        if data is not None:
            client.sendto(response, addr)
            break
        
if __name__=="__main__":
    find_sender()