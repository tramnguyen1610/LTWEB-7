import pandas as pd
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages


def xu_ly_cham_cong(request):
    employees_data = []  # Mảng chứa dữ liệu đẩy ra JS
    show_preview = False

    if request.method == 'POST':
        tu_ngay_str = request.POST.get('tu_ngay')  # VD: '2026-02-01'
        file_upload = request.FILES.get('file_cham_cong')

        # Trích xuất "Tháng/Năm" từ ngày chọn để lát hiển thị lên web
        thang_nam = "02/2026"
        if tu_ngay_str:
            try:
                dt = datetime.strptime(tu_ngay_str, "%Y-%m-%d")
                thang_nam = dt.strftime("%m/%Y")
            except:
                pass

        if file_upload:
            try:
                # 1. Đọc file, dùng skiprows=3 để lơ đi 3 dòng đầu (Tiêu đề, Địa chỉ...)
                if file_upload.name.endswith('.csv'):
                    df = pd.read_csv(file_upload, skiprows=3)
                else:
                    df = pd.read_excel(file_upload, skiprows=3)

                # 2. Quét từng nhân viên (mỗi nhân viên là 1 dòng)
                for index, row in df.iterrows():
                    # Cột index 2 là Mã NV, index 3 là Tên NV (theo cấu trúc file của Linh)
                    ma_nv = str(row.iloc[2]).strip()
                    ten_nv = str(row.iloc[3]).strip()

                    # Bỏ qua các dòng trống hoặc dòng chứa chữ tính tổng
                    if pd.isna(ma_nv) or ma_nv == 'nan' or 'Mã' in ma_nv:
                        continue

                    emp_dict = {
                        "ma": ma_nv.zfill(5),  # Định dạng 1 thành 00001
                        "ten": ten_nv,
                        "gio": 0.0,
                        "days": []
                    }

                    tong_gio = 0.0
                    col_idx = 5  # Dữ liệu ngày 1 bắt đầu từ Cột số 6 (index 5)

                    # 3. Quét tối đa 31 ngày, mỗi ngày dịch qua 2 cột (Vào - Ra)
                    for day in range(1, 32):
                        if col_idx + 1 >= len(row):
                            break  # Nếu file chỉ có 28 ngày thì dừng sớm

                        gio_vao = str(row.iloc[col_idx]).strip()
                        gio_ra = str(row.iloc[col_idx + 1]).strip()

                        # Dịch tới cột của ngày hôm sau
                        col_idx += 2

                        if gio_vao == 'nan': gio_vao = ""
                        if gio_ra == 'nan': gio_ra = ""

                        # Chỉ xử lý nếu hôm đó có dữ liệu bấm tay
                        if gio_vao or gio_ra:
                            gio_lam_ca = 0.0
                            phut_muon = 0

                            # Tính giờ làm nếu có đủ Vào - Ra
                            if gio_vao and gio_ra:
                                try:
                                    t_in = datetime.strptime(gio_vao, "%H:%M")
                                    t_out = datetime.strptime(gio_ra, "%H:%M")

                                    # Tính số giờ làm (Giờ ra - Giờ vào)
                                    delta = t_out - t_in
                                    gio_lam_ca = delta.total_seconds() / 3600.0

                                    # Tính đi muộn (Tạm lấy chuẩn ca sáng 08:00, Linh sửa theo ca linh hoạt sau)
                                    t_ca = datetime.strptime("08:00", "%H:%M")
                                    if t_in > t_ca:
                                        phut_muon = int((t_in - t_ca).total_seconds() / 60)
                                except Exception as parse_err:
                                    pass  # Nếu chuỗi giờ bị lỗi (vd: "--:--") thì bỏ qua

                            tong_gio += gio_lam_ca

                            # Lưu vào cấu trúc JSON y hệt cấu trúc gốc của Linh
                            emp_dict["days"].append({
                                "day": day,
                                "date": f"{day:02d}/{thang_nam}",
                                "shifts": [{
                                    "in": gio_vao,
                                    "out": gio_ra,
                                    "late": phut_muon if phut_muon > 0 else None
                                }]
                            })

                    # Lưu tổng giờ làm
                    emp_dict["gio"] = round(tong_gio, 2)

                    employees_data.append(emp_dict)

                show_preview = True
                messages.success(request, f"Đọc file chấm công tháng {thang_nam} thành công!")

            except Exception as e:
                messages.error(request, f"Lỗi đọc file: Vui lòng xem lại cấu trúc. Chi tiết: {str(e)}")

    # Trả cục JSON siêu bự ra ngoài cho file HTML hiển thị
    context = {
        'employees_json': json.dumps(employees_data),
        'show_preview': json.dumps(show_preview)
    }
    return render(request, 'attendance/xu_ly_cham_cong.html', context)