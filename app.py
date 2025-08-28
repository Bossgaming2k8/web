import os
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'default_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Lớp User và dữ liệu cố định
class User(UserMixin):
    def __init__(self, id):
        self.id = id

user_data = {'admin': {'password': 'password'}}

@login_manager.user_loader
def load_user(user_id):
    if user_id in user_data:
        return User(user_id)
    return None

# Biến toàn cục để lưu trữ yêu cầu thay cho database
requests_store = {}
request_id_counter = 0

# Route cho trang đăng nhập (giữ nguyên)
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

# Route cho bảng điều khiển (đã chỉnh sửa)
@app.route('/dashboard')
@login_required
def dashboard():
    # Sắp xếp các yêu cầu theo thời gian mới nhất
    sorted_requests = sorted(requests_store.values(), key=lambda r: r['created_at'], reverse=True)
    return render_template('dashboard.html', requests=sorted_requests)

# API nhận yêu cầu từ client
@app.route('/api/request_hello', methods=['POST'])
def handle_request():
    global request_id_counter
    request_id_counter += 1
    new_request = {
        'id': request_id_counter,
        'status': 'pending',
        'created_at': datetime.now()
    }
    requests_store[request_id_counter] = new_request
    return jsonify({'request_id': request_id_counter})

# API kiểm tra trạng thái
@app.route('/api/check_status/<int:request_id>', methods=['GET'])
def check_status(request_id):
    req = requests_store.get(request_id)
    if req:
        return jsonify({'status': req['status']})
    return jsonify({'status': 'not_found'})

# API để duyệt yêu cầu
@app.route('/api/approve/<int:request_id>', methods=['POST'])
@login_required
def approve_request(request_id):
    req = requests_store.get(request_id)
    if req:
        req['status'] = 'approved'
        return jsonify({'message': 'Yêu cầu đã được duyệt.'})
    return jsonify({'message': 'Yêu cầu không tìm thấy.'}), 404

# Route để đăng xuất (giữ nguyên)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
