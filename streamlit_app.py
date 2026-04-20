import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse 

# 페이지 설정: 아이폰 등 모바일 브라우저 최적화
st.set_page_config(page_title="OAMI/PAMI Evaluation Tool", layout="centered")
st.title("🏭 OAMI Field Evaluation System")

# 1. 세션 상태 초기화: 앱을 새로고침하기 전까지 입력한 데이터를 임시 보관합니다.
if 'master_info' not in st.session_state:
    st.session_state.master_info = {"supplier": "", "evaluator": ""}
if 'process_list' not in st.session_state:
    st.session_state.process_list = []

# 2. 업체 및 평가자 정보 입력 (최초 1회 설정)
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

# 업체 정보가 설정된 경우에만 입력창을 보여줍니다.
if st.session_state.master_info["supplier"]:
    st.info(f"📍 Supplier: **{st.session_state.master_info['supplier']}** | Evaluator: **{st.session_state.master_info['evaluator']}**")
    
    # 3. 공정별 상세 평가 입력 (반복 입력 구간)
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

    # 4. 결과 확인 및 내보내기 옵션
    if st.session_state.process_list:
        st.write("---")
        st.subheader("📊 Evaluation Summary")
        
        df = pd.DataFrame(st.session_state.process_list)
        oami_avg = df["PAMI"].mean()
        st.metric(label="Total OAMI Average", value=f"{oami_avg:.2f} / 5.0")
        
        # [UPDATE] Outlook에 복사하기 좋도록 HTML 표(Table) 형태로 디자인을 생성합니다.
        # 판다스 데이터프레임을 HTML 표 코드로 변환하고, Outlook에서 깨지지 않게 테두리(border) 속성을 입힙니다.
        html_table = df.to_html(index=False)
        html_table = html_table.replace(
            '<table border="1" class="dataframe">', 
            '<table border="1" cellpadding="8" style="border-collapse: collapse; text-align: left; font-family: Arial, sans-serif; width: 100%;">'
        )
        
        # 이메일 상단에 들어갈 요약 정보와 HTML 표를 합칩니다.
        email_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9;">
            <h3 style="color: #333;">OAMI Evaluation Report</h3>
            <p><strong>Supplier:</strong> {st.session_state.master_info['supplier']}</p>
            <p><strong>Evaluator:</strong> {st.session_state.master_info['evaluator']}</p>
            <p><strong>Average OAMI:</strong> <span style="color: blue; font-size: 18px; font-weight: bold;">{oami_avg:.2f} / 5.0</span></p>
            <br>
            {html_table}
        </div>
        """

        st.subheader("📧 Email Body (Copy & Paste)")
        st.info("💡 아래 박스 안의 내용을 마우스로 드래그하여 복사(Ctrl+C)한 뒤, 메일 본문에 붙여넣기(Ctrl+V) 하세요.")
        
        # 생성된 HTML 표를 화면에 출력합니다.
        st.markdown(email_html, unsafe_allow_html=True)
        st.write("") # 간격 띄우기

        # [UPDATE] 메일 본문(body)은 사용자가 직접 표를 붙여넣을 것이므로 비워두고, 제목(subject)만 자동으로 입력된 새 메일 창을 띄웁니다.
        subject = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}"
        
        st.markdown(
            f'<a href="{mail_link}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size: 16px;">'
            f'📨 1. Open Outlook (새 메일 창 열기)</button></a>', 
            unsafe_allow_html=True
        )

        st.write("---")
        
        # CSV 백업은 만약을 위해 유지해둡니다.
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 2. Download CSV Backup (선택사항)",
            data=csv_data,
            file_name=f"OAMI_{st.session_state.master_info['supplier']}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        if st.button("🚨 Clear All Data (Start New)", use_container_width=True):
            st.session_state.master_info = {"supplier": "", "evaluator": ""}
            st.session_state.process_list = []
            st.rerun()