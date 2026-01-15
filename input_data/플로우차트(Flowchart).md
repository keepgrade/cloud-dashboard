# 플로우차트(Flowchart)

## 1. 문서 개요

| 항목 | 내용 |
| --- | --- |
| **프로젝트명** | 가비아 클라우드 서비스 지표 대시보드 |
| **작성자** | Ted(신태선) - 클라우드기획팀 |
| **작성일** | 2026-01-14 |
| **버전** | v1.0 |

---

## 2. 메인 플로우 (Mermaid)

```mermaid
flowchart TD
    A[🌐 대시보드 접속] --> B[📂 tips 데이터 로드]
    B --> C[🎚️ 필터 기본값 설정]
    C --> D[📊 초기 렌더링]
    D --> E{👆 사용자 액션}

    E -->|슬라이더 조작| F[월 과금 범위 변경]
    E -->|체크박스 토글| G[트래픽 구간 변경]
    E -->|초기화 클릭| H[필터 리셋]
    E -->|색상 옵션| I[산점도만 리렌더링]
    E -->|그룹 옵션| J[바이올린만 리렌더링]

    F --> K[⚡ tips_data 재계산]
    G --> K
    H --> K

    K --> L{데이터 존재?}
    L -->|Yes| M[✅ 전체 컴포넌트 갱신]
    L -->|No| N[⚠️ 빈 데이터 메시지]

    M --> E
    N --> E
    I --> E
    J --> E

```

---

## 3. 데이터 처리 플로우 (tips_data 함수)

```mermaid
flowchart TD
    A[tips_data 호출] --> B[input.monthly_cost 읽기]
    B --> C[input.traffic_window 읽기]
    C --> D["필터1: monthly_cost BETWEEN (min, max)"]
    D --> E["필터2: traffic_window IN (selected)"]
    E --> F[필터 결합 - AND 조건]
    F --> G[overage_ratio 계산]
    G --> H{monthly_cost == 0?}
    H -->|Yes| I[NULL 처리]
    H -->|No| J[비중 값 저장]
    I --> K[필터링된 데이터 반환]
    J --> K

```

---

## 4. 산점도 렌더링 플로우

```mermaid
flowchart TD
    A[scatterplot 호출] --> B[tips_data 가져오기]
    B --> C{데이터 == 0건?}
    C -->|Yes| D["'필터 결과가 없습니다.' 표시"]
    C -->|No| E[scatter_color 읽기]
    E --> F{color == none?}
    F -->|Yes| G[단색 산점도]
    F -->|No| H[색상 구분 산점도 + 범례]
    D --> I[Figure 반환]
    G --> I
    H --> I

```

---

## 5. 바이올린 플롯 렌더링 플로우

```mermaid
flowchart TD
    A[overage_ratio_dist 호출] --> B[tips_data 가져오기]
    B --> C{데이터 == 0건?}
    C -->|Yes| D[빈 메시지 표시]
    C -->|No| E{overage_ratio 유효값?}
    E -->|No| D
    E -->|Yes| F[ratio_split_by 읽기]
    F --> G[그룹별 바이올린 플롯 생성]
    D --> H[Figure 반환]
    G --> H

```

---

## 6. 컴포넌트 의존성

```mermaid
flowchart BT
    subgraph INPUT["📥 입력"]
        I1[monthly_cost]
        I2[traffic_window]
        I3[reset]
        I4[scatter_color]
        I5[ratio_split_by]
    end

    subgraph CORE["⚡ 핵심"]
        R1[tips_data]
    end

    subgraph OUTPUT["📤 출력"]
        O1[total_rows]
        O2[avg_overage_ratio]
        O3[avg_monthly_cost]
        O4[table]
        O5[scatterplot]
        O6[overage_ratio_dist]
    end

    I1 & I2 --> R1
    I3 -.->|reset| I1 & I2
    R1 --> O1 & O2 & O3 & O4 & O5 & O6
    I4 --> O5
    I5 --> O6

```

---

## 7. 시퀀스 다이어그램

```mermaid
sequenceDiagram
    actor User as 사용자
    participant UI as UI
    participant Data as tips_data
    participant Output as 출력

    User->>UI: 필터 변경
    UI->>Data: 재계산 트리거
    Data->>Data: 필터 적용 + 비중 계산
    Data-->>Output: 데이터 전달
    Output-->>User: 화면 갱신

```

---

## 8. 이벤트-액션 매핑

| 이벤트 | 트리거 | 영향 범위 |
| --- | --- | --- |
| 슬라이더 변경 | `input.monthly_cost` | 전체 (Value Box 3 + 차트 3) |
| 체크박스 변경 | `input.traffic_window` | 전체 (Value Box 3 + 차트 3) |
| 초기화 클릭 | `input.reset` | 필터 → 전체 |
| 산점도 색상 변경 | `input.scatter_color` | 산점도만 |
| 바이올린 그룹 변경 | `input.ratio_split_by` | 바이올린만 |

---

## 9. 변경 이력

| 버전 | 일자 | 작성자 | 변경 내용 |
| --- | --- | --- | --- |
| v1.0 | 2026-01-14 | Ted(신태선) | 최초 작성 |

---