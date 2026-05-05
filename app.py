# -*- coding: utf-8 -*-
"""
씨아이텐트 FRAME WORKS
천막·철구조물 정밀자재 산출 및 도면 시스템
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.font_manager as fm
import plotly.graph_objects as go
import io
import os
from datetime import datetime

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="씨아이텐트 FRAME WORKS",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 한글 폰트 설정 (어떤 환경에서도 한글이 깨지지 않도록)
# ============================================================
def setup_korean_font():
    """한글 폰트를 설정합니다.
    1순위: koreanize-matplotlib (pip 패키지, OS 무관)
    2순위: 시스템에 설치된 NanumGothic / 맑은고딕 / Apple SD Gothic
    """
    try:
        import koreanize_matplotlib  # noqa: F401
        return
    except ImportError:
        pass
    font_candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    ]
    for font_path in font_candidates:
        if os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
            font_name = fm.FontProperties(fname=font_path).get_name()
            plt.rcParams["font.family"] = font_name
            break
    else:
        plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

setup_korean_font()


# ============================================================
# 다운로드 파일명 생성 헬퍼 (업체명 + 저장파일명 조합)
# ============================================================
def make_filename(company, save_name, default_prefix, ext):
    parts = []
    if company and company.strip():
        parts.append(company.strip())
    if save_name and save_name.strip():
        parts.append(save_name.strip())
    if not parts:
        parts.append(default_prefix)
    safe = "_".join(parts).replace(" ", "_").replace("/", "-")
    return f"{safe}.{ext}"


# ============================================================
# 커스텀 CSS (다크 테마 + 빨간 포인트)
# ============================================================
st.markdown("""
<style>
    /* 전체 다크 배경 */
    .stApp {
        background-color: #0e1117;
    }
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #0a0d12;
        border-right: 1px solid #1f2937;
    }
    /* 카드형 컨테이너 느낌 */
    .frame-card {
        background-color: #131720;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 16px;
    }
    /* 빨간 버튼 */
    .stButton > button[kind="primary"] {
        background-color: #dc2626;
        color: white;
        border: none;
        font-weight: 600;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #b91c1c;
    }
    /* 헤더 강조 */
    h1, h2, h3 {
        color: #f3f4f6;
    }
    /* 메뉴 라디오 라벨 */
    [data-testid="stSidebar"] label {
        color: #d1d5db;
    }
    /* 성공 메시지 박스 */
    div[data-testid="stAlertContainer"] {
        background-color: #052e1f;
        border: 1px solid #10b981;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 사이드바: 브랜드 + 메뉴 + 인증
# ============================================================
with st.sidebar:
    st.markdown("### CI TENT")
    st.markdown("**FRAME WORKS**")
    st.caption("씨아이텐트 통합 자재 산출 및 도면 시스템")
    st.divider()

    st.markdown("**메뉴 선택**")
    menu = st.radio(
        "menu",
        [
            "1. 맞춤형 트러스 생성기",
            "2. 벽사다리 통합 산출 시스템",
            "3. 프리미엄 평면도 및 원단 야드",
            "4. 현장 맞춤형 대각 벽사다리",
            "5. 전문 3D 천막 창고 시뮬레이터",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**고객연락 인증**")
    st.caption("PDF·엑셀 다운로드 비밀번호(공통): 8637")
    pwd = st.text_input("비번", type="password", placeholder="비번 입력")
    memo = st.text_area("후기", placeholder="", height=80)
    if st.button("확인", type="primary", use_container_width=True):
        if pwd == "8637":
            st.session_state["authed"] = True
            st.success("인증 완료")
        else:
            st.error("비밀번호가 일치하지 않습니다.")

    st.divider()
    st.caption(
        "※ 개인정보 수집 안내: 비번/후기는 비밀번호 안내 및 접속확인(접속여부) "
        "목적으로만 수집되며, 목적 달성 후 안전하게 관리됩니다. 무분별한 도용을 "
        "막기 위해 사용자 인증을 진행하고 있습니다. 전문가용 도구이므로 실제 "
        "현업 종사자분들께만 비밀번호를 안내해 드립니다."
    )
    st.caption("특허 출원번호: 10-2026-0076694")
    st.divider()
    st.markdown("**[고객지원 및 기술문의]**")
    st.caption("제조원: 씨아이텐트(CI TENT)")
    st.caption("대표: 최희준")
    st.caption("문의: 1644-XXXX")  # 실제 번호로 교체
    if st.button("관리자 코드", use_container_width=True):
        st.toast("관리자 모드는 별도 인증이 필요합니다.")


# ============================================================
# 공통 헤더
# ============================================================
def render_header():
    col1, col2 = st.columns([1, 6])
    with col2:
        st.markdown("# FRAME WORKS")
        st.caption("천막·철구조물 정밀자재산출 솔루션  |  씨아이텐트")


# ============================================================
# 모듈 1: 맞춤형 트러스 생성기
# ============================================================
def calc_truss_geometry(span_cm, divisions, base_height_cm, peak_height_cm, hbeam_cm):
    """트러스 기하 계산.
    span_cm: 전체 스판 (cm)
    divisions: 등분 수
    base_height_cm: 끝단/외경 시작높이 (밑더블 외경 높이)
    peak_height_cm: 최고점 상단 높이
    hbeam_cm: 수평재 바닥기준 높이
    """
    span_mm = span_cm * 10
    seg = span_mm / divisions  # 한 칸 길이
    # 상현 빗변 길이 (한쪽)
    rise_mm = (peak_height_cm - base_height_cm) * 10
    half_span_mm = span_mm / 2
    top_chord_half = float(np.hypot(rise_mm, half_span_mm))
    angle_deg = float(np.degrees(np.arctan2(rise_mm, half_span_mm)))

    # 다대(수직) 각각의 길이 = 그 위치의 상현 높이 - 하현
    x_positions = np.linspace(0, span_mm, divisions + 1)
    top_y = []
    for x in x_positions:
        if x <= half_span_mm:
            y = base_height_cm * 10 + (rise_mm * x / half_span_mm)
        else:
            y = base_height_cm * 10 + (rise_mm * (span_mm - x) / half_span_mm)
        top_y.append(y)
    top_y = np.array(top_y)
    vertical_lengths_mm = top_y  # 하현이 0이라고 가정 (단순화)

    return {
        "span_mm": span_mm,
        "seg_mm": seg,
        "top_chord_half_mm": top_chord_half,
        "angle_deg": angle_deg,
        "x_positions": x_positions,
        "top_y": top_y,
        "vertical_lengths_mm": vertical_lengths_mm,
        "hbeam_mm": hbeam_cm * 10,
    }


def draw_truss(geom, truss_type_name="밑더블 삼각"):
    fig, ax = plt.subplots(figsize=(14, 5), facecolor="white")
    ax.set_facecolor("white")

    span = geom["span_mm"]
    xs = geom["x_positions"]
    top_y = geom["top_y"]
    base_y = top_y.min()  # 하현 위치 (밑더블에서 위쪽 하현)
    bottom_y = 0  # 최하단

    # 하현(아래쪽 - 회색)
    ax.plot([0, span], [bottom_y, bottom_y], color="#374151", linewidth=2.5)
    # 상현(상단 - 회색 굵게)
    ax.plot(xs, top_y, color="#6b7280", linewidth=3)
    # 수평재(보라색) - 밑더블 분리선
    ax.plot([0, span], [base_y, base_y], color="#a855f7", linewidth=2.5)

    # 수직 다대 (파란색)
    for i, x in enumerate(xs):
        ax.plot([x, x], [bottom_y, top_y[i]], color="#1e3a8a", linewidth=2)

    # 살대 (대각 - 노란색 지그재그)
    for i in range(len(xs) - 1):
        x1, x2 = xs[i], xs[i + 1]
        y1, y2 = top_y[i], top_y[i + 1]
        # 위쪽 삼각: 상현과 하현(=base_y) 사이
        if i % 2 == 0:
            ax.plot([x1, x2], [base_y, y2], color="#eab308", linewidth=1.8)
        else:
            ax.plot([x1, x2], [y1, base_y], color="#eab308", linewidth=1.8)
        # 아래쪽 삼각: base_y와 bottom_y 사이
        if i % 2 == 0:
            ax.plot([x1, x2], [bottom_y, base_y], color="#eab308", linewidth=1.5)
        else:
            ax.plot([x1, x2], [base_y, bottom_y], color="#eab308", linewidth=1.5)

    # 치수 라벨 - 하단 칸별 길이
    for i in range(len(xs) - 1):
        mid = (xs[i] + xs[i + 1]) / 2
        ax.text(mid, -180, f"{geom['seg_mm']:.1f}", ha="center", fontsize=8, color="#dc2626")
        ax.text(xs[i], -320, f"{xs[i]:.1f}", ha="center", fontsize=7, color="#dc2626")
    ax.text(xs[-1], -320, f"{xs[-1]:.1f}", ha="center", fontsize=7, color="#dc2626")
    ax.text(span / 2, -480, f"전체 스판 : {span:.1f} mm", ha="center",
            fontsize=11, color="#111827", fontweight="bold")

    # 상단 정보 텍스트
    info = (
        f"트러스 도면 ({truss_type_name})\n"
        f"스판: {span/10:.1f}cm | 등분: {len(xs)-1} (자간: {geom['seg_mm']/10:.1f}cm) | "
        f"밑더블 외경 높이: {base_y/10:.1f}cm\n"
        f"상현바 빗변길이(한쪽 구간): {geom['top_chord_half_mm']:.1f} mm"
    )
    ax.text(span / 2, top_y.max() + 350, info, ha="center", fontsize=11,
            color="#111827", fontweight="bold")

    ax.set_xlim(-200, span + 200)
    ax.set_ylim(-700, top_y.max() + 700)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    return fig


def module_1_truss():
    render_header()
    st.markdown("## 📐 1. 맞춤형 트러스 생성기")

    with st.container(border=True):
        col_in, col_pipe = st.columns(2)
        with col_in:
            st.markdown("### 도면 치수 입력")
            truss_type = st.selectbox(
                "트러스 형태 선택",
                ["[1] 일반 삼각", "[2] 평지붕", "[3] 더블 삼각", "[4] 모노",
                 "[5] 사다리꼴", "[6] 아치형", "[7] 밑더블 삼각", "[8] 서브형"],
                index=6,
            )
            span_cm = st.number_input("1. 전체 스판(cm)", value=1200.0, step=10.0)
            divisions = st.number_input("2. 등분 수 (다대 개수 결정)", value=12, step=1, min_value=2)
            base_h = st.number_input("3. 끝단/외경 시작높이(cm) (서브형 폭/밑더블 분리)", value=80.0, step=5.0)
            hbeam_h = st.number_input("3.1. 수평재 바닥기준 높이(cm) (서브형/수평보)", value=150.0, step=5.0)
            peak_h = st.number_input("4. 최고점 상단 높이(cm)", value=250.0, step=5.0)

        with col_pipe:
            st.markdown("### 파이프 규격 설정")
            d_chord = st.number_input("5. 상/하현부 및 수평 파이프 지름(mm)", value=59.90, step=0.1)
            d_main = st.number_input("6. 다대(일반) 지름(mm)", value=38.10, step=0.1)
            d_ridge = st.number_input("7. 용마루(중앙) 지름(mm)", value=59.90, step=0.1)
            d_diag = st.number_input("8.1. 살대(대각) 지름(mm)", value=31.80, step=0.1)
            d_offset = st.number_input("8.2. 살대 이격 거리(mm)", value=10.00, step=0.5)

        if st.button("도면 및 산출표 생성하기", type="primary"):
            geom = calc_truss_geometry(span_cm, int(divisions), base_h, peak_h, hbeam_h)
            st.session_state["truss_geom"] = geom
            st.session_state["truss_type"] = truss_type

    if "truss_geom" in st.session_state:
        geom = st.session_state["truss_geom"]
        st.success(f"✅ Truss_{st.session_state['truss_type'].split('] ')[-1]}_{int(span_cm)} 산출이 완료되었습니다. 아래 버튼을 눌러 다운로드하세요.")
        fig = draw_truss(geom, st.session_state["truss_type"].split("] ")[-1])
        st.pyplot(fig, use_container_width=True)

        # 산출 표
        with st.expander("📊 자재 산출표 보기"):
            data = {
                "항목": [
                    "전체 스판",
                    "등분 수 (자간)",
                    "상현 빗변길이(한쪽)",
                    "상현 각도",
                    "수직 다대 평균길이",
                    "용마루 높이",
                ],
                "값": [
                    f"{geom['span_mm']:.1f} mm",
                    f"{len(geom['x_positions'])-1} 칸 / {geom['seg_mm']:.1f} mm",
                    f"{geom['top_chord_half_mm']:.1f} mm",
                    f"{geom['angle_deg']:.2f}°",
                    f"{np.mean(geom['vertical_lengths_mm']):.1f} mm",
                    f"{geom['top_y'].max():.1f} mm",
                ],
            }
            st.table(data)

        st.markdown("#### 📥 도면 파일 다운로드 (PDF / 엑셀 / CAD)")

        # 업체명 / 저장 파일명 입력
        col_cn, col_fn = st.columns(2)
        with col_cn:
            company_1 = st.text_input("업체명", placeholder="예: 씨아이텐트", key="company_truss")
        with col_fn:
            savename_1 = st.text_input("저장 파일명", placeholder="예: 물류센터_A동", key="savename_truss")

        c1, c2, c3 = st.columns(3)
        with c1:
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf", bbox_inches="tight")
            st.download_button("📄 PDF 도면 다운로드", buf.getvalue(),
                               file_name=make_filename(company_1, savename_1, f"citent_truss_{int(span_cm)}", "pdf"),
                               mime="application/pdf", use_container_width=True,
                               disabled=not st.session_state.get("authed", False))
        with c2:
            csv_data = f"항목,값\n전체스판(mm),{geom['span_mm']}\n등분수,{len(geom['x_positions'])-1}\n상현빗변(mm),{geom['top_chord_half_mm']:.1f}\n각도(deg),{geom['angle_deg']:.2f}\n"
            st.download_button("📊 엑셀 산출표 다운로드", csv_data.encode("utf-8-sig"),
                               file_name=make_filename(company_1, savename_1, f"citent_truss_{int(span_cm)}", "csv"),
                               mime="text/csv", use_container_width=True,
                               disabled=not st.session_state.get("authed", False))
        with c3:
            buf2 = io.BytesIO()
            fig.savefig(buf2, format="svg", bbox_inches="tight")
            st.download_button("📐 CAD(SVG) 도면 다운로드", buf2.getvalue(),
                               file_name=make_filename(company_1, savename_1, f"citent_truss_{int(span_cm)}", "svg"),
                               mime="image/svg+xml", use_container_width=True,
                               disabled=not st.session_state.get("authed", False))


# ============================================================
# 모듈 2: 벽사다리 통합 산출
# ============================================================
def draw_wall_ladder(total_cm, width_cm, label, color_main, divisions=24):
    fig, ax = plt.subplots(figsize=(14, 1.6), facecolor="white")
    ax.set_facecolor("white")
    total_mm = total_cm * 10
    seg = total_mm / divisions
    h = width_cm * 10  # 사다리 폭 (높이로 시각화)

    # 외곽 사각
    ax.add_patch(Rectangle((0, 0), total_mm, h, fill=False, edgecolor="#374151", linewidth=2))
    # 다대 수직선들
    for i in range(divisions + 1):
        x = i * seg
        ax.plot([x, x], [0, h], color="#1e3a8a", linewidth=1.5)
    # 살대 지그재그
    for i in range(divisions):
        x1, x2 = i * seg, (i + 1) * seg
        if i % 2 == 0:
            ax.plot([x1, x2], [0, h], color="#eab308", linewidth=1.3)
        else:
            ax.plot([x1, x2], [h, 0], color="#eab308", linewidth=1.3)
    # 라벨
    ax.text(total_mm / 2, h + 90, f"{label}  (폭: {width_cm:.1f}cm)",
            ha="center", fontsize=11, fontweight="bold", color=color_main)
    ax.text(total_mm / 2, h + 30, f"총길이: {total_mm:.1f}cm", ha="center",
            fontsize=9, color="#dc2626")

    # 자간 표시 (몇 개만)
    sample = max(1, divisions // 6)
    for i in range(0, divisions, sample):
        x = (i + 0.5) * seg
        ax.text(x, -60, f"{seg/10:.1f}cm", ha="center", fontsize=7, color="#16a34a")

    ax.set_xlim(-100, total_mm + 100)
    ax.set_ylim(-180, h + 180)
    ax.set_aspect("auto")
    ax.axis("off")
    plt.tight_layout()
    return fig


def module_2_wall_ladder():
    render_header()
    st.markdown("## 🪜 2. 벽사다리 통합 산출 시스템")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 도면 치수 입력")
            total = st.number_input("1. 전체 총기장(cm)", value=2000.0, step=50.0)
            sub_w = st.number_input("2. 보강사다리 폭(cm)", value=70.0, step=5.0)
            main_w = st.number_input("3. 메인사다리 폭(cm)", value=70.0, step=5.0)
            sub_qty = st.number_input("4. 보강사다리 총 제작 수량(세트)", value=1, step=1)
            main_qty = st.number_input("5. 메인사다리 총 제작 수량(세트)", value=2, step=1)
            d_offset = st.number_input("6. 살대 꼭지점 이격 거리(mm)", value=10.0, step=0.5)

            st.markdown("### 용마루 & 벽사다리 치수")
            ridge_w = st.number_input("용마루 폭(높이)(cm)", value=70.0, step=5.0)
            ridge_base = st.number_input("용마루 공제 기준 사이즈(mm)", value=59.9, step=0.1)
            ridge_qty = st.number_input("용마루 제작 수량(세트)", value=1, step=1)
            wall_snagi = st.number_input("벽사다리 스나기 사이즈(mm)", value=89.10, step=0.1)

        with col2:
            st.markdown("### 파이프 규격 설정")
            sub_chord = st.number_input("보강사다리 상하현대(mm)", value=38.10, step=0.1)
            sub_vert = st.number_input("보강사다리 수직/사재(mm)", value=31.80, step=0.1)
            main_chord = st.number_input("메인사다리 상하현대(mm)", value=42.20, step=0.1)
            main_snagi = st.number_input("메인사다리 스나기(mm)", value=89.10, step=0.1)
            main_vert = st.number_input("메인사다리 수직다대(mm)", value=38.10, step=0.1)
            main_diag = st.number_input("메인사다리 살대(mm)", value=31.80, step=0.1)
            ridge_chord = st.number_input("용마루 상하현대(mm)", value=42.20, step=0.1)
            ridge_vert = st.number_input("용마루 수직다대(mm)", value=38.10, step=0.1)
            ridge_diag = st.number_input("용마루 살대(mm)", value=31.80, step=0.1)

        if st.button("도면 및 산출표 생성하기", type="primary"):
            st.session_state["ladder_done"] = True
            st.session_state["ladder_params"] = dict(
                total=total, sub_w=sub_w, main_w=main_w,
                sub_qty=sub_qty, main_qty=main_qty,
                ridge_w=ridge_w, ridge_qty=ridge_qty,
            )

    if st.session_state.get("ladder_done"):
        p = st.session_state["ladder_params"]
        st.success(f"✅ 벽사다리 도면 산출이 완료되었습니다. 총 {p['sub_qty']+p['main_qty']+p['ridge_qty']} 세트")

        st.pyplot(draw_wall_ladder(p["total"], p["sub_w"], "1. 보강사다리", "#374151"),
                  use_container_width=True)
        st.pyplot(draw_wall_ladder(p["total"], p["main_w"], "2. 메인사다리", "#1e3a8a"),
                  use_container_width=True)
        st.pyplot(draw_wall_ladder(p["total"], p["ridge_w"], "3. 용마루", "#a855f7"),
                  use_container_width=True)


# ============================================================
# 모듈 3: 프리미엄 평면도 및 원단 야드
# ============================================================
def draw_floorplan(sets):
    """sets: list of dicts with bottom, left, right, divs"""
    fig, ax = plt.subplots(figsize=(14, 6), facecolor="white")
    ax.set_facecolor("white")

    colors = ["#fed7aa", "#bbf7d0", "#bfdbfe", "#fde68a", "#e9d5ff", "#fecaca"]
    cur_x = 0
    total_area_m2 = 0

    for i, s in enumerate(sets):
        bottom = s["bottom"]  # cm
        left = s["left"]
        right = s["right"]
        divs = max(1, int(s["divs"]))
        color = colors[i % len(colors)]

        # 사다리꼴
        verts = [(cur_x, 0), (cur_x + bottom, 0), (cur_x + bottom, right),
                 (cur_x, left)]
        poly = plt.Polygon(verts, closed=True, facecolor=color, edgecolor="#1e3a8a",
                           linewidth=1.5, alpha=0.7)
        ax.add_patch(poly)

        # 등분선
        seg = bottom / divs
        for k in range(1, divs):
            x = cur_x + k * seg
            # 상단 (사다리꼴 위쪽 사선): 보간
            t = k / divs
            y_top = left + (right - left) * t
            ax.plot([x, x], [0, y_top], color="#9ca3af", linestyle="--", linewidth=0.8)
            ax.text(x, y_top - 5, f"{seg:.1f}", ha="center", fontsize=7, color="#16a34a")

        # 하단 길이 표시
        ax.text(cur_x + bottom / 2, -15, f"{bottom:.1f}", ha="center",
                fontsize=9, color="#dc2626")
        # 좌우 높이
        if i == 0:
            ax.text(cur_x - 15, left / 2, f"좌: {left:.1f}", ha="right",
                    fontsize=9, color="#111827")
        ax.text(cur_x + bottom + 15, right / 2, f"{'우' if i==len(sets)-1 else ''}: {right:.1f}",
                ha="left", fontsize=9, color="#111827")

        # 상단 사선 길이
        slope = float(np.hypot(bottom, right - left))
        ax.text(cur_x + bottom / 2, max(left, right) + 20,
                f"상단 사선 합계: {slope:.1f}cm", ha="center", fontsize=9, color="#16a34a")

        # 하단 분할 표시
        for k in range(divs):
            ax.text(cur_x + (k + 0.5) * seg, 5, f"{seg:.1f}",
                    ha="center", fontsize=7, color="#dc2626")

        # 평수 (사다리꼴 면적)
        area_cm2 = (left + right) / 2 * bottom
        area_m2 = area_cm2 / 10000
        total_area_m2 += area_m2

        cur_x += bottom

    pyeong = total_area_m2 / 3.3058
    ax.text(cur_x / 2, max([s["left"] for s in sets] + [s["right"] for s in sets]) + 80,
            f"■ 평면도 및 평수 (사용자 지정 등분) ■\n합계 평수: {pyeong:.2f}평",
            ha="center", fontsize=13, fontweight="bold", color="#111827")

    ax.set_xlim(-50, cur_x + 50)
    ax.set_ylim(-80, max([s["left"] for s in sets] + [s["right"] for s in sets]) + 200)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    return fig, total_area_m2, pyeong


def module_3_floorplan():
    render_header()
    st.markdown("## 🖼️ 3. 프리미엄 디자인 평면도 및 원단")

    with st.container(border=True):
        out_opt = st.radio(
            "출력 옵션 선택",
            ["1. 평면도 및 평수", "2. 원단 야드", "3. 모두 출력"],
            index=2,
        )
        n_sets = st.number_input("■ 총 제작 세트 수량을 입력하세요", value=3, step=1, min_value=1)

        st.markdown("### 세트별 치수 입력 (cm)")
        sets = []
        for i in range(int(n_sets)):
            st.markdown(f"**[{i+1}번 셋트]**")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                b = st.number_input("하단 가로", value=200.0, key=f"b_{i}", step=10.0)
            with c2:
                lh = st.number_input("좌측 세로", value=150.0, key=f"l_{i}", step=10.0)
            with c3:
                rh = st.number_input("우측 세로", value=180.0, key=f"r_{i}", step=10.0)
            with c4:
                dv = st.number_input("등분 수 (칸)", value=4, key=f"d_{i}", step=1, min_value=1)
            sets.append({"bottom": b, "left": lh, "right": rh, "divs": dv})

        if st.button("도면 산출하기", type="primary"):
            st.session_state["floor_sets"] = sets
            st.session_state["floor_opt"] = out_opt

    if "floor_sets" in st.session_state:
        fig, area_m2, pyeong = draw_floorplan(st.session_state["floor_sets"])
        st.pyplot(fig, use_container_width=True)

        opt = st.session_state["floor_opt"]
        col1, col2 = st.columns(2)
        if "1." in opt or "3." in opt:
            with col1:
                st.metric("총 면적", f"{area_m2:.2f} m²")
                st.metric("총 평수", f"{pyeong:.2f} 평")
        if "2." in opt or "3." in opt:
            with col2:
                # 원단 야드 (1 yard ≈ 91.44cm, 폭 1.5m 기준 가정)
                fabric_width_m = 1.5
                fabric_len_m = area_m2 / fabric_width_m * 1.15  # 여유 15%
                fabric_yd = fabric_len_m / 0.9144
                st.metric("필요 원단 길이", f"{fabric_len_m:.2f} m  /  {fabric_yd:.2f} yd")
                st.caption("폭 1.5m 기준 / 여유율 15% 포함")


# ============================================================
# 모듈 4: 현장 맞춤형 대각 벽사다리
# ============================================================
def calc_diagonal_ladder(total_cm, left_h_cm, right_h_cm, big_div, small_div, offset_mm):
    total_mm = total_cm * 10
    lh_mm = left_h_cm * 10
    rh_mm = right_h_cm * 10
    big_seg = total_mm / big_div
    small_seg = big_seg / small_div if small_div > 0 else big_seg

    # 상현(대각) 길이
    diag_total = float(np.hypot(total_mm, rh_mm - lh_mm))
    # 각 큰 칸의 다대 길이
    xs = np.linspace(0, total_mm, big_div + 1)
    ys_top = lh_mm + (rh_mm - lh_mm) * (xs / total_mm)
    return {
        "total_mm": total_mm,
        "lh_mm": lh_mm,
        "rh_mm": rh_mm,
        "big_seg": big_seg,
        "small_seg": small_seg,
        "diag_total": diag_total,
        "xs": xs,
        "ys_top": ys_top,
    }


def draw_diagonal_ladder(g):
    fig, ax = plt.subplots(figsize=(14, 4.5), facecolor="white")
    ax.set_facecolor("white")

    total = g["total_mm"]
    lh, rh = g["lh_mm"], g["rh_mm"]

    # 외곽 (상현 대각, 하현, 좌측, 우측)
    ax.plot([0, total], [0, 0], color="#374151", linewidth=2)  # 하현
    ax.plot([0, total], [lh, rh], color="#6366f1", linewidth=2.5)  # 상현 대각
    ax.plot([0, 0], [0, lh], color="#a855f7", linewidth=2)  # 좌
    ax.plot([total, total], [0, rh], color="#a855f7", linewidth=2)  # 우

    # 큰 칸 다대 + 작은 칸 다대
    for i in range(len(g["xs"])):
        x = g["xs"][i]
        y_top = g["ys_top"][i]
        ax.plot([x, x], [0, y_top], color="#a855f7", linewidth=1.8)
        ax.text(x, -40, f"{x:.1f}", ha="center", fontsize=6, color="#dc2626")
        # 다대 길이 라벨
        ax.text(x + 5, y_top / 2, f"L{y_top/10:.1f}cm", fontsize=6, color="#16a34a", rotation=90)

    # 작은 살대 칸 (지그재그)
    for i in range(len(g["xs"]) - 1):
        x1, x2 = g["xs"][i], g["xs"][i + 1]
        y1, y2 = g["ys_top"][i], g["ys_top"][i + 1]
        # 작은 분할
        n_small = max(1, int(round(g["big_seg"] / g["small_seg"])))
        for k in range(n_small + 1):
            t = k / n_small
            xx = x1 + (x2 - x1) * t
            yy = y1 + (y2 - y1) * t
            ax.plot([xx, xx], [0, yy], color="#7c3aed", linewidth=0.6, alpha=0.5)
        # 지그재그 살대
        for k in range(n_small):
            t1 = k / n_small
            t2 = (k + 1) / n_small
            xa = x1 + (x2 - x1) * t1
            xb = x1 + (x2 - x1) * t2
            ya = y1 + (y2 - y1) * t1
            yb = y1 + (y2 - y1) * t2
            if k % 2 == 0:
                ax.plot([xa, xb], [0, yb], color="#eab308", linewidth=1)
            else:
                ax.plot([xa, xb], [ya, 0], color="#eab308", linewidth=1)
        # 화단(평균) 재단
        ax.text((x1 + x2) / 2, -90, f"화단 재단: {g['big_seg']/10:.1f}",
                ha="center", fontsize=7, color="#dc2626")

    # 외곽 라벨
    ax.text(-90, lh / 2, f"좌측 외경\n{lh/10:.1f}cm", ha="right", va="center",
            fontsize=9, color="#111827")
    ax.text(total + 90, rh / 2, f"우측 외경\n{rh/10:.1f}cm", ha="left", va="center",
            fontsize=9, color="#111827")
    ax.text(total / 2, -180, f"전체 총기장: {total/10:.1f}cm", ha="center",
            fontsize=11, color="#dc2626", fontweight="bold")
    ax.text(total / 2, max(lh, rh) + 60, f"상현대 대각길이: {g['diag_total']/10:.1f}cm",
            ha="center", fontsize=10, color="#6366f1", fontweight="bold")
    ax.text(total / 2, max(lh, rh) + 130, "■ 맞춤형 대각 벽사다리 ■",
            ha="center", fontsize=12, fontweight="bold", color="#111827")

    ax.set_xlim(-200, total + 200)
    ax.set_ylim(-260, max(lh, rh) + 220)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    return fig


def module_4_diagonal():
    render_header()
    st.markdown("## 📐 4. 현장 맞춤형 대각 벽사다리 도면 및 산출")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 치수 및 분할 입력")
            total = st.number_input("1. 전체 총기장(cm)", value=2000.0, step=50.0)
            lh = st.number_input("2. 좌측 외경(높이)(cm)", value=100.0, step=5.0)
            rh = st.number_input("3. 우측 외경(높이)(cm)", value=70.0, step=5.0)
            big_div = st.number_input("4. 스나기 구역(큰 칸) 등분 수", value=5, step=1, min_value=1)
            small_div = st.number_input("5. 스나기 안쪽 살대 구역 등분 수", value=4, step=1, min_value=1)
            qty = st.number_input("6. 총 제작 수량(세트)", value=1, step=1, min_value=1)
            offset = st.number_input("7. 살대 꼭지점 이격 거리(mm)", value=10.0, step=0.5)

        with col2:
            st.markdown("### 파이프 규격(mm) 설정")
            d_chord = st.number_input("상하현대 파이프 지름(mm)", value=42.20, step=0.1)
            d_snagi = st.number_input("스나기 파이프 지름(mm)", value=89.10, step=0.1)
            d_vert = st.number_input("다대 파이프 지름(mm)", value=38.10, step=0.1)
            d_diag = st.number_input("살대 파이프 지름(mm)", value=31.80, step=0.1)

        if st.button("도면 및 산출표 생성하기", type="primary"):
            g = calc_diagonal_ladder(total, lh, rh, int(big_div), int(small_div), offset)
            st.session_state["diag_geom"] = g
            st.session_state["diag_qty"] = int(qty)

    if "diag_geom" in st.session_state:
        g = st.session_state["diag_geom"]
        st.success("✅ 대각 벽사다리 산출이 완료되었습니다. 아래 버튼을 눌러 다운로드하세요.")
        fig = draw_diagonal_ladder(g)
        st.pyplot(fig, use_container_width=True)

        st.markdown("#### 도면 파일 다운로드 (PDF / 엑셀 / CAD)")

        # 업체명 / 저장 파일명 입력
        col_cn, col_fn = st.columns(2)
        with col_cn:
            company_4 = st.text_input("업체명", placeholder="예: 씨아이텐트", key="company_diag")
        with col_fn:
            savename_4 = st.text_input("저장 파일명", placeholder="예: 물류센터_A동", key="savename_diag")

        c1, c2, c3 = st.columns(3)
        authed = st.session_state.get("authed", False)
        with c1:
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf", bbox_inches="tight")
            st.download_button("📄 PDF 도면 다운로드", buf.getvalue(),
                               file_name=make_filename(company_4, savename_4, "citent_diagonal_ladder", "pdf"),
                               mime="application/pdf", use_container_width=True,
                               disabled=not authed)
        with c2:
            csv_data = (
                f"항목,값\n전체총기장(mm),{g['total_mm']}\n"
                f"좌측외경(mm),{g['lh_mm']}\n우측외경(mm),{g['rh_mm']}\n"
                f"상현대대각길이(mm),{g['diag_total']:.1f}\n"
                f"큰칸세그(mm),{g['big_seg']:.1f}\n작은칸세그(mm),{g['small_seg']:.1f}\n"
            )
            st.download_button("📊 엑셀 산출표 다운로드", csv_data.encode("utf-8-sig"),
                               file_name=make_filename(company_4, savename_4, "citent_diagonal_ladder", "csv"),
                               mime="text/csv", use_container_width=True,
                               disabled=not authed)
        with c3:
            buf2 = io.BytesIO()
            fig.savefig(buf2, format="svg", bbox_inches="tight")
            st.download_button("📐 CAD(SVG) 도면 다운로드", buf2.getvalue(),
                               file_name=make_filename(company_4, savename_4, "citent_diagonal_ladder", "svg"),
                               mime="image/svg+xml", use_container_width=True,
                               disabled=not authed)


# ============================================================
# 모듈 5: 3D 천막 창고 시뮬레이터
# ============================================================
def build_tent_3d(L, W, H1, peak, roof_type, wall_color, roof_color, vent_n, vent_color,
                  belt_h, doors, windows):
    fig = go.Figure()

    # 벽면 (직육면체)
    # 하단 4개 벽
    walls_x = [
        [0, L, L, 0, 0],
        [0, 0, 0, 0, 0],
        [L, L, L, L, L],
        [0, L, L, 0, 0],
    ]
    walls_y = [
        [0, 0, 0, 0, 0],
        [0, W, W, 0, 0],
        [0, W, W, 0, 0],
        [W, W, W, W, W],
    ]
    walls_z = [
        [0, 0, H1 - belt_h, H1 - belt_h, 0],
        [0, 0, H1 - belt_h, H1 - belt_h, 0],
        [0, 0, H1 - belt_h, H1 - belt_h, 0],
        [0, 0, H1 - belt_h, H1 - belt_h, 0],
    ]
    for x, y, z in zip(walls_x, walls_y, walls_z):
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            color=wall_color, opacity=0.95,
            i=[0, 0], j=[1, 2], k=[2, 3],
            showscale=False, hoverinfo="skip",
        ))

    # 상단 띠 (포인트)
    belt_z_low = H1 - belt_h
    belt_z_high = H1
    for x, y in [
        ([0, L, L, 0], [0, 0, 0, 0]),
        ([0, 0, 0, 0], [0, W, W, 0]),
        ([L, L, L, L], [0, W, W, 0]),
        ([0, L, L, 0], [W, W, W, W]),
    ]:
        fig.add_trace(go.Mesh3d(
            x=x, y=y,
            z=[belt_z_low, belt_z_low, belt_z_high, belt_z_high],
            color=roof_color, opacity=1,
            i=[0, 0], j=[1, 2], k=[2, 3],
            showscale=False, hoverinfo="skip",
        ))

    # 지붕 (삼각/모노/평지붕)
    z_peak = H1 + peak
    if roof_type == "삼각 지붕":
        # 두 사면
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0],
            y=[0, 0, W / 2, W / 2],
            z=[H1, H1, z_peak, z_peak],
            color=roof_color, opacity=1,
            i=[0, 0], j=[1, 2], k=[2, 3], showscale=False,
        ))
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0],
            y=[W, W, W / 2, W / 2],
            z=[H1, H1, z_peak, z_peak],
            color=roof_color, opacity=1,
            i=[0, 0], j=[1, 2], k=[2, 3], showscale=False,
        ))
        # 박공 삼각면 (양 끝)
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0],
            y=[0, W, W / 2],
            z=[H1, H1, z_peak],
            color=wall_color, opacity=1,
            i=[0], j=[1], k=[2], showscale=False,
        ))
        fig.add_trace(go.Mesh3d(
            x=[L, L, L],
            y=[0, W, W / 2],
            z=[H1, H1, z_peak],
            color=wall_color, opacity=1,
            i=[0], j=[1], k=[2], showscale=False,
        ))
    elif roof_type == "평지붕":
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[0, 0, W, W],
            z=[H1, H1, H1, H1],
            color=roof_color, opacity=1,
            i=[0, 0], j=[1, 2], k=[2, 3], showscale=False,
        ))
    else:  # 모노(외쪽)
        fig.add_trace(go.Mesh3d(
            x=[0, L, L, 0], y=[0, 0, W, W],
            z=[H1, H1, z_peak, z_peak],
            color=roof_color, opacity=1,
            i=[0, 0], j=[1, 2], k=[2, 3], showscale=False,
        ))

    # 벤츄레타 (지붕 위 작은 박스들)
    if vent_n > 0 and roof_type == "삼각 지붕":
        for i in range(int(vent_n)):
            cx = (i + 1) * L / (int(vent_n) + 1)
            cy = W / 2
            fig.add_trace(go.Mesh3d(
                x=[cx - 0.4, cx + 0.4, cx + 0.4, cx - 0.4,
                   cx - 0.4, cx + 0.4, cx + 0.4, cx - 0.4],
                y=[cy - 0.4, cy - 0.4, cy + 0.4, cy + 0.4,
                   cy - 0.4, cy - 0.4, cy + 0.4, cy + 0.4],
                z=[z_peak, z_peak, z_peak, z_peak,
                   z_peak + 0.4, z_peak + 0.4, z_peak + 0.4, z_peak + 0.4],
                color=vent_color, opacity=1, alphahull=0, showscale=False,
            ))

    # 문 / 창문
    for d in doors:
        wall = d["wall"]
        cx, cy = d["pos"]
        dw, dh = d["w"], d["h"]
        if wall in ("앞", "뒤"):
            y0 = 0 if wall == "앞" else W
            fig.add_trace(go.Mesh3d(
                x=[cx - dw / 2, cx + dw / 2, cx + dw / 2, cx - dw / 2],
                y=[y0, y0, y0, y0],
                z=[0, 0, dh, dh],
                color="#5b3a1c", opacity=1,
                i=[0, 0], j=[1, 2], k=[2, 3], showscale=False,
            ))
    for w in windows:
        wall = w["wall"]
        cx, cy = w["pos"]
        ww, wh = w["w"], w["h"]
        z0 = w["z"]
        if wall in ("앞", "뒤"):
            y0 = 0 if wall == "앞" else W
            fig.add_trace(go.Mesh3d(
                x=[cx - ww / 2, cx + ww / 2, cx + ww / 2, cx - ww / 2],
                y=[y0, y0, y0, y0],
                z=[z0, z0, z0 + wh, z0 + wh],
                color="#7dd3fc", opacity=0.8,
                i=[0, 0], j=[1, 2], k=[2, 3], showscale=False,
            ))

    fig.update_layout(
        scene=dict(
            xaxis_title="길이 L(m)",
            yaxis_title="폭 W(m)",
            zaxis_title="높이(m)",
            aspectmode="data",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1)),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        paper_bgcolor="white",
    )
    return fig


def module_5_3d():
    render_header()
    st.markdown("## 🏕️ 5. 전문 3D 천막 창고 맞춤형 시뮬레이터")

    tab1, tab2, tab3 = st.tabs(["🎨 기본 외형", "🚪 문/창문", "🏗️ 구조/하중"])

    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### ⚙️ 제원 및 지붕")
            roof_type = st.selectbox("지붕 타입", ["삼각 지붕", "평지붕", "모노 지붕"])
            peak = st.number_input("지붕 솟은 높이(m)", value=2.0, step=0.1)
            L = st.slider("길이(L) : m", 5.0, 50.0, 15.0, 0.5)
            W = st.slider("폭(W) : m", 3.0, 30.0, 8.0, 0.5)
            H1 = st.slider("벽면 전체 높이(H1) : m", 2.0, 10.0, 4.0, 0.1)

            st.markdown("### 🎨 디자인 설정")
            belt_h = st.slider("상단 띠(포인트) 높이 : m", 0.0, 2.0, 0.8, 0.1)
            wall_color = st.color_picker("하단 벽 색상", "#f5f5f5")
            roof_color = st.color_picker("상단 띠/지붕", "#1f3a5f")

            st.markdown("### 🌬️ 환기 설비")
            c1, c2 = st.columns(2)
            with c1:
                vent_n = st.number_input("벤츄레타(개)", value=2, step=1, min_value=0)
            with c2:
                vent_color = st.color_picker("벤츄레타 색상", "#a3a3a3")

        # 문/창문 입력값을 세션에서 가져오기
        doors = st.session_state.get("doors", [
            {"wall": "앞", "pos": (3, 0), "w": 2.0, "h": 2.5},
        ])
        windows = st.session_state.get("windows", [
            {"wall": "앞", "pos": (8, 0), "w": 1.2, "h": 1.0, "z": 1.5},
        ])

        with col2:
            fig3d = build_tent_3d(L, W, H1, peak, roof_type, wall_color, roof_color,
                                   vent_n, vent_color, belt_h, doors, windows)
            st.plotly_chart(fig3d, use_container_width=True, theme=None)
            st.caption(
                "우측 상단의 'Download plot as a png' (카메라 아이콘) 버튼을 누르시면 "
                "고화질(1920×1080)로 현재 3D 도면 화면을 저장할 수 있습니다."
            )

    with tab2:
        st.markdown("### 🚪 문 / 창문 배치")
        n_doors = st.number_input("문 개수", value=1, step=1, min_value=0, max_value=4)
        doors = []
        for i in range(int(n_doors)):
            st.markdown(f"**문 {i+1}**")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                w = st.selectbox("위치", ["앞", "뒤"], key=f"dw_{i}")
            with c2:
                cx = st.number_input("X 위치(m)", value=3.0, key=f"dx_{i}")
            with c3:
                dw = st.number_input("문 폭(m)", value=2.0, key=f"ddw_{i}")
            with c4:
                dh = st.number_input("문 높이(m)", value=2.5, key=f"ddh_{i}")
            doors.append({"wall": w, "pos": (cx, 0), "w": dw, "h": dh})
        st.session_state["doors"] = doors

        n_win = st.number_input("창문 개수", value=1, step=1, min_value=0, max_value=8)
        windows = []
        for i in range(int(n_win)):
            st.markdown(f"**창문 {i+1}**")
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                w = st.selectbox("위치", ["앞", "뒤"], key=f"ww_{i}")
            with c2:
                cx = st.number_input("X 위치(m)", value=8.0, key=f"wx_{i}")
            with c3:
                ww = st.number_input("창 폭(m)", value=1.2, key=f"www_{i}")
            with c4:
                wh = st.number_input("창 높이(m)", value=1.0, key=f"wwh_{i}")
            with c5:
                z = st.number_input("바닥에서 높이(m)", value=1.5, key=f"wz_{i}")
            windows.append({"wall": w, "pos": (cx, 0), "w": ww, "h": wh, "z": z})
        st.session_state["windows"] = windows

    with tab3:
        st.markdown("### 🏗️ 구조 / 하중 정보")
        c1, c2 = st.columns(2)
        with c1:
            wind = st.number_input("설계 풍속(m/s)", value=30.0, step=1.0)
            snow = st.number_input("적설하중(kg/㎡)", value=50.0, step=10.0)
        with c2:
            spacing = st.number_input("프레임 간격(m)", value=2.0, step=0.5)
            material = st.selectbox("프레임 자재", ["일반강관(STK)", "각관", "용융아연도금"])

        # 간단 구조 산출
        try:
            n_frames = int(L / spacing) + 1 if 'L' in dir() else 8
        except Exception:
            n_frames = 8
        st.metric("필요 프레임 수", f"{n_frames} 개")
        st.info(f"※ 풍속 {wind}m/s, 적설 {snow}kg/㎡ 기준 설계 적용 시 권장 프레임 간격 {spacing}m")


# ============================================================
# 메인 라우팅
# ============================================================
if menu.startswith("1"):
    module_1_truss()
elif menu.startswith("2"):
    module_2_wall_ladder()
elif menu.startswith("3"):
    module_3_floorplan()
elif menu.startswith("4"):
    module_4_diagonal()
elif menu.startswith("5"):
    module_5_3d()
