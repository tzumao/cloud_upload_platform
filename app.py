from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# 確保上傳資料夾存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# 設定時區（預設台灣時間）
LOCAL_TZ = os.getenv('LOCAL_TZ', 'Asia/Taipei')
TZ = ZoneInfo(LOCAL_TZ)

# 列出所有檔案
def list_files():
    files = []
    folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if not os.path.isfile(path):
            continue
        size_kb = os.path.getsize(path) / 1024
        mtime = os.path.getmtime(path)
        dt_local = datetime.fromtimestamp(mtime, TZ)
        files.append({
            "name": filename,
            "size": f"{size_kb:.2f} KB",
            "time": dt_local.strftime('%Y-%m-%d %H:%M:%S'),
            "ts": mtime,
        })
    files.sort(key=lambda x: x["ts"], reverse=True)
    return files

@app.route('/')
def index():
    return render_template('index.html', files=list_files())

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    if f:
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
