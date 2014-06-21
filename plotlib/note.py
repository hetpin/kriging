#IMPLEMENT NOTES
1. Bu nhiet do theo do cao
- Khi tinh toan: Bu nhiet do khi doc tu co so du lieu, trong ham getTempOfAAtationFromTo(); 
Trong ham generateGlobalMatrix(), goi getTempOfAAtationFromTo(), luu vao list_data[];
Su dung lai list_data[] trong cac ham  genModelForArea(), krigeOne()
- Khi test: Trong ham calculateSE(), lay nhiet do 1 ngay cua 1 tram qua ham getTempOfAAtationADay();
Sau do cung bu nhiet do theo do cao, roi so sanh voi ket qua kriging
* Lam nhu the nay thi chi co the validation duoc.
Van de la khi tinh toan, bu va tru nhiet do theo do cao can phai thuc hien truoc vao sau trong Tinh Toan;
Vi chua ket hop dc du lieu DEM nen chua lam buoc nay

2. Trend surface
- Fit du lieu bang mot trend surface
- Tru toan bo du lieu cho trend value, sau do tinh COV, Fit model; Tuy nhien theo cong thuc tinh COV thi 
viec tru tat cac du lieu cho x se khong anh huong den COV, do do bo qua buoc nay :))
- Dung model de kriging, Tru trendvalue o day.
- Kriging xong thi bu trend value.
*DONE