import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse 
# Streamlit 앱 내부에 사용자 정의 HTML과 JavaScript를 삽입하기 위한 라이브러리입니다.
import streamlit.components.v1 as components

# 페이지 설정: 아이콘(📝)과 탭 제목을 영문으로 설정
st.set_page_config(page_title="Supplier OAMI", page_icon="📝", layout="centered")

# 메인 타이틀
st.title("📝 Supplier OAMI Evaluation App")

# 1. 세션 상태 초기화: 앱을 새로고침하기 전까지 입력한 데이터를 임시 보관합니다.
if 'master_info' not in st.session_state:
    st.session_state.master_info = {"supplier": "", "evaluator": ""}
if 'process_list' not in st.session_state:
    st.session_state.process_list = []

# 2. 업체 및 평가자 정보 입력
with st.expander("📌 Step 1: Supplier & Evaluator Info", expanded=st.session_state.master_info["supplier"] == ""):
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        # 라벨에 필수 입력(Required*)임을 명시했습니다.
        supplier = st.text_input("Supplier Name - Required*", value=st.session_state.master_info["supplier"])
    with sub_col2:
        # 라벨에 필수 입력(Required*)임을 명시했습니다.
        evaluator = st.text_input("Evaluator Name - Required*", value=st.session_state.master_info["evaluator"])
    
    # [UPDATE] 버튼 텍스트를 직관적인 'Go Evaluation'으로 변경했습니다.
    if st.button("Go Evaluation"):
        # 업체명이나 평가자 이름 중 하나라도 비어있으면 다음으로 넘어가지 못하게 막는 로직입니다.
        if not supplier or not evaluator:
            st.error("🚨 Please enter both Supplier Name and Evaluator Name.")
        else:
            st.session_state.master_info["supplier"] = supplier
            st.session_state.master_info["evaluator"] = evaluator
            st.success("Ready for evaluation.")

# 업체 정보가 완전히 설정된 경우에만 하단 평가 입력창(Step 2)을 보여줍니다.
if st.session_state.master_info["supplier"] and st.session_state.master_info["evaluator"]:
    st.info(f"📍 Supplier: **{st.session_state.master_info['supplier']}** | Evaluator: **{st.session_state.master_info['evaluator']}**")
    
    # 3. 공정별 상세 평가 입력
    with st.form("pami_input_form", clear_on_submit=True):
        st.subheader("📝 Step 2: PAMI Input per Process")
        
        p_name = st.text_input("Process Name (Optional)")
        p_desc = st.text_input("Description - Required*", placeholder="Enter details...")

        # Process Type 라디오 버튼 (MH, P, WIP)
        st.write("Process Type - Required*")
        p_type = st.radio(
            "Process Type Select", 
            options=["MH", "P", "WIP"],
            index=None, 
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.write("PAMI Score (1: Manual ~ 5: Fully Automated) - Required*")
        p_score = st.radio(
            "PAMI Score Select", 
            options=[1, 2, 3, 4, 5], 
            index=None, 
            horizontal=True,
            label_visibility="collapsed" 
        )
        
        # Remark 필드
        p_remark = st.text_input("Remark (Optional)", placeholder="Add any specific notes...")
        
        add_button = st.form_submit_button("Add to List")
        
        if add_button:
            if not p_desc or p_type is None or p_score is None:
                st.error("🚨 Required fields: Description, Process Type, PAMI Score.")
            else:
                # 자동 번호 매김 (No.)
                current_no = len(st.session_state.process_list) + 1
                
                new_process = {
                    "No.": current_no,
                    "Supplier": st.session_state.master_info["supplier"],
                    "Evaluator": st.session_state.master_info["evaluator"],
                    "Process": p_name if p_name else "N/A",
                    "Description": p_desc,
                    "Type": p_type,
                    "PAMI": p_score,
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "Remark": p_remark if p_remark else ""
                }
                st.session_state.process_list.append(new_process)
                st.toast(f"Added No.{current_no}")

    # 4. 결과 요약 및 내보내기
    if st.session_state.process_list:
        st.write("---")
        st.subheader("📊 Evaluation Summary")
        
        df = pd.DataFrame(st.session_state.process_list)
        
        # 컬럼 배치 순서: No.가 Process 바로 앞에 오도록 구성
        cols = ["Supplier", "Evaluator", "No.", "Process", "Type", "Description", "PAMI", "Remark", "Time"]
        df = df[cols]
        
        # 요약 지표 영역에 '전체 공정 수'와 'OAMI 평균'을 나란히 표시합니다.
        oami_avg = df["PAMI"].mean()
        total_processes = len(df)
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Total Processes", value=f"{total_processes}")
        with m_col2:
            st.metric(label="Total OAMI Average", value=f"{oami_avg:.2f} / 5.0")
        
        # 복사 방식 구분을 위한 탭 설정
        tab_text, tab_table = st.tabs(["📱 1. Mobile (Text Copy)", "🖥️ 2. PC (Table Copy)"])
        
        with tab_text:
            st.info("💡 Best for Mobile. Click the copy icon in the top right of the box.")
            
            # 모바일 텍스트 리포트에도 공정 수(Total Processes)를 추가했습니다.
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
                text_report += f"{row['No.']:<3} | {row['Process']} | {row['Type']:<4} | {row['PAMI']}pt | {row['Description']} | {row['Remark']} | {row['Time']}\n"
            
            text_report += f"==================================================="
            st.code(text_report, language="text")

        with tab_table:
            st.info("💡 Use this to maintain table formatting in PC Outlook.")
            
            html_table = df.to_html(index=False)
            html_table = html_table.replace(
                '<table border="1" class="dataframe">', 
                '<table border="1" cellpadding="8" style="border-collapse: collapse; text-align: left; font-family: Arial, sans-serif; width: 100%; background-color: #ffffff;">'
            )
            
            # 이메일용 HTML 요약 정보에도 공정 수(Total Processes)를 추가했습니다.
            email_content_html = f"""
            <div id="email-content" style="font-family: Arial, sans-serif; padding: 15px; border: 1px solid #ddd; background-color: #f8f9fa;">
                <h3 style="color: #333; margin-top:0;">OAMI Report: {st.session_state.master_info['supplier']}</h3>
                <p style="margin: 5px 0;"><strong>Total Processes:</strong> {total_processes}</p>
                <p style="margin: 5px 0;"><strong>Average OAMI: <span style="color: blue;">{oami_avg:.2f} / 5.0</span></strong></p>
                {html_table}
            </div>
            """
            
            # 자바스크립트 기반 복사 버튼
            custom_html_with_copy_button = f"""
            <div style="margin-bottom: 10px;">
                <button onclick="copyRichText()" style="width:100%; height:40px; background-color:#28a745; color:white; border:none; border-radius:5px; font-size:16px; font-weight:bold; cursor:pointer;">
                    📋 Copy Table for Outlook
                </button>
            </div>
            {email_content_html}
            <script>
            function copyRichText() {{
                var body = document.getElementById('email-content');
                var range = document.createRange();
                range.selectNode(body);
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                try {{
                    document.execCommand('copy');
                    var btn = document.querySelector('button');
                    btn.innerText = '✅ Copied! (Paste into Outlook)';
                    btn.style.backgroundColor = '#198754';
                    setTimeout(function(){{ 
                        btn.innerText = '📋 Copy Table for Outlook'; 
                        btn.style.backgroundColor = '#28a745';
                    }}, 2000);
                }} catch(err) {{
                    alert('Copy failed. Please select manually.');
                }}
                window.getSelection().removeAllRanges();
            }}
            </script>
            """
            components.html(custom_html_with_copy_button, height=450, scrolling=True)

        st.write("") 
        
        # 아웃룩 연동 버튼
        subject = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}"
        
        st.markdown(
            f'<a href="{mail_link}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size: 16px;">'
            f'📨 Open Outlook Mail App</button></a>', 
            unsafe_allow_html=True
        )

        st.write("---")
        
        # CSV 다운로드 백업
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