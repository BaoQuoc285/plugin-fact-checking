# OPTIMIZE_PROMPT_TEMPLATE = (
#     "Hãy chuyển phát biểu sau thành một truy vấn tìm kiếm ngắn gọn, trung lập, mô tả sự kiện và ưu tiên lấy kết quả từ các trang báo chí uy tín hoặc Wikipedia. "
#     "Chỉ thêm từ khóa 'báo chí', 'tin tức' hoặc 'Wikipedia' nếu thực sự cần thiết để phân biệt với các nguồn không chính thống, nhưng KHÔNG thêm từ này vào cuối truy vấn một cách máy móc.\n"
#     "Nếu phát biểu đã là sự kiện hoặc tên riêng, giữ nguyên nội dung chính.\n"
#     'Phát biểu: "{claim}"\n\n'
#     "Truy vấn tìm kiếm:"
#     "Kết quả chỉ chứa truy vấn tìm kiếm\n"
# )

# OPTIMIZE_PROMPT_TEMPLATE = (
#     "Bạn là một trợ lý AI giúp tối ưu hóa câu phát biểu thành truy vấn tìm kiếm ngắn gọn và chính xác, "
#     "nhằm tìm kiếm thông tin từ các nguồn đáng tin cậy như báo chí chính thống hoặc Wikipedia.\n"
#     "- Biến đổi phát biểu thành truy vấn TRUNG LẬP, sử dụng ngôn ngữ mô tả sự kiện, tránh từ ngữ thiên kiến hoặc suy diễn.\n"
#     "- Chỉ thêm các từ như 'báo chí', 'Wikipedia', 'tin tức' nếu THỰC SỰ cần để phân biệt với blog, mạng xã hội, diễn đàn.\n"
#     "- Nếu phát biểu chứa tên riêng, địa danh, sự kiện cụ thể (ví dụ: 'bão Noru năm 2022'), hãy giữ lại nguyên văn.\n"
#     "- Truy vấn KHÔNG được chứa cảm xúc, phỏng đoán, hoặc kết luận (ví dụ: 'có đúng không', 'có phải là lừa đảo'...)\n"
#     "- Chỉ in ra TRUY VẤN TÌM KIẾM, không thêm lời giải thích hay thông tin nào khác.\n\n"
#     'Phát biểu: "{claim}"\n\n'
#     "Truy vấn tìm kiếm:"
# )

OPTIMIZE_PROMPT_TEMPLATE = (
    "Bạn là một hệ thống trợ lý AI chuyên hỗ trợ kiểm chứng thông tin. "
    "Nhiệm vụ của bạn là chuyển một phát biểu đầu vào thành truy vấn tìm kiếm ngắn gọn, chuẩn hóa và trung lập, "
    "nhằm truy xuất các nguồn tin đáng tin cậy (như báo chí chính thống, trang chính phủ, hoặc Wikipedia).\n\n"
    
    "- Biến đổi phát biểu thành truy vấn trung lập, mang tính mô tả sự kiện, tránh dùng từ ngữ cảm tính, suy đoán hoặc gây tranh cãi.\n"
    "- Ưu tiên giữ nguyên tên riêng, địa danh, mốc thời gian hoặc sự kiện cụ thể nếu có.\n"
    "- Loại bỏ các phần không liên quan như cảm xúc cá nhân, nghi vấn ('có phải', 'đúng không'), hoặc các cụm gây sai lệch.\n"
    "- Chuẩn hóa các cụm từ phổ biến thành dạng dễ tìm kiếm: ví dụ 'ông Biden' → 'Joe Biden', 'bão số 4 năm 2022' → 'bão Noru 2022'.\n"
    "- Nếu cần thiết để lọc kết quả chính thống, có thể thêm từ khóa như 'báo chí', 'Wikipedia', 'tin tức' — nhưng chỉ khi thật sự hữu ích.\n"
    "- Chỉ in ra duy nhất dòng TRUY VẤN TÌM KIẾM. Không thêm giải thích hay nội dung thừa.\n\n"
    
    'Phát biểu: "{claim}"\n\n'
    "Truy vấn tìm kiếm:"
)
#CHUYỂN PROMPT THÀNH CÂU HỎI QUERY TỐI ƯU HÓA
# OPTIMIZE_PROMPT_TEMPLATE = (
#     "Dựa trên phát biểu sau, hãy tạo một câu hỏi tìm kiếm ngắn gọn, dễ hiểu và chính xác nhất trên web để thu thập bằng chứng nhằm kiểm chứng phát biểu đó.\n\n"
#     "Phát biểu: \"{claim}\"\n\n"
#     "Câu hỏi tìm kiếm:" \
#     "Kết quả chỉ chứa câu hỏi tìm kiếm"
# )

# OPTIMIZE_PROMPT_TEMPLATE = (
#     "Chuyển phát biểu sau thành một câu truy vấn tìm kiếm ngắn gọn, trung lập và mô tả sự kiện. "
#     "Mục tiêu là kiểm chứng phát biểu đó trên web bằng cách truy xuất thông tin và bằng chứng.\n\n"
#     "Ví dụ:\n"
#     'Phát biểu: "Sơn Tùng M-TP đạo nhạc"\n'
#     'Truy vấn tìm kiếm: "Sơn Tùng M-TP có đạo nhạc không?"\n\n'
#     'Phát biểu: "Jack bỏ con"\n'
#     'Truy vấn tìm kiếm: "Jack bỏ con có thật không?"\n\n'
#     'Phát biểu: "Hồ Chí Minh là thủ đô của Việt Nam"\n'
#     'Truy vấn tìm kiếm: "Hồ Chí Minh có phải là thủ đô của Việt Nam không?"\n\n'
#     'Phát biểu: "{claim}"\n\n'
#     "Truy vấn tìm kiếm:"
# )

PROMPTS = {
    "OPTIMIZE_QUERY": OPTIMIZE_PROMPT_TEMPLATE,
}