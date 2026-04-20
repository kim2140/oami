import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse 
import json # [NEW] 데이터 복구용 JSON 처리를 위해 추가
import streamlit.components.v1 as components

# 페이지 설정: 아이콘(📝)과 탭 제목 설정
st.set_page_config(page_title="Supplier OAMI", page_icon="📝", layout="centered")

# 메인 타이틀 (App으로 명칭 변경)
st.title("📝 Supplier OAMI Evaluation App")

# 1. 세션 상태 초기화
if 'master_info' not in st.session_state:
    st.session_state.master_info = {"supplier": "", "evaluator": ""}
if 'process_list' not in st.session_state:
    st.session_state.process_list = []

# [NEW] 데이터 복구(Restore) 기능 로직
# 사용자가 복구 코드를 붙여넣으면 세션 데이터를 즉시 재구성합니다.
def restore_data(json_str):
    try:
        data = json.loads(json_str)
        st.session_state.master_info = data['info']
        st.session_state.process_list = data['list']
        st.success("✅ Data restored successfully!")
    except:
        st.error("🚨 Invalid recovery code.")

# 2. 업체 및 평가자 정보 입력 (필수값 검증)
with st.expander("📌 Step 1: Supplier & Evaluator Info", expanded=st.session_state.master_info["supplier"] == ""):
    # [NEW] 데이터 복구 섹션 (가장 상단에 배치하여 새로고침 시 바로 복구 가능하게 함)
    recovery_input = st.text_input("Recovery Code (Paste here to restore if page refreshed)", placeholder="Paste your backup code here...")
    if st.button("Restore Data"):
        restore_data(recovery_input)
    
    st.write("---")
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        supplier = st.text_input("Supplier Name - Required*", value=st.session_state.master_info["supplier"])
    with sub_col2:
        evaluator = st.text_input("Evaluator Name - Required*", value=st.session_state.master_info["evaluator"])
    
    if st.button("Go Evaluation"):
        if not supplier or not evaluator:
            st.error("🚨 Please enter both Supplier Name and Evaluator Name.")
        else:
            st.session_state.master_info["supplier"] = supplier
            st.session_state.master_info["evaluator"] = evaluator
            st.success("Ready for evaluation.")

# 업체 정보가 설정된 경우에만 입력창 표시
if st.session_state.master_info["supplier"] and st.session_state.master_info["evaluator"]:
    st.info(f"📍 Supplier: **{st.session_state.master_info['supplier']}** | Evaluator: **{st.session_state.master_info['evaluator']}**")
    
    # 3. 공정별 상세 평가 입력 (Radio 버튼 및 Remark 필드 포함)
    with st.form("pami_input_form", clear_on_submit=True):
        st.subheader("📝 Step 2: PAMI Input per Process")
        
        p_name = st.text_input("Process Name (Optional)")
        p_desc = st.text_input("Description - Required*", placeholder="Enter details...")

        st.write("Process Type - Required*")
        p_type = st.radio("Process Type Select", options=["MH", "P", "WIP"], index=None, horizontal=True, label_visibility="collapsed")
        
        st.write("PAMI Score (1: Manual ~ 5: Fully Automated) - Required*")
        p_score = st.radio("PAMI Score Select", options=[1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed")
        
        p_remark = st.text_input("Remark (Optional)", placeholder="Add any specific notes...")
        
        if st.form_submit_button("Add to List"):
            if not p_desc or p_type is None or p_score is None:
                st.error("🚨 Required fields: Description, Process Type, PAMI Score.")
            else:
                current_no = len(st.session_state.process_list) + 1
                new_process = {
                    "No.": current_no,
                    "Supplier": st.session_state.master_info["supplier"],
                    "Evaluator": st.session_state.master_info["evaluator"],
                    "Process": p_name if p_name else "N/A",
                    "Description": p_desc,
                    "Type": p_type,
                    "PAMI": p_score,
                    "Remark": p_remark if p_remark else "",
                    "Time": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.process_list.append(new_process)
                st.toast(f"Added No.{current_no}")

    # 4. 결과 요약 및 내보내기
    if st.session_state.process_list:
        st.write("---")
        
        # [NEW] 실시간 자동 백업 코드 생성
        # 데이터가 하나라도 입력되면 하단에 복구용 JSON 코드를 자동으로 만듭니다.
        backup_dict = {
            "info": st.session_state.master_info,
            "list": st.session_state.process_list
        }
        backup_json = json.dumps(backup_dict)

        st.subheader("📊 Evaluation Summary")
        
        df = pd.DataFrame(st.session_state.process_list)
        cols = ["Supplier", "Evaluator", "No.", "Process", "Type", "Description", "PAMI", "Remark", "Time"]
        df = df[cols]
        
        oami_avg = df["PAMI"].mean()
        total_processes = len(df)
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Total Processes", value=f"{total_processes}")
        with m_col2:
            st.metric(label="Total OAMI Average", value=f"{oami_avg:.2f} / 5.0")
        
        # 복사 방식 탭 설정
        tab_text, tab_table, tab_recovery = st.tabs(["📱 1. Mobile (Text Copy)", "🖥️ 2. PC (Table Copy)", "🛡️ 3. Safety Backup"])
        
        with tab_text:
            st.info("💡 Best for Mobile. Click the copy icon.")
            text_report = f"OAMI Evaluation Report\nSupplier: {st.session_state.master_info['supplier']}\nAvg OAMI: {oami_avg:.2f}\n"
            text_report += f"No. | Process | Type | PAMI | Description | Remark | Time\n"
            for i, row in df.iterrows():
                text_report += f"{row['No.']} | {row['Process']} | {row['Type']} | {row['PAMI']}pt | {row['Description']} | {row['Remark']} | {row['Time']}\n"
            st.code(text_report, language="text")

        with tab_table:
            st.info("💡 For PC Outlook. Click the Green button below.")
            html_table = df.to_html(index=False).replace('<table border="1" class="dataframe">', '<table border="1" cellpadding="8" style="border-collapse: collapse; text-align: left; font-family: Arial; width: 100%;">')
            email_content_html = f"<div id='email-content' style='background:#f8f9fa; padding:15px;'><h3>OAMI Report: {st.session_state.master_info['supplier']}</h3><p>Avg: {oami_avg:.2f}</p>{html_table}</div>"
            custom_html = f"<button onclick='copyRichText()' style='width:100%;height:40px;background:#28a745;color:white;border:none;border-radius:5px;cursor:pointer;'>📋 Copy Table for Outlook</button>{email_content_html}<script>function copyRichText(){{var body=document.getElementById('email-content');var range=document.createRange();range.selectNode(body);window.getSelection().removeAllRanges();window.getSelection().addRange(range);document.execCommand('copy');alert('Copied!');}}</script>"
            components.html(custom_html, height=450, scrolling=True)

        with tab_recovery:
            st.warning("⚠️ If you accidentally refresh the page, use this code to recover your data.")
            st.code(backup_json, language="json")

        st.write("") 
        subject = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}"
        st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size: 16px;">📨 Open Outlook Mail App</button></a>', unsafe_allow_html=True)

        st.write("---")
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(label="📥 Download CSV Backup", data=csv_data, file_name=f"OAMI_{st.session_state.master_info['supplier']}.csv", mime="text/csv", use_container_width=True)

        if st.button("🚨 Clear All Data (Start New)", use_container_width=True):
            st.session_state.master_info = {"supplier": "", "evaluator": ""}
            st.session_state.process_list = []
            st.rerun()