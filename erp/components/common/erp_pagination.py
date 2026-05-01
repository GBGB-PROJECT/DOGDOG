import math


def calc_total_pages(total_count, page_size):
    # 🔥 ERP 조회 화면 공통 전체 페이지 계산
    return max(1, math.ceil((total_count or 0) / page_size))


def get_page_window(current_page, total_pages, radius=2):
    # 🔥 현재 페이지 주변 번호 생성
    start_page = max(1, current_page - radius)
    end_page = min(total_pages, current_page + radius)
    return range(start_page, end_page + 1)
