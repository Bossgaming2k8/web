import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import time
from datetime import datetime

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

# Biến toàn cục để lưu trữ khóa
current_key = "defaultkey12345678901234" # Khóa mặc định ban đầu
key_approval_status = "pending"

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
    global key_approval_status, current_key
    # Dữ liệu hiển thị trên dashboard
    dashboard_data = {
        'status': key_approval_status,
        'key': current_key,
        'last_updated': datetime.now()
    }
    return render_template('dashboard.html', data=dashboard_data)

# API để A1 lấy khóa
@app.route('/api/get_key', methods=['GET'])
def get_key():
    global key_approval_status
    # Kiểm tra trạng thái phê duyệt. Nếu được duyệt, gửi khóa về
    if key_approval_status == "approved":
        key_to_send = current_key
        key_approval_status = "pending" # Reset trạng thái sau khi gửi
        return jsonify({'key': key_to_send})
    
    return jsonify({'status': 'waiting_for_approval'})

# API để A1 gửi khóa mới lên
@app.route('/api/send_key', methods=['POST'])
def send_key():
    global current_key, key_approval_status
    new_key = request.form.get('key')
    if new_key:
        current_key = new_key
        key_approval_status = "pending" # Đợi người dùng phê duyệt khóa mới
        return jsonify({'message': 'Khoa moi da duoc gui va dang cho phe duyet.'})
    return jsonify({'message': 'Khong co khoa duoc gui.'}), 400

# API để duyệt khóa
@app.route('/api/approve_key', methods=['POST'])
@login_required
def approve_key():
    global key_approval_status
    key_approval_status = "approved"
    return jsonify({'message': 'Khoa da duoc phe duyet. A1 co the lay duoc.'})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
