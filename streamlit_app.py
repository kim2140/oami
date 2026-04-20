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
        
        # [UPDATE] 선택 옵션을 제거하고 심플하게 텍스트를 직접 입력(Key-in)받도록 변경했습니다.
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
            # 필수값 검증 (공정명 제외)
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
        st.dataframe(df, use_container_width=True)

        # 내보내기 옵션 1: CSV 다운로드 (엑셀 호환)
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Download CSV for Excel",
            data=csv_data,
            file_name=f"OAMI_{st.session_state.master_info['supplier']}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        # 내보내기 옵션 2: 이메일 본문용 텍스트 생성
        st.subheader("📧 Email Data (For Outlook)")
        
        # Outlook 본문에 넣기 좋게 표 형식을 텍스트로 만듭니다.
        email_body = f"OAMI Evaluation Report\n"
        email_body += f"Supplier: {st.session_state.master_info['supplier']}\n"
        email_body += f"Evaluator: {st.session_state.master_info['evaluator']}\n"
        email_body += f"Average OAMI: {oami_avg:.2f}\n"
        email_body += "-"*30 + "\n"
        for i, row in df.iterrows():
            email_body += f"[{row['Type']}] {row['Process']}: {row['PAMI']}pt - {row['Description']}\n"
        
        st.text_area("Copy this text to your Outlook body:", value=email_body, height=200)

        # Outlook 실행 링크 (모바일에서도 작동)
        subject = f"OAMI Report: {st.session_state.master_info['supplier']}"
        encoded_body = urllib.parse.quote(email_body)
        mail_link = f"mailto:?subject={subject}&body={encoded_body}"
        
        st.markdown(f'<a href="{mail_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:40px; border-radius:5px; border:none; cursor:pointer;">📧 Open Default Mail App</button></a>', unsafe_allow_name=True)

        if st.button("🚨 Clear All Data (Start New)"):
            st.session_state.master_info = {"supplier": "", "evaluator": ""}
            st.session_state.process_list = []
            st.rerun()