# streamlit: 웹/모바일 UI 구성을 위한 프레임워크입니다.
# pandas: 데이터 표 관리 및 평균 계산, 엑셀 변환을 위해 사용합니다.
# io.BytesIO: 생성된 엑셀 파일을 메모리에서 직접 다운로드하기 위해 사용합니다.
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# 페이지 설정: 모바일에서 보기 편하도록 레이아웃을 설정합니다.
# 아이폰의 사파리(Safari) 브라우저에서도 화면 너비에 맞춰 자동으로 최적화되도록 돕는 기본 설정입니다.
st.set_page_config(page_title="OAMI/PAMI 평가 도구", layout="centered")

# 모든 코드에 상세한 주석을 추가하고 복사 붙여넣기가 용이하도록 작성합니다.
st.title("🏭 OAMI 현장 평가 시스템")

# 1. 세션 상태 초기화: 앱이 새로고침되어도 입력 중인 업체 정보와 공정 리스트가 유지되도록 합니다.
if 'master_info' not in st.session_state:
    st.session_state.master_info = {"supplier": "", "evaluator": ""}
if 'process_list' not in st.session_state:
    st.session_state.process_list = []

# 2. 업체 및 평가자 정보 입력 (최초 1회 설정)
# expander를 사용하여 입력 후에는 화면을 접어 공간을 확보할 수 있게 합니다.
with st.expander("📌 1단계: 업체 및 평가자 정보 설정", expanded=st.session_state.master_info["supplier"] == ""):
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        supplier = st.text_input("방문 업체명", value=st.session_state.master_info["supplier"])
    with sub_col2:
        evaluator = st.text_input("평가자 성함", value=st.session_state.master_info["evaluator"])
    
    if st.button("정보 고정하기"):
        st.session_state.master_info["supplier"] = supplier
        st.session_state.master_info["evaluator"] = evaluator
        st.success("업체 정보가 설정되었습니다. 이제 하단에서 공정별 점수를 입력하세요.")

# 업체 정보가 입력된 경우에만 공정 평가 입력을 활성화합니다.
if st.session_state.master_info["supplier"]:
    st.info(f"📍 현재 평가 중: **{st.session_state.master_info['supplier']}** (평가자: {st.session_state.master_info['evaluator']})")
    
    # 3. 공정별 상세 평가 입력 (반복 입력 구간)
    # 아이폰 키보드가 올라왔을 때도 화면 짤림 없이 부드럽게 스크롤되며 입력 폼이 유지됩니다.
    with st.form("pami_input_form", clear_on_submit=True):
        st.subheader("📝 2단계: 공정별 PAMI 입력")
        
        # [UPDATE] 모바일 기기에서의 시각적 순서(위->아래)를 고려하여 배치를 수정했습니다.
        # 모바일에서는 col1 내용이 먼저 보이고, 그 아래로 col2 내용이 이어집니다.
        col1, col2 = st.columns(2)
        with col1:
            # [UPDATE] 공정명은 필수가 아니므로(선택사항) 라벨에 명시했습니다.
            p_name = st.text_input("Process (공정명) - 선택사항")
            # [UPDATE] Description을 Process Type보다 위로 올리기 위해 col1에 먼저 배치했습니다.
            p_desc = st.text_input("Description (상세 내용) - 필수*")
            
        with col2:
            # [UPDATE] Process Type의 기본값을 없애기 위해 index=None을 추가했습니다. 빈칸 상태로 시작합니다.
            p_type = st.selectbox(
                "Process Type - 필수*", 
                ["MH (Material Handling)", "Process", "WIP (Work in Process)"],
                index=None, 
                placeholder="유형을 선택하세요"
            )
            
        # [UPDATE] PAMI 점수 입력을 기존 숫자 입력(number_input)에서 라디오 버튼(radio)으로 변경했습니다.
        # 모바일(아이폰) 사용성을 극대화하기 위해 horizontal=True 속성을 추가하여 1~5 버튼이 가로로 넓게 나열되도록 했습니다.
        st.write("PAMI 점수 (1점: 수작업 ~ 5점: 완전 자동화) - 필수*")
        p_score = st.radio(
            "PAMI 점수 선택", 
            options=[1, 2, 3, 4, 5], 
            index=None, # [UPDATE] 기본값(default 3점)을 제거했습니다. 사용자가 무조건 터치해야 합니다.
            horizontal=True,
            label_visibility="collapsed" # 위의 st.write로 라벨을 대신하므로, 라디오 버튼 자체의 라벨은 숨깁니다.
        )
        
        add_button = st.form_submit_button("공정 추가")
        
        if add_button:
            # [UPDATE] '공정명(Process)'을 제외한 나머지 항목들을 필수값(Mandatory)으로 검증하는 로직입니다.
            missing_fields = []
            if not p_desc:
                missing_fields.append("Description")
            if p_type is None:
                missing_fields.append("Process Type")
            if p_score is None:
                missing_fields.append("PAMI 점수")
                
            if missing_fields:
                # 필수값이 하나라도 누락되었을 경우 에러 메시지를 띄우고 데이터 추가를 중단합니다.
                st.error(f"🚨 다음 필수 항목을 입력해주세요: {', '.join(missing_fields)}")
            else:
                # 공정명이 비어있을 경우 엑셀에서 보기 좋게 처리하기 위해 기본 텍스트를 넣습니다.
                final_p_name = p_name if p_name else ""
                
                # 입력된 데이터를 리스트에 추가합니다.
                new_process = {
                    "Process": final_p_name,
                    "Description": p_desc,
                    "Type": p_type,
                    "PAMI Score": p_score,
                    "Timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.process_list.append(new_process)
                st.toast("✅ 공정이 성공적으로 추가되었습니다!")

    # 4. 결과 확인 및 OAMI 계산
    if st.session_state.process_list:
        st.write("---")
        st.subheader("📊 평가 결과 요약")
        
        df = pd.DataFrame(st.session_state.process_list)
        
        # 전체 OAMI 평균 계산 (PAMI 점수들의 평균)
        oami_avg = df["PAMI Score"].mean()
        
        # 상단에 큰 글씨로 OAMI 평균을 표시합니다.
        st.metric(label=f"{st.session_state.master_info['supplier']} 최종 OAMI 평균", value=f"{oami_avg:.2f} / 5.0")
        
        # 입력된 공정별 리스트 표시
        st.dataframe(df, use_container_width=True)

        # 5. 엑셀 다운로드 기능
        # 업체 정보와 공정 정보를 합쳐서 최종 리포트용 데이터프레임을 만듭니다.
        final_df = df.copy()
        final_df.insert(0, "Evaluator", st.session_state.master_info["evaluator"])
        final_df.insert(0, "Supplier", st.session_state.master_info["supplier"])
        final_df["Final OAMI"] = oami_avg

        # 라이브러리(xlsxwriter)가 설치되어 있지 않을 때 빨간색 에러 코드로 앱이 멈추는 것을 방지합니다.
        # try-except 구문을 사용하여 사용자에게 설치 안내 메시지를 띄워주도록 안전하게 변경했습니다.
        @st.cache_data
        def convert_df_to_excel(df_to_convert):
            try:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_to_convert.to_excel(writer, index=False, sheet_name='OAMI_Report')
                return output.getvalue()
            except ModuleNotFoundError:
                # 에러 발생 시 파일 변환을 중단하고 알림을 보냅니다.
                return None

        excel_data = convert_df_to_excel(final_df)
        
        # excel_data가 정상적으로 생성되었을 때만 다운로드 버튼을 보여줍니다.
        if excel_data is not None:
            # 아이폰에서 다운로드 버튼을 누르면 사파리의 다운로드 관리자를 통해 '파일' 앱에 정상적으로 저장됩니다.
            st.download_button(
                label="📥 평가 결과 엑셀 파일로 받기",
                data=excel_data,
                file_name=f"OAMI_평가_{st.session_state.master_info['supplier']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("🚨 엑셀 변환 라이브러리가 누락되었습니다. 환경 설정(Requirements)에 'xlsxwriter'를 추가해 주세요.")
        
        # 데이터 초기화 버튼 (다음 업체 방문 시 사용)
        if st.button("🚨 모든 데이터 초기화 (다음 업체 시작)"):
            st.session_state.master_info = {"supplier": "", "evaluator": ""}
            st.session_state.process_list = []
            st.rerun()