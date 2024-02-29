# Hướng dẫn quản lý kho dữ liệu Label Studio

## Mục lục

1. [Cài đặt](#1-setup)
2. [Danh sách công cụ](#2-tools)

<a id="1-setup"></a>
## 1. Cài đặt

### Yêu cầu

- Python 3.8+

### Cài đặt thư viện

Sau khi clone repo về, di chuyển vào thư mục chứa các công cụ và chạy lệnh sau để cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

<a id="2-tools"></a>
## 2. Danh sách công cụ

### Công cụ quản lý nguồn dữ liệu `data_source.py`

Công cụ `data_source.py` hỗ trợ lấy danh sách các thư mục chứa dữ liệu trên server Label Studio của các project.

```bash
# Hiển thị trợ giúp
python data_source.py --help

# Lấy tất cả các thư mục chứa dữ liệu của tất cả các project
python data_source.py

# Lấy danh sách các thư mục trên server Label Studio nhưng không sử dụng bởi bất kỳ project nào
python data_source.py -t unused

# Lấy danh sách các thư mục chứa dữ liệu của tất cả các project nhưng không tìm thấy trên server Label Studio
python data_source.py -t missing

# Lấy tất cả các thư mục chứa dữ liệu của một project
python data_source.py -p PROJECT_ID
```

Lưu ý: 
- `PROJECT_ID` là ID của project trên Label Studio. Có thể lấy thông tin này từ URL của project.
    
    VD: `URL` là `http://localhost:8080/projects/1/`, `PROJECT_ID` là `1`

- Công cụ sử dụng file `.env` để lấy thông tin cấu hình. Nội dung file tham khảo file `.env.template`.
  Có thể thay đổi vị trí file `.env` bằng cách sử dụng tham số `--env` khi chạy công cụ.
