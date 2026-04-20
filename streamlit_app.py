import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import json
import os
import glob 
import time 

# 페이지 설정: 브라우저 탭 아이콘 및 제목 설정
st.set_page_config(page_title="Supplier OAMI", page_icon="📝", layout="centered")

# 메인 타이틀
st.title("📝 Supplier OAMI Evaluation App")

# 백업 데이터를 저장할 전용 폴더를 생성합니다.
BACKUP_DIR = "oami_backups"
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# 파일명 생성 함수: 업체명_평가자명.json 형태로 만듭니다. (동일 업체/평가자면 Overwrite 됨)
def get_backup_filename(supplier, evaluator):
    # 특수문자로 인한 파일 생성 오류를 막기 위해 안전한 문자로만 파일명을 만듭니다.
    safe_sup = "".join(c for c in supplier if c.isalnum() or c in " _-").strip()
    safe_eval = "".join(c for c in evaluator if c.isalnum() or c in " _-").strip()
    return os.path.join(BACKUP_DIR, f"{safe_sup}_{safe_eval}.json")

# 오래된 백업 파일 정리 함수: 3일(3 * 24시간)이 지난 파일은 자동으로 삭제합니다.
def cleanup_old_backups():
    now = time.time()
    for f in glob.glob(os.path.join(BACKUP_DIR, "*.json")):
        # 파일의 마지막 수정 시간이 현재 시간보다 3일(3 * 86400초) 이전이면 삭제
        if os.stat(f).st_mtime < now - (3 * 86400):
            try:
                os.remove(f)
            except:
                pass

# 실시간 자동 백업 함수 (업체명_평가자명 파일로 저장)
def save_temp_backup():
    # 사용자가 엑셀로 다운받아서 백업이 중단된 상태라면 저장하지 않습니다.
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

# 엑셀 다운로드 시 실행될 콜백 함수: 백업을 중단하고 기존 파일을 즉시 삭제합니다.
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

# 앱 시작 시 오래된 3일 전 백업 파일들을 청소합니다.
cleanup_old_backups()

# 1. 세션 상태 초기화
if 'master_info' not in st.session_state:
    st.session_state.master_info = {"supplier": "", "evaluator": ""}
if 'process_list' not in st.session_state:
    st.session_state.process_list = []
# 평가가 시작되었는지 확인하는 상태값 (이 값이 True면 입력창이 잠깁니다)
if 'is_evaluating' not in st.session_state:
    st.session_state.is_evaluating = False
# 엑셀 다운로드 이후 백업을 중지하는 상태값
if 'stop_backup' not in st.session_state:
    st.session_state.stop_backup = False
# [UPDATE] 초기화 버튼 클릭 확인을 위한 상태값 추가
if 'show_confirm_clear' not in st.session_state:
    st.session_state.show_confirm_clear = False

# 2. Step 1: 업체 및 평가자 정보
with st.expander("📌 Step 1: Supplier & Evaluator Info", expanded=not st.session_state.is_evaluating):
    
    # 과거 최대 3일치의 백업 데이터 목록을 불러와서 선택할 수 있게 합니다.
    backup_files = glob.glob(os.path.join(BACKUP_DIR, "*.json"))
    if backup_files and not st.session_state.is_evaluating:
        st.subheader("Check Backup History (Past 3 Days)")
        backup_options = {}
        for bf in backup_files:
            try:
                with open(bf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # 드롭다운에 보여질 라벨 (예: Samsung by Jaewon Kim (2026-04-20 15:30:00))
                    label = f"{data['info']['supplier']} by {data['info']['evaluator']} ({data['last_updated']})"
                    backup_options[label] = data
            except: pass
        
        if backup_options:
            selected_backup = st.selectbox("Restore previous session", options=["-- Select a backup --"] + list(backup_options.keys()))
            if selected_backup != "-- Select a backup --":
                if st.button("Restore Selected Session"):
                    # 과거 데이터를 세션에 덮어씌우고 평가 모드로 바로 진입합니다.
                    st.session_state.master_info = backup_options[selected_backup]['info']
                    st.session_state.process_list = backup_options[selected_backup]['list']
                    st.session_state.is_evaluating = True
                    st.session_state.stop_backup = False
                    st.rerun()
        st.write("---")
    
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        # is_evaluating 상태가 True이면 입력창이 disabled(비활성화) 되어 수정할 수 없습니다.
        supplier_input = st.text_input("Supplier Name - Required*", value=st.session_state.master_info["supplier"], disabled=st.session_state.is_evaluating)
    with sub_col2:
        # is_evaluating 상태가 True이면 입력창이 disabled(비활성화) 되어 수정할 수 없습니다.
        evaluator_input = st.text_input("Evaluator Name - Required*", value=st.session_state.master_info["evaluator"], disabled=st.session_state.is_evaluating)
    
    # 평가가 아직 시작되지 않았을 때만 'Go Evaluation' 버튼을 보여줍니다.
    if not st.session_state.is_evaluating:
        if st.button("Go Evaluation"):
            if not supplier_input or not evaluator_input:
                st.error("🚨 Please enter both Supplier Name and Evaluator Name.")
            else:
                st.session_state.master_info["supplier"] = supplier_input
                st.session_state.master_info["evaluator"] = evaluator_input
                # 필수값이 입력되면 상태를 변경하여 위 텍스트 창들을 잠그고 하단 창을 엽니다.
                st.session_state.is_evaluating = True
                save_temp_backup()
                st.rerun()

# 업체 정보가 설정되고 평가 상태(is_evaluating)가 활성화된 경우에만 2단계 활성화
if st.session_state.is_evaluating:
    st.info(f"📍 Supplier: **{st.session_state.master_info['supplier']}** | Evaluator: **{st.session_state.master_info['evaluator']}**")
    
    if st.session_state.stop_backup:
        st.warning("⚠️ CSV downloaded. Automatic backup is now disabled for this session.")
        
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
                save_temp_backup() # 프로세스 추가 시마다 실시간 자동 백업
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
            st.info("💡 Best for Mobile. Click the copy icon.")
            
            # 모바일 출력용 텍스트 양식 유지
            text_report = f"===================================================\n"
            text_report += f"              OAMI Evaluation Report\n"
            text_report += f"===================================================\n"
            text_report += f"▶ Supplier : {st.session_state.master_info['supplier']}\n"
            text_report += f"▶ Evaluator: {st.session_state.master_info['evaluator']}\n"
            text_report += f"▶ Processes: {total_processes}\n"
            text_report += f"▶ Avg OAMI : {oami_avg:.2f} / 5.0\n"
            text_report += f"---------------------------------------------------\n"
            text_report += f"No. | Process | Type | PAMI | Description | Remark | Time\n"
            text_report += f"---------------------------------------------------\n"
            for i, row in df.iterrows():
                # 데이터 출력 순서: No. -> Process -> Type -> PAMI -> Description -> Remark -> Time
                text_report += f"{row['No.']:<3} | {row['Process']} | {row['Type']:<4} | {row['PAMI']}pt | {row['Description']} | {row['Remark']} | {row['Time']}\n"
            text_report += f"==================================================="
            st.code(text_report, language="text")

        with tab_table:
            # HTML 표 생성
            import streamlit.components.v1 as components
            html_table = df.to_html(index=False).replace('<table border="1" class="dataframe">', '<table border="1" cellpadding="8" style="border-collapse: collapse; text-align: left; font-family: Arial; width: 100%;">')
            email_html = f"<div id='email-content' style='background:#f8f9fa; padding:15px;'><h3 style='margin-top:0;'>OAMI Report: {st.session_state.master_info['supplier']}</h3><p><strong>Total Processes:</strong> {total_processes}</p><p><strong>Average OAMI: <span style='color:blue;'>{oami_avg:.2f} / 5.0</span></strong></p>{html_table}</div>"
            copy_button_html = f"<div style='margin-bottom:10px;'><button onclick='copyTable()' style='width:100%;height:40px;background:#28a745;color:white;border:none;border-radius:5px;cursor:pointer;font-weight:bold;'>📋 Copy Table for Outlook</button></div><script>function copyTable(){{var body=document.getElementById('email-content');var range=document.createRange();range.selectNode(body);window.getSelection().removeAllRanges();window.getSelection().addRange(range);try{{document.execCommand('copy');alert('Table Copied! Paste into Outlook.');}}catch(e){{alert('Copy failed.');}}window.getSelection().removeAllRanges();}}</script>"
            components.html(copy_button_html + email_html, height=450, scrolling=True)

        st.write("")
        # Outlook 실행
        subject = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}"
        st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size:16px;">📨 Open Outlook Mail App</button></a>', unsafe_allow_html=True)

        st.write("---")
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        
        # 엑셀 다운로드 버튼: on_click 파라미터를 사용해 다운로드 즉시 백업 중지 및 파일 삭제를 수행합니다.
        st.download_button(
            label="📥 Download CSV Backup", 
            data=csv_data, 
            file_name=f"OAMI_{st.session_state.master_info['supplier']}_{datetime.now().strftime('%Y%m%d')}.csv", 
            mime="text/csv", 
            use_container_width=True,
            on_click=handle_download
        )

        # [UPDATE] 데이터 초기화 버튼에 Yes/No 확인 로직을 추가했습니다.
        if not st.session_state.show_confirm_clear:
            if st.button("🚨 Clear All Data (Start New)", use_container_width=True):
                st.session_state.show_confirm_clear = True
                st.rerun()
        else:
            st.warning("⚠️ Are you sure you want to clear all data? This cannot be undone.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✔️ Yes, Clear Data", use_container_width=True):
                    # 클리어 할 때도 현재 작업 중인 백업 파일 삭제
                    supplier = st.session_state.master_info.get("supplier", "")
                    evaluator = st.session_state.master_info.get("evaluator", "")
                    if supplier and evaluator:
                        fname = get_backup_filename(supplier, evaluator)
                        if os.path.exists(fname):
                            try:
                                os.remove(fname)
                            except:
                                pass
                    
                    st.session_state.master_info = {"supplier": "", "evaluator": ""}
                    st.session_state.process_list = []
                    st.session_state.is_evaluating = False # 잠금 해제
                    st.session_state.stop_backup = False
                    st.session_state.show_confirm_clear = False # 상태 초기화
                    st.rerun()
            with col_no:
                if st.button("❌ No, Cancel", use_container_width=True):
                    st.session_state.show_confirm_clear = False # 확인창 닫기
                    st.rerun()