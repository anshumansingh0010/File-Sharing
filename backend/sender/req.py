import time
import psutil
import socket


def get_broadcast_address():
    try:
        interfaces = psutil.net_if_addrs()
        for interface_name, snic_addresses in interfaces.items():
            for addr in snic_addresses:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    if addr.broadcast:
                        return addr.broadcast
    except Exception:
        pass
    return '<broadcast>'


def get_local_ips():
    ips = {"127.0.0.1", "::1", "0.0.0.0"}
    try:
        interfaces = psutil.net_if_addrs()
        for interface_name, snic_addresses in interfaces.items():
            for addr in snic_addresses:
                if addr.family == socket.AF_INET and addr.address:
                    ips.add(addr.address)
    except Exception:
        pass
    return ips


def get_ip(stop_signal, receiver_list):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        try:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception:
            pass
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.settimeout(1.0)
    message = socket.gethostname().encode()
    broadcast_addr = get_broadcast_address()
    local_ips = get_local_ips()
    local_hostname = socket.gethostname().lower()
    
    try:
        while not stop_signal.is_set():
            targets = {broadcast_addr, '<broadcast>'}
            for target in targets:
                try:
                    server.sendto(message, (target, 37020))
                except Exception:
                    pass
            
            try:
                data, addr = server.recvfrom(1024)
                if data:
                    target_ip = addr[0]
                    host_name = data.decode().strip()
                    # Do not discover self as a receiver
                    if target_ip in local_ips or host_name.lower() == local_hostname:
                        continue
                    receiver_list.put({host_name, target_ip})
            except socket.timeout:
                pass
            except Exception as e:
                if stop_signal.is_set():
                    break
                print(f"An error occurred in discovery: {e}")
            
            time.sleep(1.5)  

    finally:
        server.close()
        print("Discovery sender stopped.")




