-- Phân quyền
CREATE USER [dev_readonly] WITH PASSWORD = 'Read@77346';
EXEC sp_addrolemember 'db_datareader', 'dev_readonly';



SELECT name, type_desc FROM sys.database_principals WHERE type IN ('S', 'E', 'X');

SELECT dp1.name AS DatabaseRoleName, dp2.name AS MemberName  
FROM sys.database_role_members AS drm  
JOIN sys.database_principals AS dp1 ON drm.role_principal_id = dp1.principal_id  
JOIN sys.database_principals AS dp2 ON drm.member_principal_id = dp2.principal_id;


CREATE TABLE Quan (
    QuanID INT IDENTITY PRIMARY KEY,
    TenQuan NVARCHAR(100) NOT NULL,
    MoTa NVARCHAR(255)
);

CREATE TABLE LoaiDiemThamQuan (
    LoaiID INT IDENTITY PRIMARY KEY,
    TenLoai NVARCHAR(100) NOT NULL,
    MoTa NVARCHAR(300)
);

CREATE TABLE DiemThamQuan (
    DiemID INT IDENTITY PRIMARY KEY,
    TenDiem NVARCHAR(200) NOT NULL,
    MoTa NVARCHAR(2000),
    DiaChi NVARCHAR(300),
    QuanID INT,
    LoaiID INT,
    ViDo DECIMAL(10,6) NOT NULL,
    KinhDo DECIMAL(10,6) NOT NULL,
    GioMoCua TIME,
    GioDongCua TIME,
    FOREIGN KEY (QuanID) REFERENCES Quan(QuanID),
    FOREIGN KEY (LoaiID) REFERENCES LoaiDiemThamQuan(LoaiID)
);

CREATE TABLE HinhAnhDiem (
    HinhID INT IDENTITY PRIMARY KEY,
    DiemID INT,
    UrlHinh NVARCHAR(255) NOT NULL,
    MoTaHinh NVARCHAR(200),
    FOREIGN KEY (DiemID) REFERENCES DiemThamQuan(DiemID)
);

INSERT INTO Quan (TenQuan, MoTa) VALUES
(N'Quận 1', N'Trung tâm thương mại và du lịch lớn của TP.HCM'),
(N'Quận 3', N'Khu vực nhiều công trình kiến trúc cổ và văn hóa'),
(N'Quận 5', N'Thuộc khu người Hoa – nhiều điểm du lịch văn hóa'),
(N'Quận 7', N'Khu đô thị Phú Mỹ Hưng hiện đại'),
(N'Thủ Đức', N'Khu vực phát triển nhanh, nhiều khu du lịch sinh thái');

INSERT INTO LoaiDiemThamQuan (TenLoai, MoTa) VALUES
(N'Lịch sử', N'Các địa điểm mang giá trị lịch sử, di tích cách mạng'),
(N'Văn hóa', N'Địa điểm mang đặc trưng văn hóa, tín ngưỡng'),
(N'Giải trí', N'Khu vui chơi, mua sắm, giải trí'),
(N'Sinh thái', N'Khu du lịch sinh thái, thiên nhiên'),
(N'Kiến trúc', N'Công trình kiến trúc nổi tiếng');

INSERT INTO DiemThamQuan (TenDiem, MoTa, DiaChi, QuanID, LoaiID, ViDo, KinhDo, GioMoCua, GioDongCua)
VALUES
-- Quận 1
(N'Dinh Độc Lập', N'Di tích lịch sử quan trọng, nơi lưu giữ nhiều kỷ vật của thời kỳ kháng chiến.', 
 N'135 Nam Kỳ Khởi Nghĩa, Quận 1, TP.HCM', 1, 1, 10.777017, 106.695859, '07:30', '17:00'),

(N'Nhà thờ Đức Bà', N'Biểu tượng kiến trúc Pháp cổ, tọa lạc tại trung tâm thành phố.', 
 N'01 Công xã Paris, Quận 1, TP.HCM', 1, 5, 10.779783, 106.699018, '08:00', '18:00'),

(N'Chợ Bến Thành', N'Một trong những biểu tượng nổi tiếng nhất của TP.HCM, thu hút nhiều khách du lịch.', 
 N'Lê Lợi, Phường Bến Thành, Quận 1, TP.HCM', 1, 3, 10.772309, 106.698113, '07:00', '18:00'),

-- Quận 3
(N'Bảo tàng Chứng tích Chiến tranh', N'Nơi trưng bày hiện vật và hình ảnh về cuộc kháng chiến chống Mỹ.', 
 N'28 Võ Văn Tần, Quận 3, TP.HCM', 2, 1, 10.779284, 106.692399, '07:30', '17:30'),

-- Quận 5
(N'Chùa Bà Thiên Hậu', N'Một ngôi chùa cổ của người Hoa, nổi tiếng linh thiêng.', 
 N'710 Nguyễn Trãi, Phường 11, Quận 5, TP.HCM', 3, 2, 10.754271, 106.663649, '06:00', '17:00'),

-- Quận 7
(N'Crescent Mall', N'Trung tâm mua sắm hiện đại, kết hợp khu vực giải trí và ẩm thực.', 
 N'101 Tôn Dật Tiên, Quận 7, TP.HCM', 4, 3, 10.731249, 106.721024, '09:00', '22:00'),

(N'Hồ Bán Nguyệt & Cầu Ánh Sao', N'Khu vực cảnh quan đẹp, thích hợp dạo bộ và chụp ảnh.', 
 N'Phú Mỹ Hưng, Quận 7, TP.HCM', 4, 4, 10.729777, 106.721950, '00:00', '23:59'),

-- Thủ Đức
(N'Khu du lịch Suối Tiên', N'Khu du lịch văn hóa – giải trí lớn với chủ đề thần thoại dân gian Việt Nam.', 
 N'120 Xa Lộ Hà Nội, Phường Tân Phú, TP. Thủ Đức', 5, 3, 10.870885, 106.800547, '08:00', '17:30'),

(N'Chùa Bửu Long', N'Ngôi chùa mang phong cách Thái Lan, nằm bên hồ nước yên bình.', 
 N'81 Nguyễn Xiển, Phường Long Bình, TP. Thủ Đức', 5, 2, 10.841021, 106.830705, '07:00', '17:00');

 INSERT INTO HinhAnhDiem (DiemID, UrlHinh, MoTaHinh) VALUES
(1, N'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Dinh_%C4%90%E1%BB%99c_L%E1%BA%ADp_v%C3%A0o_n%C3%A0m_2024.jpg/1200px-Dinh_%C4%90%E1%BB%99c_L%E1%BA%ADp_v%C3%A0o_n%C3%A0m_2024.jpg', N'Mặt tiền Dinh Độc Lập'),
(2, N'https://saigonhotel.com.vn/wp-content/uploads/2019/11/f5d8fc3e-nha-tho-duc-ba-thumbnail-min-1.webp', N'Nhà thờ Đức Bà từ góc đường Lê Duẩn'),
(3, N'https://cdn.xanhsm.com/2024/11/78626cf9-cho-ben-thanh-6.jpg', N'Cổng chính chợ Bến Thành'),
(4, N'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/08/bao-tang-chung-tich-chien-tranh-1-e1504148866695.jpg', N'Bảo tàng Chứng tích Chiến tranh'),
(5, N'https://dulichvn.org.vn/nhaptin/uploads/images/2020/Thang10/02102020-chua-ba-Thien-Hau.jpg', N'Chùa Bà Thiên Hậu – Quận 5'),
(6, N'https://crescent.com.vn/wp-content/uploads/2025/04/vi-tri-crescent-mall-ho-ban-nguyet-68047f.webp', N'Crescent Mall nhìn từ trên cao'),
(7, N'https://r2.nucuoimekong.com/wp-content/uploads/ban-do-di-cau-anh-sao.jpg', N'Cầu Ánh Sao về đêm'),
(8, N'https://r2.nucuoimekong.com/wp-content/uploads/khu-du-lich-suoi-tien-hcm.jpg', N'Cổng chính khu du lịch Suối Tiên'),
(9, N'https://cdn.vntrip.vn/cam-nang/wp-content/uploads/2017/09/chua-buu-long.jpg', N'Chùa Bửu Long – phong cách Thái Lan');

select * from DiemThamQuan

CREATE USER [dev_editor1] WITH PASSWORD = 'StrongPass@123';
EXEC sp_addrolemember 'db_datareader', 'dev_editor1';
EXEC sp_addrolemember 'db_datawriter', 'dev_editor1';
EXEC sp_addrolemember 'db_owner', 'dev_editor1';

drop table HinhAnhDiem;