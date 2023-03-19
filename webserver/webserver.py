from flask import Flask, request, render_template
import sqlite3
from itsdangerous import URLSafeTimedSerializer, BadData
import gameserver.database as user_database


app = Flask(__name__)
#TODO: SECURITY LMFAO
app.secret_key = "starfleet"

@app.route('/confirm_email')
def confirm_email():
    token = request.args.get('token', '')
    s = URLSafeTimedSerializer(secret_key=app.secret_key)
    try:
        data = s.loads(token)
        email = data['email']
    except BadData:
        return render_template('error.html', message='Invalid token')

    try:
        user = user_database.get_user_by_email(email)
        if user is not None:
            user_id, username, password_hash, email, is_confirmed = user
            if not is_confirmed:
                conn = user_database.create_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET is_confirmed = 1 WHERE id = ?", (user_id,))
                conn.commit()

                if cursor.rowcount == 1:
                    return render_template('success.html')
                else:
                    return render_template('error.html', message='Authorization failed')
            else:
                return render_template('error.html', message='Account already authorized')
        else:
            return render_template('error.html', message='User not found')

    except sqlite3.Error as e:
        return render_template('error.html', message=f"Database error: {e}")

if __name__ == '__main__':
    app.run(host='localhost', port=5000, ssl_context=('cert.pem', 'key.pem'))
