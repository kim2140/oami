import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse 
# [NEW] Streamlit 앱 내부에 사용자 정의 HTML과 JavaScript를 삽입하기 위한 라이브러리입니다.
import streamlit.components.v1 as components

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
        
        # Outlook에 복사하기 좋도록 HTML 표(Table) 형태로 디자인을 생성합니다.
        # 판다스 데이터프레임을 HTML 표 코드로 변환하고, Outlook에서 깨지지 않게 테두리(border) 속성을 입힙니다.
        html_table = df.to_html(index=False)
        html_table = html_table.replace(
            '<table border="1" class="dataframe">', 
            '<table border="1" cellpadding="8" style="border-collapse: collapse; text-align: left; font-family: Arial, sans-serif; width: 100%;">'
        )
        
        # [NEW] 메일 본문에 들어갈 텍스트와 표를 HTML 태그(div)로 한 번 더 감쌉니다.
        # id="email-content"를 부여하여 자바스크립트가 이 부분만 정확히 찾아 복사할 수 있게 만듭니다.
        email_content_html = f"""
        <div id="email-content" style="font-family: Arial, sans-serif; padding: 15px; border: 1px solid #ddd; background-color: #ffffff; border-radius: 5px;">
            <h3 style="color: #333; margin-top: 0;">OAMI Evaluation Report</h3>
            <p style="margin: 5px 0;"><strong>Supplier:</strong> {st.session_state.master_info['supplier']}</p>
            <p style="margin: 5px 0;"><strong>Evaluator:</strong> {st.session_state.master_info['evaluator']}</p>
            <p style="margin: 5px 0;"><strong>Average OAMI:</strong> <span style="color: blue; font-size: 18px; font-weight: bold;">{oami_avg:.2f} / 5.0</span></p>
            <br>
            {html_table}
        </div>
        """

        # [NEW] 'Copy' 버튼과 클립보드 복사 로직을 수행하는 자바스크립트를 결합한 최종 HTML 블록을 생성합니다.
        # 웹 브라우저의 document.execCommand('copy') 기능을 사용하여 서식(Rich Text)을 그대로 클립보드에 담습니다.
        custom_html_with_copy_button = f"""
        <div style="margin-bottom: 10px;">
            <button onclick="copyRichText()" style="width:100%; height:40px; background-color:#28a745; color:white; border:none; border-radius:5px; font-size:16px; font-weight:bold; cursor:pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                📋 Copy Table for Outlook (표 복사하기)
            </button>
        </div>
        {email_content_html}
        <script>
        function copyRichText() {{
            // 1. 복사할 내용이 담긴 요소를 찾습니다.
            var body = document.getElementById('email-content');
            // 2. 텍스트를 드래그하는 것과 같은 가상의 선택 영역(Range)을 만듭니다.
            var range = document.createRange();
            range.selectNode(body);
            // 3. 기존의 선택 영역을 지우고 방금 만든 영역을 선택합니다.
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
            try {{
                // 4. 선택된 영역을 클립보드로 복사합니다. (서식이 유지됩니다)
                document.execCommand('copy');
                // 5. 복사가 완료되면 버튼 텍스트를 변경하여 피드백을 줍니다.
                var btn = document.querySelector('button');
                btn.innerText = '✅ Copied! (복사 완료! Outlook에 붙여넣으세요)';
                btn.style.backgroundColor = '#198754';
                // 2초 뒤에 원래 버튼 텍스트로 되돌립니다.
                setTimeout(function(){{ 
                    btn.innerText = '📋 Copy Table for Outlook (표 복사하기)'; 
                    btn.style.backgroundColor = '#28a745';
                }}, 2000);
            }} catch(err) {{
                alert('복사에 실패했습니다. 수동으로 드래그하여 복사해 주세요.');
            }}
            // 6. 복사가 끝났으므로 화면의 선택(드래그) 상태를 해제합니다.
            window.getSelection().removeAllRanges();
        }}
        </script>
        """

        st.subheader("📧 Email Body (One-Click Copy)")
        
        # [NEW] components.html을 사용하여 위에서 만든 자바스크립트 내장 HTML을 화면에 렌더링합니다.
        # height를 넉넉하게 주어 표가 잘리지 않도록 하고, 필요시 스크롤되도록 설정합니다.
        components.html(custom_html_with_copy_button, height=450, scrolling=True)

        st.write("") # 간격 띄우기

        # 메일 본문(body)은 사용자가 직접 표를 붙여넣을 것이므로 비워두고, 제목(subject)만 자동으로 입력된 새 메일 창을 띄웁니다.
        subject = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        mail_link = f"mailto:?subject={urllib.parse.quote(subject)}"
        
        st.markdown(
            f'<a href="{mail_link}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
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