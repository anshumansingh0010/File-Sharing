import socket
import random
import string
import time
import os


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


class Authenticate:
    
    def __init__(self, exp_time=120, token_exp=600):
        self.exp_time = exp_time
        self.otp = self.generate_otp()
        self.created_at = time.time()
        self.token_exp = token_exp
        
    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))  
    
    def generate_token(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=20))  
     
    def isValid(self, client_otp):
        if time.time() - self.created_at > self.exp_time:
            return False, "OTP expired"
        if client_otp != self.otp:
            return False, "Invalid OTP"
        self.token: str = self.generate_token()
        return True, "Access granted"
    
    
class Sender:
    def __init__(self, ip, port=2121, *filenames):
        self.receiver_ip = ip
        self.receiver_port = port
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.files = self._expand_paths(filenames)
        
    def _expand_paths(self, paths):
        expanded = []
        for path in paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                expanded.append((path, os.path.basename(path)))
            elif os.path.isdir(path):
                base_dir = os.path.dirname(os.path.abspath(path))
                for root, _, files in os.walk(path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, start=base_dir)
                        expanded.append((full_path, rel_path))
        return expanded

    def start(self, label):
        buf = bytearray()
        try:
            self.sender.connect((self.receiver_ip, self.receiver_port))
            send_line(self.sender, "Want to receive file")
            msg = recv_line(self.sender, buf)
            if not msg.startswith("Yes"):
                err = "Handshake failed: Invalid response"
                label(err)
                return False, err
            
            auth = Authenticate()
            receiver_name = msg[3:]
            label(f"OTP for {receiver_name} is {auth.otp}")
            send_line(self.sender, "Enter OTP")
            self.receiver_otp = recv_line(self.sender, buf).strip()
            
            success, message = auth.isValid(self.receiver_otp)
            send_line(self.sender, message)
            
            if success:
                self.send_all(buf, label)
                success_msg = f"Successfully sent {len(self.files)} item(s) to {receiver_name}."
                label(success_msg)
                return True, success_msg
            else:
                fail_msg = f"Transfer Failed: {message}"
                label(fail_msg)
                return False, fail_msg
        except Exception as e:
            print(f"Sender Error: {e}")
            err_msg = f"Error: {e}"
            label(err_msg)
            return False, err_msg
        finally:
            self.sender.close()
            print("Connection closed.")
    
    def send_all(self, buf: bytearray, label=None):
        total = len(self.files)
        send_line(self.sender, f"COUNT:{total}")
        for idx, (full_path, rel_name) in enumerate(self.files, 1):
            if label:
                label(f"Sending {rel_name} ({idx}/{total})...")
            self.send_file(full_path, rel_name, buf)
        
    def send_file(self, full_path, rel_name, buf):
        filesize = os.path.getsize(full_path)
        send_line(self.sender, f"{rel_name}|{filesize}")
        
        ack = recv_line(self.sender, buf)
        if ack != "ACK":
            raise ConnectionError(f"Expected ACK from receiver, got: {ack}")
        
        with open(full_path, "rb") as f:
            while True:
                data = f.read(4096)
                if not data:
                    break
                self.sender.sendall(data)
        print(f"Sent {rel_name}")


        