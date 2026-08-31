# =============================================================================
# Supplier OAMI Evaluation App
# Version: 2.10.0
#
# [버전 히스토리 - 최신순]
#   v2.10.0 - Description 프리셋 목록을 20개로 확장(입고/보관 → 자재 이동 →
#             절삭/성형/가공 → 접합 → 표면처리 → 품질 → 포장 순). "Insert"
#             버튼은 번거롭다는 피드백에 따라 제거하고, 드롭다운에서 고르는
#             즉시 Description 칸에 반영되도록 변경 (드롭다운은 리셋하지
#             않고 고른 값을 그대로 유지).
#   v2.9.0 - Description 프리셋 목록을 제조업 공정에 맞게 확장: 자재 이동
#            (Moving/Feeding/Loading/Unloading) → 가공/조립(Assembly/
#            Welding/Machining/Painting) → 품질/포장(Inspection/Packaging)
#            순의 기본 공정 단어 10개로 구성. 세부 내용은 이어서 직접
#            입력(key-in)하는 방식은 그대로 유지.
#   v2.8.0 - "Description 프리셋 셀렉트가 안 된다"는 피드백에 따라 방식 변경:
#            자동 적용(on_change) 대신 드롭다운에서 고르고 "Insert into
#            Description" 버튼을 눌러야 반영되는 2단계 방식으로 바꿔 동작을
#            더 명확하게 함. 프리셋 목록도 실제 요청하신 Moving/Feeding/
#            Assembly/Welding으로 교체.
#   v2.7.0 - Description 입력칸에 미리 정의된(predefined) 문구를 고를 수 있는
#            프리셋 드롭다운 추가. 프리셋을 고르면 Description 칸이 그
#            문구로 채워지고, 이어서 타이핑해 내용을 덧붙이거나 전부 지우고
#            새로 쓸 수 있음. (DESCRIPTION_PRESETS 목록은 예시이므로 실제
#            사용하는 문구로 직접 교체 필요)
#   v2.6.0 - "Large로 바꾸고 새로고침하면 Medium으로 돌아간다" 문제 해결.
#            글자 크기 선택값을 URL 쿼리 파라미터(?text_size=...)에도 저장해서
#            브라우저를 새로고침(F5)해도 마지막 선택이 유지되도록 함.
#   v2.5.0 - 글자 크기 선택 UI를 아이콘 버튼 → 다시 라디오 버튼으로 되돌림
#            (휴대폰 좁은 화면에서 버튼 3개가 세로로 쌓이는 문제 해결).
#            v2.3.0 라디오 버전에 있었던 "화면 전환 시 선택값이 사라지는"
#            문제는 index+key 동시 사용이 원인으로 보여 제거해서 해결.
#            옵션 앞 "A" 글자 크기를 다르게 표시하는 것은 그대로 유지.
#   v2.4.0 - "인터넷 안 되면 앱이 멈춘다" 문제 해결: 인터넷 연결 여부를 빠르게
#            사전 확인(최대 2.5초) + 소켓 타임아웃(8초) 적용해 오프라인 시
#            더 이상 화면이 멈추지 않고 즉시 로컬 저장만으로 계속 진행됨.
#            화면에 온라인/오프라인 상태 표시 추가. 클라우드 재동기화도
#            세션당 1회 → 1분 간격 재시도로 변경해 인터넷 복구 시 자동 반영.
#   v2.3.1 - 글자 크기 선택 UI를 라디오 버튼 → 크기별 아이콘 버튼(A/A/A)으로 변경
#            (버튼 안 "A" 자체를 작게/중간/크게 실제 크기로 표시, 선택된 크기는
#             색상(primary) + 체크(✓) 표시로 강조)
#   v2.3.0 - 화면 UI 텍스트(라벨/버튼/안내·경고·에러 메시지) 영어로 변경
#            + 글자 크기 선택 기능(Small/Medium/Large) 추가 (메인 화면 최상단)
#   v2.2.1 - Summary/Export 컬럼 순서 변경 (No. > Process > Description > Type > PAMI > Remark > Time)
#   v2.2.0 - 저장/복구/동기화 로직 재설계 (로컬+클라우드 이중 저장,
#            timestamp 비교 기반 복구 목록 표시, 1일 1회 자동 동기화) - Fix 1 재설계
#   v2.1.0 - Google Sheets 14일 초과 백업 행 자동 삭제 (세션/wake-up 시 1회 실행) - Fix 2
#
# [개요]
# 공급업체 OAMI(Operation Assessment & Management Index) 평가 앱.
# 프로세스별 Type(MH/P/WIP) 및 PAMI 점수(1~5)를 입력하고
# Google Sheets(클라우드) + 서버 로컬 파일에 이중 백업.
#
# [v2.10.0 변경사항 - Description 프리셋 20개 확장 + Insert 버튼 제거]
#   - "20개로 늘려주고, Insert 버튼은 더 귀찮으니 빼달라"는 요청에 따라 추가.
#   - 기존 10개에 Receiving/Storage/Cutting/Drilling/Grinding/Molding/
#     Stamping/Soldering/Cleaning/Testing을 더해 총 20개로 확장. 입고/보관
#     → 자재 이동 → 절삭/성형/가공 → 접합 → 표면처리 → 품질 → 포장 순으로
#     배치해 제조 공정 흐름을 따라가며 고를 수 있게 함.
#   - "Insert" 버튼을 없애고, 드롭다운에서 고르는 즉시(on_change) Description
#     칸에 반영되도록 되돌림. 다만 v2.7.0 때와 달리 드롭다운을 다시 안내
#     문구로 리셋하지는 않음 — 그 리셋 때문에 "선택이 안 먹힌다"는 오해가
#     있었으므로(v2.8.0 참고), 이번엔 고른 값이 드롭다운에 그대로 남아있게
#     해서 지금 뭐가 적용됐는지 눈으로 바로 확인할 수 있게 함.
#
# [v2.9.0 변경사항 - Description 프리셋 목록을 제조업 공정에 맞게 확장]
#   - "제조업 프로세스에 맞게 간단하고 단순하게 바꿔달라, 나머지는 직접
#     입력(key-in)하면 된다"는 요청에 따라 추가.
#   - 기존 4개(Moving/Feeding/Assembly/Welding)에 Loading/Unloading/
#     Machining/Painting/Inspection/Packaging을 더해 총 10개로 구성.
#     자재 이동 → 가공/조립 → 품질/포장 순으로 배치해 실제 공정 흐름과
#     비슷하게 훑어볼 수 있도록 함.
#   - 목록은 여전히 공정 "이름"만 담은 단순한 구성이며, 세부 설명은 Insert
#     버튼으로 채운 뒤 이어서 직접 타이핑하는 기존 방식 그대로 사용.
#
# [v2.8.0 변경사항 - Description 프리셋 동작 방식 개선]
#   - "테스트 해봤는데 셀렉트가 안 된다"는 피드백에 따라 추가.
#   - 추정 원인: 이전 버전은 드롭다운에서 고르는 즉시(on_change) 자동으로
#     Description에 반영하고, 드롭다운 자체는 다시 "-- Select a preset --"
#     안내 문구로 리셋했음. 방금 고른 항목이 화면에서 바로 사라져 보이기
#     때문에, 실제로는 반영이 됐어도 "선택이 안 먹힌다"고 오해하기 쉬웠음.
#   - 개선: 드롭다운(고른 값 그대로 유지) + "➕ Insert" 버튼의 2단계 방식으로
#     변경. 버튼을 눌러야만 Description 칸에 반영되므로, 언제 무엇이
#     적용됐는지 훨씬 명확함.
#   - Description 프리셋 목록을 예시 문구 대신 실제 요청하신 내용
#     (Moving / Feeding / Assembly / Welding)으로 교체.
#
# [v2.7.0 변경사항 - Description 프리셋 추가]
#   - "Description에 predefined 내용을 먼저 넣어두고, 그 뒤에 추가로 입력할
#     수 있게 해달라"는 요청에 따라 추가.
#   - Description 입력칸 위에 프리셋 선택 드롭다운(Description Preset)을
#     추가. 프리셋을 고르면 Description 칸이 그 문구로 채워지고, 사용자는
#     이어서 타이핑해 내용을 덧붙이거나, 전부 지우고 새로 쓸 수도 있음.
#   - 프리셋 드롭다운은 st.form 밖에 배치함 — form 안의 위젯은 "Save/Update"
#     버튼을 눌러야만 값이 반영되므로, 고르자마자 Description 칸에 바로
#     채워지게 하려면 폼 바깥에 있어야 함.
#   - DESCRIPTION_PRESETS 목록(파일 상단 상수)은 실제 현장 문구를 몰라서
#     넣어둔 예시(placeholder)이므로, 회사에서 실제로 자주 쓰는 문구로
#     직접 교체해서 사용할 것.
#
# [v2.6.0 변경사항 - 글자 크기, 새로고침해도 유지되도록 개선]
#   - "Large로 바꾸고 새로고침을 하면 다시 Medium으로 바뀐다"는 피드백에 따라 추가.
#   - 원인: st.session_state는 브라우저를 새로고침(F5)하면 완전히 새로운
#     세션으로 취급되어 통째로 초기화됨. (같은 화면 안에서 버튼을 눌러
#     발생하는 "rerun"과는 다른 상황 — rerun에서는 session_state가 유지됨)
#   - 해결: 글자 크기 선택값을 session_state뿐 아니라 URL 쿼리 파라미터
#     (예: ?text_size=Large)에도 함께 저장. 새로고침해도 URL은 그대로
#     남아있으므로, 다음 로딩 시 session_state 대신 쿼리 파라미터에서
#     마지막 선택값을 읽어와 그대로 복원함.
#
# [v2.5.0 변경사항 - 글자 크기 UI를 라디오 버튼으로 되돌림]
#   - "휴대폰으로 열었더니 버튼 3개가 세로로 나와서 보기 불편하다"는 피드백에
#     따라, v2.3.1에서 도입했던 아이콘 버튼(A/A/A)을 다시 라디오 버튼으로 변경.
#     라디오는 좁은 화면에서도 옵션 3개가 가로 한 줄로 유지됨.
#   - "예전 라디오 버전은 화면 전환 시 선택값이 사라지는 것 같았다"는 피드백도
#     함께 해결: v2.3.0에서는 st.radio(index=1, key="font_size_choice")처럼
#     index와 key를 동시에 넘겼는데, 이 조합이 화면이 다시 그려질 때 선택값을
#     index 기본값으로 되돌리는 원인으로 보여, index는 제거하고 session_state
#     초기화만으로 기본값을 잡도록 수정 (Streamlit 공식 권장 방식).
#   - 라디오 옵션 앞의 "A" 글자를 작게/중간/크게 실제 크기로 다르게 표시하는
#     것은 그대로 유지 (CSS :nth-of-type으로 옵션별 스타일 지정).
#
# [v2.4.0 변경사항 - 오프라인 대응 강화]
#   - "인터넷이 안 되면 작동을 멈춘다"는 피드백에 따라 추가.
#   - 문제 원인: 구글 API 호출에 타임아웃이 없어, 인터넷이 끊기면 응답이
#     올 때까지 화면이 무한 대기(hang)하며 "멈춘 것처럼" 보였음.
#   - has_internet() 함수로 실제 API를 부르기 전에 www.googleapis.com:443 접속을
#     짧게(최대 2.5초) 시도해 인터넷 여부를 먼저 판단 → 오프라인이면
#     클라우드 시도 자체를 건너뛰고 즉시 로컬 저장만 진행 (화면 멈춤 없음)
#   - socket.setdefaulttimeout()으로 8초 상한을 걸어, 혹시 연결은 되지만
#     응답이 느린 경우에도 무한 대기하지 않도록 안전장치 추가
#   - Step 2 화면에 "☁️ Cloud sync: connected" / "📴 No internet connection"
#     상태 문구를 추가해, 지금 로컬에만 저장 중인지 클라우드까지 저장되고
#     있는지 사용자가 바로 확인 가능
#   - 자동 동기화(로컬→클라우드)를 "세션당 1회"에서 "1분 간격으로 재시도"로
#     변경 → 같은 세션을 계속 켜둔 채로 인터넷이 나중에 복구돼도, 이후
#     아무 저장 동작(프로세스 추가/수정 등) 한 번만 있으면 자동으로 클라우드에
#     반영됨 (페이지 새로고침 불필요)
#
# [v2.3.1 변경사항 - 글자 크기 UI 개선]
#   - 글자 크기 선택을 라디오 버튼에서 3개의 아이콘 버튼(Small/Medium/Large)으로 변경
#   - 버튼 안의 "A" 글자 크기 자체를 작게/중간/크게 다르게 표시해서
#     텍스트 설명 없이도 크기 차이를 한눈에 알 수 있도록 구성
#   - 현재 선택된 크기는 버튼 색상(primary 강조색) + 체크(✓) 표시로 명확히 구분
#
# [v2.3.0 변경사항 - UI 영어화 + 글자 크기 선택]
#   - 화면에 보이는 라벨/버튼/안내·경고·에러 메시지를 영어로 변경
#     (내부 로그 메시지(logger.*)와 코드 주석은 요청에 따라 한글 그대로 유지)
#   - "글자가 작아서 안 보인다"는 피드백에 따라, 메인 화면 최상단에
#     Small / Medium / Large 글자 크기 선택 UI 추가
#     → 선택 즉시 앱 전체(라벨/버튼/표/안내문 등)에 CSS로 일괄 적용, 기본값 Medium
#
# [v2.2.0 변경사항 - Fix 1 재설계]
#
# ▶ 저장 로직
#   - 항상 로컬 파일 + 클라우드 동시 저장 시도
#   - 인터넷 없으면 로컬 파일에만 저장 (클라우드 실패해도 로컬은 항상 저장)
#
# ▶ 복구 목록 표시 기준 (로컬/클라우드 timestamp 비교)
#   - 클라우드 연결 불가 → 로컬만 표시
#   - 클라우드 연결 가능 + 로컬이 클라우드보다 10초 초과 최신
#     → 로컬이 더 최신 데이터이므로 로컬만 표시
#   - 클라우드 연결 가능 + 클라우드가 최신(또는 10초 이내 차이)
#     → 클라우드만 표시 (정상 상태)
#
# ▶ 자동 동기화 (하루 1회)
#   - 로컬 timestamp가 클라우드보다 10초 이상 앞서면
#     로컬 데이터를 클라우드에 덮어써서 동기화
#   - 동기화 완료 후 복구 목록은 클라우드만 표시
#
# [v2.1.0 변경사항 - Fix 2]
#   - Google Sheets 14일 초과 행 자동 삭제 (세션 시작 시 1회 실행)
#   - 앱 휴지기 후 wake-up 시에도 만료 데이터 정리됨
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import json
import os
import glob
import time
import logging
import io
import socket  # [v2.4.0] 인터넷 연결 여부 확인 및 소켓 타임아웃 설정용

# =====================================================================
# 로깅 설정
# =====================================================================
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# =====================================================================
# 구글 API 라이브러리 임포트
# =====================================================================
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    HAS_GOOGLE_LIBS = True
except ImportError:
    HAS_GOOGLE_LIBS = False

# 브라우저 탭 아이콘 및 제목
st.set_page_config(page_title="Supplier OAMI", page_icon="📝", layout="centered")
st.markdown("### 📝 Supplier OAMI Evaluation App")

# =====================================================================
# [v2.3.0] 글자 크기 선택 (Small / Medium / Large)
# [v2.3.1] 라디오 버튼 → 크기별 아이콘 버튼(A/A/A)으로 변경
# [v2.5.0] 아이콘 버튼 → 다시 라디오 버튼으로 되돌림
#   - 버튼 3개가 휴대폰 같은 좁은 화면에서는 가로 폭이 부족해 세로로
#     쌓여 보기 불편하다는 피드백 반영 (라디오는 좁은 화면에서도 한 줄 유지)
#   - v2.3.0 라디오 버전에서 있었던 "화면 전환 시 선택값이 사라지는(초기화되는)
#     것처럼 보이는" 문제는 st.radio에 index와 key를 동시에 넘긴 것이 원인으로
#     보여, 이번엔 session_state 초기화만으로 기본값을 잡고 index는 넘기지 않음
#   - 라디오 옵션 앞에 표시되는 "A" 글자 크기는 여전히 작게/중간/크게 다르게
#     표시해서(CSS nth-of-type 사용) 텍스트만으로도 크기 차이를 알 수 있게 유지
# "글자가 작아서 안 보인다"는 피드백에 따라 추가.
# 메인 화면 최상단에 배치하고, 선택값은 세션 동안 유지되며
# 앱 전체 텍스트(라벨/버튼/표/안내문 등)에 CSS로 즉시 적용된다. 기본값은 Medium.
# =====================================================================
FONT_SIZE_PRESETS = {
    "Small":  "13px",
    "Medium": "16px",
    "Large":  "20px",
}

# [v2.3.1, v2.5.0에서도 유지] 라디오 옵션 앞 "A" 아이콘 자체의 크기 — 전역
# 글자 크기(FONT_SIZE_PRESETS)와는 별개로, 항상 작게/중간/크게 뚜렷한 크기
# 차이를 보여주기 위한 고정 값
FONT_ICON_SIZES = {
    "Small":  "14px",
    "Medium": "18px",
    "Large":  "24px",
}

# [v2.5.0] index 파라미터를 쓰지 않고 session_state로만 기본값을 초기화한다.
# st.radio(..., index=1, key="font_size_choice")처럼 index와 key를 함께
# 넘기면, 화면이 다시 그려질 때(rerun) 선택값이 index 기본값으로 되돌아가며
# 순간적으로 사라지는 것처럼 보이는 현상이 있었기 때문.
#
# [v2.6.0] "Large로 바꾸고 새로고침(F5)하면 다시 Medium으로 돌아간다"는
# 피드백에 따라 추가.
# session_state는 브라우저를 새로고침하면 완전히 새로운 세션으로 초기화되어
# 사라지므로(같은 화면 안에서의 rerun과는 다름), 새로고침에도 남는 URL의
# 쿼리 파라미터(?text_size=...)에 선택값을 함께 저장해서, 새로고침 시
# session_state 대신 쿼리 파라미터에서 마지막 선택값을 읽어오도록 함.
_qp_size = st.query_params.get("text_size", "Medium")
if _qp_size not in FONT_SIZE_PRESETS:
    _qp_size = "Medium"

if "font_size_choice" not in st.session_state:
    st.session_state.font_size_choice = _qp_size


def apply_font_size(size_label):
    """선택된 글자 크기를 앱 전역 CSS로 적용."""
    base_px = FONT_SIZE_PRESETS.get(size_label, FONT_SIZE_PRESETS["Medium"])
    st.markdown(f"""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"] {{
        font-size: {base_px} !important;
    }}
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div,
    .stText, .stCaption, [data-testid="stCaptionContainer"],
    .stAlert, .stAlert p, .stAlert div,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"],
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] div,
    .stButton button p, .stButton button div,
    .stDownloadButton button p, .stDownloadButton button div,
    .stTextInput input, .stTextArea textarea,
    .stRadio label p, .stRadio div[role="radiogroup"] label p,
    .stCheckbox label p,
    .stSelectbox div, .stSelectbox span,
    .stExpander summary p, .stExpander summary span, .stExpander div,
    table, table td, table th,
    code, pre,
    .stTabs [data-baseweb="tab"] {{
        font-size: {base_px} !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def render_font_size_radio():
    """
    [v2.5.0] Small/Medium/Large 라디오 버튼 렌더링 (아이콘 버튼에서 복귀).
    - 휴대폰처럼 좁은 화면에서도 옵션 3개가 가로 한 줄로 자연스럽게 표시됨
      (버튼 3개는 좁은 화면에서 세로로 쌓여 불편했음)
    - 각 옵션 앞의 "A" 글자 크기를 실제로 다르게(14px/18px/24px) 표시해서
      텍스트 설명 없이도 크기 차이를 한눈에 알 수 있도록 구성
      (Streamlit key="font_size_choice" 위젯의 컨테이너에 자동으로 붙는
      "st-key-font_size_choice" 클래스 + CSS :nth-of-type으로 옵션별 스타일 지정)
    - index를 넘기지 않고 session_state 초기화만으로 기본값을 잡아서,
      화면 전환(rerun) 후에도 선택값이 사라지지 않도록 함
    - [v2.6.0] 선택값을 URL 쿼리 파라미터(?text_size=...)에도 함께 저장해서,
      브라우저를 새로고침(F5)해도 마지막에 고른 크기가 유지되도록 함
    """
    st.markdown(f"""
    <style>
    .st-key-font_size_choice div[role="radiogroup"] label:nth-of-type(1) p {{ font-size: {FONT_ICON_SIZES['Small']}  !important; }}
    .st-key-font_size_choice div[role="radiogroup"] label:nth-of-type(2) p {{ font-size: {FONT_ICON_SIZES['Medium']} !important; }}
    .st-key-font_size_choice div[role="radiogroup"] label:nth-of-type(3) p {{ font-size: {FONT_ICON_SIZES['Large']}  !important; }}
    </style>
    """, unsafe_allow_html=True)

    st.radio(
        "🔠 Text Size",
        options=list(FONT_SIZE_PRESETS.keys()),
        horizontal=True,
        key="font_size_choice"
    )

    # [v2.6.0] 새로고침 후에도 유지되도록 현재 선택값을 URL에 동기화
    st.query_params["text_size"] = st.session_state.font_size_choice


render_font_size_radio()
apply_font_size(st.session_state.font_size_choice)
st.write("")

# 로컬 백업 폴더
BACKUP_DIR = "oami_backups"
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# 유효값 상수
VALID_TYPES  = {"MH", "P", "WIP"}
VALID_SCORES = {1, 2, 3, 4, 5}

# =====================================================================
# [v2.7.0] Description 프리셋(predefined) 목록
# "Description 칸에 미리 정의된 문구를 먼저 넣어두고, 그 뒤에 이어서 추가로
# 입력할 수 있게 해달라"는 요청에 따라 추가.
# [v2.8.0] 목록을 실제 요청하신 문구(Moving/Feeding/Assembly/Welding)로 교체.
# [v2.9.0] "제조업 프로세스에 맞게, 간단하고 단순하게" 요청에 따라 자재
# 이동(Moving/Feeding/Loading/Unloading) → 가공/조립(Assembly/Welding/
# Machining/Painting) → 품질/포장(Inspection/Packaging) 순서로 자주 쓰이는
# 기본 공정 단어 위주로 구성.
# [v2.10.0] "20개로 늘려달라"는 요청에 따라 10개 추가 → 총 20개.
# 입고/보관 → 자재 이동 → 절삭/성형/가공 → 접합 → 표면처리 → 품질 →
# 포장 순서로, 제조 공정 흐름을 따라가며 훑어볼 수 있게 배치.
# 세부 내용은 프리셋 적용 후 이어서 직접 타이핑(key-in)하면 됨.
#
# 목록은 아래에 한 줄에 하나씩, 따옴표 안에 적고 쉼표로 구분하면 됩니다.
# 필요하면 자유롭게 추가/삭제/수정해서 쓰세요.
# =====================================================================
DESCRIPTION_PRESETS = [
    "Receiving",
    "Storage",
    "Moving",
    "Feeding",
    "Loading",
    "Unloading",
    "Cutting",
    "Drilling",
    "Grinding",
    "Machining",
    "Molding",
    "Stamping",
    "Assembly",
    "Welding",
    "Soldering",
    "Painting",
    "Cleaning",
    "Inspection",
    "Testing",
    "Packaging",
]
DESCRIPTION_PRESET_PLACEHOLDER = "-- Select a preset (optional) --"

# 백업 보관 기간 (일)
BACKUP_RETENTION_DAYS = 14

# 로컬/클라우드 시간 차이 임계값 (초) — 이 값 초과 시 로컬이 더 최신으로 판단
# 정상 상태에서 로컬→클라우드 저장 시간차는 1~3초이므로
# 30초를 초과하면 오프라인 중 작업한 것으로 판단
TS_DIFF_THRESHOLD_SEC = 30

# =====================================================================
# [v2.4.0] 네트워크 연결 확인 & 타임아웃 설정
# "인터넷이 안 되면 앱이 멈춘다"는 피드백에 따라 추가.
# - 소켓 기본 타임아웃을 지정해 구글 API 호출이 무한 대기하지 않도록 방지
#   (연결은 되는데 응답만 느린 경우에 대한 안전장치)
# - 실제 클라우드 API를 부르기 전에 www.googleapis.com:443 접속을 짧게 시도해서
#   인터넷 연결 여부를 먼저 빠르게 판단 (최대 2.5초) → 오프라인이면
#   클라우드 시도 자체를 건너뛰어 화면이 멈추지 않고 즉시 로컬 저장만 진행
# - 판단 결과는 10초간 캐시하여, 반복 호출 시마다 매번 다시 확인하느라
#   생기는 불필요한 지연을 방지
# =====================================================================
NETWORK_TIMEOUT_SEC = 8           # 구글 API 호출 자체의 최대 대기 시간(초)
INTERNET_CHECK_TIMEOUT_SEC = 2.5  # 인터넷 연결 여부 사전 확인 시 최대 대기 시간(초)

socket.setdefaulttimeout(NETWORK_TIMEOUT_SEC)


@st.cache_data(ttl=10)
def has_internet():
    """
    인터넷(정확히는 Google API 서버) 연결 여부를 빠르게 확인. 10초간 결과 캐시.

    [v2.4.0] 처음엔 8.8.8.8:53(구글 DNS)로 확인했으나, 회사/보안 네트워크처럼
    53번(DNS) 포트는 막고 443번(HTTPS)만 허용하는 환경에서는 실제로는 인터넷이
    되는데도 "오프라인"으로 잘못 판단하는 문제가 있어, 실제로 사용하는 Google
    Sheets API 서버(www.googleapis.com)의 443번(HTTPS) 포트로 직접 확인하도록 변경.
    """
    try:
        socket.create_connection(("www.googleapis.com", 443), timeout=INTERNET_CHECK_TIMEOUT_SEC)
        return True
    except OSError:
        return False


# =====================================================================
# Google Sheets 헬퍼 함수
# =====================================================================
def get_sheets_service():
    """Google Sheets API 서비스 객체와 sheet_id 반환. 실패 시 (None, None)."""
    if not HAS_GOOGLE_LIBS or "google_drive" not in st.secrets:
        return None, None
    # [v2.4.0] 인터넷이 끊긴 상태면 API 호출 자체를 시도하지 않고 바로 포기
    # → 무한 대기(행업) 없이 즉시 로컬 전용 모드로 동작
    if not has_internet():
        return None, None
    try:
        credentials_info = dict(st.secrets["google_drive"])
        sheet_id = credentials_info.pop("sheet_id", None)
        credentials_info.pop("folder_id", None)
        if "private_key" in credentials_info:
            credentials_info["private_key"] = credentials_info["private_key"].replace("\\n", "\n")
        creds = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)
        return service, sheet_id
    except Exception as e:
        logger.error(f"Google Sheets 인증 실패: {e}")
        return None, None


def _get_all_rows(service, sheet_id):
    """Sheets A:C 전체 행 반환."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="A:C"
        ).execute()
        return result.get("values", [])
    except Exception as e:
        logger.error(f"Google Sheets 읽기 실패: {e}")
        return []


def _find_row_index(rows, filename):
    """파일명으로 행 인덱스(1-based) 탐색. 없으면 -1."""
    base_name = os.path.basename(filename)
    for i, row in enumerate(rows):
        if len(row) > 0 and row[0] == base_name:
            return i + 1
    return -1


def upload_or_update_gsheet(filename, content_dict):
    """Sheets에 백업 데이터 업로드(신규) 또는 갱신(기존 행). 성공 True, 실패 False."""
    service, sheet_id = get_sheets_service()
    if not service or not sheet_id:
        return False
    base_name  = os.path.basename(filename)
    json_data  = json.dumps(content_dict, ensure_ascii=False)
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        rows    = _get_all_rows(service, sheet_id)
        row_idx = _find_row_index(rows, filename)
        new_row = [[base_name, json_data, timestamp]]
        if row_idx > 0:
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"A{row_idx}:C{row_idx}",
                valueInputOption="RAW",
                body={"values": new_row}
            ).execute()
        else:
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range="A:C",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": new_row}
            ).execute()
        return True
    except Exception as e:
        logger.error(f"Google Sheets 업로드 실패 ({base_name}): {e}")
        return False


def delete_gsheet_row_if_exists(filename):
    """Sheets에서 해당 파일명 행을 빈 값으로 덮어써 삭제 처리."""
    service, sheet_id = get_sheets_service()
    if not service or not sheet_id:
        return False
    try:
        rows    = _get_all_rows(service, sheet_id)
        row_idx = _find_row_index(rows, filename)
        if row_idx > 0:
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"A{row_idx}:C{row_idx}",
                valueInputOption="RAW",
                body={"values": [["", "", ""]]}
            ).execute()
        return True
    except Exception as e:
        logger.error(f"Google Sheets 삭제 실패: {e}")
        return False


def get_gsheet_cloud_timestamp(filename):
    """
    Sheets에서 해당 파일명 행의 timestamp 문자열 반환.
    없거나 실패 시 None.
    """
    service, sheet_id = get_sheets_service()
    if not service or not sheet_id:
        return None
    try:
        rows    = _get_all_rows(service, sheet_id)
        row_idx = _find_row_index(rows, filename)
        if row_idx > 0:
            row = rows[row_idx - 1]
            return row[2] if len(row) >= 3 else None
        return None
    except Exception as e:
        logger.error(f"Sheets timestamp 조회 실패: {e}")
        return None


def get_gsheet_backup_list():
    """Sheets에서 유효한 백업 목록 반환. {label: data} 딕트."""
    service, sheet_id = get_sheets_service()
    options = {}
    if not service or not sheet_id:
        return options
    try:
        rows = _get_all_rows(service, sheet_id)
        for row in rows:
            if len(row) >= 2 and row[0] and row[1]:
                try:
                    data  = json.loads(row[1])
                    ts    = row[2] if len(row) >= 3 else "unknown"
                    label = (
                        f"[☁️ Cloud] {data['info']['supplier']} "
                        f"by {data['info']['evaluator']} ({ts})"
                    )
                    options[label] = data
                except (json.JSONDecodeError, KeyError):
                    continue
    except Exception as e:
        logger.error(f"Google Sheets 백업 목록 로딩 실패: {e}")
    return options


# =====================================================================
# [Fix 2] Google Sheets 14일 초과 행 자동 삭제
# 앱 세션 시작(wake-up 포함) 시 1회 실행.
# timestamp(C열)를 파싱해 14일 초과 행을 빈 행으로 덮어씀.
# =====================================================================
def cleanup_old_gsheet_backups():
    """Sheets에서 14일 초과 백업 행을 삭제. 세션당 1회."""
    if st.session_state.get("_gsheet_cleanup_done", False):
        return
    service, sheet_id = get_sheets_service()
    if not service or not sheet_id:
        st.session_state._gsheet_cleanup_done = True
        return
    try:
        rows   = _get_all_rows(service, sheet_id)
        cutoff = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
        for i, row in enumerate(rows):
            row_num = i + 1
            if len(row) < 3 or not row[0]:
                continue
            try:
                ts = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                if ts < cutoff:
                    service.spreadsheets().values().update(
                        spreadsheetId=sheet_id,
                        range=f"A{row_num}:C{row_num}",
                        valueInputOption="RAW",
                        body={"values": [["", "", ""]]}
                    ).execute()
                    logger.warning(f"[GSheet Cleanup] 만료 행 삭제: row {row_num}, ts={row[2]}")
            except ValueError:
                continue
    except Exception as e:
        logger.error(f"Google Sheets 만료 정리 실패: {e}")
    st.session_state._gsheet_cleanup_done = True


# =====================================================================
# 파일명 생성 함수
# =====================================================================
def get_backup_filename(supplier, evaluator):
    """supplier + evaluator 조합으로 로컬 백업 파일 경로 생성."""
    safe_sup  = "".join(c for c in supplier  if c.isalnum() or c in " _-").strip().replace(" ", "_")
    safe_eval = "".join(c for c in evaluator if c.isalnum() or c in " _-").strip().replace(" ", "_")
    return os.path.join(BACKUP_DIR, f"{safe_sup}_{safe_eval}.json")


# =====================================================================
# 로컬 파일 만료 정리 (서버 측, 세션당 1회)
# =====================================================================
def cleanup_old_local_backups():
    """로컬 백업 파일 중 14일 초과분 삭제. 세션당 1회."""
    if st.session_state.get("_local_cleanup_done", False):
        return
    now = time.time()
    for f in glob.glob(os.path.join(BACKUP_DIR, "*.json")):
        try:
            if os.stat(f).st_mtime < now - (BACKUP_RETENTION_DAYS * 86400):
                os.remove(f)
        except Exception as e:
            logger.warning(f"로컬 백업 파일 정리 실패 ({f}): {e}")
    st.session_state._local_cleanup_done = True


# =====================================================================
# [v2.2.0] timestamp 차이 계산 유틸
# =====================================================================
def ts_diff_seconds(local_ts_str, cloud_ts_str):
    """
    로컬 - 클라우드 timestamp 차이(초) 반환.
    양수 = 로컬이 더 최신, 음수 = 클라우드가 더 최신.
    파싱 실패 시 0 반환.
    """
    try:
        fmt      = "%Y-%m-%d %H:%M:%S"
        local_ts = datetime.strptime(local_ts_str, fmt)
        cloud_ts = datetime.strptime(cloud_ts_str, fmt)
        return (local_ts - cloud_ts).total_seconds()
    except Exception:
        return 0


# =====================================================================
# [v2.2.0] 저장: 로컬 + 클라우드 항상 동시 저장
#
# - 로컬은 인터넷 유무와 관계없이 항상 저장 (오프라인 대비)
# - 클라우드는 가능할 때만 저장 (실패해도 로컬이 유지됨)
# =====================================================================
def save_temp_backup():
    """항상 로컬 저장 + 클라우드 저장 시도. stop_backup 시 동작 안 함."""
    if st.session_state.get("stop_backup", False):
        return
    supplier  = st.session_state.master_info.get("supplier", "")
    evaluator = st.session_state.master_info.get("evaluator", "")
    if not supplier or not evaluator:
        return

    backup_data = {
        "info":         st.session_state.master_info,
        "list":         st.session_state.process_list,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    fname = get_backup_filename(supplier, evaluator)

    # ① 로컬 파일 저장 — 인터넷 없어도 항상 실행
    try:
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"로컬 백업 저장 실패: {e}")

    # ② 클라우드 저장 — 실패해도 로컬이 유지되므로 문제없음
    upload_or_update_gsheet(fname, backup_data)


# =====================================================================
# [v2.2.0] 자동 동기화: 하루 1회
# 로컬 timestamp가 클라우드보다 TS_DIFF_THRESHOLD_SEC 초 이상 앞서면
# 로컬 → 클라우드 덮어쓰기.
# 오프라인 중 작업했던 내용이 다음날 앱 접속 시 자동으로 클라우드에 반영됨.
#
# [v2.4.0] "세션당 1회" → "SYNC_RECHECK_INTERVAL_SEC초 간격으로 재시도"로 변경.
# 기존에는 세션 시작 시 한 번 확인하고 나면(_sync_done=True) 그 세션 동안은
# 다시는 확인하지 않아서, 같은 세션을 계속 켜둔 채로 인터넷이 중간에 복구돼도
# 자동으로 클라우드에 반영되지 않는 문제가 있었음. 이제는 마지막 확인 후
# 일정 시간이 지나면 다시 확인하므로, 인터넷이 돌아온 뒤 아무 저장 동작
# (프로세스 추가/수정 등으로 화면이 다시 그려지는 시점)이 한 번만 있으면
# 자동으로 클라우드에 반영된다.
# =====================================================================
SYNC_RECHECK_INTERVAL_SEC = 60  # 이 시간(초)마다 로컬→클라우드 동기화 필요 여부 재확인


def sync_local_to_cloud_if_needed():
    """로컬이 더 최신이면 클라우드에 덮어씀. 마지막 확인 후 SYNC_RECHECK_INTERVAL_SEC초가
    지나기 전까지는 다시 확인하지 않음 (매번 재시도하며 불필요하게 지연되는 것 방지)."""
    last_check = st.session_state.get("_last_sync_check_ts", 0)
    if time.time() - last_check < SYNC_RECHECK_INTERVAL_SEC:
        return
    st.session_state._last_sync_check_ts = time.time()  # 먼저 기록 (오류 나도 중복 실행 방지)

    supplier  = st.session_state.master_info.get("supplier", "")
    evaluator = st.session_state.master_info.get("evaluator", "")
    if not supplier or not evaluator:
        return

    fname = get_backup_filename(supplier, evaluator)
    if not os.path.exists(fname):
        return  # 로컬 파일 없으면 동기화 불필요

    # 로컬 timestamp 읽기
    try:
        with open(fname, "r", encoding="utf-8") as f:
            local_data = json.load(f)
        local_ts = local_data.get("last_updated", "")
    except Exception:
        return

    # 클라우드 timestamp 읽기
    cloud_ts = get_gsheet_cloud_timestamp(fname)

    if cloud_ts is None:
        # [v2.4.0] 클라우드에 없는 것인지, 아니면 그냥 오프라인이라 못 읽어온 것인지 구분
        # → 오프라인이면 이번엔 조용히 넘어가고, 다음 재시도 때 다시 확인
        if not has_internet():
            return
        # 온라인인데도 클라우드에 없으면 로컬을 업로드
        upload_or_update_gsheet(fname, local_data)
        logger.warning("[Sync] 클라우드에 없음 → 로컬 업로드 완료")
        return

    diff = ts_diff_seconds(local_ts, cloud_ts)
    if diff > TS_DIFF_THRESHOLD_SEC:
        # 로컬이 더 최신 → 클라우드에 덮어씀
        upload_or_update_gsheet(fname, local_data)
        logger.warning(f"[Sync] 로컬이 {diff:.0f}초 최신 → 클라우드 덮어쓰기 완료")


# =====================================================================
# [v2.2.0] 복구 목록 빌드
#
# 판단 기준 (파일별로 개별 비교):
#   1. 클라우드 연결 불가 → 로컬만 표시
#   2. 클라우드 연결 가능 + 로컬이 10초 초과 최신
#      → 로컬이 더 최신 데이터이므로 로컬만 표시
#   3. 클라우드 연결 가능 + 클라우드가 최신(혹은 10초 이내 차이)
#      → 클라우드만 표시
# =====================================================================
def build_backup_options():
    """
    {label: data} 딕트 반환. 라벨 prefix로 출처 구분:
      [☁️ Cloud] — 클라우드 데이터
      [🖥️ Local] — 로컬 데이터 (클라우드보다 최신인 경우만)
    """
    options     = {}
    cloud_avail = get_sheets_service()[0] is not None  # 클라우드 연결 가능 여부

    # 로컬 파일 목록 스캔
    local_files = {}
    for bf in glob.glob(os.path.join(BACKUP_DIR, "*.json")):
        try:
            with open(bf, "r", encoding="utf-8") as f:
                data = json.load(f)
            local_files[bf] = data
        except Exception as e:
            logger.warning(f"로컬 백업 파일 읽기 실패 ({bf}): {e}")

    if not cloud_avail:
        # 케이스 1: 클라우드 연결 불가 → 로컬만 표시
        for bf, data in local_files.items():
            try:
                ts    = data.get("last_updated", "unknown")
                label = (
                    f"[🖥️ Local] {data['info']['supplier']} "
                    f"by {data['info']['evaluator']} ({ts})"
                )
                options[label] = data
            except KeyError:
                continue
        return options

    # 클라우드 연결 가능: 파일별로 timestamp 비교 후 표시 출처 결정
    # 먼저 클라우드 전체 목록을 한 번만 읽어서 캐싱
    service, sheet_id = get_sheets_service()
    cloud_rows = _get_all_rows(service, sheet_id) if service and sheet_id else []

    def get_cloud_data_for_file(fname):
        """cloud_rows에서 fname에 해당하는 (data, ts) 반환. 없으면 (None, None)."""
        base = os.path.basename(fname)
        for row in cloud_rows:
            if len(row) >= 2 and row[0] == base:
                try:
                    d  = json.loads(row[1])
                    ts = row[2] if len(row) >= 3 else None
                    return d, ts
                except Exception:
                    return None, None
        return None, None

    # 로컬 파일과 클라우드를 비교해 표시 출처 결정
    handled_bases = set()
    for bf, local_data in local_files.items():
        base = os.path.basename(bf)
        handled_bases.add(base)
        local_ts             = local_data.get("last_updated", "")
        cloud_data, cloud_ts = get_cloud_data_for_file(bf)

        if cloud_ts is None:
            # 클라우드에 없는 파일 → 로컬 표시
            try:
                label = (
                    f"[🖥️ Local] {local_data['info']['supplier']} "
                    f"by {local_data['info']['evaluator']} ({local_ts})"
                )
                options[label] = local_data
            except KeyError:
                continue
        else:
            diff = ts_diff_seconds(local_ts, cloud_ts)
            if diff > TS_DIFF_THRESHOLD_SEC:
                # 케이스 2: 로컬이 10초 초과 최신 → 로컬만 표시
                try:
                    label = (
                        f"[🖥️ Local] {local_data['info']['supplier']} "
                        f"by {local_data['info']['evaluator']} ({local_ts})"
                    )
                    options[label] = local_data
                except KeyError:
                    continue
            else:
                # 케이스 3: 클라우드가 최신(혹은 동일) → 클라우드만 표시
                try:
                    label = (
                        f"[☁️ Cloud] {cloud_data['info']['supplier']} "
                        f"by {cloud_data['info']['evaluator']} ({cloud_ts})"
                    )
                    options[label] = cloud_data
                except (KeyError, TypeError):
                    continue

    # 로컬에 없고 클라우드에만 있는 항목 추가
    for row in cloud_rows:
        if len(row) >= 2 and row[0] and row[0] not in handled_bases:
            try:
                data  = json.loads(row[1])
                ts    = row[2] if len(row) >= 3 else "unknown"
                label = (
                    f"[☁️ Cloud] {data['info']['supplier']} "
                    f"by {data['info']['evaluator']} ({ts})"
                )
                options[label] = data
            except (json.JSONDecodeError, KeyError):
                continue

    return options


# 다운로드 콜백
def handle_download():
    if st.session_state.get("delete_backup_checkbox", True):
        st.session_state.stop_backup = True
        supplier  = st.session_state.master_info.get("supplier", "")
        evaluator = st.session_state.master_info.get("evaluator", "")
        if supplier and evaluator:
            fname = get_backup_filename(supplier, evaluator)
            delete_gsheet_row_if_exists(fname)
            if os.path.exists(fname):
                try:
                    os.remove(fname)
                except Exception as e:
                    logger.warning(f"로컬 백업 삭제 실패: {e}")
        st.session_state.download_action_status = "deleted"
    else:
        st.session_state.stop_backup = False
        st.session_state.download_action_status = "kept"


def reindex_processes():
    for i, p in enumerate(st.session_state.process_list):
        p["No."] = i + 1


# =====================================================================
# 폼 네비게이션 및 상태 동기화
# =====================================================================
def sync_form_with_state():
    if st.session_state.is_inserting:
        st.session_state.p_name_input  = ""
        st.session_state.p_desc_input  = ""
        st.session_state.p_type_input  = None
        st.session_state.p_score_input = None
        st.session_state.p_remark_input = ""
    else:
        plist = st.session_state.process_list
        idx   = st.session_state.nav_index
        if len(plist) > 0 and 0 <= idx < len(plist):
            p = plist[idx]
            st.session_state.p_name_input   = p["Process"] if p["Process"] != "N/A" else ""
            st.session_state.p_desc_input   = p["Description"]
            st.session_state.p_type_input   = p["Type"]
            st.session_state.p_score_input  = p["PAMI"]
            st.session_state.p_remark_input = p["Remark"]
        else:
            st.session_state.is_inserting   = True
            st.session_state.nav_index      = max(len(plist) - 1, -1)
            st.session_state.p_name_input   = ""
            st.session_state.p_desc_input   = ""
            st.session_state.p_type_input   = None
            st.session_state.p_score_input  = None
            st.session_state.p_remark_input = ""
    st.session_state.show_delete_confirm = False
    st.session_state.pami_form_error     = ""


# =====================================================================
# 순환 네비게이션
# Prev: 첫 번째에서 누르면 → 마지막으로
# Next: 마지막에서 누르면 → 첫 번째로
# =====================================================================
def nav_prev():
    plist = st.session_state.process_list
    if len(plist) == 0:
        return
    if st.session_state.is_inserting:
        st.session_state.is_inserting = False
    elif st.session_state.nav_index > 0:
        st.session_state.nav_index -= 1
    else:
        st.session_state.nav_index = len(plist) - 1
    sync_form_with_state()


def nav_next():
    plist = st.session_state.process_list
    if len(plist) == 0:
        return
    if st.session_state.is_inserting:
        return
    if st.session_state.nav_index < len(plist) - 1:
        st.session_state.nav_index += 1
    else:
        st.session_state.nav_index = 0
    sync_form_with_state()


def nav_new():
    if not st.session_state.is_inserting:
        st.session_state.is_inserting = True
    sync_form_with_state()


def nav_cancel():
    if st.session_state.is_inserting and len(st.session_state.process_list) > 0:
        st.session_state.is_inserting = False
    sync_form_with_state()


def set_delete_confirm():
    st.session_state.show_delete_confirm = True


def cancel_delete():
    st.session_state.show_delete_confirm = False


def delete_current_process():
    idx = st.session_state.nav_index
    if not st.session_state.is_inserting and 0 <= idx < len(st.session_state.process_list):
        st.session_state.process_list.pop(idx)
        reindex_processes()
        if len(st.session_state.process_list) == 0:
            st.session_state.nav_index    = -1
            st.session_state.is_inserting = True
        elif idx >= len(st.session_state.process_list):
            st.session_state.nav_index    = len(st.session_state.process_list) - 1
            st.session_state.is_inserting = False
        else:
            st.session_state.is_inserting = False
        save_temp_backup()
    sync_form_with_state()


# =====================================================================
# [v2.7.0] Description 프리셋 적용
# [v2.8.0] "셀렉트가 안 된다"는 피드백에 따라, 자동 적용(on_change) 대신
# 드롭다운 + "Insert" 버튼의 2단계 방식으로 변경했었음.
# [v2.10.0] "Insert 버튼이 오히려 더 번거롭다"는 피드백에 따라 다시 되돌림.
# 다만 v2.7.0 때와 달리, 이번엔 고른 뒤 드롭다운을 안내 문구로 리셋하지
# 않는다 — 그 "자동 리셋"이 방금 고른 선택지가 화면에서 바로 사라져 보이게
# 만들어 "선택이 안 먹힌다"는 오해를 낳았던 원인으로 보이기 때문. 이번엔
# 드롭다운에 고른 값이 그대로 남아있으면서, 고르는 즉시 Description 칸에도
# 반영되므로 버튼 없이도 지금 뭐가 적용됐는지 바로 확인할 수 있다.
# 프리셋 드롭다운은 st.form 밖에 있어야 선택 즉시 화면이 갱신되고
# Description 칸에 반영된다 (form 안의 위젯은 제출 전까지 값이 반영되지
# 않으므로, 폼 바깥에 둔다).
# =====================================================================
def apply_description_preset():
    """드롭다운에서 프리셋을 고르면 즉시 Description 입력칸을 그 문구로
    채운다 (드롭다운 자신은 리셋하지 않고 고른 값을 그대로 유지). 사용자는
    이후 이어서 타이핑하거나, 전부 지우고 새로 쓸 수 있다."""
    selected = st.session_state.get("desc_preset_select", DESCRIPTION_PRESET_PLACEHOLDER)
    if selected and selected != DESCRIPTION_PRESET_PLACEHOLDER:
        st.session_state.p_desc_input = selected


def process_form_submit():
    p_name   = st.session_state.p_name_input
    p_desc   = st.session_state.p_desc_input
    p_type   = st.session_state.p_type_input
    p_score  = st.session_state.p_score_input
    p_remark = st.session_state.p_remark_input

    if not p_desc or p_type is None or p_score is None:
        st.session_state.pami_form_error = "🚨 Fill in Description, Type, and Score."
        return

    st.session_state.pami_form_error = ""

    if st.session_state.is_inserting:
        target_idx        = st.session_state.nav_index + 1
        is_appending_at_end = (target_idx == len(st.session_state.process_list))
        new_process = {
            "Supplier":   st.session_state.master_info["supplier"],
            "Evaluator":  st.session_state.master_info["evaluator"],
            "No.":        0,
            "Process":    p_name if p_name else "N/A",
            "Type":       p_type,
            "Description": p_desc,
            "PAMI":       p_score,
            "Remark":     p_remark if p_remark else "",
            "Time":       datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.process_list.insert(target_idx, new_process)
        reindex_processes()
        st.session_state.nav_index    = target_idx
        st.session_state.is_inserting = is_appending_at_end
        st.session_state.success_toast = f"Added successfully as No. {target_idx + 1}"
    else:
        idx = st.session_state.nav_index
        p   = st.session_state.process_list[idx]
        p["Process"]     = p_name if p_name else "N/A"
        p["Description"] = p_desc
        p["Type"]        = p_type
        p["PAMI"]        = p_score
        p["Remark"]      = p_remark if p_remark else ""
        p["Time"]        = datetime.now().strftime("%H:%M:%S")
        st.session_state.success_toast = f"Updated No. {idx + 1}"

    save_temp_backup()
    sync_form_with_state()


# =====================================================================
# 앱 시작 시 정리 작업 (세션당 1회)
# =====================================================================
cleanup_old_local_backups()
cleanup_old_gsheet_backups()

# =====================================================================
# 세션 상태 초기화
# =====================================================================
if 'master_info'           not in st.session_state:
    st.session_state.master_info           = {"supplier": "", "evaluator": ""}
if 'process_list'          not in st.session_state:
    st.session_state.process_list          = []
if 'is_evaluating'         not in st.session_state:
    st.session_state.is_evaluating         = False
if 'stop_backup'           not in st.session_state:
    st.session_state.stop_backup           = False
if 'download_action_status' not in st.session_state:
    st.session_state.download_action_status = None
if 'show_confirm_clear'    not in st.session_state:
    st.session_state.show_confirm_clear    = False
if 'pami_form_error'       not in st.session_state:
    st.session_state.pami_form_error       = ""
if 'success_toast'         not in st.session_state:
    st.session_state.success_toast         = ""
if 'show_delete_confirm'   not in st.session_state:
    st.session_state.show_delete_confirm   = False
if 'nav_index'             not in st.session_state:
    st.session_state.nav_index             = -1
if 'is_inserting'          not in st.session_state:
    st.session_state.is_inserting          = True

# 평가 중일 때 동기화 시도 (하루 1회)
if st.session_state.is_evaluating:
    sync_local_to_cloud_if_needed()

# 토스트 메시지 출력
if st.session_state.success_toast:
    st.toast(st.session_state.success_toast)
    st.session_state.success_toast = ""

# =====================================================================
# Step 1: Supplier & Evaluator Info
# =====================================================================
with st.expander("📌 Step 1: Supplier & Evaluator Info", expanded=not st.session_state.is_evaluating):

    if not st.session_state.is_evaluating:
        # [v2.2.0] 복구 목록: 로컬/클라우드 timestamp 비교 후 단일 출처만 표시
        backup_options = build_backup_options()

        if backup_options:
            st.markdown(f"**Check Backup History (Past {BACKUP_RETENTION_DAYS} Days)**")
            selected_backup = st.selectbox(
                "Restore previous session",
                options=["-- Select a backup --"] + list(backup_options.keys())
            )
            if selected_backup != "-- Select a backup --":
                if st.button("Restore Selected Session"):
                    st.session_state.master_info  = backup_options[selected_backup]['info']
                    st.session_state.process_list = backup_options[selected_backup]['list']
                    st.session_state.is_evaluating         = True
                    st.session_state.stop_backup           = False
                    st.session_state.download_action_status = None
                    st.session_state.nav_index    = len(st.session_state.process_list) - 1
                    st.session_state.is_inserting = True
                    sync_form_with_state()
                    st.rerun()
            st.write("---")

    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        supplier_input = st.text_input(
            "Supplier Name - Required*",
            value=st.session_state.master_info["supplier"],
            disabled=st.session_state.is_evaluating
        )
    with sub_col2:
        evaluator_input = st.text_input(
            "Evaluator Name - Required*",
            value=st.session_state.master_info["evaluator"],
            disabled=st.session_state.is_evaluating
        )

    if not st.session_state.is_evaluating:
        if st.button("Go Evaluation"):
            if not supplier_input or not evaluator_input:
                st.error("🚨 Please enter both Supplier Name and Evaluator Name.")
            else:
                st.session_state.master_info["supplier"]  = supplier_input
                st.session_state.master_info["evaluator"] = evaluator_input
                st.session_state.is_evaluating = True
                save_temp_backup()
                st.rerun()

# =====================================================================
# Step 2: PAMI Input
# =====================================================================
if st.session_state.is_evaluating:
    st.info(
        f"📍 Supplier: **{st.session_state.master_info['supplier']}** | "
        f"Evaluator: **{st.session_state.master_info['evaluator']}**"
    )

    # [v2.4.0] 온라인/오프라인 상태 표시
    # 인터넷이 끊겨도 앱이 멈추지 않고 로컬 저장만으로 계속 진행되는데,
    # 지금 클라우드까지 저장되고 있는지 사용자가 바로 알 수 있도록 안내.
    if has_internet():
        st.caption("☁️ Cloud sync: connected — your data is backed up locally and to the cloud.")
    else:
        st.caption(
            "📴 No internet connection — your data is still being saved locally. "
            "It will sync to the cloud automatically once you're back online."
        )

    if st.session_state.stop_backup:
        st.warning("⚠️ CSV downloaded. Automatic backup is now disabled for this session.")

    # =====================================================================
    # Bulk Upload via Excel
    # [v2.3.0] 안내문/에러/경고 메시지를 영어로 변경 (화면 표시용 텍스트만 대상)
    # =====================================================================
    with st.expander("📂 Bulk Upload via Excel", expanded=False):
        st.markdown("**Use the Excel template below to register multiple processes at once.**")

        template_df = pd.DataFrame({
            "Process Name": ["Assembly 1", "Testing"],
            "Description":  ["Engine assembly", "Final check"],
            "Type":         ["MH", "P"],
            "Score":        [4, 5],
            "Remark":       ["Routine check", "Critical step"]
        })
        towrite = io.BytesIO()
        template_df.to_excel(towrite, index=False, engine='openpyxl')
        towrite.seek(0)

        st.download_button(
            label="📥 Download Excel Template",
            data=towrite,
            file_name="OAMI_Bulk_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the template, fill it in, then upload it below."
        )

        uploaded_file = st.file_uploader("Upload filled Excel template", type=["xlsx", "xls"])
        if uploaded_file is not None:
            if st.button("🚀 Upload & Apply Data"):
                try:
                    df_uploaded   = pd.read_excel(uploaded_file)
                    required_cols = ["Description", "Type", "Score"]
                    if not all(col in df_uploaded.columns for col in required_cols):
                        st.error(
                            f"🚨 Invalid Excel template. "
                            f"The following columns are required: {', '.join(required_cols)}"
                        )
                    else:
                        added_count = 0
                        skipped_rows = []
                        for row_idx, row in df_uploaded.iterrows():
                            desc = row.get("Description")
                            if pd.isna(desc) or str(desc).strip() == "":
                                continue
                            raw_type = str(row.get("Type", "")).strip().upper()
                            if raw_type not in VALID_TYPES:
                                skipped_rows.append(
                                    f"Row {row_idx + 2}: Type '{row.get('Type')}' is invalid (MH/P/WIP only)"
                                )
                                continue
                            try:
                                raw_score = int(row.get("Score", 0))
                            except (ValueError, TypeError):
                                raw_score = 0
                            if raw_score not in VALID_SCORES:
                                skipped_rows.append(
                                    f"Row {row_idx + 2}: Score '{row.get('Score')}' is invalid (1~5 only)"
                                )
                                continue
                            new_process = {
                                "Supplier":    st.session_state.master_info["supplier"],
                                "Evaluator":   st.session_state.master_info["evaluator"],
                                "No.":         0,
                                "Process":     str(row.get("Process Name", "N/A")) if pd.notna(row.get("Process Name")) else "N/A",
                                "Type":        raw_type,
                                "Description": str(desc).strip(),
                                "PAMI":        raw_score,
                                "Remark":      str(row.get("Remark", "")) if pd.notna(row.get("Remark")) else "",
                                "Time":        datetime.now().strftime("%H:%M:%S")
                            }
                            st.session_state.process_list.append(new_process)
                            added_count += 1

                        if added_count > 0:
                            reindex_processes()
                            save_temp_backup()
                            st.session_state.is_inserting = True
                            st.session_state.nav_index    = len(st.session_state.process_list) - 1
                            sync_form_with_state()
                            st.success(f"✅ {added_count} process(es) were successfully registered in bulk!")
                        if skipped_rows:
                            st.warning(
                                f"⚠️ {len(skipped_rows)} row(s) were skipped because they are invalid:\n\n"
                                + "\n".join(skipped_rows)
                            )
                        if added_count == 0 and not skipped_rows:
                            st.warning("⚠️ No valid process data found in the Excel file to register.")
                        if added_count > 0:
                            time.sleep(1)
                            st.rerun()
                except Exception as e:
                    st.error(f"🚨 An error occurred while reading the file: {e}")

    st.write("---")

    # =====================================================================
    # 네비게이션 버튼 - 순환 방식
    # =====================================================================
    if st.session_state.process_list or st.session_state.is_inserting:
        nav_c1, nav_c2, nav_c3 = st.columns(3)
        with nav_c1:
            st.button("⬅️ Prev", on_click=nav_prev,
                      disabled=len(st.session_state.process_list) == 0,
                      use_container_width=True)
        with nav_c2:
            st.button("Next ➡️", on_click=nav_next,
                      disabled=st.session_state.is_inserting or len(st.session_state.process_list) == 0,
                      use_container_width=True)
        with nav_c3:
            st.button("➕ New", on_click=nav_new,
                      disabled=st.session_state.is_inserting,
                      use_container_width=True)
        st.write("")

        if st.session_state.is_inserting:
            st.markdown(
                f"<div style='text-align:center; font-weight:bold; color:#0d6efd;'>"
                f"✨ Add New Process as No. {st.session_state.nav_index + 2}</div>",
                unsafe_allow_html=True
            )
        else:
            total       = len(st.session_state.process_list)
            current_num = st.session_state.nav_index + 1
            current_desc = st.session_state.process_list[st.session_state.nav_index].get('Description', '')
            st.markdown(
                f"<div style='text-align:center; font-weight:bold; color:#198754;'>"
                f"✏️ Editing No. {current_num} / {total} : {current_desc}</div>",
                unsafe_allow_html=True
            )

    # =====================================================================
    # [v2.7.0] Description 프리셋 선택
    # [v2.8.0] 드롭다운 + "Insert" 버튼의 2단계 방식으로 변경했었음.
    # [v2.10.0] "Insert 버튼이 더 번거롭다"는 피드백에 따라 버튼 제거,
    # 드롭다운에서 고르는 즉시(on_change) Description 칸에 반영되도록 변경.
    # (자세한 이유는 apply_description_preset() 함수 주석 참고)
    # st.form 밖에 있어야 선택 즉시 반영되므로, 폼 시작 전에 배치한다.
    # =====================================================================
    st.selectbox(
        "📋 Description Preset (optional)",
        options=[DESCRIPTION_PRESET_PLACEHOLDER] + DESCRIPTION_PRESETS,
        key="desc_preset_select",
        on_change=apply_description_preset,
        help="Pick a preset to fill the Description field below right away. "
             "You can keep typing after it, or clear it and write your own."
    )

    # =====================================================================
    # PAMI 입력 폼
    # =====================================================================
    with st.form("pami_input_form", clear_on_submit=False):
        st.markdown("**📝 Step 2: PAMI Input per Process**")
        if st.session_state.pami_form_error:
            st.error(st.session_state.pami_form_error)
        st.text_input("Process Name (Optional)", key="p_name_input")
        st.text_input("Description - Required*", placeholder="Enter details, or pick a preset above...", key="p_desc_input")
        st.write("Type - Required*")
        st.radio("Type", options=["MH", "P", "WIP"], index=None, horizontal=True,
                 label_visibility="collapsed", key="p_type_input")
        st.write("Score (1~5) - Required*")
        st.radio("Score", options=[1, 2, 3, 4, 5], index=None, horizontal=True,
                 label_visibility="collapsed", key="p_score_input")
        st.text_input("Remark (Optional)", key="p_remark_input")
        btn_text = "Save New Process" if st.session_state.is_inserting else "Update Process"
        st.form_submit_button(btn_text, on_click=process_form_submit)

    # =====================================================================
    # Cancel / Delete 버튼
    # =====================================================================
    if st.session_state.process_list or st.session_state.is_inserting:
        act_c1, act_c2 = st.columns(2)
        with act_c1:
            st.button("🚫 Cancel", on_click=nav_cancel,
                      disabled=(not st.session_state.is_inserting) or (len(st.session_state.process_list) == 0),
                      use_container_width=True)
        with act_c2:
            st.button("🗑️ Delete", on_click=set_delete_confirm,
                      disabled=st.session_state.is_inserting,
                      use_container_width=True)

        if st.session_state.show_delete_confirm and not st.session_state.is_inserting:
            st.error(f"⚠️ Are you sure you want to delete Process **No. {st.session_state.nav_index + 1}**?")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.button("✔️ Yes, Delete", on_click=delete_current_process, use_container_width=True)
            with d_col2:
                st.button("❌ Cancel", on_click=cancel_delete, use_container_width=True)

    # =====================================================================
    # Evaluation Summary & Export
    # =====================================================================
    if st.session_state.process_list:
        st.write("---")
        st.markdown("**📊 Evaluation Summary**")

        df   = pd.DataFrame(st.session_state.process_list)
        cols = ["Supplier", "Evaluator", "No.", "Process", "Type", "Description", "PAMI", "Remark", "Time"]
        df   = df[cols]

        oami_avg        = df["PAMI"].mean()
        total_processes = len(df)

        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Total Processes", value=f"{total_processes}")
        with m_col2:
            st.metric(label="Total OAMI Average", value=f"{oami_avg:.2f} / 5.0")

        raw_text = (
            f"Supplier: {st.session_state.master_info['supplier']} | "
            f"Evaluator: {st.session_state.master_info['evaluator']} | "
            f"Processes: {total_processes} | Avg OAMI: {oami_avg:.2f}\n"
        )
        # [v2.2.1] 컬럼 순서 변경: No. > Process > Description > Type > PAMI > Remark > Time
        raw_text += "No.|Process|Description|Type|PAMI|Remark|Time\n"
        for _, row in df.iterrows():
            raw_text += (
                f"{row['No.']}|{row['Process']}|{row['Description']}|"
                f"{row['Type']}|{row['PAMI']}|{row['Remark']}|{row['Time']}\n"
            )

        tab_mobile, tab_pc = st.tabs(["📱 1. Mobile (Text)", "🖥️ 2. PC (Table)"])

        with tab_mobile:
            st.info(
                "💡 **Tip:** Click the button below to copy the text, "
                "or use the 'Open Outlook Mail App' button to auto-fill your email body."
            )
            safe_raw_text  = json.dumps(raw_text)
            copy_text_html = f"""
            <button id="btn-copy-text" onclick="copyToClipboard()" style="width:100%; height:40px; background-color:#0d6efd; color:white; border:none; border-radius:5px; font-weight:bold; font-size:14px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                📋 Copy Text for Outlook
            </button>
            <script>
            function copyToClipboard() {{
                var textToCopy = {safe_raw_text};
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(textToCopy).then(showSuccess).catch(function() {{ fallbackCopy(textToCopy); }});
                }} else {{ fallbackCopy(textToCopy); }}
                function fallbackCopy(text) {{
                    var ta = document.createElement("textarea");
                    ta.value = text;
                    ta.style.cssText = "position:fixed;top:0;left:0;opacity:0;";
                    document.body.appendChild(ta);
                    ta.focus(); ta.select();
                    try {{ document.execCommand('copy') ? showSuccess() : alert("Copy failed."); }}
                    catch(e) {{ alert("Copy failed."); }}
                    document.body.removeChild(ta);
                }}
                function showSuccess() {{
                    var btn = document.getElementById('btn-copy-text');
                    btn.innerText = '✅ Copied!';
                    btn.style.backgroundColor = '#198754';
                    setTimeout(function() {{ btn.innerText='📋 Copy Text for Outlook'; btn.style.backgroundColor='#0d6efd'; }}, 2000);
                }}
            }}
            </script>
            """
            st.html(copy_text_html)
            st.code(raw_text, language="text")

        with tab_pc:
            st.info(
                "💡 Wide and clean table copy optimized for PC environments. "
                "**Note:** Tables cannot be auto-filled in the Mail App. "
                "You must copy and paste this table manually."
            )
            # [v2.2.1] 컬럼 순서 변경: Description을 Type 앞으로
            export_cols = ["No.", "Process", "Description", "Type", "PAMI", "Remark", "Time"]
            html_table  = df[export_cols].to_html(index=False).replace(
                '<table border="1" class="dataframe">',
                '<table border="1" cellpadding="8" style="border-collapse:collapse; text-align:left; font-family:Arial; width:100%;">'
            )
            email_html = (
                f"<div id='pc-email-content' style='background:#f8f9fa; padding:15px;'>"
                f"<strong>OAMI Report: {st.session_state.master_info['supplier']}</strong><br><br>"
                f"<strong>Total Processes:</strong> {total_processes}<br>"
                f"<strong>Average OAMI: <span style='color:blue;'>{oami_avg:.2f} / 5.0</span></strong>"
                f"<br><br>{html_table}</div>"
            )
            copy_table_html = f"""
            <button id="btn-copy-table" onclick='copyPCTable()' style='width:100%; height:40px; background-color:#28a745; color:white; border:none; border-radius:5px; font-weight:bold; font-size:14px; cursor:pointer; margin-bottom:10px; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>
                📋 Copy Table for Outlook
            </button>
            <script>
            function copyPCTable() {{
                var body  = document.getElementById('pc-email-content');
                var range = document.createRange();
                range.selectNode(body);
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                try {{
                    document.execCommand('copy');
                    var btn = document.getElementById('btn-copy-table');
                    btn.innerText='✅ Copied!'; btn.style.backgroundColor='#198754';
                    setTimeout(function() {{ btn.innerText='📋 Copy Table for Outlook'; btn.style.backgroundColor='#28a745'; }}, 2000);
                }} catch(e) {{ alert('Copy failed.'); }}
                window.getSelection().removeAllRanges();
            }}
            </script>
            """
            st.html(f"<div style='max-height:450px; overflow-y:auto;'>{copy_table_html}{email_html}</div>")

        st.write("")

        subject      = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        body_encoded = urllib.parse.quote(raw_text)
        mail_link    = f"mailto:?subject={urllib.parse.quote(subject)}&body={body_encoded}"
        st.markdown(
            f'<a href="{mail_link}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size:14px;">'
            f'📨 Open Outlook Mail App (Auto-fill Text)</button></a>',
            unsafe_allow_html=True
        )

        st.write("---")
        st.warning(
            "⚠️ **Warning:** System backups are temporary and can be deleted at any time. "
            "**You must download the CSV file to keep your data permanently.**"
        )
        st.checkbox(
            "🗑️ Delete system backup file after download (Recommended for security)",
            value=True,
            key="delete_backup_checkbox"
        )

        summary_line  = (
            f"# Supplier: {st.session_state.master_info['supplier']} | "
            f"Evaluator: {st.session_state.master_info['evaluator']} | "
            f"Processes: {total_processes} | Avg OAMI: {oami_avg:.2f}\n"
        )
        # [v2.2.1] CSV 컬럼 순서 변경: Description을 Type 앞으로
        export_df     = df[["No.", "Process", "Description", "Type", "PAMI", "Remark", "Time"]]
        csv_data_bytes = (summary_line + export_df.to_csv(index=False)).encode('utf-8-sig')

        st.download_button(
            label="📥 Download CSV Backup",
            data=csv_data_bytes,
            file_name=f"OAMI_{st.session_state.master_info['supplier']}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            on_click=handle_download
        )

        if st.session_state.download_action_status == "deleted":
            st.success("✅ System report has been deleted. Please save it in the appropriate folder.")
        elif st.session_state.download_action_status == "kept":
            st.info("ℹ️ CSV downloaded successfully. The system backup remains on the server.")

        # 데이터 초기화
        if not st.session_state.show_confirm_clear:
            if st.button("🚨 Clear All Data (Start New)", use_container_width=True):
                st.session_state.show_confirm_clear = True
                st.rerun()
        else:
            st.error("⚠️ Are you sure? This will delete all current progress.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✔️ Yes, Clear Data", use_container_width=True):
                    supplier  = st.session_state.master_info.get("supplier", "")
                    evaluator = st.session_state.master_info.get("evaluator", "")
                    if supplier and evaluator:
                        fname = get_backup_filename(supplier, evaluator)
                        delete_gsheet_row_if_exists(fname)
                        if os.path.exists(fname):
                            try:
                                os.remove(fname)
                            except Exception as e:
                                logger.warning(f"초기화 중 백업 삭제 실패: {e}")
                    for key in ['master_info', 'process_list', 'is_evaluating', 'stop_backup',
                                'download_action_status', 'show_confirm_clear', 'nav_index',
                                'is_inserting', 'show_delete_confirm',
                                'p_name_input', 'p_desc_input', 'p_type_input',
                                'p_score_input', 'p_remark_input',
                                '_last_sync_check_ts']:  # [v2.4.0] _sync_done → _last_sync_check_ts
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            with col_no:
                if st.button("❌ No, Cancel", use_container_width=True):
                    st.session_state.show_confirm_clear = False
                    st.rerun()

# =====================================================================
# Footer - README 링크 (앱 최하단, 항상 표시)
# =====================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#aaa; font-size:13px; padding:4px 0 8px 0;'>"
    "📖 How to use &nbsp;→&nbsp; "
    "<a href='https://github.com/kim2140/oami#readme' target='_blank' style='color:#0d6efd; text-decoration:none;'>English</a>"
    " &nbsp;/&nbsp; "
    "<a href='https://github.com/kim2140/oami/blob/main/README_KO.md' target='_blank' style='color:#0d6efd; text-decoration:none;'>한국어</a>"
    "</div>",
    unsafe_allow_html=True
)