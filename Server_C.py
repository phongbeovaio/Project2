import socket
import threading
import time

class PersistentServer:
    def __init__(self, host='192.168.100.2', port=8080):
        self.host = host
        self.port = port
        self.base_sequence = 1000
        self.sequence_increment = 100
        self.active_sessions = {}
        self.socket = None

    def start_server(self):
        """Khởi động server hỗ trợ kết nối liên tục"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(10)

        print(f"[SERVER] 🚀 Server chạy trên {self.host}:{self.port}")
        print(f"[SERVER] 📊 Sequence base: {self.base_sequence}, increment: {self.sequence_increment}")
        print("-" * 60)

        while True:
            try:
                print(f"[SERVER] ⏳ Đang chờ kết nối từ client...")
                client_socket, addr = self.socket.accept()
                print(f"[SERVER] 🔗 Kết nối mới từ {addr}")

                session_id = f"{addr[0]}:{addr[1]}"
                current_seq = self.base_sequence + len(self.active_sessions) * self.sequence_increment

                self.active_sessions[session_id] = {
                    'socket': client_socket,
                    'addr': addr,
                    'sequence': current_seq,
                    'start_time': time.time(),
                    'message_count': 0
                }

                print(f"[SERVER] 📋 Session ID: {session_id}")
                print(f"[SERVER] 🔢 Initial sequence: {current_seq}")
                print(f"[SERVER] 📋 Active sessions: {len(self.active_sessions)}")

                client_thread = threading.Thread(
                    target=self.handle_persistent_client,
                    args=(session_id,)
                )
                client_thread.daemon = True
                client_thread.start()

            except KeyboardInterrupt:
                print("\n[SERVER] 🛑 Tắt server...")
                break
            except Exception as e:
                print(f"[SERVER] ❌ Lỗi khi chấp nhận kết nối: {e}")

        self.socket.close()
        print(f"[SERVER] 🔚 Server đã đóng")

    def handle_persistent_client(self, session_id):
        """Xử lý client với kết nối liên tục"""
        session = self.active_sessions[session_id]
        client_socket = session['socket']
        addr = session['addr']

        print(f"[SERVER] 🔄 Bắt đầu xử lý client {session_id}")
        try:
            while True:
                print(f"[SERVER] ⏳ Đang chờ dữ liệu từ {session_id}...")
                data = client_socket.recv(1024)
                print(f"[SERVER] 📥 Nhận dữ liệu thô (raw): {len(data)} bytes")

                if not data:
                    print(f"[SERVER] ⚠️ Không còn dữ liệu, đóng kết nối từ {session_id}")
                    break

                print(f"[SERVER] 📊 Dữ liệu thô (hex): {data.hex()}")
                try:
                    message = data.decode('utf-8', errors='replace')
                    print(f"[SERVER] 📝 Nội dung giải mã: {message[:50]}... (tổng {len(message)} ký tự)")
                except UnicodeDecodeError as e:
                    print(f"[SERVER] ❌ Lỗi giải mã dữ liệu: {e}. Dữ liệu thô: {data.hex()}")

                session['message_count'] += 1
                session['sequence'] += len(data)
                print(f"[SERVER] 🔢 Sequence hiện tại: {session['sequence']}")
                print(f"[SERVER] 📩 Tin nhắn #{session['message_count']} từ {addr}")

                if any(keyword in message for keyword in ['SPOOFED', 'ATTACK', 'HIJACKED']):
                    print(f"[SERVER] 🚨 CẢNH BÁO: Phát hiện tin nhắn đáng ngờ từ {addr}!")
                    print(f"[SERVER] 🚨 Nội dung: {message}")

                response = f"ACK #{session['message_count']}: Seq={session['sequence']}, Next={session['sequence'] + self.sequence_increment}"
                print(f"[SERVER] 📤 Gửi phản hồi: {response}")
                try:
                    client_socket.send(response.encode())
                    print(f"[SERVER] ✅ Phản hồi gửi thành công")
                except BrokenPipeError:
                    print(f"[SERVER] ❌ Lỗi gửi phản hồi: Client {session_id} đã ngắt kết nối")
                    break
                except Exception as e:
                    print(f"[SERVER] ❌ Lỗi gửi phản hồi: {e}")

                print(f"[SERVER] ⏳ Đợi 1 giây trước khi nhận tiếp...")
                time.sleep(1)

        except Exception as e:
            print(f"[SERVER] ❌ Lỗi xử lý {session_id}: {e}")
        finally:
            print(f"[SERVER] 🔌 Đóng socket cho {session_id}")
            client_socket.close()
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            print(f"[SERVER] 🗑️ Đã xóa session {session_id}")
            print(f"[SERVER] 📋 Active sessions: {len(self.active_sessions)}")

    def show_active_sessions(self):
        """Hiển thị các session đang hoạt động"""
        print(f"\n[SERVER] 📊 ACTIVE SESSIONS ({len(self.active_sessions)}):")
        for sid, session in self.active_sessions.items():
            duration = time.time() - session['start_time']
            print(f"  {sid}: Seq={session['sequence']}, Messages={session['message_count']}, Duration={duration:.1f}s")

def main():
    server = PersistentServer()

    server_thread = threading.Thread(target=server.start_server)
    server_thread.daemon = True
    server_thread.start()

    print("Server đã khởi động. Nhấn Enter để xem sessions, Ctrl+C để thoát.")

    try:
        while True:
            input()
            server.show_active_sessions()
    except KeyboardInterrupt:
        print("\n[SERVER] Tắt server...")

if __name__ == "__main__":
    main()