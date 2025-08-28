from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# Cấu hình Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secret_key_that_you_should_change'

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Lớp User để Flask-Login hoạt động
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Cấu hình user cố định
user_data = {'admin': {'av101': 'av101'}}

# Hàm load user cho Flask-Login
@login_manager.user_loader
def load_user(user_id):
    if user_id in user_data:
        return User(user_id)
    return None

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

# Route cho trang dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.id)

# Route để đăng xuất
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
