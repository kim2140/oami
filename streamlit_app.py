import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse 

# 페이지 설정: 모바일 브라우저 최적화
st.set_page_config(page_title="Supplier OAMI", page_icon="📋", layout="centered")
st.title("📊 Supplier OAMI Evaluation System")

# 1. 세션 상태 초기화
if 'master_info' not in st.session_state:
    st.session_state.master_info = {"supplier": "", "evaluator": ""}
if 'process_list' not in st.session_state:
    st.session_state.process_list = []

# 2. 업체 및 평가자 정보 입력
with st.expander("📌 Step 1: Supplier & Evaluator Info", expanded=st.session_state.master_info["supplier"] == ""):
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        supplier = st.text_input("Supplier Name", value=st.session_state.master_info["supplier"])
    with sub_col2:
        evaluator = st.text_input("Evaluator Name", value=st.session_state.master_info["evaluator"])
    
    if st.button("Confirm Information"):
        st.session_state.master_info["supplier"] = supplier
        st.session_state.master_info["evaluator"] = evaluator
        st.success("Evaluator info confirmed.")

# 3. 공정별 상세 평가 입력
if st.session_state.master_info["supplier"]:
    st.info(f"📍 Supplier: **{st.session_state.master_info['supplier']}** | Evaluator: **{st.session_state.master_info['evaluator']}**")
    
    with st.form("pami_input_form", clear_on_submit=True):
        st.subheader("📝 Step 2: PAMI Input per Process")
        
        p_name = st.text_input("Process Name (Optional)")
        p_desc = st.text_input("Description - Required*", placeholder="Enter process description...")

        p_type = st.selectbox(
            "Process Type - Required*", 
            ["MH (Material Handling)", "Process", "WIP (Work in Process)"],
            index=None, 
            placeholder="Select Type..."
        )
        
        st.write("PAMI Score (1: Manual ~ 5: Fully Automated) - Required*")
        p_score = st.radio(
            "PAMI Score Select", 
            options=[1, 2, 3, 4, 5], 
            index=None, 
            horizontal=True,
            label_visibility="collapsed" 
        )
        
        add_button = st.form_submit_button("Add to List")
        
        if add_button:
            if not p_desc or p_type is None or p_score is None:
                st.error("🚨 Please fill in all required fields (Description, Type, Score).")
            else:
                new_process = {
                    "Supplier": st.session_state.master_info["supplier"],
                    "Evaluator": st.session_state.master_info["evaluator"],
                    "Process": p_name if p_name else "N/A",
                    "Description": p_desc,
                    "Type": p_type,
                    "PAMI": p_score,
                    "Time": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.process_list.append(new_process)
                st.toast(f"Added: {p_name if p_name else 'Process'}")

    # 4. 결과 확인 및 내보내기 (모바일 최적화 UI 적용)
    if st.session_state.process_list:
        st.write("---")
        st.subheader("📊 Evaluation Summary")
        
        df = pd.DataFrame(st.session_state.process_list)
        oami_avg = df["PAMI"].mean()
        st.metric(label="Total OAMI Average", value=f"{oami_avg:.2f} / 5.0")
        
        # [UPDATE] 모바일 환경의 복사 오류를 해결하기 위해 탭(Tab) 구조로 분리했습니다.
        tab_text, tab_table = st.tabs(["📱 1. Text Copy (모바일용)", "🖥️ 2. Table Copy (수동 복사용)"])
        
        with tab_text:
            st.info("💡 스마트폰 브라우저에서는 이 방식이 가장 확실합니다. 아래 박스 우측 상단의 **'복사 아이콘(문서 2개 겹친 모양)'**을 누르면 전체 내용이 즉시 복사됩니다.")
            
            # 메일 본문에 보기 좋게 들어갈 구조화된 텍스트 템플릿을 생성합니다.
            text_report = f"====================================\n"
            text_report += f"      OAMI Evaluation Report\n"
            text_report += f"====================================\n"
            text_report += f"▶ Supplier : {st.session_state.master_info['supplier']}\n"
            text_report += f"▶ Evaluator: {st.session_state.master_info['evaluator']}\n"
            text_report += f"▶ Avg OAMI : {oami_avg:.2f} / 5.0\n"
            text_report += f"------------------------------------\n\n"
            
            for i, row in df.iterrows():
                text_report += f"[{row['Type']}] {row['Process']}\n"
                text_report += f" └ Score: {row['PAMI']}pt | Desc: {row['Description']}\n\n"
            
            text_report += f"===================================="
            
            # st.code는 모바일에서도 100% 작동하는 전용 복사 버튼을 제공합니다.
            st.code(text_report, language="markdown")

        with tab_table:
            st.info("💡 표 형태를 유지하고 싶으시다면, 아래 표 영역을 손가락으로 **길게 눌러(Long-press)** 전체를 블록 지정한 뒤 복사해 주세요.")
            
            html_table = df.to_html(index=False)
            html_table = html_table.replace(
                '<table border="1" class="dataframe">', 
                '<table border="1" cellpadding="8" style="border-collapse: collapse; text-align: left; font-family: Arial, sans-serif; width: 100%; background-color: #ffffff;">'
            )
            
            email_html = f"""
            <div style="font-family: Arial, sans-serif; padding: 10px; border: 1px solid #ddd; background-color: #f8f9fa;">
                <h3 style="color: #333; margin-top:0;">OAMI Report: {st.session_state.master_info['supplier']}</h3>
                <p><strong>Average OAMI: <span style="color: blue;">{oami_avg:.2f} / 5.0</span></strong></p>
                {html_table}
            </div>
            """
            st.markdown(email_html, unsafe_allow_html=True)

        st.write("") # 간격
        
        # Outlook 실행 버튼 (두 탭 공통 하단 배치)
        subject = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}"
        
        st.markdown(
            f'<a href="{mail_link}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
            f'📨 Open Outlook (복사 후 클릭)</button></a>', 
            unsafe_allow_html=True
        )

        st.write("---")
        
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Download CSV Backup",
            data=csv_data,
            file_name=f"OAMI_{st.session_state.master_info['supplier']}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        if st.button("🚨 Clear All Data (Start New)", use_container_width=True):
            st.session_state.master_info = {"supplier": "", "evaluator": ""}
            st.session_state.process_list = []
            st.rerun()