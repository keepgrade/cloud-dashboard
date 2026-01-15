# 정책 정의서 (Policy Definition)

## 1. 문서 개요

| 항목 | 내용 |
| --- | --- |
| **프로젝트명** | 가비아 클라우드 서비스 지표 대시보드 |
| **작성자** | Ted(신태선) - 클라우드기획팀 |
| **작성일** | 2026-01-14 |
| **버전** | v1.0 |

---

## 2. 필터링 정책

| 정책 ID | 정책명 | 정책 상세 | 비고 |
| --- | --- | --- | --- |
| POL-F001 | 월 과금 범위 필터 | `monthly_cost_krw BETWEEN (min, max)` 조건으로 필터링. **경계값 포함** | 슬라이더 사용 |
| POL-F002 | 트래픽 구간 필터 | `traffic_window IN (selected_values)` 조건으로 필터링 | 체크박스 다중선택 |
| POL-F003 | 필터 결합 방식 | 모든 필터 조건은 **AND** 조건으로 결합 | `idx1 & idx2` |
| POL-F004 | 필터 기본값 - 슬라이더 | 데이터의 전체 범위 `(min, max)` | 최초 로드 시 |
| POL-F005 | 필터 기본값 - 체크박스 | `["BUSINESS", "PEAK"]` 모두 선택 | 최초 로드 시 |
| POL-F006 | 필터 초기화 | 버튼 클릭 시 모든 필터를 기본값으로 복원 | reset 버튼 |

---

## 3. 데이터 계산 정책

| 정책 ID | 항목 | 계산 공식 | 예외 처리 |
| --- | --- | --- | --- |
| POL-D001 | 오버리지 비중 | `overage_ratio = overage_cost_krw ÷ monthly_cost_krw` | 분모가 0이면 **NULL** 처리 |
| POL-D002 | 조회 건수 | `len(filtered_dataframe)` | 0 포함 표시 |
| POL-D003 | 평균 오버리지 비중 | `mean(overage_ratio)` | NULL 값 제외 후 계산, 유효값 없으면 "-" |
| POL-D004 | 평균 월 과금 | `mean(monthly_cost_krw)` | 유효값 없으면 "-" |

---

## 4. 표시 형식 정책

| 정책 ID | 항목 | 형식 | 예시 |
| --- | --- | --- | --- |
| POL-V001 | 월 과금 금액 | 원화 기호 + 천단위 콤마 + 정수 | `₩1,234,567` |
| POL-V002 | 오버리지 비중 | 백분율 + 소수점 1자리 | `12.5%` |
| POL-V003 | 조회 건수 | 정수 | `1,234` |
| POL-V004 | 슬라이더 접두어 | 원화 기호 | `₩` |
| POL-V005 | 빈 데이터 지표 | 하이픈 | `-` |
| POL-V006 | 빈 데이터 차트 | 안내 메시지 | `필터 결과가 없습니다.` |

---

## 5. 차트 정책

### 5.1 공통 정책

| 정책 ID | 항목 | 설정값 |
| --- | --- | --- |
| POL-C001 | 차트 테마 | `seaborn whitegrid` |
| POL-C002 | 빈 데이터 처리 | 메시지 중앙 표시 + 축 숨김 (`set_axis_off`) |
| POL-C003 | 레이아웃 | `fig.tight_layout()` 적용 |

### 5.2 데이터 테이블 정책

| 정책 ID | 항목 | 설정값 |
| --- | --- | --- |
| POL-C010 | 최대 표시 행 수 | **200행** (`.head(200)`) |
| POL-C011 | 컴포넌트 타입 | `DataGrid` |

### 5.3 산점도 정책

| 정책 ID | 항목 | 설정값 |
| --- | --- | --- |
| POL-C020 | 차트 크기 | `figsize=(7.2, 4.2)` |
| POL-C021 | 점 크기 | `s=35` |
| POL-C022 | 점 투명도 | `alpha=0.75` |
| POL-C023 | 점 테두리 | `edgecolor="none"` (없음) |
| POL-C024 | X축 | `monthly_cost_krw` |
| POL-C025 | Y축 | `overage_cost_krw` |
| POL-C026 | 기본 색상 모드 | `none` (단색) |
| POL-C027 | 범례 위치 | `loc="best"` (자동) |

### 5.4 산점도 색상 옵션 정책

| 정책 ID | 옵션값 | 설명 | hue 파라미터 |
| --- | --- | --- | --- |
| POL-C030 | `none` | 색상 구분 없음 (기본값) | 미적용 |
| POL-C031 | `customer_segment` | 고객 세그먼트별 색상 | `hue="customer_segment"` |
| POL-C032 | `promo_applied` | 프로모션 적용 여부별 색상 | `hue="promo_applied"` |
| POL-C033 | `weekday` | 요일별 색상 | `hue="weekday"` |
| POL-C034 | `traffic_window` | 트래픽 구간별 색상 | `hue="traffic_window"` |

### 5.5 바이올린 플롯 정책

| 정책 ID | 항목 | 설정값 |
| --- | --- | --- |
| POL-C040 | 차트 크기 | `figsize=(10.5, 4.2)` |
| POL-C041 | 내부 표시 | `inner="box"` (박스플롯) |
| POL-C042 | 꼬리 절단 | `cut=0` (데이터 범위만 표시) |
| POL-C043 | Y축 | `overage_ratio` |
| POL-C044 | 기본 그룹 기준 | `weekday` (요일) |

### 5.6 바이올린 플롯 그룹 옵션 정책

| 정책 ID | 옵션값 | 설명 |
| --- | --- | --- |
| POL-C050 | `customer_segment` | 고객 세그먼트별 분포 |
| POL-C051 | `promo_applied` | 프로모션 적용 여부별 분포 |
| POL-C052 | `weekday` | 요일별 분포 (기본값) |
| POL-C053 | `traffic_window` | 트래픽 구간별 분포 |

---

## 6. UI/UX 정책

| 정책 ID | 구성요소 | 정책 상세 | 설정값 |
| --- | --- | --- | --- |
| POL-U001 | 페이지 타이틀 | 브라우저 탭에 표시되는 제목 | `가비아 클라우드 \| 서비스 지표 대시보드 \| Ted(신태선)-클라우드기획팀` |
| POL-U002 | 페이지 레이아웃 | 콘텐츠 영역 채우기 | `fillable=True` |
| POL-U003 | 사이드바 기본 상태 | 디바이스별 기본 열림/닫힘 | `open="desktop"` (데스크톱만 열림) |
| POL-U004 | 상단 카드 레이아웃 | Value Box 영역 | `fill=False` |
| POL-U005 | 중단 카드 레이아웃 | 테이블 + 산점도 2열 | `col_widths=[6, 6]` |
| POL-U006 | 하단 카드 레이아웃 | 바이올린 플롯 전체 너비 | `col_widths=[12]` |
| POL-U007 | 카드 전체화면 | 모든 메인 카드에 전체화면 기능 | `full_screen=True` |
| POL-U008 | Popover 위치 | 산점도 옵션 팝오버 | `placement="top"` |
| POL-U009 | 라디오 버튼 배치 | 옵션 가로 배열 | `inline=True` |
| POL-U010 | 외부 스타일 | CSS 파일 포함 | `styles.css` |

---

## 7. 아이콘 정책

| 정책 ID | 용도 | 아이콘 | FontAwesome 코드 |
| --- | --- | --- | --- |
| POL-I001 | 조회 건수 Value Box | 👤 사용자 | `fa.icon_svg("user", "regular")` |
| POL-I002 | 오버리지 비중 Value Box | 💰 지갑 | `fa.icon_svg("wallet")` |
| POL-I003 | 평균 월과금 Value Box | 💵 달러 | `fa.icon_svg("dollar-sign")` |
| POL-I004 | 차트 옵션 Popover | ⋯ 더보기 | `fa.icon_svg("ellipsis")` |

---

## 8. 반응형 동작 정책

| 정책 ID | 트리거 | 동작 | 영향 범위 |
| --- | --- | --- | --- |
| POL-R001 | `monthly_cost` 변경 | `tips_data()` 재계산 | Value Box 3개 + 차트 3개 |
| POL-R002 | `traffic_window` 변경 | `tips_data()` 재계산 | Value Box 3개 + 차트 3개 |
| POL-R003 | `reset` 클릭 | 필터 기본값 복원 → `tips_data()` 재계산 | 필터 UI + Value Box 3개 + 차트 3개 |
| POL-R004 | `scatter_color` 변경 | `scatterplot()` 재실행 | 산점도 차트만 |
| POL-R005 | `ratio_split_by` 변경 | `overage_ratio_dist()` 재실행 | 바이올린 플롯만 |

---

## 9. 예외 처리 정책

| 정책 ID | 예외 상황 | 처리 방식 | 사용자 표시 |
| --- | --- | --- | --- |
| POL-E001 | 필터 결과 0건 - Value Box | 계산 스킵 | `"-"` 표시 |
| POL-E002 | 필터 결과 0건 - 차트 | 빈 Figure 생성 | `"필터 결과가 없습니다."` 중앙 표시 |
| POL-E003 | 월 과금 0원 (나누기 오류) | `replace(0, None)` | 해당 행 비중 계산에서 제외 |
| POL-E004 | 오버리지 비중 유효값 없음 | `dropna()` 후 확인 | 바이올린 플롯에 빈 메시지 |

---

## 10. 트래픽 구간 정의

| 구간 코드 | 표시명 | 설명 |
| --- | --- | --- |
| `BUSINESS` | 업무시간 | 주간 업무 시간대 트래픽 |
| `PEAK` | 야간/피크 | 야간 또는 피크 시간대 트래픽 |

---

## 11. 데이터 필드 정책

| 필드명 | 타입 | 용도 | 허용값 |
| --- | --- | --- | --- |
| `monthly_cost_krw` | Integer | 월 과금 | 0 이상 정수 |
| `overage_cost_krw` | Integer | 오버리지 비용 | 0 이상 정수 |
| `traffic_window` | String | 트래픽 구간 | `BUSINESS`, `PEAK` |
| `customer_segment` | String | 고객 세그먼트 | 자유 문자열 |
| `promo_applied` | Boolean | 프로모션 적용 | `True`, `False` |
| `weekday` | String | 요일 | `Mon`~`Sun` |

---

## 12. 정책 우선순위

| 우선순위 | 정책 분류 | 설명 |
| --- | --- | --- |
| 1 (최상) | 예외 처리 정책 | 오류 방지 및 안정성 확보 |
| 2 | 데이터 계산 정책 | 정확한 지표 산출 |
| 3 | 필터링 정책 | 사용자 의도 반영 |
| 4 | 표시 형식 정책 | 가독성 확보 |
| 5 | UI/UX 정책 | 사용 편의성 |

---

## 13. 변경 이력

| 버전 | 일자 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v1.0 | 2026-01-14 | Ted(신태선) | 최초 작성 |

---