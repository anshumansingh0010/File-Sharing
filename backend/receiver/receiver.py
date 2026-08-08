import socket
import os
import threading
from backend.receiver import res


def send_line(sock: socket.socket, line: str):
    data = (line + "\n").encode("utf-8")
    sock.sendall(data)


def recv_line(sock: socket.socket, buf: bytearray) -> str:
    while b"\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf.extend(chunk)
    
    if b"\n" in buf:
        line_bytes, rest = buf.split(b"\n", 1)
        buf.clear()
        buf.extend(rest)
        return line_bytes.decode("utf-8", errors="replace").strip("\r")
    else:
        line_bytes = bytes(buf)
        buf.clear()
        return line_bytes.decode("utf-8", errors="replace").strip("\r")


class FileStore:
    
    def __init__(self):
        self.downloads_path = os.path.join(os.path.expanduser("~"), "Downloads/Received")
        os.makedirs(self.downloads_path, exist_ok=True)

    def receive_file(self, conn: socket.socket, buf: bytearray, filename: str, filesize: int):
        clean_filename = os.path.normpath(filename).lstrip("/\\")
        if clean_filename.startswith("..") or os.path.isabs(clean_filename):
            clean_filename = os.path.basename(clean_filename)

        save_path = os.path.join(self.downloads_path, clean_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        remaining = filesize
        with open(save_path, "wb") as f:
            if buf:
                to_write = bytes(buf[:remaining])
                f.write(to_write)
                remaining -= len(to_write)
                del buf[:len(to_write)]

            while remaining > 0:
                data = conn.recv(min(remaining, 4096))
                if not data:
                    raise ConnectionError(f"Connection closed prematurely while receiving {filename}")
                f.write(data)
                remaining -= len(data)
        print(f"Successfully received: {filename}")


class SessionManager:
    
    def __init__(self):
        self.file_store = FileStore()
     
    def start_session(self, conn: socket.socket, addr, getOtp):
        print(f"Connected by {addr}")
        buf = bytearray()

        req_msg = recv_line(conn, buf)
        if req_msg != "Want to receive file":
            print(f"Unexpected initial message: {req_msg}")
            return

        send_line(conn, f"Yes{socket.gethostname()}")

        prompt_msg = recv_line(conn, buf)
        print(f"Prompt from sender: {prompt_msg}")

        otp = getOtp()
        if not otp:
            send_line(conn, "CANCEL")
            return

        send_line(conn, str(otp))

        auth_res = recv_line(conn, buf)
        print(f"Auth Status : {auth_res}")

        if auth_res == "Access granted":
            count_data = recv_line(conn, buf)
            if not count_data.startswith("COUNT:"):
                raise ValueError(f"Invalid count message: {count_data}")
            num_files = int(count_data.split(":", 1)[1])
            for _ in range(num_files):
                header = recv_line(conn, buf)
                if "|" not in header:
                    raise ValueError(f"Invalid file header: {header}")
                filename, filesize_str = header.rsplit("|", 1)
                filesize = int(filesize_str)

                send_line(conn, "ACK")
                self.file_store.receive_file(conn, buf, filename, filesize)
        else:
            raise PermissionError(f"Authentication failed: {auth_res}")


class Receiver:
    def __init__(self, port=2121):
        self.host = ""
        self.port = port
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manager = SessionManager()
        self.stop_event = threading.Event()
        self.stop_discovery = threading.Event()
        
    def stop(self):
        self.stop_event.set()
        self.stop_discovery.set()
        try:
            self.receiver.close()
        except Exception:
            pass

    def start(self, getOtp):
        self.stop_event.clear()
        self.stop_discovery.clear()
        discovery_thread = threading.Thread(target=res.find_sender, args=(self.stop_discovery,), daemon=True)
        discovery_thread.start()

        self.receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.receiver.settimeout(1.0)
        try:
            self.receiver.bind((self.host, self.port))
            self.receiver.listen(5)
        except Exception as e:
            self.stop_discovery.set()
            raise e

        print(f"Listening on port {self.port}")
        try:
            while not self.stop_event.is_set():
                try:
                    conn, addr = self.receiver.accept()
                    conn.settimeout(None)
                    try:
                        self.manager.start_session(conn, addr, getOtp)
                    except Exception as e:
                        print(f"Session Error: {e}")
                        if self.stop_event.is_set():
                            break
                        raise e
                    finally:
                        print("Connection closed.")
                        conn.close()
                    break
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.stop_event.is_set():
                        break
                    raise e
        finally:
            self.stop_discovery.set()
            try:
                self.receiver.close()
            except Exception:
                pass
            print("Receiver Stopped")


