import time
import psutil
import socket


def get_broadcast_address():
    
    interfaces = psutil.net_if_addrs()
    for interface_name, snic_addresses in interfaces.items():
        for addr in snic_addresses:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                if addr.broadcast:
                    return addr.broadcast
                
    return '<broadcast>'


def get_ip():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(0.2)
    target_ip=None
    message = (f"your very important message from {socket.gethostname()}").encode()
    while True:
        server.sendto(message, (get_broadcast_address(), 37020))
        
        time.sleep(1)
        try:
            data,addr=server.recvfrom(1024)
            if data:
                target_ip=addr[0]
                break
        except:
            print("message sent!")
            continue
    print(target_ip)
    return target_ip

if __name__=="__main__":
    get_ip()
