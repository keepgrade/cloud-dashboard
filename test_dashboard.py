import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# 테스트할 페이지 정보
BASE_URL = "https://huhhuhman.shinyapps.io/cloud-dashboard/"
WAIT_TIMEOUT = 15  # Timeout 설정 (15초)

# CSS Selector 맵핑
SELECTORS = {
    "page_title": "h1.navbar-brand",
    "monthly_cost_slider": "#monthly_cost + div .irs-from",  # 슬라이더의 "from" 값
    "traffic_window_business_checkbox": "input[name='traffic_window'][value='BUSINESS']",
    "traffic_window_peak_checkbox": "input[name='traffic_window'][value='PEAK']",
    "filter_reset_button": "#reset",
    "total_rows_value_box": "#total_rows",
    "scatterplot": "#scatterplot",
}

# Chrome WebDriver 설정 (Fixture)
@pytest.fixture
def driver():
    """Chrome WebDriver를 설정하고 테스트가 끝나면 종료."""
    driver = webdriver.Chrome()
    driver.set_window_size(1920, 1080)  # 브라우저 크기 설정
    driver.get(BASE_URL)
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )  # 페이지가 완전히 로드될 때까지 대기
    yield driver
    driver.quit()

# 공통 함수: 특정 엘리먼트를 기다렸다가 반환
def wait_and_find_element(driver, by, selector, timeout=WAIT_TIMEOUT):
    """Wait for an element to appear and return it."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    except:
        raise AssertionError(f"Element not found: {selector}")

# 공통 함수: 특정 엘리먼트의 텍스트를 반환
def get_element_text(driver, by, selector, timeout=WAIT_TIMEOUT):
    """Fetch text from an element after waiting for it to appear."""
    element = wait_and_find_element(driver, by, selector, timeout)
    return element.text

### 테스트 케이스 1: 페이지 초기 로드 확인 및 UI 검증 ###
def test_tc001_initial_page_loading_and_ui_state(driver):
    """TC-001: 페이지 로드 후 기본 UI 상태 확인."""
    page_title = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["page_title"])
    assert page_title == "가비아 클라우드 | 서비스 지표 대시보드 | Ted(신태선)-클라우드기획팀", "Page title mismatch!"

### 테스트 케이스 2: 슬라이더 값을 잘못된 값으로 설정하여 실패 ###
def test_tc002_monthly_cost_slider_data_update(driver):
    """TC-002: Intentionally fail by expecting an incorrect slider value."""
    actual_value = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider"])
    expected_value = "₩999,999"  # 잘못된 값을 설정 (테스트 실패를 유도)
    assert actual_value == expected_value, f"Expected {expected_value}, but got {actual_value}"

### 테스트 케이스 3: 트래픽 구간 체크박스 확인 ###
def test_tc003_traffic_window_checkbox(driver):
    """TC-003: 트래픽 구간 체크박스 기본 선택 상태 확인."""
    business_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    peak_checkbox = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_peak_checkbox"])
    assert business_checkbox.is_selected(), "Business checkbox is not selected!"
    assert peak_checkbox.is_selected(), "Peak checkbox is not selected!"

### 테스트 케이스 4: 필터 초기화 버튼 동작 확인 ###
def test_tc004_filter_reset_button(driver):
    """TC-004: 필터 초기화 버튼 눌렀을 때 슬라이더 초기화 확인."""
    reset_button = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["filter_reset_button"])
    reset_button.click()

    slider_value = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["monthly_cost_slider"])
    assert slider_value == "₩90,000", f"Reset button did not restore slider to ₩90,000. Got {slider_value}."

### 테스트 케이스 5: 산점도 차트 표시 확인 ###
def test_tc005_scatterplot_visible(driver):
    """TC-005: 산점도가 제대로 표시되는지 확인."""
    scatterplot = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["scatterplot"])
    assert scatterplot.is_displayed(), "Scatterplot is not visible!"

### 테스트 케이스 6: 바이올린 플롯 표시 확인 ###
def test_tc006_violin_plot_visible(driver):
    """TC-006: 바이올린 플롯이 표시되는지 확인."""
    violin_plot = wait_and_find_element(driver, By.CSS_SELECTOR, "#overage_ratio_dist")
    assert violin_plot.is_displayed(), "Violin plot is not visible!"

### 테스트 케이스 7: KPI value box 확인 ###
def test_tc007_kpi_value_box(driver):
    """TC-007: KPI value box가 올바른 텍스트를 표시하는지 확인."""
    total_rows = get_element_text(driver, By.CSS_SELECTOR, SELECTORS["total_rows_value_box"])
    assert total_rows and re.fullmatch(r"\d+", total_rows), "Invalid KPI value (total rows)."

### 테스트 케이스 8: 사이드바 보이는지 확인 ###
def test_tc008_sidebar_is_visible(driver):
    """TC-008: 사이드바가 잘 보이는지 확인."""
    sidebar = wait_and_find_element(driver, By.CSS_SELECTOR, SELECTORS["traffic_window_business_checkbox"])
    assert sidebar is not None, "Sidebar is not visible!"

### 테스트 케이스 9: 전체화면 버튼 확인 ###
def test_tc009_fullscreen_button_exists(driver):
    """TC-009: 전체화면 버튼이 있는지 확인."""
    fullscreen_button = wait_and_find_element(driver, By.CSS_SELECTOR, "button.fullscreen-button-selector")
    assert fullscreen_button.is_displayed(), "Fullscreen button is not displayed!"

### 테스트 케이스 10: 성공하는 더미 테스트 ###
def test_tc010_dummy_test_success(driver):
    """TC-010: 성공하는 더미 테스트."""
    pass  # 항상 성공하는 테스트