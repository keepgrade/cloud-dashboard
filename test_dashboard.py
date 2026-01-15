import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 테스트할 페이지 정보
BASE_URL = "https://huhhuhman.shinyapps.io/cloud-dashboard/"
WAIT_TIMEOUT = 20

# Chrome WebDriver 설정 (Fixture)
@pytest.fixture
def driver():
    """Chrome WebDriver를 설정하고 테스트가 끝나면 종료."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=options)
    driver.get(BASE_URL)
    
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(3)  # Shiny 앱 렌더링 대기
    
    yield driver
    driver.quit()


def wait_and_find_element(driver, by, selector, timeout=WAIT_TIMEOUT):
    """Wait for an element to appear and return it."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )


### TC-001: 페이지 타이틀 확인 ✅ ###
def test_tc001_initial_page_loading_and_ui_state(driver):
    """TC-001: 페이지 로드 후 기본 UI 상태 확인."""
    page_title_element = wait_and_find_element(
        driver, By.XPATH, "//h1[contains(@class, 'navbar-brand')]"
    )
    page_title = page_title_element.text.strip()
    assert "가비아 클라우드" in page_title


### TC-002: 실패 테스트 ❌ ###
def test_tc002_monthly_cost_slider_intentional_fail(driver):
    """TC-002: 실패하는 테스트."""
    slider_input = wait_and_find_element(driver, By.ID, "monthly_cost")
    actual_min_value = slider_input.get_attribute("data-from")
    expected_value = "999999"  # 실제: 90000 →  실패
    assert actual_min_value == expected_value, \
        f"❌ 실패: Expected {expected_value}, but got {actual_min_value}"


### TC-003: 트래픽 체크박스 확인 ✅ ###
def test_tc003_traffic_window_checkbox(driver):
    """TC-003: 트래픽 구간 체크박스 기본 선택 상태 확인."""
    business_checkbox = wait_and_find_element(
        driver, By.XPATH, "//input[@name='traffic_window' and @value='BUSINESS']"
    )
    peak_checkbox = wait_and_find_element(
        driver, By.XPATH, "//input[@name='traffic_window' and @value='PEAK']"
    )
    assert business_checkbox.is_selected()
    assert peak_checkbox.is_selected()


### TC-004: 필터 초기화 버튼 확인 ✅ ###
def test_tc004_filter_reset_button_exists(driver):
    """TC-004: 필터 초기화 버튼 존재 확인."""
    reset_button = wait_and_find_element(driver, By.ID, "reset")
    assert reset_button.is_enabled()
    assert "필터 초기화" in reset_button.text


### TC-005: 산점도 컨테이너 확인 ✅ ###
def test_tc005_scatterplot_container_visible(driver):
    """TC-005: 산점도 컨테이너 존재 확인."""
    scatterplot = wait_and_find_element(driver, By.ID, "scatterplot")
    assert "shiny-plot-output" in scatterplot.get_attribute("class")


### TC-006: 바이올린 플롯 확인 ✅ ###
def test_tc006_violin_plot_container_visible(driver):
    """TC-006: 바이올린 플롯 컨테이너 존재 확인."""
    violin_plot = wait_and_find_element(driver, By.ID, "overage_ratio_dist")
    assert "shiny-plot-output" in violin_plot.get_attribute("class")


### TC-007: KPI Value Box 확인 ✅ ###
def test_tc007_kpi_value_boxes_exist(driver):
    """TC-007: KPI value box 요소 존재 확인."""
    total_rows = wait_and_find_element(driver, By.ID, "total_rows")
    avg_overage = wait_and_find_element(driver, By.ID, "avg_overage_ratio")
    avg_cost = wait_and_find_element(driver, By.ID, "avg_monthly_cost")
    assert total_rows and avg_overage and avg_cost


### TC-008: 사이드바 요소 확인 ✅ ###
def test_tc008_sidebar_elements_exist(driver):
    """TC-008: 사이드바 필터 요소 존재 확인."""
    slider_label = wait_and_find_element(
        driver, By.XPATH, "//label[@id='monthly_cost-label']"
    )
    assert "월 과금" in slider_label.text


### TC-009: 카드 헤더 확인 ✅ ###
def test_tc009_card_headers_exist(driver):
    """TC-009: 차트 카드 헤더 존재 확인."""
    card_headers = driver.find_elements(
        By.XPATH, "//div[contains(@class, 'card-header')]"
    )
    assert len(card_headers) >= 2


### TC-010: Value Box 타이틀 확인 ✅ ###
def test_tc010_value_box_titles_exist(driver):
    """TC-010: Value Box 타이틀 존재 확인."""
    value_box_titles = driver.find_elements(
        By.XPATH, "//div[contains(@class, 'value-box-title')]//p"
    )
    assert len(value_box_titles) >= 3
    title_combined = " ".join([t.text for t in value_box_titles])
    assert "조회 대상" in title_combined
