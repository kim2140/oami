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
    # 사용자가 체크박스를 선택하여 삭제를 원할 때만 파일 삭제 로직을 수행합니다.
    if st.session_state.get("delete_backup_checkbox", True):
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
        st.session_state.download_action_status = "deleted"
    else:
        # 삭제하지 않는 옵션 선택 시, 백업을 유지합니다.
        st.session_state.stop_backup = False
        st.session_state.download_action_status = "kept"

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

# [UPDATE] 오류의 원인이었던 초기화 변수명을 정확하게 'download_action_status'로 수정했습니다.
if 'download_action_status' not in st.session_state:
    st.session_state.download_action_status = None

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
                    # [UPDATE] 복구 시에도 상태 변수를 올바르게 초기화합니다.
                    st.session_state.download_action_status = None 
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
        
        tab_mobile, tab_pc = st.tabs(["📱 1. Mobile (Text)", "🖥️ 2. PC (Table)"])
        
        with tab_mobile:
            st.info("💡 **Tip:** Click the copy button below and paste it into your Outlook Mail App. If the button fails, use the small copy icon inside the text box.")
            
            raw_text = f"Supplier: {st.session_state.master_info['supplier']} | Evaluator: {st.session_state.master_info['evaluator']} | Processes: {total_processes} | Avg OAMI: {oami_avg:.2f}\n"
            raw_text += "No.|Process|Type|PAMI|Description|Remark|Time\n"
            for _, row in df.iterrows():
                raw_text += f"{row['No.']}|{row['Process']}|{row['Type']}|{row['PAMI']}|{row['Description']}|{row['Remark']}|{row['Time']}\n"

            # 텍스트를 JS로 안전하게 전달하기 위해 JSON 변환을 사용
            safe_raw_text = json.dumps(raw_text)
            
            copy_text_html = f"""
            <button onclick="copyToClipboard()" style="width: 100%; height: 40px; background-color: #0d6efd; color: white; border: none; border-radius: 5px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                📋 Copy Text for Outlook
            </button>
            <script>
            function copyToClipboard() {{
                var textToCopy = {safe_raw_text};
                
                // 최신 클립보드 API를 우선 시도
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(textToCopy).then(function() {{
                        showSuccess();
                    }}).catch(function() {{
                        fallbackCopyTextToClipboard(textToCopy);
                    }});
                }} else {{
                    fallbackCopyTextToClipboard(textToCopy);
                }}

                // 구버전 및 모바일 기기를 위한 완벽한 Fallback 처리
                function fallbackCopyTextToClipboard(text) {{
                    var textArea = document.createElement("textarea");
                    textArea.value = text;
                    
                    // 화면 스크롤 방지 및 완벽한 숨김 처리
                    textArea.style.position = "fixed";
                    textArea.style.top = "0";
                    textArea.style.left = "0";
                    textArea.style.opacity = "0";
                    
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    
                    try {{
                        var successful = document.execCommand('copy');
                        if(successful) {{ showSuccess(); }} 
                        else {{ alert("Copy failed. Please copy manually."); }}
                    }} catch (err) {{
                        alert("Copy failed. Please copy manually.");
                    }}
                    document.body.removeChild(textArea);
                }}

                function showSuccess() {{
                    var btn = document.querySelector('button');
                    btn.innerText = '✅ Copied!';
                    btn.style.backgroundColor = '#198754';
                    setTimeout(function(){{
                        btn.innerText = '📋 Copy Text for Outlook';
                        btn.style.backgroundColor = '#0d6efd';
                    }}, 2000);
                }}
            }}
            </script>
            """
            components.html(copy_text_html, height=50)
            
            st.code(raw_text, language="text")

        with tab_pc:
            st.info("💡 Wide and clean table copy optimized for PC environments.")
            html_table = df.to_html(index=False).replace('<table border="1" class="dataframe">', '<table border="1" cellpadding="8" style="border-collapse: collapse; text-align: left; font-family: Arial; width: 100%;">')
            email_html = f"<div id='pc-email-content' style='background:#f8f9fa; padding:15px;'><h3 style='margin-top:0;'>OAMI Report: {st.session_state.master_info['supplier']}</h3><p><strong>Total Processes:</strong> {total_processes}</p><p><strong>Average OAMI: <span style='color:blue;'>{oami_avg:.2f} / 5.0</span></strong></p>{html_table}</div>"
            
            copy_table_html = f"""
            <button onclick='copyPCTable()' style='width:100%; height:40px; background-color:#28a745; color:white; border:none; border-radius:5px; font-weight:bold; font-size:16px; cursor:pointer; margin-bottom:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                📋 Copy Table for Outlook
            </button>
            <script>
            function copyPCTable(){{
                var body = document.getElementById('pc-email-content');
                var range = document.createRange();
                range.selectNode(body);
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                try{{
                    document.execCommand('copy');
                    var btn = document.querySelector('button'); 
                    btn.innerText='✅ Copied!'; 
                    btn.style.backgroundColor='#198754'; 
                    setTimeout(function(){{
                        btn.innerText='📋 Copy Table for Outlook'; 
                        btn.style.backgroundColor='#28a745';
                    }}, 2000);
                }}catch(e){{
                    alert('Copy failed.');
                }}
                window.getSelection().removeAllRanges();
            }}
            </script>
            """
            components.html(copy_table_html + email_html, height=450, scrolling=True)

        st.write("")
        
        subject = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}"
        st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size:16px;">📨 Open Outlook Mail App</button></a>', unsafe_allow_html=True)

        st.write("---")
        
        st.warning("⚠️ **Warning:** System backups are temporary and can be deleted at any time. **You must download the CSV file to keep your data permanently.**")
        
        st.checkbox("🗑️ Delete system backup file after download (Recommended for security)", value=True, key="delete_backup_checkbox")
        
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Download CSV Backup", 
            data=csv_data, 
            file_name=f"OAMI_{st.session_state.master_info['supplier']}_{datetime.now().strftime('%Y%m%d')}.csv", 
            mime="text/csv", 
            use_container_width=True,
            on_click=handle_download
        )

        if st.session_state.download_action_status == "deleted":
            st.success("✅ System report has been deleted. Please save it in the appropriate folder.")
        elif st.session_state.download_action_status == "kept":
            st.info("ℹ️ CSV downloaded successfully. The system backup remains on the server.")

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
                    # [UPDATE] 데이터 지울 때도 상태 변수를 올바르게 초기화합니다.
                    st.session_state.download_action_status = None 
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