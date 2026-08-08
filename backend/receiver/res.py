import socket

def find_sender(stop_event=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        try:
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception:
            pass
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.settimeout(1.0)
    
    try:
        client.bind(("", 37020))
    except Exception as e:
        print(f"UDP discovery bind error: {e}")
        client.close()
        return

    response = socket.gethostname().encode()
    try:
        while stop_event is None or not stop_event.is_set():
            try:
                data, addr = client.recvfrom(1024)
                if data is not None:
                    client.sendto(response, addr)
            except socket.timeout:
                continue

            except Exception as e:
                if stop_event and stop_event.is_set():
                    break
                print(f"UDP discovery receive error: {e}")
    finally:
        client.close()
        print("UDP Discovery Responder stopped.")

if __name__ == "__main__":
    find_sender()