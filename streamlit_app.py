import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import json
import os
import glob 
import time 
import streamlit.components.v1 as components
import io # [NEW] 엑셀 템플릿 생성을 위한 in-memory 바이너리 스트림 처리를 위해 추가

# 브라우저 탭 아이콘 및 제목 영문 설정
st.set_page_config(page_title="Supplier OAMI", page_icon="📝", layout="centered")

# 메인 타이틀
# [UPDATE] 글자 크기를 줄이고 굵게(Bold) 통일하여 공간 낭비를 줄였습니다.
st.markdown("### 📝 Supplier OAMI Evaluation App")

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
        # [UPDATE] 소제목 크기를 줄이고 굵게 통일했습니다.
        st.markdown("**Check Backup History (Past 3 Days)**")
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

    # =====================================================================
    # [NEW] 엑셀 템플릿 기반 일괄 업로드(Bulk Upload) 기능 추가
    # 엑셀 다운로드로 양식을 받고, 작성 후 업로드하면 일괄 등록되도록 구현
    # =====================================================================
    with st.expander("📂 Bulk Upload via Excel", expanded=False):
        st.markdown("**엑셀 템플릿을 사용하여 여러 프로세스를 한 번에 등록할 수 있습니다.**")
        
        # 1) 다운로드할 엑셀 템플릿 데이터프레임 생성
        template_df = pd.DataFrame({
            "Process Name": ["Assembly 1", "Testing"],
            "Description": ["Engine assembly", "Final check"],
            "Type": ["MH", "P"], # MH, P, WIP 중 선택
            "Score": [4, 5],     # 1 ~ 5 사이 정수
            "Remark": ["Routine check", "Critical step"]
        })
        
        # in-memory 버퍼에 엑셀 파일 작성
        towrite = io.BytesIO()
        template_df.to_excel(towrite, index=False, engine='openpyxl')
        towrite.seek(0)
        
        st.download_button(
            label="📥 Download Excel Template",
            data=towrite,
            file_name="OAMI_Bulk_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="양식을 다운로드하여 내용을 채운 뒤 아래에 업로드하세요."
        )
        
        # 2) 엑셀 파일 업로더
        uploaded_file = st.file_uploader("Upload filled Excel template", type=["xlsx", "xls"])
        
        # 3) 업로드 후 데이터 반영 로직
        if uploaded_file is not None:
            if st.button("🚀 Upload & Apply Data"):
                try:
                    df_uploaded = pd.read_excel(uploaded_file)
                    # 필수 컬럼 검증
                    required_cols = ["Description", "Type", "Score"]
                    if not all(col in df_uploaded.columns for col in required_cols):
                        st.error(f"🚨 엑셀 양식이 올바르지 않습니다. 다음 컬럼이 반드시 필요합니다: {', '.join(required_cols)}")
                    else:
                        # 엑셀의 각 행을 순회하며 프로세스 리스트에 추가
                        added_count = 0
                        for _, row in df_uploaded.iterrows():
                            # 빈 값이거나 누락된 필수 값 처리
                            desc = row.get("Description")
                            if pd.isna(desc) or str(desc).strip() == "":
                                continue # Description이 비어있으면 해당 행 스킵
                            
                            new_process = {
                                "Supplier": st.session_state.master_info["supplier"],
                                "Evaluator": st.session_state.master_info["evaluator"],
                                "No.": 0, 
                                "Process": str(row.get("Process Name", "N/A")) if pd.notna(row.get("Process Name")) else "N/A",
                                "Type": str(row.get("Type", "MH")) if pd.notna(row.get("Type")) else "MH",
                                "Description": str(desc),
                                "PAMI": int(row.get("Score", 3)) if pd.notna(row.get("Score")) else 3,
                                "Remark": str(row.get("Remark", "")) if pd.notna(row.get("Remark")) else "",
                                "Time": datetime.now().strftime("%H:%M:%S")
                            }
                            st.session_state.process_list.append(new_process)
                            added_count += 1
                        
                        if added_count > 0:
                            # 새 데이터가 추가되었으므로 인덱스 재정렬 및 백업 저장
                            reindex_processes()
                            save_temp_backup()
                            
                            # 네비게이션을 가장 마지막 위치로 리셋
                            st.session_state.is_inserting = True
                            st.session_state.nav_index = len(st.session_state.process_list) - 1
                            sync_form_with_state()
                            
                            st.success(f"✅ {added_count}개의 프로세스가 성공적으로 일괄 등록되었습니다!")
                            time.sleep(1) # 성공 메시지 확인을 위한 짧은 대기 후 새로고침
                            st.rerun()
                        else:
                            st.warning("⚠️ 등록할 유효한 프로세스 데이터가 엑셀에 없습니다.")
                except Exception as e:
                    st.error(f"🚨 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.write("---")
    # =====================================================================
    
    if st.session_state.process_list or st.session_state.is_inserting:
        nav_c1, nav_c2, nav_c3 = st.columns(3)
        
        prev_disabled = len(st.session_state.process_list) == 0 or (st.session_state.nav_index <= 0 and not st.session_state.is_inserting)
        with nav_c1: st.button("⬅️ Prev", on_click=nav_prev, disabled=prev_disabled, use_container_width=True)
        
        next_disabled = st.session_state.is_inserting
        with nav_c2: st.button("Next ➡️", on_click=nav_next, disabled=next_disabled, use_container_width=True)
        
        new_disabled = st.session_state.is_inserting
        with nav_c3: st.button("➕ New", on_click=nav_new, disabled=new_disabled, use_container_width=True)

        st.write("") 
        # [UPDATE] 폰트 크기를 통일하고, Editing 시 Description을 함께 표시하여 직관성을 높였습니다.
        if st.session_state.is_inserting:
            target_no = st.session_state.nav_index + 2
            st.markdown(f"<div style='text-align: center; font-weight: bold; color: #0d6efd;'>✨ Add New Process as No. {target_no}</div>", unsafe_allow_html=True)
        else:
            current_desc = st.session_state.process_list[st.session_state.nav_index].get('Description', '')
            st.markdown(f"<div style='text-align: center; font-weight: bold; color: #198754;'>✏️ Editing No. {st.session_state.nav_index + 1} : {current_desc}</div>", unsafe_allow_html=True)

    with st.form("pami_input_form", clear_on_submit=False):
        # [UPDATE] 큰 헤더 대신 기본 텍스트 굵게 처리하여 세로 공간 절약
        st.markdown("**📝 Step 2: PAMI Input per Process**")
        
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
        # [UPDATE] 큰 헤더 대신 기본 텍스트 굵게 처리하여 세로 공간 절약
        st.markdown("**📊 Evaluation Summary**")
        
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
        
        # [UPDATE] 텍스트 모바일 복사 영역에 순서를 변경 (Description이 PAMI 앞으로 오도록)
        raw_text = f"Supplier: {st.session_state.master_info['supplier']} | Evaluator: {st.session_state.master_info['evaluator']} | Processes: {total_processes} | Avg OAMI: {oami_avg:.2f}\n"
        raw_text += "No.|Process|Type|Description|PAMI|Remark|Time\n"
        for _, row in df.iterrows():
            raw_text += f"{row['No.']}|{row['Process']}|{row['Type']}|{row['Description']}|{row['PAMI']}|{row['Remark']}|{row['Time']}\n"
        
        tab_mobile, tab_pc = st.tabs(["📱 1. Mobile (Text)", "🖥️ 2. PC (Table)"])
        
        with tab_mobile:
            st.info("💡 **Tip:** Click the button below to copy the text, or use the 'Open Outlook Mail App' button to auto-fill your email body.")
            
            safe_raw_text = json.dumps(raw_text)
            
            # [UPDATE] HTML 삽입 버튼 폰트 사이즈를 기본 14px 텍스트 크기 단위로 맞추었습니다.
            copy_text_html = f"""
            <button onclick="copyToClipboard()" style="width: 100%; height: 40px; background-color: #0d6efd; color: white; border: none; border-radius: 5px; font-weight: bold; font-size: 14px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
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
            
            # [UPDATE] PC용 표도 Description과 PAMI 순서를 반영하도록 Dataframe 재생성 적용
            export_cols = ["No.", "Process", "Type", "Description", "PAMI", "Remark", "Time"]
            html_table = df[export_cols].to_html(index=False).replace('<table border="1" class="dataframe">', '<table border="1" cellpadding="8" style="border-collapse: collapse; text-align: left; font-family: Arial; width: 100%;">')
            
            # [UPDATE] 큰 헤더 사이즈 <h3> 대신 굵은 글씨로 통일했습니다.
            email_html = f"<div id='pc-email-content' style='background:#f8f9fa; padding:15px;'><strong>OAMI Report: {st.session_state.master_info['supplier']}</strong><br><br><strong>Total Processes:</strong> {total_processes}<br><strong>Average OAMI: <span style='color:blue;'>{oami_avg:.2f} / 5.0</span></strong><br><br>{html_table}</div>"
            
            copy_table_html = f"""
            <button onclick='copyPCTable()' style='width:100%; height:40px; background-color:#28a745; color:white; border:none; border-radius:5px; font-weight:bold; font-size:14px; cursor:pointer; margin-bottom:10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
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
        # [UPDATE] 오픈 메일 버튼 폰트 사이즈도 14px로 통일했습니다.
        st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size:14px;">📨 Open Outlook Mail App (Auto-fill Text)</button></a>', unsafe_allow_html=True)

        st.write("---")
        
        st.warning("⚠️ **Warning:** System backups are temporary and can be deleted at any time. **You must download the CSV file to keep your data permanently.**")
        
        st.checkbox("🗑️ Delete system backup file after download (Recommended for security)", value=True, key="delete_backup_checkbox")
        
        # [UPDATE] CSV 파일 생성 시 첫 줄에 요약 텍스트 추가 및 컬럼 순서를 Description 뒤에 PAMI가 오도록 수정
        summary_text_for_csv = f"Supplier: {st.session_state.master_info['supplier']} | Evaluator: {st.session_state.master_info['evaluator']} | Processes: {total_processes} | Avg OAMI: {oami_avg:.2f}\n"
        export_df = df[["No.", "Process", "Type", "Description", "PAMI", "Remark", "Time"]]
        
        # 요약 문자열과 csv 문자열을 결합 후 한글 깨짐 방지를 위해 utf-8-sig 인코딩
        csv_string = summary_text_for_csv + export_df.to_csv(index=False)
        csv_data_bytes = csv_string.encode('utf-8-sig')

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