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


def get_ip(stop_signal,receiver_list):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(1.0)
    message = socket.gethostname().encode()
    broadcast_addr=get_broadcast_address()
    while not stop_signal.is_set():
        server.sendto(message, (broadcast_addr, 37020))
        print("message sent!")
        
        try:
            data,addr=server.recvfrom(1024)
            if data:
                target_ip=addr[0]
                host_name=data.decode()
                receiver_list.put({host_name,target_ip})
        except socket.timeout:
            continue
        except Exception as e:
            print(f"An error occured : {e}")


