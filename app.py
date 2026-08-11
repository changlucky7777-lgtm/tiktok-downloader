from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import glob

app = Flask(__name__)

# Sử dụng đường dẫn tuyệt đối cho thư mục downloads để tránh lỗi tìm file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'downloads')

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        raw_urls = request.form.get('url', '')
        download_type = request.form.get('type', 'video')
        
        urls = [url.strip() for url in raw_urls.splitlines() if url.strip()]
        if not urls:
            return render_template('index.html', error="Vui lòng nhập link TikTok!")
        
        downloaded_files = []
        
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
            'quiet': True,
        }

        if download_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            })

        for tiktok_url in urls:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(tiktok_url, download=True)
                    
                    # Tìm tất cả file khớp với ID video vừa tải
                    files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{info['id']}*"))
                    for f in files:
                        base_name = os.path.basename(f)
                        if base_name not in downloaded_files:
                            downloaded_files.append(base_name)
            except Exception as e:
                print(f"Lỗi: {str(e)}")
        
        if not downloaded_files:
            return render_template('index.html', error="Không thể tải video. Vui lòng kiểm tra lại link!")
            
        return render_template('index.html', success="Đã xong! Nhấn nút bên dưới để tải:", files=downloaded_files)
            
    return render_template('index.html')

@app.route('/download')
def download_file():
    filename = request.args.get('file')
    if not filename:
        return "Tên file không hợp lệ!", 400
        
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "Không tìm thấy file trên server!", 404

if __name__ == '__main__':
    app.run()
