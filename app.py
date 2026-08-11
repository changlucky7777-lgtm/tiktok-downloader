from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import glob

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'

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
        
        # Cấu hình chuyên cho TikTok
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s',
            'quiet': True,
        }

        # Nếu tải nhạc nền
        if download_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            })

        for tiktok_url in urls:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(tiktok_url, download=True)
                    
                    # Thu thập file
                    files = glob.glob(f"{DOWNLOAD_FOLDER}/{info['id']}*")
                    for f in files:
                        base_name = os.path.basename(f)
                        if base_name not in downloaded_files:
                            downloaded_files.append(base_name)
            except Exception as e:
                print(f"Lỗi: {str(e)}")
        
        return render_template('index.html', success="Đã xong! Nhấn nút để tải:", files=downloaded_files)
            
    return render_template('index.html')

@app.route('/download')
def download_file():
    filename = request.args.get('file')
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True) if os.path.exists(file_path) else "Lỗi file!", 404

if __name__ == '__main__':
    app.run()