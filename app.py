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
            return render_template('index.html', error="Vui lòng nhập link!")
        
        downloaded_files = []
        
        # Cấu hình yt-dlp đa năng
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s_%(title)s.%(ext)s',
            'quiet': True,
        }

        # Nếu chọn audio
        if download_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            })

        for tiktok_url in urls:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(tiktok_url, download=True)
                    
                    # Thu thập file kết quả
                    if download_type == 'audio':
                        base_name = f"{info['id']}.mp3"
                        downloaded_files.append(base_name)
                    else:
                        # Tự động lấy file (video hoặc ảnh slide)
                        files = glob.glob(f"{DOWNLOAD_FOLDER}/{info['id']}*")
                        for f in files:
                            downloaded_files.append(os.path.basename(f))
                            
            except Exception as e:
                print(f"Lỗi tải {tiktok_url}: {str(e)}")
        
        return render_template('index.html', success="Đã xong! Nhấn nút để tải:", files=list(set(downloaded_files)))
            
    return render_template('index.html')

@app.route('/download')
def download_file():
    filename = request.args.get('file')
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    return send_file(file_path, as_attachment=True) if os.path.exists(file_path) else "Lỗi file!", 404

if __name__ == '__main__':
    app.run(debug=True)