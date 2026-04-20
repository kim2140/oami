import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import json
import os # 파일 존재 여부 확인을 위해 추가

# 페이지 설정: 브라우저 탭 아이콘 및 제목 설정
st.set_page_config(page_title="Supplier OAMI", page_icon="📝", layout="centered")

# 메인 타이틀
st.title("📝 Supplier OAMI Evaluation App")

# 백업 파일 경로 정의 (서버 내 임시 파일)
BACKUP_FILE = "oami_temp_backup.json"

# [NEW] 실시간 자동 백업 함수: 데이터가 변할 때마다 호출됩니다.
def save_temp_backup():
    backup_data = {
        "info": st.session_state.master_info,
        "list": st.session_state.process_list,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=4)

# [NEW] 백업 데이터 불러오기 함수
def load_temp_backup():
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# 1. 세션 상태 초기화
if 'master_info' not in st.session_state:
    st.session_state.master_info = {"supplier": "", "evaluator": ""}
if 'process_list' not in st.session_state:
    st.session_state.process_list = []

# 2. Step 1: 업체 및 평가자 정보 (백업 확인 기능 포함)
with st.expander("📌 Step 1: Supplier & Evaluator Info", expanded=st.session_state.master_info["supplier"] == ""):
    
    # [NEW] 백업 데이터 확인 섹션
    st.subheader("Check Backup History")
    backup = load_temp_backup()
    if backup:
        st.warning(f"Found recent backup: {backup['info']['supplier']} by {backup['info']['evaluator']} ({backup['last_updated']})")
        if st.button("Restore Previous Session"):
            st.session_state.master_info = backup['info']
            st.session_state.process_list = backup['list']
            st.rerun()
    else:
        st.info("No temporary backup found.")
    
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
            save_temp_backup() # 정보 확정 시 자동 백업
            st.success("Ready for evaluation.")

# 업체 정보가 설정된 경우에만 2단계 활성화
if st.session_state.master_info["supplier"] and st.session_state.master_info["evaluator"]:
    st.info(f"📍 Supplier: **{st.session_state.master_info['supplier']}** | Evaluator: **{st.session_state.master_info['evaluator']}**")
    
    # 3. Step 2: 공정별 상세 평가 입력
    with st.form("pami_input_form", clear_on_submit=True):
        st.subheader("📝 Step 2: PAMI Input per Process")
        
        p_name = st.text_input("Process Name (Optional)")
        p_desc = st.text_input("Description - Required*", placeholder="Enter details...")

        st.write("Process Type - Required*")
        p_type = st.radio("Type", options=["MH", "P", "WIP"], index=None, horizontal=True, label_visibility="collapsed")
        
        st.write("PAMI Score (1~5) - Required*")
        p_score = st.radio("Score", options=[1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed")
        
        p_remark = st.text_input("Remark (Optional)")
        
        if st.form_submit_button("Add to List"):
            if not p_desc or p_type is None or p_score is None:
                st.error("🚨 Fill in Description, Type, and Score.")
            else:
                current_no = len(st.session_state.process_list) + 1
                new_process = {
                    "Supplier": st.session_state.master_info["supplier"],
                    "Evaluator": st.session_state.master_info["evaluator"],
                    "No.": current_no,
                    "Process": p_name if p_name else "N/A",
                    "Type": p_type,
                    "Description": p_desc,
                    "PAMI": p_score,
                    "Remark": p_remark if p_remark else "",
                    "Time": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.process_list.append(new_process)
                save_temp_backup() # [NEW] 프로세스 추가 시마다 실시간 자동 백업
                st.toast(f"Added No.{current_no}")

    # 4. 결과 요약 및 내보내기
    if st.session_state.process_list:
        st.write("---")
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
        
        # 복사 옵션 탭
        tab_text, tab_table = st.tabs(["📱 1. Mobile (Text)", "🖥️ 2. PC (Table)"])
        
        with tab_text:
            text_report = f"OAMI Evaluation: {st.session_state.master_info['supplier']}\nAvg: {oami_avg:.2f}\n"
            text_report += "No | Type | Process | PAMI | Description\n"
            for _, row in df.iterrows():
                text_report += f"{row['No']} | {row['Type']} | {row['Process']} | {row['PAMI']}pt | {row['Description']}\n"
            st.code(text_report, language="text")

        with tab_table:
            # HTML 표 생성
            import streamlit.components.v1 as components
            html_table = df.to_html(index=False).replace('<table border="1" class="dataframe">', '<table border="1" cellpadding="8" style="border-collapse: collapse; text-align: left; font-family: Arial; width: 100%;">')
            email_html = f"<div id='email-content' style='background:#f8f9fa; padding:15px;'><h3>OAMI Report: {st.session_state.master_info['supplier']}</h3><p>Processes: {total_processes} / Avg: {oami_avg:.2f}</p>{html_table}</div>"
            copy_button_html = f"<button onclick='copyTable()' style='width:100%;height:40px;background:#28a745;color:white;border:none;border-radius:5px;cursor:pointer;font-weight:bold;'>📋 Copy Table for Outlook</button><script>function copyTable(){{var body=document.getElementById('email-content');var range=document.createRange();range.selectNode(body);window.getSelection().removeAllRanges();window.getSelection().addRange(range);document.execCommand('copy');alert('Table Copied!');}}</script>"
            components.html(copy_button_html + email_html, height=450, scrolling=True)

        # Outlook 실행
        subject = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}"
        st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold;">📨 Open Outlook Mail App</button></a>', unsafe_allow_html=True)

        st.write("---")
        # 데이터 리셋 (백업 파일도 함께 삭제)
        if st.button("🚨 Clear All Data (Start New)", use_container_width=True):
            if os.path.exists(BACKUP_FILE):
                os.remove(BACKUP_FILE)
            st.session_state.master_info = {"supplier": "", "evaluator": ""}
            st.session_state.process_list = []
            st.rerun()