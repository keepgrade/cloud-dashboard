import faicons as fa

import matplotlib.pyplot as plt
import seaborn as sns

from shiny import reactive, render
from shiny.express import input, ui

from shared import app_dir, tips


# -----------------------------
# Static
# -----------------------------
sns.set_theme(style="whitegrid")

cost_rng = (
    int(tips["monthly_cost_krw"].min()),
    int(tips["monthly_cost_krw"].max()),
)

ui.page_opts(title="가비아 클라우드 | 서비스 지표 대시보드 | Ted(신태선)-클라우드기획팀 ", fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_slider(
        "monthly_cost",
        "월 과금 범위(원)",
        min=cost_rng[0],
        max=cost_rng[1],
        value=cost_rng,
        pre="₩",
    )

    ui.input_checkbox_group(
        "traffic_window",
        "트래픽 구간",
        {"BUSINESS": "업무시간", "PEAK": "야간/피크"},
        selected=["BUSINESS", "PEAK"],
        inline=True,
    )

    ui.input_action_button("reset", "필터 초기화")


ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
}


# -----------------------------
# Reactive data
# -----------------------------
@reactive.calc
def tips_data():
    rng = input.monthly_cost()
    idx1 = tips["monthly_cost_krw"].between(rng[0], rng[1])
    idx2 = tips["traffic_window"].isin(input.traffic_window())
    d = tips.loc[idx1 & idx2].copy()

    denom = d["monthly_cost_krw"].replace(0, None)
    d["overage_ratio"] = d["overage_cost_krw"] / denom
    return d


# -----------------------------
# Summary boxes (render.express는 return 금지)
# -----------------------------
with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["user"]):
        "조회 대상 건수(샘플)"

        @render.express
        def total_rows():
            tips_data().shape[0]

    with ui.value_box(showcase=ICONS["wallet"]):
        "평균 오버리지 비중(샘플)"

        @render.express
        def avg_overage_ratio():
            d = tips_data()
            if d.shape[0] == 0:
                "-"
            else:
                f"{d['overage_ratio'].dropna().mean():.1%}"

    with ui.value_box(showcase=ICONS["currency-dollar"]):
        "평균 월 과금(샘플)"

        @render.express
        def avg_monthly_cost():
            d = tips_data()
            if d.shape[0] == 0:
                "-"
            else:
                f"₩{d['monthly_cost_krw'].mean():,.0f}"


# -----------------------------
# Main cards
# -----------------------------
with ui.layout_columns(col_widths=[6, 6, 12]):

    with ui.card(full_screen=True):
        ui.card_header("원천 데이터 미리보기 (목업)")

        @render.data_frame
        def table():
            return render.DataGrid(tips_data().head(200))

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "월 과금 vs 오버리지 (상관관계)"
            with ui.popover(title="색상 기준", placement="top"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "scatter_color",
                    None,
                    {
                        "none": "없음",
                        "customer_segment": "고객 세그먼트",
                        "promo_applied": "프로모션 적용",
                        "weekday": "요일",
                        "traffic_window": "트래픽 구간",
                    },
                    selected="none",
                    inline=True,
                )

        # Express에서는 ui.output_plot() 같은 placeholder를 쓰지 말고
        # @render.plot을 "이 위치에" 두면 해당 위치에 출력됩니다.
        @render.plot
        def scatterplot():
            d = tips_data()

            fig, ax = plt.subplots(figsize=(7.2, 4.2))
            if d.shape[0] == 0:
                ax.text(0.5, 0.5, "필터 결과가 없습니다.", ha="center", va="center")
                ax.set_axis_off()
                return fig

            color = input.scatter_color()
            if color == "none":
                sns.scatterplot(
                    data=d,
                    x="monthly_cost_krw",
                    y="overage_cost_krw",
                    ax=ax,
                    s=35,
                    alpha=0.75,
                    edgecolor="none",
                )
            else:
                sns.scatterplot(
                    data=d,
                    x="monthly_cost_krw",
                    y="overage_cost_krw",
                    hue=color,
                    ax=ax,
                    s=35,
                    alpha=0.75,
                    edgecolor="none",
                )
                ax.legend(loc="best", title=color)

            ax.set_xlabel("monthly_cost_krw")
            ax.set_ylabel("overage_cost_krw")
            fig.tight_layout()
            return fig

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "오버리지 비중 분포 (그룹별)"
            with ui.popover(title="분석 기준 선택"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "ratio_split_by",
                    "그룹:",
                    {
                        "customer_segment": "고객 세그먼트",
                        "promo_applied": "프로모션 적용",
                        "weekday": "요일",
                        "traffic_window": "트래픽 구간",
                    },
                    selected="weekday",
                    inline=True,
                )

        @render.plot
        def overage_ratio_dist():
            d = tips_data()
            fig, ax = plt.subplots(figsize=(10.5, 4.2))

            if d.shape[0] == 0 or d["overage_ratio"].dropna().shape[0] == 0:
                ax.text(0.5, 0.5, "필터 결과가 없습니다.", ha="center", va="center")
                ax.set_axis_off()
                return fig

            split = input.ratio_split_by()
            dd = d[[split, "overage_ratio"]].dropna()

            # violin이 무거우면 boxplot으로 바꾸면 더 가벼움
            sns.violinplot(
                data=dd,
                x=split,
                y="overage_ratio",
                inner="box",
                cut=0,
                ax=ax,
            )

            ax.set_xlabel(split)
            ax.set_ylabel("overage_ratio")
            fig.tight_layout()
            return fig


ui.include_css(app_dir / "styles.css")


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("monthly_cost", value=cost_rng)
    ui.update_checkbox_group("traffic_window", selected=["BUSINESS", "PEAK"])
