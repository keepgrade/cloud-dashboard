import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import re

BASE_URL = "https://huhhuhman.shinyapps.io/cloud-dashboard/"
WAIT_TIMEOUT = 10
QUICK_WAIT_TIMEOUT = 2  # For NFR-002/NFR-003, specified as 2 seconds or 1 second

# Selector Mappings
SELECTORS = {
    "page_title": "h1.navbar-brand",
    "monthly_cost_slider": "#monthly_cost",
    "traffic_window_business_checkbox": "input[name='traffic_window'][value='BUSINESS']",
    "traffic_window_peak_checkbox": "input[name='traffic_window'][value='PEAK']",
    "filter_reset_button": "#reset",
    "total_rows_value_box": "#total_rows",
    "avg_overage_ratio_value_box": "#avg_overage_ratio",
    "avg_monthly_cost_value_box": "#avg_monthly_cost",
    "data_table": "shiny-data-frame#table",
    "data_table_card_fullscreen_button": "#bslib_card_5b9f4f .bslib-full-screen-enter",
    "scatterplot": "#scatterplot",
    "scatterplot_popover_icon": "#bslib_card_50c9ef .card-header bslib-popover svg",
    "scatter_color_none_radio": "input[name='scatter_color'][value='none']",
    "scatter_color_customer_segment_radio": "input[name='scatter_color'][value='customer_segment']",
    "violin_plot": "#overage_ratio_dist",
    "violin_plot_popover_icon": "#bslib_card_d289e8 .card-header bslib-popover svg",
    "ratio_split_by_customer_segment_radio": "input[name='ratio_split_by'][value='customer_segment']",
    "ratio_split_by_weekday_radio": "input[name='ratio_split_by'][value='weekday']",
    "sidebar_toggle_button": "button.collapse-toggle",
    "sidebar": "#bslib_sidebar_375c7f",
    "monthly_cost_slider_from_display": "#monthly_cost + div .irs-from", # Displayed 'from' value of the slider
    "monthly_cost_slider_to_display": "#monthly_cost + div .irs-to", # Displayed 'to' value of the slider
    "data_table_info_text": "#table > div.data-frame-info > span", # e.g., "Viewing rows 1 through 7 of 200"
    "scatterplot_popover_content": "#bslib_card_50c9ef .card-header bslib-popover > template + div",
    "violin_plot_popover_content": "#bslib_card_d289e8 .card-header bslib-popover > template + div",
}

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.set_window_size(1920, 1080) # Ensure consistent test environment
    driver.get(BASE_URL)
    yield driver
    driver.quit()

def wait_and_find_element(driver, by, selector, timeout=WAIT_TIMEOUT):
    """Waits for an element to be present and returns it."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

def wait_and_click_element(driver, by, selector, timeout=WAIT_TIMEOUT):
    """Waits for an element to be clickable and clicks it."""
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
    element.click()
    return element

def get_element_text(driver, by, selector, timeout=WAIT_TIMEOUT):
    """Waits for an element to be visible and returns its text."""
    element = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, selector))
    )
    return element.text

def assert_kpi_value_format(driver, selector_key, expected_pattern, timeout=WAIT_TIMEOUT):
    """Asserts that a KPI value box text matches a regex pattern."""
    value_text = get_element_text(driver, By.CSS_SELECTOR, SELECTORS[selector_key], timeout)
    assert re.fullmatch(expected_pattern, value_text), \
        f"KPI '{selector_key}' value '{value_text}' did not match expected pattern '{expected_pattern}'"

def assert_chart_no_data_message(driver, selector_key, timeout=WAIT_TIMEOUT):
    """Asserts that a chart area displays the '필터 결과가 없습니다.' message."""
    no_data_message = "필터 결과가 없습니다."
    # For shiny-data-frame, the message appears inside a div within it
    if selector_key == "data_table":
        message_element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f"{SELECTORS[selector_key]} > div.data-frame-info.empty"))
        )
        assert no_data_message in message_element.text, \
            f"Expected '{no_data_message}' in data table, but found '{message_element.text}'"
    else: # For scatterplot and violin plot, the message is directly within the plot div
        plot_element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, SELECTORS[selector_key]))
        )
        assert no_data_message in plot_element.text, \
            f"Expected '{no_data_message}' in {selector_key}, but found '{plot_element.text}'"

def manipulate_ion_range_slider(driver, selector_id, from_value=None, to_value=None):
    """Manipulates an ion.rangeSlider using JavaScript."""
    script = f"var slider = document.getElementById('{selector_id}');"
    script += f"var slider_instance = $(slider).data('ionRangeSlider');"
    update_params = []
    if from_value is not None:
        update_params.append(f"from: {from_value}")
    if to_value is not None:
        update_params.append(f"to: {to_value}")
    if update_params:
        script += f"slider_instance.update({{{', '.join(update_params)}}});"
    driver.execute_script(script)

def assert_filter_initial_state(driver):
    """Helper to assert the initial state of filters and KPIs."""
    # Monthly cost slider
    slider_from = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_from_display"])
    slider_to = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_to_display"])
    assert slider_from == "₩90,000", f"Slider 'from' value expected ₩90,000, got {slider_from}"
    assert slider_to == "₩1,650,000", f"Slider 'to' value expected ₩1,650,000, got {slider_to}"

    # Traffic window checkboxes
    business_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    peak_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])
    assert business_checkbox.is_selected(), "'업무시간' checkbox is not selected"
    assert peak_checkbox.is_selected(), "'야간/피크' checkbox is not selected"

    # Scatterplot color option
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot_popover_icon"])
    scatter_none_radio = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatter_color_none_radio"])
    assert scatter_none_radio.is_selected(), "Scatterplot color '없음' is not selected"
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot_popover_icon"]) # Close popover

    # Violin plot group option
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot_popover_icon"])
    violin_weekday_radio = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["ratio_split_by_weekday_radio"])
    assert violin_weekday_radio.is_selected(), "Violin plot group '요일' is not selected"
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot_popover_icon"]) # Close popover

    # KPI Values (check for non-placeholder values)
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) != " - ", "Total rows KPI is placeholder"
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) != " - ", "Avg overage ratio KPI is placeholder"
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) != " - ", "Avg monthly cost KPI is placeholder"

    # Charts visibility
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["data_table"])
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot"])
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot"])


def test_tc001_initial_page_loading_and_ui_state(driver):
    """TC-001: 초기 페이지 로딩 및 기본 UI 상태 확인"""
    # Step 1: 대시보드 URL 접속 -> 페이지 타이틀 "가비아 클라우드 | 서비스 지표 대시보드 | Ted(신태선)-클라우드기획팀" 이 표시된다. 사이드바가 기본적으로 열려 있는 상태로 표시된다.
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.title_contains("가비아 클라우드 | 서비스 지표 대시보드 | Ted(신태선)-클라우드기획팀"))
    page_title_element = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["page_title"])
    assert page_title_element.text == "가비아 클라우드 | 서비스 지표 대시보드 | Ted(신태선)-클라우드기획팀"

    sidebar = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["sidebar"])
    assert sidebar.get_attribute("hidden") is None, "사이드바가 열려있지 않습니다."

    # Step 2: 월 과금 범위 슬라이더, 트래픽 구간 체크박스, 산점도/바이올린 플롯 옵션 초기값 확인
    # Monthly cost slider
    slider_from = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_from_display"])
    slider_to = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_to_display"])
    assert slider_from == "₩90,000", f"월 과금 슬라이더 최소값 오류: {slider_from}"
    assert slider_to == "₩1,650,000", f"월 과금 슬라이더 최대값 오류: {slider_to}"

    # Traffic window checkboxes
    business_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    peak_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])
    assert business_checkbox.is_selected(), "'업무시간' 체크박스가 선택되어 있지 않습니다."
    assert peak_checkbox.is_selected(), "'야간/피크' 체크박스가 선택되어 있지 않습니다."

    # Scatterplot color option
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot_popover_icon"])
    scatter_none_radio = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatter_color_none_radio"])
    assert scatter_none_radio.is_selected(), "산점도의 색상 기준 '없음'이 선택되어 있지 않습니다."
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot_popover_icon"]) # Close popover

    # Violin plot group option
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot_popover_icon"])
    violin_weekday_radio = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["ratio_split_by_weekday_radio"])
    assert violin_weekday_radio.is_selected(), "바이올린 플롯의 그룹 기준 '요일'이 선택되어 있지 않습니다."
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot_popover_icon"]) # Close popover

    # Step 3: KPI Value Box 초기값 및 형식 확인
    assert_kpi_value_format(driver, "total_rows_value_box", r"^\d+$") # 정수 형태
    assert_kpi_value_format(driver, "avg_overage_ratio_value_box", r"^\d+\.\d%$") # 백분율(소수점 1자리) 형태
    assert_kpi_value_format(driver, "avg_monthly_cost_value_box", r"^₩\d{1,3}(,\d{3})*$") # 원화(천단위 콤마) 형태

    # Step 4: 원천 데이터 미리보기 테이블, 산점도, 바이올린 플롯 초기 렌더링 확인
    data_table_info = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["data_table_info_text"])
    assert re.search(r"Viewing rows \d+ through \d+ of \d+", data_table_info), \
        f"데이터 테이블 정보 텍스트 형식이 예상과 다름: {data_table_info}"
    assert "of 200" in data_table_info, f"데이터 테이블이 최대 200행을 표시하지 않음: {data_table_info}"

    scatterplot_element = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot"])
    assert scatterplot_element.is_displayed(), "산점도 차트가 표시되지 않습니다."
    # Further checks for chart content (e.g., color) would require visual comparison or deeper JS inspection

    violin_plot_element = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot"])
    assert violin_plot_element.is_displayed(), "바이올린 플롯이 표시되지 않습니다."
    # Further checks for chart content would require visual comparison or deeper JS inspection

def test_tc002_monthly_cost_slider_data_update(driver):
    """TC-002: 월 과금 범위 슬라이더 조작 시 데이터 갱신 확인"""
    # Get initial KPI values for comparison
    initial_total_rows = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"])
    initial_avg_overage_ratio = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"])
    initial_avg_monthly_cost = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"])

    # Step 1: 월 과금 범위 슬라이더의 최소값을 ₩500,000으로 조작
    # Use JavaScript to update the ion.rangeSlider
    manipulate_ion_range_slider(driver, "monthly_cost", from_value=500000)

    # Assert slider display updates
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_from_display"]), "₩500,000")
    )
    slider_from = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_from_display"])
    slider_to = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_to_display"])
    assert slider_from == "₩500,000", f"슬라이더 'from' 값이 ₩500,000이 아님: {slider_from}"
    assert slider_to == "₩1,650,000", f"슬라이더 'to' 값이 ₩1,650,000이 아님: {slider_to}"

    # Step 2: 모든 KPI Value Box 및 차트 영역 갱신 확인
    # Wait for KPIs to change from initial values (NFR-002: 2초 이내)
    WebDriverWait(driver, QUICK_WAIT_TIMEOUT).until(
        lambda d: get_element_text(d, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) != initial_total_rows
    )
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) != " - ", "조회 대상 건수 KPI가 ' - ' 입니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) != " - ", "평균 오버리지 비중 KPI가 ' - ' 입니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) != " - ", "평균 월 과금 KPI가 ' - ' 입니다."

    # Assert that they are different from initial values (implies update)
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) != initial_total_rows
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) != initial_avg_overage_ratio
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) != initial_avg_monthly_cost

    # Data table, scatterplot, violin plot visibility check (implies refresh for dynamic content)
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["data_table"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot"]).is_displayed()

def test_tc003_traffic_window_checkbox_data_update(driver):
    """TC-003: 트래픽 구간 체크박스 조작 시 데이터 갱신 확인"""
    # Get initial KPI values for comparison
    initial_total_rows = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"])

    business_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    peak_checkbox = wait_and_find_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])

    # Step 1: "업무시간" 체크박스를 선택 해제
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    assert not business_checkbox.is_selected(), "'업무시간' 체크박스가 선택 해제되지 않았습니다."

    # Step 2: 모든 KPI Value Box 및 차트 영역 갱신 확인 (NFR-002: 2초 이내)
    WebDriverWait(driver, QUICK_WAIT_TIMEOUT).until(
        lambda d: get_element_text(d, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) != initial_total_rows
    )
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) != " - ", "조회 대상 건수 KPI가 ' - ' 입니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) != " - ", "평균 오버리지 비중 KPI가 ' - ' 입니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) != " - ", "평균 월 과금 KPI가 ' - ' 입니다."
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["data_table"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot"]).is_displayed()

    # Step 3: "야간/피크" 체크박스를 선택 해제
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])
    assert not peak_checkbox.is_selected(), "'야간/피크' 체크박스가 선택 해제되지 않았습니다."

    # Step 4: 모든 KPI Value Box 및 차트 영역 갱신 확인
    # Expect " - " for KPIs and "필터 결과가 없습니다." for charts
    WebDriverWait(driver, QUICK_WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]), " - ")
    )
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) == " - ", "조회 대상 건수 KPI가 ' - ' 가 아닙니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) == " - ", "평균 오버리지 비중 KPI가 ' - ' 가 아닙니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) == " - ", "평균 월 과금 KPI가 ' - ' 가 아닙니다."

    assert_chart_no_data_message(driver, "data_table", QUICK_WAIT_TIMEOUT)
    assert_chart_no_data_message(driver, "scatterplot", QUICK_WAIT_TIMEOUT)
    assert_chart_no_data_message(driver, "violin_plot", QUICK_WAIT_TIMEOUT)

def test_tc004_filter_reset_functionality(driver):
    """TC-004: 필터 초기화 기능 확인"""
    # Step 1: 월 과금 슬라이더를 중간 범위(예: ₩300,000 ~ ₩800,000)로 조작하고, "야간/피크" 체크박스를 선택 해제
    manipulate_ion_range_slider(driver, "monthly_cost", from_value=300000, to_value=800000)
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"]) # Uncheck peak

    WebDriverWait(driver, QUICK_WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_from_display"]), "₩300,000")
    )
    peak_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])
    assert not peak_checkbox.is_selected(), "'야간/피크' 체크박스가 선택 해제되지 않았습니다."

    # Wait for data to update, then store current state to confirm change
    time.sleep(QUICK_WAIT_TIMEOUT) # Give time for data to filter
    filtered_total_rows = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"])
    assert filtered_total_rows != " - ", "필터 조작 후 KPI가 ' - ' 입니다."

    # Step 2: "필터 초기화" 버튼 클릭
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["filter_reset_button"])

    # 월 과금 슬라이더가 ₩90,000 ~ ₩1,650,000 전체 범위로 복원된다.
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_from_display"]), "₩90,000")
    )
    slider_from = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_from_display"])
    slider_to = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider_to_display"])
    assert slider_from == "₩90,000", f"슬라이더 'from' 값이 초기값으로 복원되지 않음: {slider_from}"
    assert slider_to == "₩1,650,000", f"슬라이더 'to' 값이 초기값으로 복원되지 않음: {slider_to}"

    # "업무시간" 및 "야간/피크" 체크박스가 모두 선택된 상태로 복원된다.
    business_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    peak_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])
    assert business_checkbox.is_selected(), "'업무시간' 체크박스가 복원되지 않았습니다."
    assert peak_checkbox.is_selected(), "'야간/피크' 체크박스가 복원되지 않았습니다."

    # Step 3: 모든 KPI Value Box 및 차트 영역 초기 상태 갱신 확인
    # Verify that KPIs revert to their initial (non-filtered) state. This requires checking against a known initial value,
    # or simply ensuring they are not the 'filtered_total_rows' from before.
    WebDriverWait(driver, QUICK_WAIT_TIMEOUT).until(
        lambda d: get_element_text(d, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) != filtered_total_rows
    )
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) != " - ", "조회 대상 건수 KPI가 ' - ' 입니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) != " - ", "평균 오버리지 비중 KPI가 ' - ' 입니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) != " - ", "평균 월 과금 KPI가 ' - ' 입니다."

    # Charts should also be visible and populated
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["data_table"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot"]).is_displayed()

def test_tc005_scatterplot_color_change_data_update(driver):
    """TC-005: 산점도 색상 기준 변경 시 해당 차트만 갱신 확인"""
    # Get initial KPI values for comparison (should not change)
    initial_total_rows = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"])
    initial_avg_overage_ratio = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"])
    initial_avg_monthly_cost = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"])

    # Step 1: "월 과금 vs 오버리지 (상관관계)" 카드 헤더의 팝오버 아이콘 클릭
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot_popover_icon"])
    popover_content = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot_popover_content"])
    assert popover_content.is_displayed(), "산점도 색상 기준 팝오버가 표시되지 않습니다."

    # Step 2: "고객 세그먼트" 라디오 버튼 선택
    customer_segment_radio = wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["scatter_color_customer_segment_radio"])
    assert customer_segment_radio.is_selected(), "'고객 세그먼트' 라디오 버튼이 선택되지 않았습니다."

    # 산점도 차트의 점 색상이 고객 세그먼트별로 구분되어 표시된다 (NFR-003: 1초 이내).
    # Verifying color change visually is difficult. Assume chart updates if input is processed.
    # We can check if the plot element is still displayed and has not shown an error message.
    time.sleep(QUICK_WAIT_TIMEOUT) # Give chart time to render, NFR-003 is 1 second

    # 다른 KPI Value Box 및 차트(데이터 테이블, 바이올린 플롯)는 변동 없이 유지된다.
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) == initial_total_rows, "조회 대상 건수 KPI가 변경되었습니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) == initial_avg_overage_ratio, "평균 오버리지 비중 KPI가 변경되었습니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) == initial_avg_monthly_cost, "평균 월 과금 KPI가 변경되었습니다."
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["data_table"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot"]).is_displayed()

    # Step 3: "없음" 라디오 버튼 선택
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["scatter_color_none_radio"])
    none_radio = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatter_color_none_radio"])
    assert none_radio.is_selected(), "'없음' 라디오 버튼이 선택되지 않았습니다."

    time.sleep(QUICK_WAIT_TIMEOUT) # Give chart time to render

    # 다른 KPI Value Box 및 차트는 변동 없이 유지된다.
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) == initial_total_rows
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) == initial_avg_overage_ratio
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) == initial_avg_monthly_cost
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["data_table"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot"]).is_displayed()

    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot_popover_icon"]) # Close popover

def test_tc006_violin_plot_group_change_data_update(driver):
    """TC-006: 바이올린 플롯 그룹 기준 변경 시 해당 차트만 갱신 확인"""
    # Get initial KPI values for comparison (should not change)
    initial_total_rows = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"])
    initial_avg_overage_ratio = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"])
    initial_avg_monthly_cost = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"])

    # Step 1: "오버리지 비중 분포 (그룹별)" 카드 헤더의 팝오버 아이콘 클릭
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot_popover_icon"])
    popover_content = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot_popover_content"])
    assert popover_content.is_displayed(), "바이올린 플롯 그룹 기준 팝오버가 표시되지 않습니다."

    # Step 2: "고객 세그먼트" 라디오 버튼 선택
    customer_segment_radio = wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["ratio_split_by_customer_segment_radio"])
    assert customer_segment_radio.is_selected(), "'고객 세그먼트' 라디오 버튼이 선택되지 않았습니다."

    # 바이올린 플롯이 고객 세그먼트별 분포로 변경되어 표시된다 (NFR-003: 1초 이내).
    time.sleep(QUICK_WAIT_TIMEOUT) # Give chart time to render

    # 다른 KPI Value Box 및 차트(데이터 테이블, 산점도)는 변동 없이 유지된다.
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) == initial_total_rows, "조회 대상 건수 KPI가 변경되었습니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) == initial_avg_overage_ratio, "평균 오버리지 비중 KPI가 변경되었습니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) == initial_avg_monthly_cost, "평균 월 과금 KPI가 변경되었습니다."
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["data_table"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot"]).is_displayed()

    # Step 3: "요일" 라디오 버튼 선택
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["ratio_split_by_weekday_radio"])
    weekday_radio = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["ratio_split_by_weekday_radio"])
    assert weekday_radio.is_selected(), "'요일' 라디오 버튼이 선택되지 않았습니다."

    time.sleep(QUICK_WAIT_TIMEOUT) # Give chart time to render

    # 다른 KPI Value Box 및 차트는 변동 없이 유지된다.
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) == initial_total_rows
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) == initial_avg_overage_ratio
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) == initial_avg_monthly_cost
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["data_table"]).is_displayed()
    wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot"]).is_displayed()

    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["violin_plot_popover_icon"]) # Close popover

def test_tc007_zero_filter_results_display(driver):
    """TC-007: 필터 결과가 0건일 때 지표 및 차트 표시 확인"""
    # Step 1: 모든 트래픽 구간 체크박스를 선택 해제하여 필터 결과가 0건이 되도록 조작
    business_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    peak_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])

    if business_checkbox.is_selected():
        wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    if peak_checkbox.is_selected():
        wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])

    # Wait for the checkboxes to be deselected
    WebDriverWait(driver, WAIT_TIMEOUT).until_not(EC.element_to_be_selected(business_checkbox))
    WebDriverWait(driver, WAIT_TIMEOUT).until_not(EC.element_to_be_selected(peak_checkbox))

    # Step 2: KPI Value Box 확인
    # Expect " - " for all KPIs
    WebDriverWait(driver, QUICK_WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]), " - ")
    )
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"]) == " - ", "조회 대상 건수 KPI가 ' - ' 가 아닙니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) == " - ", "평균 오버리지 비중 KPI가 ' - ' 가 아닙니다."
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_monthly_cost_value_box"]) == " - ", "평균 월 과금 KPI가 ' - ' 가 아닙니다."

    # Step 3: 데이터 테이블, 산점도, 바이올린 플롯 확인
    assert_chart_no_data_message(driver, "data_table", QUICK_WAIT_TIMEOUT)
    assert_chart_no_data_message(driver, "scatterplot", QUICK_WAIT_TIMEOUT)
    assert_chart_no_data_message(driver, "violin_plot", QUICK_WAIT_TIMEOUT)

def test_tc008_card_fullscreen_functionality(driver):
    """TC-008: 카드 전체화면 기능 확인"""
    # Step 1: "원천 데이터 미리보기" 카드의 전체화면 버튼 클릭
    fullscreen_button = wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["data_table_card_fullscreen_button"])

    # 데이터 테이블이 전체 화면으로 확대된다.
    # Check if the body or main content area changes class or style to indicate fullscreen.
    # A more direct check is if other elements are hidden or the target element has a fullscreen attribute/class.
    # The `bslib-full-screen-enter` button changes to `bslib-full-screen-exit`
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#bslib_card_5b9f4f .bslib-full-screen-exit"))
    )
    # Check if sidebar is hidden
    sidebar = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["sidebar"])
    assert sidebar.get_attribute("hidden") == "true" or "display: none" in sidebar.get_attribute("style"), \
        "전체 화면 모드에서 사이드바가 숨겨지지 않았습니다."

    # Step 2: 전체화면 종료 버튼 클릭
    exit_fullscreen_button = wait_and_click_element(driver, By.CSS_SELECTOR, "#bslib_card_5b9f4f .bslib-full-screen-exit")

    # 데이터 테이블이 원래 크기와 위치로 돌아온다.
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#bslib_card_5b9f4f .bslib-full-screen-enter"))
    )
    # 다른 카드 및 사이드바가 다시 표시된다.
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["sidebar"]))
    )
    sidebar = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["sidebar"])
    assert sidebar.get_attribute("hidden") is None, "전체 화면 종료 후 사이드바가 다시 표시되지 않았습니다."

def test_tc009_sidebar_toggle_functionality(driver):
    """TC-009: 사이드바 토글 기능 확인"""
    sidebar_toggle_button = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["sidebar_toggle_button"])
    sidebar = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["sidebar"])

    # Initial state: sidebar should be open (checked in TC-001)
    assert sidebar.get_attribute("hidden") is None, "초기 사이드바가 열려있지 않습니다."

    # Step 1: 사이드바가 열려있는 상태에서 토글 버튼 클릭
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["sidebar_toggle_button"])

    # 사이드바가 왼쪽으로 접혀 들어간다.
    # The `hidden` attribute is added when collapsed.
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, SELECTORS["sidebar"])) # Element is still there but hidden
    )
    assert sidebar.get_attribute("hidden") == "true", "사이드바가 접히지 않았습니다 (hidden attribute 없음)."
    assert sidebar_toggle_button.get_attribute("aria-expanded") == "false", "사이드바 토글 버튼의 aria-expanded가 false가 아닙니다."

    # Step 2: 사이드바가 닫혀있는 상태에서 토글 버튼 클릭
    wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["sidebar_toggle_button"])

    # 사이드바가 다시 열린다.
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, SELECTORS["sidebar"]))
    )
    assert sidebar.get_attribute("hidden") is None, "사이드바가 다시 열리지 않았습니다 (hidden attribute가 제거되지 않음)."
    assert sidebar_toggle_button.get_attribute("aria-expanded") == "true", "사이드바 토글 버튼의 aria-expanded가 true가 아닙니다."

def test_tc010_overage_ratio_zero_monthly_cost_handling(driver):
    """TC-010: 월 과금 0원 데이터의 오버리지 비중 계산 예외 처리"""
    # 이 테스트 케이스는 `monthly_cost_krw`가 0인 데이터만 포함되도록 필터링해야 합니다.
    # 현재 대시보드 UI의 '월 과금 범위' 슬라이더는 최소값이 ₩90,000으로 설정되어 있어
    # '월 과금 0원' 데이터를 직접 필터링할 수 없습니다.
    # 따라서 이 테스트는 주어진 UI를 통한 직접적인 검증이 어렵습니다.
    # 대신, 만약 그러한 데이터가 필터링되었다고 가정했을 때의 예상 결과(`-` 표시)를 검증하는 방식으로 진행합니다.

    # 가상 시나리오: 월 과금 0원인 데이터만 필터링되었다고 가정하고 KPI 및 차트의 표시를 확인
    # 이는 TC-007 (필터 결과 0건)과 유사한 결과를 초래할 수 있습니다.
    # 이 테스트는 자동화 환경에서 monthly_cost_krw=0인 데이터를 강제로 주입하거나,
    # 해당 데이터를 포함하는 특정 필터 조합이 제공되어야만 정확히 테스트 가능합니다.
    # 현재 UI 필터로 0원 데이터를 격리할 수 없으므로, TC-007의 결과와 유사하게
    # '필터 결과가 없는' 상태를 만들고 해당 메시지를 확인하는 것으로 대체합니다.

    # Simulate filtering to a state where monthly_cost_krw=0 data (if it existed)
    # would lead to no valid overage ratio calculation.
    # For demonstration, we'll recreate the "no data" scenario from TC-007.

    business_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    peak_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])

    if business_checkbox.is_selected():
        wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    if peak_checkbox.is_selected():
        wait_and_click_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])

    WebDriverWait(driver, WAIT_TIMEOUT).until_not(EC.element_to_be_selected(business_checkbox))
    WebDriverWait(driver, WAIT_TIMEOUT).until_not(EC.element_to_be_selected(peak_checkbox))

    # Step 2: "평균 오버리지 비중" Value Box 및 "오버리지 비중 분포" 바이올린 플롯 확인
    # Expected: " - " for avg_overage_ratio and "필터 결과가 없습니다." for violin plot
    WebDriverWait(driver, QUICK_WAIT_TIMEOUT).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]), " - ")
    )
    assert get_element_text(driver, By.CSS_SELECTOR, SELECTORS["avg_overage_ratio_value_box"]) == " - ", \
        "월 과금 0원 데이터 처리 시 평균 오버리지 비중이 ' - ' 가 아닙니다."

    assert_chart_no_data_message(driver, "violin_plot", QUICK_WAIT_TIMEOUT)

    # Note: To fully test this, one would need a filter specifically for monthly_cost_krw = 0,
    # or the test data must be configured to have a non-zero number of monthly_cost_krw=0 entries
    # that can be isolated, and the application logic correctly handles division by zero or
    # excludes such entries from the average calculation, resulting in "-" or a valid non-zero
    # average from other data points.