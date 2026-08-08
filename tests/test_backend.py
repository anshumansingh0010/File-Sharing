import unittest
import os
import sys

# Ensure workspace root is in sys.path when script is executed directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import shutil
import tempfile
import time
import threading
import socket
import queue
from backend.sender.sender import Sender, Authenticate
from backend.receiver.receiver import Receiver, FileStore
from backend.sender import req
from backend.receiver import res



class TestBackend(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.download_dir = os.path.join(self.temp_dir, "Received")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_authenticate_otp_valid(self):
        auth = Authenticate(exp_time=2)
        valid, msg = auth.isValid(auth.otp)
        self.assertTrue(valid)
        self.assertEqual(msg, "Access granted")

    def test_authenticate_otp_invalid(self):
        auth = Authenticate()
        valid, msg = auth.isValid("000000")
        self.assertFalse(valid)
        self.assertEqual(msg, "Invalid OTP")

    def test_authenticate_otp_expired(self):
        auth = Authenticate(exp_time=0.1)
        time.sleep(0.2)
        valid, msg = auth.isValid(auth.otp)
        self.assertFalse(valid)
        self.assertEqual(msg, "OTP expired")

    def test_sender_folder_expansion(self):
        # Create folder structure
        folder_path = os.path.join(self.temp_dir, "test_folder")
        sub_dir = os.path.join(folder_path, "sub")
        os.makedirs(sub_dir, exist_ok=True)

        file1 = os.path.join(folder_path, "file1.txt")
        file2 = os.path.join(sub_dir, "file2.txt")
        with open(file1, "w") as f:
            f.write("hello")
        with open(file2, "w") as f:
            f.write("world")

        sender = Sender("127.0.0.1", 2121, folder_path)
        rel_paths = [rel for full, rel in sender.files]
        self.assertIn("test_folder/file1.txt", rel_paths)
        self.assertIn("test_folder/sub/file2.txt", rel_paths)

    def test_file_store_sanitization(self):
        store = FileStore()
        store.downloads_path = self.download_dir
        os.makedirs(self.download_dir, exist_ok=True)

        buf = bytearray()
        sock_a, sock_b = socket.socketpair()
        sock_a.sendall(b"content")

        store.receive_file(sock_b, buf, "../../../etc/passwd_fake", 7)
        sock_a.close()
        sock_b.close()

        saved_file = os.path.join(self.download_dir, "passwd_fake")
        self.assertTrue(os.path.exists(saved_file))
        with open(saved_file, "r") as f:
            self.assertEqual(f.read(), "content")

    def test_end_to_end_file_transfer(self):
        # Create test file
        test_file = os.path.join(self.temp_dir, "sample.txt")
        with open(test_file, "w") as f:
            f.write("End-to-End Test Content 12345")

        receiver = Receiver(port=2125)
        receiver.manager.file_store.downloads_path = self.download_dir

        captured_otp = []

        def get_otp_callback():
            # Wait for sender to generate OTP
            while not captured_otp:
                time.sleep(0.05)
            return captured_otp[0]

        def run_receiver():
            try:
                receiver.start(get_otp_callback)
            except Exception as e:
                pass

        rec_thread = threading.Thread(target=run_receiver, daemon=True)
        rec_thread.start()
        time.sleep(0.2)

        def label_callback(msg):
            if "OTP for" in msg:
                otp = msg.split("is ")[1].strip()
                captured_otp.append(otp)

        sender = Sender("127.0.0.1", 2125, test_file)
        success = sender.start(label_callback)

        rec_thread.join(timeout=3)
        self.assertTrue(success)

        received_file = os.path.join(self.download_dir, "sample.txt")
        self.assertTrue(os.path.exists(received_file))
        with open(received_file, "r") as f:
            self.assertEqual(f.read(), "End-to-End Test Content 12345")

    def test_end_to_end_invalid_otp(self):
        test_file = os.path.join(self.temp_dir, "sample2.txt")
        with open(test_file, "w") as f:
            f.write("Data")

        receiver = Receiver(port=2126)
        receiver.manager.file_store.downloads_path = self.download_dir

        def get_wrong_otp():
            return "999999"

        def run_receiver():
            try:
                receiver.start(get_wrong_otp)
            except Exception:
                pass

        rec_thread = threading.Thread(target=run_receiver, daemon=True)
        rec_thread.start()
        time.sleep(0.2)

        status_logs = []
        def label_callback(msg):
            status_logs.append(msg)

        sender = Sender("127.0.0.1", 2126, test_file)
        success = sender.start(label_callback)

        rec_thread.join(timeout=3)
        self.assertFalse(success)
        self.assertTrue(any("Transfer Failed" in log for log in status_logs))

    def test_udp_discovery_filters_self(self):
        stop_discovery = threading.Event()
        resp_thread = threading.Thread(target=res.find_sender, args=(stop_discovery,), daemon=True)
        resp_thread.start()
        time.sleep(0.2)

        stop_req = threading.Event()
        rx_queue = queue.Queue()
        req_thread = threading.Thread(target=req.get_ip, args=(stop_req, rx_queue), daemon=True)
        req_thread.start()

        found = None
        for _ in range(5):
            if not rx_queue.empty():
                found = rx_queue.get()
                break
            time.sleep(0.1)

        stop_req.set()
        stop_discovery.set()
        req_thread.join(timeout=2)
        resp_thread.join(timeout=2)

        # Self-discovery should be filtered out
        self.assertIsNone(found)



if __name__ == "__main__":
    unittest.main()
