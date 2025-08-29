import os
import time
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'default_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

user_data = {'admin': {'password': 'password'}}

@login_manager.user_loader
def load_user(user_id):
    if user_id in user_data:
        return User(user_id)
    return None

# Biến toàn cục để lưu trữ thông tin client
clients = {}

# Route cho trang đăng nhập
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in user_data and user_data[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Sắp xếp client theo thời gian mới nhất
    # clients.items() trả về một list các tuple (key, value)
    sorted_clients_items = sorted(clients.items(), key=lambda item: item[1]['last_seen'], reverse=True)
    return render_template('dashboard.html', clients=sorted_clients_items)

# API để client gửi yêu cầu
@app.route('/api/request_run', methods=['POST'])
def request_run():
    data = request.json
    client_id = data.get('client_id')
    
    if not client_id:
        return jsonify({'message': 'Client ID bị thiếu.'}), 400
        
    if client_id not in clients:
        # Nếu là client mới, tạo key và IV duy nhất
        key = secrets.token_bytes(32) # Khóa 256-bit
        iv = secrets.token_bytes(16)  # IV 128-bit
        clients[client_id] = {
            'status': 'pending',
            'last_seen': datetime.now(),
            'key': key.hex(),
            'iv': iv.hex()
        }
    else:
        # Nếu là client cũ, cập nhật thời gian
        clients[client_id]['last_seen'] = datetime.now()
        clients[client_id]['status'] = 'pending'
    
    return jsonify({'message': 'Yêu cầu đã được gửi.'})

# API để client lấy key giải mã
@app.route('/api/get_key/<string:client_id>', methods=['GET'])
def get_key(client_id):
    client = clients.get(client_id)
    if not client:
        return jsonify({'message': 'Client không tồn tại.'}), 404
        
    if client['status'] == 'approved':
        return jsonify({
            'key': client['key'],
            'iv': client['iv']
        })
    return jsonify({'message': 'Chưa được phê duyệt.'}), 403

# API để duyệt yêu cầu
@app.route('/api/approve/<string:client_id>', methods=['POST'])
@login_required
def approve_request(client_id):
    client = clients.get(client_id)
    if not client:
        return jsonify({'message': 'Client không tồn tại.'}), 404
        
    client['status'] = 'approved'
    return jsonify({'message': 'Yêu cầu đã được duyệt.'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
