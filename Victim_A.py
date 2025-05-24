import socket
import time
import threading

class PersistentClient:
    def __init__(self, server_host='192.168.100.2', server_port=8080):
        self.server_host = server_host
        self.server_port = server_port
        self.client_id = "CLIENT_A"
        self.socket = None
        self.connected = False
        
    def establish_connection(self):
        """Thiết lập kết nối TCP liên tục"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.connected = True
            print(f"[{self.client_id}] ✅ Đã thiết lập kết nối TCP liên tục với server")
            return True
        except Exception as e:
            print(f"[{self.client_id}] ❌ Lỗi kết nối: {e}")
            return False
    
    def send_continuous_data(self):
        """Gửi dữ liệu liên tục trên cùng một kết nối TCP"""
        if not self.connected:
            print(f"[{self.client_id}] Chưa có kết nối!")
            return
            
        message_count = 1
        try:
            while self.connected:
                message = f"[{self.client_id}] Persistent message #{message_count} - {time.ctime()}"
                
                # Gửi dữ liệu trên kết nối hiện tại
                self.socket.send(message.encode())
                print(f"[{self.client_id}] Gửi: Message #{message_count}")
                
                # Nhận phản hồi
                try:
                    self.socket.settimeout(5.0)
                    response = self.socket.recv(1024).decode()
                    print(f"[{self.client_id}] Nhận: {response}")
                except socket.timeout:
                    print(f"[{self.client_id}] ⚠️ Timeout - server không phản hồi")
                
                message_count += 1
                time.sleep(3)  # Gửi mỗi 3 giây
                
        except Exception as e:
            print(f"[{self.client_id}] ❌ Lỗi gửi dữ liệu: {e}")
            self.connected = False
        finally:
            self.close_connection()
    
    def close_connection(self):
        """Đóng kết nối"""
        if self.socket:
            self.socket.close()
            self.connected = False
            print(f"[{self.client_id}] Đã đóng kết nối")

def main():
    client = PersistentClient()
    
    print("=== MÁY A - CLIENT VỚI KẾT NỐI LIÊN TỤC ===")
    
    if client.establish_connection():
        try:
            client.send_continuous_data()
        except KeyboardInterrupt:
            print(f"\n[{client.client_id}] Dừng gửi dữ liệu...")
            client.close_connection()

if __name__ == "__main__":
    main()