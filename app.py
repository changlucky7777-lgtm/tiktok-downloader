from flask import Flask, render_template, request, send_file
import yt_dlp
import os

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
            return render_template('index.html', error="Vui lòng nhập ít nhất một link TikTok!")
        
        downloaded_files = []
        
        for tiktok_url in urls:
            try:
                if download_type == 'audio':
                    ydl_opts = {
                        'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s',
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    }
                else:
                    ydl_opts = {
                        'outtmpl': f'{DOWNLOAD_FOLDER}/%(id)s.%(ext)s',
                    }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(tiktok_url, download=True)
                    if download_type == 'audio':
                        filename = os.path.join(DOWNLOAD_FOLDER, f"{info['id']}.mp3")
                    else:
                        filename = ydl.prepare_filename(info)
                    
                    # Chỉ lấy tên file để hiển thị hoặc tải trực tiếp
                    downloaded_files.append(os.path.basename(filename))
            except Exception as e:
                print(f"Lỗi khi tải link {tiktok_url}: {str(e)}")
        
        if not downloaded_files:
            return render_template('index.html', error="Không thể tải được video/âm thanh từ các link bạn cung cấp.")
        
        # Trả về danh sách các file đã tải xong để hiển thị nút tải riêng lẻ
        return render_template('index.html', success="Xử lý thành công! Chọn file bên dưới để tải về:", files=downloaded_files)
            
    return render_template('index.html')

@app.route('/download')
def download_file():
    filename = request.args.get('file')
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if filename and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "Không tìm thấy file!", 404

if __name__ == '__main__':
    app.run(debug=True)