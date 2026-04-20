import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import json
import os
import glob 
import time 
import streamlit.components.v1 as components

# 브라우저 탭 아이콘 및 제목 영문 설정
st.set_page_config(page_title="Supplier OAMI", page_icon="📝", layout="centered")

# 메인 타이틀
st.title("📝 Supplier OAMI Evaluation App")

# 백업 전용 폴더 설정
BACKUP_DIR = "oami_backups"
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# 파일명 생성 함수
def get_backup_filename(supplier, evaluator):
    safe_sup = "".join(c for c in supplier if c.isalnum() or c in " _-").strip()
    safe_eval = "".join(c for c in evaluator if c.isalnum() or c in " _-").strip()
    return os.path.join(BACKUP_DIR, f"{safe_sup}_{safe_eval}.json")

# 오래된 백업 파일 정리 함수 (3일 경과 시 삭제)
def cleanup_old_backups():
    now = time.time()
    for f in glob.glob(os.path.join(BACKUP_DIR, "*.json")):
        if os.stat(f).st_mtime < now - (3 * 86400):
            try:
                os.remove(f)
            except:
                pass

# 실시간 자동 백업 함수
def save_temp_backup():
    if st.session_state.get("stop_backup", False):
        return
    supplier = st.session_state.master_info.get("supplier", "")
    evaluator = st.session_state.master_info.get("evaluator", "")
    if not supplier or not evaluator: return

    backup_data = {
        "info": st.session_state.master_info,
        "list": st.session_state.process_list,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    fname = get_backup_filename(supplier, evaluator)
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=4)

# 엑셀 다운로드 클릭 시 실행될 콜백 함수
def handle_download():
    st.session_state.stop_backup = True
    supplier = st.session_state.master_info.get("supplier", "")
    evaluator = st.session_state.master_info.get("evaluator", "")
    if supplier and evaluator:
        fname = get_backup_filename(supplier, evaluator)
        if os.path.exists(fname):
            try:
                os.remove(fname)
            except:
                pass
    st.session_state.download_completed = True

# 폼 제출 프로세스 (조건부 초기화)
def process_form_submit():
    p_name = st.session_state.p_name_input
    p_desc = st.session_state.p_desc_input
    p_type = st.session_state.p_type_input
    p_score = st.session_state.p_score_input
    p_remark = st.session_state.p_remark_input
    
    if not p_desc or p_type is None or p_score is None:
        st.session_state.pami_form_error = "🚨 Fill in Description, Type, and Score."
    else:
        st.session_state.pami_form_error = ""
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
        save_temp_backup()
        st.session_state.success_toast = f"Added No.{current_no}"
        
        # 입력 필드 초기화
        st.session_state.p_name_input = ""
        st.session_state.p_desc_input = ""
        st.session_state.p_type_input = None
        st.session_state.p_score_input = None
        st.session_state.p_remark_input = ""

# 앱 구동 시 3일 지난 백업 파일 청소
cleanup_old_backups()

# 1. 세션 상태 초기화
if 'master_info' not in st.session_state:
    st.session_state.master_info = {"supplier": "", "evaluator": ""}
if 'process_list' not in st.session_state:
    st.session_state.process_list = []
if 'is_evaluating' not in st.session_state:
    st.session_state.is_evaluating = False
if 'stop_backup' not in st.session_state:
    st.session_state.stop_backup = False
if 'download_completed' not in st.session_state:
    st.session_state.download_completed = False
if 'show_confirm_clear' not in st.session_state:
    st.session_state.show_confirm_clear = False
if 'pami_form_error' not in st.session_state:
    st.session_state.pami_form_error = ""
if 'success_toast' not in st.session_state:
    st.session_state.success_toast = ""

# 토스트 메시지 출력
if st.session_state.success_toast:
    st.toast(st.session_state.success_toast)
    st.session_state.success_toast = ""

# 2. Step 1: Supplier & Evaluator Info
with st.expander("📌 Step 1: Supplier & Evaluator Info", expanded=not st.session_state.is_evaluating):
    backup_files = glob.glob(os.path.join(BACKUP_DIR, "*.json"))
    if backup_files and not st.session_state.is_evaluating:
        st.subheader("Check Backup History (Past 3 Days)")
        backup_options = {}
        for bf in backup_files:
            try:
                with open(bf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    label = f"{data['info']['supplier']} by {data['info']['evaluator']} ({data['last_updated']})"
                    backup_options[label] = data
            except: pass
        
        if backup_options:
            selected_backup = st.selectbox("Restore previous session", options=["-- Select a backup --"] + list(backup_options.keys()))
            if selected_backup != "-- Select a backup --":
                if st.button("Restore Selected Session"):
                    st.session_state.master_info = backup_options[selected_backup]['info']
                    st.session_state.process_list = backup_options[selected_backup]['list']
                    st.session_state.is_evaluating = True
                    st.session_state.stop_backup = False
                    st.session_state.download_completed = False
                    st.rerun()
        st.write("---")
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        supplier_input = st.text_input("Supplier Name - Required*", value=st.session_state.master_info["supplier"], disabled=st.session_state.is_evaluating)
    with sub_col2:
        evaluator_input = st.text_input("Evaluator Name - Required*", value=st.session_state.master_info["evaluator"], disabled=st.session_state.is_evaluating)
    
    if not st.session_state.is_evaluating:
        if st.button("Go Evaluation"):
            if not supplier_input or not evaluator_input:
                st.error("🚨 Please enter both Supplier Name and Evaluator Name.")
            else:
                st.session_state.master_info["supplier"] = supplier_input
                st.session_state.master_info["evaluator"] = evaluator_input
                st.session_state.is_evaluating = True
                save_temp_backup()
                st.rerun()

# 3. Step 2: PAMI Input
if st.session_state.is_evaluating:
    st.info(f"📍 Supplier: **{st.session_state.master_info['supplier']}** | Evaluator: **{st.session_state.master_info['evaluator']}**")
    
    if st.session_state.stop_backup:
        st.warning("⚠️ CSV downloaded. Automatic backup is now disabled for this session.")
        
    with st.form("pami_input_form", clear_on_submit=False):
        st.subheader("📝 Step 2: PAMI Input per Process")
        if st.session_state.pami_form_error:
            st.error(st.session_state.pami_form_error)
        
        st.text_input("Process Name (Optional)", key="p_name_input")
        st.text_input("Description - Required*", placeholder="Enter details...", key="p_desc_input")
        st.write("Type - Required*")
        st.radio("Type", options=["MH", "P", "WIP"], index=None, horizontal=True, label_visibility="collapsed", key="p_type_input")
        st.write("Score (1~5) - Required*")
        st.radio("Score", options=[1, 2, 3, 4, 5], index=None, horizontal=True, label_visibility="collapsed", key="p_score_input")
        st.text_input("Remark (Optional)", key="p_remark_input")
        st.form_submit_button("Add to List", on_click=process_form_submit)

    # 4. Evaluation Summary & Export
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
        
        # [UPDATE] 탭을 없애고 직관적인 텍스트 기반 단일 화면으로 통합했습니다.
        st.info("💡 **Excel Tip:** Click the big button below, paste into Excel, and use `Data > Text to Columns` with the `|` delimiter.")
        
        # [UPDATE] 띄어쓰기 여백을 모두 없애고 오직 '|' 기호로만 데이터를 구분합니다.
        raw_text = f"Supplier: {st.session_state.master_info['supplier']} | Evaluator: {st.session_state.master_info['evaluator']} | Avg OAMI: {oami_avg:.2f}\n"
        raw_text += "No.|Process|Type|PAMI|Description|Remark|Time\n"
        for _, row in df.iterrows():
            raw_text += f"{row['No.']}|{row['Process']}|{row['Type']}|{row['PAMI']}|{row['Description']}|{row['Remark']}|{row['Time']}\n"

        # [UPDATE] 매우 크고 터치하기 쉬운 복사 버튼(HTML/JS)
        # 텍스트 데이터는 숨겨진 textarea에 담아두고 자바스크립트로 복사합니다.
        copy_html = f"""
        <textarea id="copyText" style="position: absolute; left: -9999px;">{raw_text}</textarea>
        <button onclick="copyToClipboard()" style="width: 100%; height: 60px; background-color: #0d6efd; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 20px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            📋 COPY DATA FOR EXCEL
        </button>
        <script>
        function copyToClipboard() {{
            var copyText = document.getElementById("copyText");
            copyText.select();
            copyText.setSelectionRange(0, 99999); /* For mobile devices */
            try {{
                document.execCommand("copy");
                var btn = document.querySelector('button');
                btn.innerText = '✅ COPIED! (Ready to Paste)';
                btn.style.backgroundColor = '#198754';
                setTimeout(function(){{
                    btn.innerText = '📋 COPY DATA FOR EXCEL';
                    btn.style.backgroundColor = '#0d6efd';
                }}, 2000);
            }} catch (err) {{
                alert("Copy failed. Please copy the text block manually.");
            }}
        }}
        </script>
        """
        components.html(copy_html, height=80)
        
        # 복사될 텍스트의 내용을 사용자가 확인할 수 있도록 화면에 노출합니다.
        st.code(raw_text, language="text")

        st.write("")
        subject = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}"
        st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#333333; color:white; font-weight:bold; font-size:16px;">📨 Open Mail App</button></a>', unsafe_allow_html=True)

        st.write("---")
        
        st.warning("⚠️ **Warning:** System backups are temporary and can be deleted at any time. **You must download the CSV file to keep your data permanently.**")
        
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Download CSV Backup", 
            data=csv_data, 
            file_name=f"OAMI_{st.session_state.master_info['supplier']}_{datetime.now().strftime('%Y%m%d')}.csv", 
            mime="text/csv", 
            use_container_width=True,
            on_click=handle_download
        )

        if st.session_state.download_completed:
            st.success("✅ System report has been deleted. Please save it in the appropriate folder.")

        # 데이터 초기화 (Yes/No)
        if not st.session_state.show_confirm_clear:
            if st.button("🚨 Clear All Data (Start New)", use_container_width=True):
                st.session_state.show_confirm_clear = True
                st.rerun()
        else:
            st.error("⚠️ Are you sure? This will delete all current progress.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✔️ Yes, Clear Data", use_container_width=True):
                    supplier = st.session_state.master_info.get("supplier", "")
                    evaluator = st.session_state.master_info.get("evaluator", "")
                    if supplier and evaluator:
                        fname = get_backup_filename(supplier, evaluator)
                        if os.path.exists(fname): os.remove(fname)
                    
                    st.session_state.master_info = {"supplier": "", "evaluator": ""}
                    st.session_state.process_list = []
                    st.session_state.is_evaluating = False 
                    st.session_state.stop_backup = False
                    st.session_state.download_completed = False
                    st.session_state.show_confirm_clear = False 
                    
                    if 'p_name_input' in st.session_state: st.session_state.p_name_input = ""
                    if 'p_desc_input' in st.session_state: st.session_state.p_desc_input = ""
                    if 'p_type_input' in st.session_state: st.session_state.p_type_input = None
                    if 'p_score_input' in st.session_state: st.session_state.p_score_input = None
                    if 'p_remark_input' in st.session_state: st.session_state.p_remark_input = ""
                    
                    st.rerun()
            with col_no:
                if st.button("❌ No, Cancel", use_container_width=True):
                    st.session_state.show_confirm_clear = False 
                    st.rerun()