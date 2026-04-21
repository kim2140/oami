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

# [UPDATE] 화면을 깨지게 만들었던 강제 가로 정렬 CSS 코드를 완전히 삭제했습니다.
# 이제 모바일 환경에서는 Streamlit 기본 동작에 따라 안전하게 세로로 배열됩니다.

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

# 오래된 백업 파일 정리 함수
def cleanup_old_backups():
    now = time.time()
    for f in glob.glob(os.path.join(BACKUP_DIR, "*.json")):
        if os.stat(f).st_mtime < now - (3 * 86400):
            try: os.remove(f)
            except: pass

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

# 엑셀 다운로드 콜백 함수
def handle_download():
    if st.session_state.get("delete_backup_checkbox", True):
        st.session_state.stop_backup = True
        supplier = st.session_state.master_info.get("supplier", "")
        evaluator = st.session_state.master_info.get("evaluator", "")
        if supplier and evaluator:
            fname = get_backup_filename(supplier, evaluator)
            if os.path.exists(fname):
                try: os.remove(fname)
                except: pass
        st.session_state.download_action_status = "deleted"
    else:
        st.session_state.stop_backup = False
        st.session_state.download_action_status = "kept"

# 프로세스 리스트 재정렬 함수 (No. 업데이트)
def reindex_processes():
    for i, p in enumerate(st.session_state.process_list):
        p["No."] = i + 1

# 폼 네비게이션 및 상태 동기화 로직
def sync_form_with_state():
    if st.session_state.is_inserting:
        st.session_state.p_name_input = ""
        st.session_state.p_desc_input = ""
        st.session_state.p_type_input = None
        st.session_state.p_score_input = None
        st.session_state.p_remark_input = ""
    else:
        if len(st.session_state.process_list) > 0:
            p = st.session_state.process_list[st.session_state.nav_index]
            st.session_state.p_name_input = p["Process"] if p["Process"] != "N/A" else ""
            st.session_state.p_desc_input = p["Description"]
            st.session_state.p_type_input = p["Type"]
            st.session_state.p_score_input = p["PAMI"]
            st.session_state.p_remark_input = p["Remark"]
    st.session_state.show_delete_confirm = False
    st.session_state.pami_form_error = ""

def nav_prev():
    if st.session_state.is_inserting and st.session_state.nav_index >= 0:
        st.session_state.is_inserting = False
    elif not st.session_state.is_inserting and st.session_state.nav_index > 0:
        st.session_state.nav_index -= 1
    sync_form_with_state()

def nav_next():
    if not st.session_state.is_inserting:
        if st.session_state.nav_index < len(st.session_state.process_list) - 1:
            st.session_state.nav_index += 1
        else:
            st.session_state.is_inserting = True
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
            st.session_state.nav_index = -1
            st.session_state.is_inserting = True
        elif idx >= len(st.session_state.process_list):
            st.session_state.nav_index = len(st.session_state.process_list) - 1
            st.session_state.is_inserting = False
        else:
            st.session_state.is_inserting = False
            
        save_temp_backup()
    sync_form_with_state()

def process_form_submit():
    p_name = st.session_state.p_name_input
    p_desc = st.session_state.p_desc_input
    p_type = st.session_state.p_type_input
    p_score = st.session_state.p_score_input
    p_remark = st.session_state.p_remark_input
    
    if not p_desc or p_type is None or p_score is None:
        st.session_state.pami_form_error = "🚨 Fill in Description, Type, and Score."
        return
        
    st.session_state.pami_form_error = ""
    
    if st.session_state.is_inserting:
        target_idx = st.session_state.nav_index + 1
        
        is_appending_at_end = (target_idx == len(st.session_state.process_list))
        
        new_process = {
            "Supplier": st.session_state.master_info["supplier"],
            "Evaluator": st.session_state.master_info["evaluator"],
            "No.": 0, 
            "Process": p_name if p_name else "N/A",
            "Type": p_type,
            "Description": p_desc,
            "PAMI": p_score,
            "Remark": p_remark if p_remark else "",
            "Time": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.process_list.insert(target_idx, new_process)
        reindex_processes()
        
        st.session_state.nav_index = target_idx
        
        if is_appending_at_end:
            st.session_state.is_inserting = True
        else:
            st.session_state.is_inserting = False
            
        st.session_state.success_toast = f"Added successfully as No. {target_idx + 1}"
    else:
        idx = st.session_state.nav_index
        p = st.session_state.process_list[idx]
        p["Process"] = p_name if p_name else "N/A"
        p["Description"] = p_desc
        p["Type"] = p_type
        p["PAMI"] = p_score
        p["Remark"] = p_remark if p_remark else ""
        p["Time"] = datetime.now().strftime("%H:%M:%S")
        st.session_state.success_toast = f"Updated No. {idx + 1}"
        
    save_temp_backup()
    sync_form_with_state()

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
if 'download_action_status' not in st.session_state:
    st.session_state.download_action_status = None
if 'show_confirm_clear' not in st.session_state:
    st.session_state.show_confirm_clear = False
if 'pami_form_error' not in st.session_state:
    st.session_state.pami_form_error = ""
if 'success_toast' not in st.session_state:
    st.session_state.success_toast = ""
if 'show_delete_confirm' not in st.session_state:
    st.session_state.show_delete_confirm = False
if 'nav_index' not in st.session_state:
    st.session_state.nav_index = -1
if 'is_inserting' not in st.session_state:
    st.session_state.is_inserting = True

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
                    st.session_state.download_action_status = None 
                    
                    st.session_state.nav_index = len(st.session_state.process_list) - 1
                    st.session_state.is_inserting = True
                    sync_form_with_state()
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
    
    if st.session_state.process_list or st.session_state.is_inserting:
        nav_c1, nav_c2, nav_c3 = st.columns(3)
        
        prev_disabled = len(st.session_state.process_list) == 0 or (st.session_state.nav_index <= 0 and not st.session_state.is_inserting)
        with nav_c1: st.button("⬅️ Prev", on_click=nav_prev, disabled=prev_disabled, use_container_width=True)
        
        next_disabled = st.session_state.is_inserting
        with nav_c2: st.button("Next ➡️", on_click=nav_next, disabled=next_disabled, use_container_width=True)
        
        new_disabled = st.session_state.is_inserting
        with nav_c3: st.button("➕ New", on_click=nav_new, disabled=new_disabled, use_container_width=True)

        st.write("") 
        if st.session_state.is_inserting:
            target_no = st.session_state.nav_index + 2
            st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 1.1em; color: #0d6efd;'>✨ Add New Process as No. {target_no}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 1.1em; color: #198754;'>✏️ Editing No. {st.session_state.nav_index + 1}</div>", unsafe_allow_html=True)

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
        
        btn_text = "Save New Process" if st.session_state.is_inserting else "Update Process"
        st.form_submit_button(btn_text, on_click=process_form_submit)

    # Cancel과 Delete 버튼
    if st.session_state.process_list or st.session_state.is_inserting:
        act_c1, act_c2 = st.columns(2)
        
        cancel_disabled = (not st.session_state.is_inserting) or (len(st.session_state.process_list) == 0)
        with act_c1: st.button("🚫 Cancel", on_click=nav_cancel, disabled=cancel_disabled, use_container_width=True)
        
        del_disabled = st.session_state.is_inserting
        with act_c2: st.button("🗑️ Delete", on_click=set_delete_confirm, disabled=del_disabled, use_container_width=True)

        if st.session_state.show_delete_confirm and not st.session_state.is_inserting:
            st.error(f"⚠️ Are you sure you want to delete Process **No. {st.session_state.nav_index + 1}**?")
            d_col1, d_col2 = st.columns(2)
            with d_col1: st.button("✔️ Yes, Delete", on_click=delete_current_process, use_container_width=True)
            with d_col2: st.button("❌ Cancel", on_click=cancel_delete, use_container_width=True)

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
        
        raw_text = f"Supplier: {st.session_state.master_info['supplier']} | Evaluator: {st.session_state.master_info['evaluator']} | Processes: {total_processes} | Avg OAMI: {oami_avg:.2f}\n"
        raw_text += "No.|Process|Type|PAMI|Description|Remark|Time\n"
        for _, row in df.iterrows():
            raw_text += f"{row['No.']}|{row['Process']}|{row['Type']}|{row['PAMI']}|{row['Description']}|{row['Remark']}|{row['Time']}\n"
        
        tab_mobile, tab_pc = st.tabs(["📱 1. Mobile (Text)", "🖥️ 2. PC (Table)"])
        
        with tab_mobile:
            st.info("💡 **Tip:** Click the button below to copy the text, or use the 'Open Outlook Mail App' button to auto-fill your email body.")
            
            safe_raw_text = json.dumps(raw_text)
            
            copy_text_html = f"""
            <button onclick="copyToClipboard()" style="width: 100%; height: 40px; background-color: #0d6efd; color: white; border: none; border-radius: 5px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                📋 Copy Text for Outlook
            </button>
            <script>
            function copyToClipboard() {{
                var textToCopy = {safe_raw_text};
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(textToCopy).then(function() {{
                        showSuccess();
                    }}).catch(function() {{
                        fallbackCopyTextToClipboard(textToCopy);
                    }});
                }} else {{
                    fallbackCopyTextToClipboard(textToCopy);
                }}
                function fallbackCopyTextToClipboard(text) {{
                    var textArea = document.createElement("textarea");
                    textArea.value = text;
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
            st.info("💡 Wide and clean table copy optimized for PC environments. **Note:** Tables cannot be auto-filled in the Mail App. You must copy and paste this table manually.")
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
        body_encoded = urllib.parse.quote(raw_text)
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}&body={body_encoded}"
        st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size:16px;">📨 Open Outlook Mail App (Auto-fill Text)</button></a>', unsafe_allow_html=True)

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
                    st.session_state.download_action_status = None 
                    st.session_state.show_confirm_clear = False 
                    
                    st.session_state.nav_index = -1 
                    st.session_state.is_inserting = True
                    st.session_state.show_delete_confirm = False
                    
                    keys_to_clear = ['p_name_input', 'p_desc_input', 'p_type_input', 'p_score_input', 'p_remark_input']
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.rerun()
            with col_no:
                if st.button("❌ No, Cancel", use_container_width=True):
                    st.session_state.show_confirm_clear = False 
                    st.rerun()