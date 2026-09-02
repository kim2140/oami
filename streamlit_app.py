# =============================================================================
# Supplier OAMI Evaluation App
# Version: 2.26.0
#
# [버전 히스토리 - 최신순]
#   v2.26.0 - "Preset에 있는 Description 글을 넣을 때는 뭔가 저장이 안 되는
#             것 같다"는 피드백에 따라 draft 자동 저장의 사각지대를 수정.
#             원인: v2.24.0~v2.25.0의 draft 자동 저장은 Description 등 입력
#             칸 자체의 on_change에 걸려 있었는데, on_change는 사용자가 그
#             위젯을 "직접" 조작했을 때만 호출된다. Description Preset(pills)
#             을 탭하면 apply_description_preset()이 p_desc_input/
#             p_type_input 값을 코드에서 프로그램적으로 바꾸는 것이라
#             Description 입력칸을 직접 건드리는 게 아니었고, 그래서 그
#             위젯의 on_change(=draft 저장)가 전혀 호출되지 않았음(Clear
#             Description 버튼도 같은 구조라 마찬가지 문제가 있었음). 즉
#             "직접 타이핑"으로 채운 내용은 draft에 잘 반영됐지만, "프리셋
#             탭"이나 "Clear 버튼"으로만 바뀐 내용은 draft에 반영되지 않는
#             사각지대가 있었음.
#             수정: apply_description_preset()과 clear_description_field()
#             끝에 save_draft_local_only() 호출을 추가해서, 프리셋을 탭하거나
#             Clear를 누른 그 즉시 스스로 draft를 저장하도록 함. 이제
#             Description을 직접 타이핑하든, 프리셋을 탭해서 채우든, Clear로
#             비우든 모든 경우에 draft가 최신 상태로 남는다.
#   v2.25.0 - "인터넷이 안 되거나 중간에 정지가 잠깐 되면 문제가 생기지
#             않을까?"라는 질문에 대응. v2.24.0에서 Process Name/Description/
#             Type/Score/Remark 다섯 칸에 걸어둔 draft 자동 저장이 매번
#             save_temp_backup()(로컬 저장 + 클라우드 저장 시도)을 그대로
#             호출하고 있었는데, 오프라인이거나 네트워크가 불안정하면 칸을
#             옮길 때마다 has_internet() 사전 확인(캐시 만료 시 최대 2.5초)
#             이나 API 호출 자체(최대 8초)만큼 짧게 멈춰 보일 수 있어서,
#             필드가 5개나 되는 만큼 이 지연이 이전(제출 버튼 딱 한 번)보다
#             훨씬 자주 체감될 수 있다는 지적이 타당했음. 이를 해결하기 위해
#             draft 자동 저장 전용으로 save_draft_local_only()라는 새 함수를
#             만들어, 로컬 파일 저장만 즉시 하고 클라우드 저장은 아예 시도
#             하지 않도록 분리함(로컬 저장은 네트워크를 타지 않으므로 인터넷
#             상태와 무관하게 항상 빠름). 클라우드 반영은 이미 있던
#             sync_local_to_cloud_if_needed()(평가 중일 때 매 rerun마다
#             확인하되 60초 간격으로만 재시도)가 맡아서, 온라인이 되면 늦어도
#             다음 화면 갱신 시점에 자동으로 클라우드에도 반영됨. 실제
#             process_list에 저장하는 Save/Update/Delete/Go Evaluation/
#             Restore 같은 "확정" 동작은 여전히 save_temp_backup()을 그대로
#             호출해 로컬+클라우드를 즉시 동시에 시도한다(이 동작들은 자주
#             일어나지 않으므로 지연 우려가 없고, 오히려 즉시 클라우드
#             반영이 더 중요함). 두 함수가 draft 생성 규칙을 다르게 적용하는
#             실수를 막기 위해 공통 로직은 _build_backup_payload_with_draft()
#             로 분리해서 함께 씀. 자세한 내용은 아래 [v2.25.0 변경사항] 및
#             save_temp_backup()/save_draft_local_only() 함수 주석 참고.
#   v2.24.0 - "타이핑을 하다가 좀 오랫동안 아무것도 안 하면 다시 처음으로
#             돌아가는 경우가 있다. Restore로 예전 글을 찾아서 다시 시작할
#             순 있지만, 그래도 이 문제를 해결해줄 수 있나"는 요청에 대응.
#             근본 원인은 Streamlit의 세션이 브라우저-서버 연결에 묶여 있어서,
#             (화면을 오래 꺼두거나 다른 앱으로 오래 전환하는 등으로) 연결이
#             끊기면 서버가 그 세션을 비우고 완전히 새 세션으로 다시 시작하는
#             데 있음 — 이건 앱 코드로 "연결 끊김 자체"를 막을 수 있는 부분이
#             아니라서 완전히 없앨 수는 없음을 사용자에게 설명함. 대신 실제
#             데이터 손실을 줄이는 방향으로 개선: 지금까지는 "Save New
#             Process"를 눌러야만 process_list에 들어가 백업됐고, 그 전에
#             타이핑만 하고 있던 새 항목 내용은 세션이 끊기면 통째로
#             사라졌음. 이제 Process Name/Description/Type/Score/Remark 다섯
#             칸에 on_change=save_temp_backup을 걸어, 칸에서 포커스가 벗어날
#             때마다(라디오는 선택 즉시) 지금까지 입력한 내용을 "draft"로
#             함께 자동 백업함. 세션이 끊겨도 "Restore Selected Session"으로
#             복구하면 이전에 저장해둔 항목들뿐 아니라 마지막으로 타이핑하던
#             draft까지 함께 돌아와서, 처음부터 다시 타이핑할 필요가 없어짐.
#             (기존 항목을 수정하던 중이었다면 원본은 이미 안전하게 저장되어
#             있으므로 draft 대상에서는 제외 — 자세한 내용은 save_temp_backup()
#             함수 주석과 아래 [v2.24.0 변경사항] 참고.)
#   v2.23.0 - "모바일로 보니까 무조건 한 줄 내려가는 거 같아. 그럼 그냥 한 줄
#             내리고 오른쪽으로 보내줘"라는 피드백에 따라 Clear Description
#             아이콘 버튼 배치 방식 변경. v2.22.0의 st.columns([6,1]) 방식은
#             화면이 넓을 때(PC)는 Description과 같은 줄에 나왔지만, 좁은
#             모바일 화면(약 380px 이하)에서는 Streamlit이 컬럼을 자동으로
#             세로로 쌓아버려서 버튼이 왼쪽 정렬로 아래 줄에 내려가는,
#             화면 크기에 따라 다른 결과가 나왔음(직접 테스트로 확인). 이를
#             컬럼 대신 st.container(key="clear_desc_row") + CSS
#             (align-items:flex-end)로 교체해서, 화면 크기와 상관없이 항상
#             "Description 아래 자기만의 줄 + 그 줄의 오른쪽 끝"에 오도록
#             통일함. 버튼이 자기 줄을 독차지하고 오른쪽 끝에 떨어져 있어서
#             Description을 쓰고 다음 칸으로 넘어갈 때 실수로 누를 확률이
#             더 줄어듦. 버튼 동작(clear_description_field 호출)은 이전과
#             동일.
#   v2.22.0 - "Clear Description 버튼이 커서 쓰다가 실수로 누를 수 있을 것
#             같다"는 스크린샷 피드백에 따라, Description 아래에 가로로 길게
#             있던 "🗑️ Clear Description" 버튼을 없애고, Description 입력칸
#             오른쪽 같은 줄에 휴지통 아이콘(🗑️)만 있는 작은 버튼으로 교체.
#             st.columns([6, 1])로 입력칸과 버튼을 한 줄에 배치하고, 버튼
#             쪽에 spacer를 넣어 세로 위치를 입력칸과 맞춤. 툴팁(help)에는
#             기존 "Clear Description" 문구를 그대로 남겨 무슨 버튼인지는
#             바로 확인 가능. 버튼이 눌렸을 때의 동작(clear_description_field
#             호출 → Description 칸만 비움)은 그대로 유지, 크기/위치만 변경.
#             (참고: PC처럼 화면이 넓을 때는 Description 오른쪽 같은 줄에
#             나오지만, 약 380px 이하의 좁은 휴대폰 화면에서는 Streamlit이
#             컬럼을 자동으로 세로로 쌓아서 버튼이 Description 아래 줄로
#             내려간다 — 크기가 작아진 효과는 그대로 유지되므로, 사용자
#             확인 후 이 상태로 유지하기로 확정함.)
#   v2.21.0 - "Process Name과 Description이 Type/Score/Remark/Save 버튼과
#             같은 테두리 박스 안에 들어가 있어야 한다"는 스크린샷 피드백에
#             따라 레이아웃 조정. v2.20.0까지는 Process Name·Description이
#             테두리 없는 영역에, Type/Score/Remark/Save만 st.form의 테두리
#             박스 안에 있어서 시각적으로 분리되어 보였음. 이번 변경으로
#             st.form을 테두리만 있는 일반 컨테이너(st.container(border=True))
#             로 교체하고, 그 안에 Process Name → Description → Clear
#             Description 버튼 → Type → Score → Remark → Save/Update 버튼을
#             전부 넣어 하나의 박스로 통일함(사용자 확인: "프리셋은 박스
#             밖(추천)" 선택 — Description Preset 버튼은 지금처럼 박스 바깥
#             위쪽에 그대로 둠). st.form을 걷어냈지만 v2.19.0에서 고친
#             "폼 안 위젯은 제출 전까지 session_state에 반영 안 됨" 문제는
#             재발하지 않음 — Process Name/Description은 원래부터 폼 밖에
#             있었고 그대로 유지, Type/Score/Remark는 st.form 없이도 즉시
#             session_state에 반영되는 일반 위젯이라 프리셋 이어붙이기·Type
#             자동 매핑 동작에 영향 없음. 제출 버튼만 st.form_submit_button
#             에서 일반 st.button(on_click=process_form_submit)으로 교체.
#   v2.20.0 - "Clear를 프리셋 안에 넣지 말고, Description을 Process Name
#             아래에 두고 거기에 Clear 버튼을 만들어달라"는 요청에 따라
#             레이아웃 조정. v2.19.0에서 프리셋 목록 맨 끝에 있던
#             "🗑️ Clear"를 pills 옵션에서 빼고, Description 입력칸 바로
#             아래의 독립된 버튼(🗑️ Clear Description)으로 옮김. Process
#             Name도 폼 밖으로 옮겨 Description 바로 위에 배치해서 원래
#             순서(Process Name → Description)를 되살림. Type/Score/Remark/
#             제출 버튼만 폼 안에 남음.
#   v2.19.0 - Description 프리셋 동작을 "하나 고르면 끝(toggle)"에서 "누를
#             때마다 뒤에 이어붙이는(append) 방식"으로 전면 변경. 예를 들어
#             Unloading을 누르고 Storaging을 누르면 Description에 두 개가
#             다 나오도록(예: "Unloading, Storaging") 함. 직접 타이핑한 글자
#             뒤에 프리셋을 눌러도 그 뒤에 이어붙고, Type은 매번 "가장 최근에
#             누른" 프리셋 기준으로 갱신됨. 프리셋 버튼 맨 끝에 전체 지우기용
#             "🗑️ Clear" 버튼을 추가. 버튼을 눌러도 선택된 채로 남지 않고
#             매번 중립 상태로 돌아가 토글처럼 보이지 않음. 이와 함께
#             Description 입력칸을 st.form 밖으로 이동(폼 안 위젯은 제출 전
#             까지 타이핑한 값이 서버에 반영되지 않아, "타이핑 후 프리셋
#             클릭 시 이어붙이기"가 실제로는 덮어써지는 문제를 테스트로 발견
#             하고 수정함 — 자세한 내용은 아래 [v2.19.0 변경사항] 참고).
#   v2.18.0 - Description 프리셋 목록/순서 정리 요청 반영: Forklifting·Shipping
#             삭제, "Pick & Place" → "Feeding"으로 교체, Stamping 다음에
#             "Piecing" 추가(Type: P로 지정), 제조업 공정 흐름(자재 투입 →
#             가공 → 조립/용접 → 도장 → 마무리/품질 → 포장)에 맞춰 전체 순서
#             재배치. 추가로 "Unloading(입고 하역)은 맨 앞, Loading(출하
#             상차)은 Packaging 바로 뒤 맨 끝"이라는 요청에 따라 두 항목의
#             위치를 각각 맨 앞/맨 뒤로 이동. (총 27개 → 26개: 2개 삭제 +
#             1개 추가, 나머지 항목의 Type 매핑은 그대로 유지)
#   v2.17.0 - "상도/중도/하도 영문 표기가 맞냐"는 질문에 따라 웹 검색으로 도장
#             공정 용어를 재검증(출처는 아래 [v2.17.0 변경사항] 참고). 검증
#             결과 하도=Primer, 중도=Intermediate Coat, 상도=Topcoat가 맞고,
#             v2.16.0에서 빠져있던 "하도(Primer)"를 추가하고 "Mid Coat"를
#             더 정확한 표준 용어인 "Intermediate Coat"로 수정. 순서도
#             Pretreatment → Primer → Intermediate Coat → Top Coat → Oven
#             (전처리 → 하도 → 중도 → 상도 → 오븐)으로 바로잡음.
#   v2.16.0 - "가공 중에 밀링/선반이 있고, Paint에 상도/중도/오븐/전처리도
#             넣어달라"는 요청에 따라 Description 프리셋 5개 추가(20개 →
#             25개): Milling, Turning(선반은 Turning으로 표기, 사용자 확인
#             거침), Pretreatment, Top Coat, Mid Coat, Oven. Milling/Turning은
#             Molding/Trimming 뒤에, 도장 관련 4개는 Welding 뒤에 배치. 전부
#             Type "P"(생산)로 지정.
#   v2.15.0 - "프리셋 글자가 전부 대문자로 되어있어서 보기 좀 그렇다"는
#             피드백에 따라 공정명 표기를 전부 대문자(STORAGING 등)에서
#             첫 글자만 대문자(Storaging 등)로 변경. 버튼에 보이는 글자와
#             Description에 실제로 채워지는 글자가 항상 같으므로 둘 다 함께
#             바뀜. 목록 순서/Type 매핑 내용 자체는 변경 없음.
#   v2.14.0 - "프리셋은 타이핑 없이 셀렉만 되게 해달라, 모바일에서 키보드가
#             뜨는게 불편하다"는 요청에 따라 Description 프리셋 위젯을
#             st.selectbox(검색용 텍스트 입력 포함) → st.pills(탭만으로 고르는
#             알약 버튼)로 변경. 키보드가 뜰 일이 없고, 화면 너비에 맞춰
#             자동 줄바꿈되어 표시됨. 선택/해제 및 Description·Type 자동 채움
#             동작은 기존과 동일하게 유지.
#   v2.13.0 - Description 프리셋 목록을 실제 현장 20개 공정(STORAGING ~
#             SHIPPING)으로 교체하고, 공정마다 지정된 Type(MH/Production/WIP)을
#             함께 저장해 프리셋을 고르면 Description과 Type(MH/P/WIP)이
#             동시에 자동으로 채워지도록 개선. 자동으로 채워진 뒤에도 Type은
#             잠기지 않으므로 필요하면 계속 직접 눌러서 바꿀 수 있음.
#   v2.12.0 - "코드 상 기본값은 3단계로 두고, 사람(기기)마다 다른 기본값을 쓸 수
#             없냐"는 요청에 따라 v2.11.1(기본값 2단계로 변경)을 되돌려 다시
#             3단계로 고정. (브라우저 localStorage로 기기별 자동 기억까지
#             시도했으나 Streamlit 컴포넌트의 iframe 보안 제약으로 자동 복원이
#             동작하지 않아 제외함 — 아래 [v2.12.0 변경사항] 상세 참고, 대안은
#             사용자 확인 후 별도 반영 예정)
#   v2.11.1 - (v2.12.0에서 되돌림) 새로 접속했을 때 적용되는 글자 크기 기본값을
#             3단계(17px)에서 2단계(15px)로 임시 변경했었음.
#   v2.11.0 - 글자 크기 조절을 Small/Medium/Large 라디오 3단계에서 "−"/"+"
#             줌인·줌아웃 5단계(13/15/17/20/24px)로 변경. 가장 작은 크기는
#             기존과 동일(13px)하게 유지하고, 가장 큰 크기는 기존 Large
#             (20px)보다 더 키움(24px). 새로고침해도 유지되는 것은 그대로.
#   v2.10.0 - Description 프리셋 목록을 20개로 확장(입고/보관 → 자재 이동 →
#             절삭/성형/가공 → 접합 → 표면처리 → 품질 → 포장 순). "Insert"
#             버튼은 번거롭다는 피드백에 따라 제거하고, 드롭다운에서 고르는
#             즉시 Description 칸에 반영되도록 변경 (드롭다운은 리셋하지
#             않고 고른 값을 그대로 유지).
#   v2.9.0 - Description 프리셋 목록을 제조업 공정에 맞게 확장: 자재 이동
#            (Moving/Feeding/Loading/Unloading) → 가공/조립(Assembly/
#            Welding/Machining/Painting) → 품질/포장(Inspection/Packaging)
#            순의 기본 공정 단어 10개로 구성. 세부 내용은 이어서 직접
#            입력(key-in)하는 방식은 그대로 유지.
#   v2.8.0 - "Description 프리셋 셀렉트가 안 된다"는 피드백에 따라 방식 변경:
#            자동 적용(on_change) 대신 드롭다운에서 고르고 "Insert into
#            Description" 버튼을 눌러야 반영되는 2단계 방식으로 바꿔 동작을
#            더 명확하게 함. 프리셋 목록도 실제 요청하신 Moving/Feeding/
#            Assembly/Welding으로 교체.
#   v2.7.0 - Description 입력칸에 미리 정의된(predefined) 문구를 고를 수 있는
#            프리셋 드롭다운 추가. 프리셋을 고르면 Description 칸이 그
#            문구로 채워지고, 이어서 타이핑해 내용을 덧붙이거나 전부 지우고
#            새로 쓸 수 있음. (DESCRIPTION_PRESETS 목록은 예시이므로 실제
#            사용하는 문구로 직접 교체 필요)
#   v2.6.0 - "Large로 바꾸고 새로고침하면 Medium으로 돌아간다" 문제 해결.
#            글자 크기 선택값을 URL 쿼리 파라미터(?text_size=...)에도 저장해서
#            브라우저를 새로고침(F5)해도 마지막 선택이 유지되도록 함.
#   v2.5.0 - 글자 크기 선택 UI를 아이콘 버튼 → 다시 라디오 버튼으로 되돌림
#            (휴대폰 좁은 화면에서 버튼 3개가 세로로 쌓이는 문제 해결).
#            v2.3.0 라디오 버전에 있었던 "화면 전환 시 선택값이 사라지는"
#            문제는 index+key 동시 사용이 원인으로 보여 제거해서 해결.
#            옵션 앞 "A" 글자 크기를 다르게 표시하는 것은 그대로 유지.
#   v2.4.0 - "인터넷 안 되면 앱이 멈춘다" 문제 해결: 인터넷 연결 여부를 빠르게
#            사전 확인(최대 2.5초) + 소켓 타임아웃(8초) 적용해 오프라인 시
#            더 이상 화면이 멈추지 않고 즉시 로컬 저장만으로 계속 진행됨.
#            화면에 온라인/오프라인 상태 표시 추가. 클라우드 재동기화도
#            세션당 1회 → 1분 간격 재시도로 변경해 인터넷 복구 시 자동 반영.
#   v2.3.1 - 글자 크기 선택 UI를 라디오 버튼 → 크기별 아이콘 버튼(A/A/A)으로 변경
#            (버튼 안 "A" 자체를 작게/중간/크게 실제 크기로 표시, 선택된 크기는
#             색상(primary) + 체크(✓) 표시로 강조)
#   v2.3.0 - 화면 UI 텍스트(라벨/버튼/안내·경고·에러 메시지) 영어로 변경
#            + 글자 크기 선택 기능(Small/Medium/Large) 추가 (메인 화면 최상단)
#   v2.2.1 - Summary/Export 컬럼 순서 변경 (No. > Process > Description > Type > PAMI > Remark > Time)
#   v2.2.0 - 저장/복구/동기화 로직 재설계 (로컬+클라우드 이중 저장,
#            timestamp 비교 기반 복구 목록 표시, 1일 1회 자동 동기화) - Fix 1 재설계
#   v2.1.0 - Google Sheets 14일 초과 백업 행 자동 삭제 (세션/wake-up 시 1회 실행) - Fix 2
#
# [개요]
# 공급업체 OAMI(Operation Assessment & Management Index) 평가 앱.
# 프로세스별 Type(MH/P/WIP) 및 PAMI 점수(1~5)를 입력하고
# Google Sheets(클라우드) + 서버 로컬 파일에 이중 백업.
#
# [v2.26.0 변경사항 - 프리셋/Clear로 바뀐 Description도 draft에 반영]
#   - 사용자 피드백: "Preset에 있는 Description 글을 넣을 때는 뭔가 저장이
#     안 되는 것 같은데."
#   - 원인: Streamlit의 on_change 콜백은 "그 위젯을 사용자가 직접 조작"할
#     때만 호출된다. Description Preset(pills)을 탭하면 실행되는
#     apply_description_preset()은 Description 입력칸(p_desc_input)의 값을
#     코드에서 직접 바꾸는 것이지, 그 입력칸을 사용자가 직접 타이핑/블러한
#     게 아니다. 따라서 v2.24.0~v2.25.0에서 Description 입력칸에 걸어둔
#     on_change=save_draft_local_only는 프리셋 탭으로 인한 변경에는 전혀
#     반응하지 않았다. Clear Description 버튼(clear_description_field())도
#     같은 방식으로 값을 직접 비우기 때문에 동일한 사각지대가 있었다.
#     결과적으로 "직접 타이핑"만 draft에 반영되고, "프리셋으로만 채운
#     Description"이나 "Clear로 방금 비운 상태"는 draft에 반영되지 않는
#     문제가 있었다.
#   - 수정: apply_description_preset()과 clear_description_field() 각각의
#     끝부분에 save_draft_local_only()를 명시적으로 호출하도록 추가. 이
#     두 함수는 이미 Description/Type 값을 다 바꾼 뒤이므로, 그 시점에
#     draft를 저장하면 프리셋/Clear로 인한 변경도 정확히 반영된다. 결과적
#     으로 Description을 (1) 직접 타이핑, (2) 프리셋 탭, (3) Clear로 비움
#     — 이 세 가지 경로 전부 draft 자동 저장을 타게 됐다.
#   - save_draft_local_only()는 v2.25.0에서 만든 대로 로컬 저장만 하므로,
#     프리셋 탭이 잦아도(연속으로 여러 개를 탭하는 경우 포함) 네트워크
#     지연 없이 항상 빠르게 끝난다.
#
# [v2.25.0 변경사항 - draft 자동 저장을 "로컬만" 하도록 분리(오프라인 대응)]
#   - 사용자 질문: "일단 테스트는 다 좋은데 혹시 인터넷이 안되거나 중간에
#     정지가 잠깐 되면 문제가 생기지 않을까?" — v2.24.0에서 새로 추가한
#     draft 자동 저장(Process Name/Description/Type/Score/Remark 다섯 칸의
#     on_change)이 매번 save_temp_backup()을 그대로 호출하고 있었는데, 이
#     함수는 로컬 저장뿐 아니라 클라우드 저장까지 항상 시도한다.
#   - 문제점 분석: 클라우드 저장 시도 전에 has_internet()으로 먼저 인터넷
#     연결을 확인하는데(정상 상태여도 최대 INTERNET_CHECK_TIMEOUT_SEC=2.5초,
#     10초간 캐시), 그 캐시가 만료된 시점에 오프라인이거나 네트워크가
#     불안정하면 그때마다 다시 2.5초를 기다려야 한다. 어쩌다 연결은 됐는데
#     도중에 끊기는 경우엔 API 호출 자체의 최대 대기 시간(NETWORK_TIMEOUT_
#     SEC=8초)만큼 걸릴 수도 있다. 이 지연 자체는 v2.4.0 때부터 있던
#     기존 안전장치라 새로운 버그는 아니지만, v2.24.0으로 인해 이 지연이
#     발생할 수 있는 지점이 "제출 버튼 누를 때 딱 한 번"에서 "다섯 개
#     입력칸에서 포커스가 벗어날 때마다"로 늘어나서, 오프라인/불안정한
#     네트워크에서는 체감 빈도가 훨씬 높아질 수 있었다.
#   - 해결: draft 자동 저장 전용 함수 save_draft_local_only()를 새로 만들어
#     로컬 파일 저장만 하고 클라우드 저장은 시도하지 않도록 함. 로컬 파일
#     저장은 네트워크를 전혀 타지 않는 순수 디스크 쓰기라 인터넷 상태와
#     무관하게 항상 즉시 끝난다. draft는 세션이 갑자기 끊겼을 때를 대비한
#     임시 보호장치일 뿐 최종 제출이 아니므로, 클라우드 반영이 즉시일
#     필요는 없다고 판단 — 클라우드 반영은 이미 있던
#     sync_local_to_cloud_if_needed()(평가 중일 때 매 rerun마다 확인하되
#     SYNC_RECHECK_INTERVAL_SEC=60초 간격으로만 재시도)가 맡는다. 즉,
#     인터넷이 끊긴 동안 타이핑해도 화면이 멈추지 않고, 온라인으로 돌아오면
#     늦어도 다음 화면 갱신 시점에 draft까지 포함해 자동으로 클라우드에
#     반영된다.
#   - 실제 process_list에 반영되는 "확정" 동작(Save New Process/Update
#     Process/Delete/Go Evaluation/Restore Selected Session)은 그대로
#     save_temp_backup()을 호출해 로컬+클라우드를 즉시 동시에 시도한다.
#     이 동작들은 다섯 입력칸처럼 자주 일어나지 않고, 오히려 즉시 클라우드
#     반영이 더 중요한 시점이라 기존 방식을 유지하는 게 맞다고 판단.
#   - 두 함수(save_temp_backup, save_draft_local_only)가 "언제 draft를
#     남길지" 규칙을 서로 다르게 구현해버리는 실수를 막기 위해, 공통 로직을
#     _build_backup_payload_with_draft()라는 헬퍼로 분리해서 두 함수가 함께
#     사용하도록 리팩터링함.
#
# [v2.24.0 변경사항 - 저장 전 타이핑 중이던 새 항목도 draft로 자동 백업]
#   - 사용자 피드백: "타이핑을 하다가 좀 오랫동안 아무것도 안 하면 다시
#     처음으로 돌아가는 경우가 있다. 물론 restore에서 과거 내가 쓴 글을
#     찾아서 다시 시작하면 되긴 하는데, 그래도 이 문제를 해결해줄 수 있나."
#   - 원인 분석: Streamlit은 브라우저 탭과 서버 사이의 연결(WebSocket)에
#     세션 상태를 묶어서 관리한다. 모바일에서 화면을 꺼두거나 다른 앱으로
#     오래 전환해서 이 연결이 끊기면, 서버는 기존 세션을 정리하고 다음 접속
#     때 완전히 새 세션(빈 master_info, 빈 process_list, is_evaluating=False)
#     으로 시작한다 — 사용자 입장에서는 "Step 1 화면으로 되돌아간" 것처럼
#     보인다. 이 연결 끊김 자체(모바일 OS의 백그라운드 탭 정지, 네트워크
#     불안정 등)는 앱 코드 레벨에서 완전히 막을 수 있는 부분이 아니다.
#   - 대신 초점을 "연결이 끊겨도 잃어버리는 내용을 최소화하는 것"으로 잡음.
#     기존에는 process_list에 실제로 "Save New Process"로 저장된 항목만
#     로컬+클라우드에 백업되고 있어서, 저장 버튼을 누르기 전 타이핑만 하고
#     있던 새 항목의 Process Name/Description/Type/Score/Remark는 세션이
#     끊기는 순간 그대로 사라졌다(Restore를 해도 "이전에 저장된 항목들"까지만
#     돌아오고, 지금 막 쓰던 내용은 못 돌아옴).
#   - 구현:
#     1) save_temp_backup()이 is_inserting=True(새 항목 입력 중)일 때는
#        현재 입력칸 다섯 개의 값을 "draft" 딕셔너리로 만들어 backup_data에
#        함께 저장하도록 확장(다섯 칸이 전부 비어있으면 draft는 저장 안 함).
#     2) Process Name/Description/Type/Score/Remark 위젯 다섯 개 모두에
#        on_change=save_temp_backup을 추가. 전부 st.form 밖의 일반 위젯이라
#        (v2.19.0~v2.21.0에서 이미 폼 밖으로 옮겨둔 상태) 텍스트 입력은
#        블러 시, 라디오는 선택 즉시 콜백이 호출되어 즉시 draft가 백업된다.
#     3) "Restore Selected Session" 버튼 콜백에서, 기존처럼 info/list를
#        복원하고 sync_form_with_state()를 호출한 "다음"에 draft가 있으면
#        그 값을 다섯 입력칸에 덮어씀(순서가 바뀌면 sync_form_with_state()가
#        새 항목용 빈 값으로 되돌려서 draft가 지워지므로 순서가 중요함).
#   - 기존 항목을 수정하던 중(is_inserting=False)이었다면 draft를 남기지
#     않는다 — 그 항목의 원본 데이터는 이미 process_list에 안전하게 저장되어
#     있고, 수정 중이던 위치(인덱스)가 세션 재시작 후 다른 항목과 어긋날
#     위험을 피하기 위함. 이 경우는 "저장된 원본을 잃는" 문제가 아니라
#     "마지막 수정 몇 글자를 다시 입력해야 할 수도 있는" 더 작은 문제로
#     남는다.
#
# [v2.23.0 변경사항 - Clear Description 버튼을 화면 크기 무관하게 오른쪽 정렬]
#   - v2.22.0에서 st.columns([6,1])로 Description 오른쪽에 버튼을 배치했으나,
#     사용자가 실제 휴대폰으로 확인해보니 좁은 화면에서는 Streamlit이 컬럼을
#     자동으로 세로로 쌓아서 버튼이 왼쪽 정렬로 아래 줄에 내려간다는 점을
#     발견(직접 브라우저 테스트로도 재확인함, 약 380px 이하에서 재현).
#   - 사용자 피드백: "모바일로 보니까 무조건 한 줄 내려가는 거 같아. 그럼
#     그냥 한 줄 내리고 오른쪽으로 보내줘 그럼 더 실수로 삭제할 확률을
#     줄일테니까" — 화면 크기에 따라 다르게 보이는 대신, 아예 처음부터
#     "Description 아래 자기만의 줄 + 오른쪽 끝" 하나로 통일하기로 함.
#   - 구현: st.columns 대신 st.container(key="clear_desc_row")를 사용.
#     Streamlit은 컨테이너에 key를 주면 해당 블록의 감싸는 div에
#     "st-key-<key>" 클래스를 자동으로 붙여주므로, 이 클래스를 selector로
#     삼아 st.markdown(..., unsafe_allow_html=True)으로 CSS
#     "display:flex; align-items:flex-end;"를 적용했다. Streamlit의 세로
#     블록(stVerticalBlock)은 기본적으로 flex-direction이 column이라 주축이
#     세로 방향이므로, 자식(버튼)을 가로(교차축) 오른쪽으로 붙이려면
#     justify-content가 아니라 align-items를 써야 한다는 점에 유의.
#   - 컬럼 분할 자체가 없는 방식이라 화면 폭에 따라 줄바꿈 여부가 달라질
#     일이 없고, PC/모바일 모두 항상 같은 모양(Description 아래 줄, 오른쪽
#     끝)으로 보인다.
#
# [v2.22.0 변경사항 - Clear Description 버튼을 작은 아이콘 버튼으로 축소]
#   - 스크린샷 피드백: "쓰다가 실수로 삭제할 수 있을 것 같은데, Description
#     옆에 작은 휴지통 버튼만 만들어줄 수 있을까?" — v2.21.0까지는
#     "🗑️ Clear Description"이 Description 입력칸 바로 아래에 가로로 긴
#     버튼으로 있어서, Description을 다 쓰고 아래로 이동하다가 실수로 누르기
#     쉬운 위치/크기였다.
#   - 디자인 확정 전 AskUserQuestion으로 버튼 위치를 확인 → "Description
#     오른쪽 같은 줄(추천)"을 선택. 즉 입력칸 아래 별도 줄이 아니라, 입력칸과
#     같은 줄 오른쪽 끝에 작게 배치하기로 확정.
#   - 구현: st.columns([6, 1])로 한 줄을 나눠, 왼쪽(넓은 칸)에는 그대로
#     Description text_input, 오른쪽(좁은 칸)에는 라벨 없이 "🗑️" 아이콘만
#     있는 st.button을 배치. 오른쪽 칸에는 Description처럼 위에 라벨이
#     없으므로, st.write("")로 빈 줄을 하나 넣어 라벨 높이만큼 아래로 내려서
#     입력칸과 버튼의 세로 위치(베이스라인)를 맞췄다.
#   - 버튼을 눌렀을 때 호출되는 함수(clear_description_field)와 동작
#     (Description 칸만 비우고 Process Name/Type/Score/Remark는 그대로 둠)은
#     전혀 바뀌지 않았다 — 버튼의 겉모습(라벨 텍스트 → 아이콘만, 전체 폭 →
#     좁은 폭, 아래 줄 → 오른쪽 같은 줄)만 바뀐 것. 버튼 위에 마우스를
#     올리면(모바일은 길게 누르면) 여전히 "Clear Description" 툴팁이 뜨므로
#     무슨 버튼인지는 계속 알 수 있다.
#
# [v2.21.0 변경사항 - Process Name/Description을 테두리 박스 안으로 통합]
#   - 스크린샷 피드백: "박스 안에 Process Name하고 Description 들어가
#     있어야지" — v2.20.0까지는 Process Name·Description이 테두리 없는
#     영역에 있고, Type/Score/Remark/Save 버튼만 st.form의 테두리 박스 안에
#     있어서 하나의 입력 폼인데도 시각적으로 둘로 나뉘어 보였다.
#   - 디자인 확정 전 AskUserQuestion으로 "프리셋 버튼까지 박스 안에 넣을지"
#     확인 → 사용자가 "프리셋은 박스 밖(추천)"을 선택. 즉 Description Preset
#     pills는 지금처럼 박스 바깥 위쪽에 그대로 두고, 그 아래 Process Name부터
#     Save/Update 버튼까지만 하나의 박스로 묶기로 확정.
#   - 구현: st.form("pami_input_form", ...)을 걷어내고
#     st.container(border=True)로 교체. 그 컨테이너 안에 Process Name →
#     Description → Clear Description 버튼 → Type → Score → Remark →
#     Save/Update 버튼을 전부 배치.
#   - st.form_submit_button(btn_text, on_click=process_form_submit)은
#     일반 st.button(btn_text, on_click=process_form_submit)으로 교체(일반
#     컨테이너에는 form 전용 submit 버튼을 쓸 수 없음).
#   - 주의: st.form을 없애도 v2.19.0에서 고쳤던 "폼 안 위젯은 제출 전까지
#     session_state 미반영" 문제는 재발하지 않는다. Process Name/Description은
#     원래부터 폼 밖에 있던 위젯을 그대로 컨테이너 안으로 옮긴 것뿐이고,
#     Type/Score/Remark 라디오·텍스트 입력도 일반 컨테이너 안에서는 다른 값
#     변경 시 즉시 session_state에 반영되므로 프리셋 이어붙이기·Type 자동
#     매핑·Remark 입력 모두 기존과 동일하게 동작한다(직접 브라우저 테스트로
#     재확인 완료).
#
# [v2.20.0 변경사항 - Clear 버튼 분리 + Process Name/Description 순서 복원]
#   - "Preset에 Clear를 넣지 말고, Description은 Process Name 아래에 위치
#     하게 하고, 거기에 Clear 버튼을 만들어달라"는 요청에 따라 추가.
#   - st.pills의 options에서 DESCRIPTION_PRESET_CLEAR_LABEL("🗑️ Clear
#     Description")을 제거 — 이제 프리셋 버튼들은 순수하게 26개 공정명만
#     보여준다.
#   - apply_description_preset()에서 "전체 지우기" 분기를 떼어내
#     clear_description_field()라는 별도 함수로 분리하고, Description 입력칸
#     바로 아래에 독립된 st.button(on_click=clear_description_field)으로
#     배치. 이 버튼은 Description 칸만 비우고 Process Name/Type/Score/Remark
#     는 그대로 둔다.
#   - v2.19.0에서 "Description을 st.form 밖으로 옮기며" Process Name보다
#     위에 놓이게 됐던 순서를 되돌리기 위해, Process Name도 함께 폼 밖으로
#     옮겨서 Description 바로 위에 배치. Process Name은 append 문제와 무관
#     하지만, 폼 밖 위젯끼리는 원하는 순서로 자유롭게 배치할 수 있어서 이
#     방법으로 원래 순서(Process Name → Description)를 되살렸다. Type/
#     Score/Remark/제출 버튼만 계속 폼 안에 남는다.
#
# [v2.19.0 변경사항 - Description 프리셋을 "선택"에서 "이어붙이기"로 변경]
#   - "누르면 그냥 타이핑이 되게 해줘, unloading 누르고 storaging 누르면 두개
#     다 나오게. toggle 형식은 필요 없고, 중간에 description을 넣거나 지울 수
#     있고, description에 글을 쓰고 preset을 누르면 뒤에 내용을 넣어달라.
#     Type은 마지막 preset 기준으로 맞추고, 마지막에 delete키를 하나 넣어달라"
#     는 요청에 따라 추가.
#   - apply_description_preset() 로직을 "고른 값으로 Description을 덮어쓰기"
#     에서 "고를 때마다 기존 내용 뒤에 ', '로 이어붙이기"로 변경. 직접
#     타이핑한 문구 뒤에 프리셋을 눌러도 동일하게 이어붙는다.
#   - Type은 프리셋을 누를 때마다 그 프리셋의 매핑값으로 갱신되므로, 여러 개를
#     연달아 누르면 자연스럽게 "가장 최근에 누른" 프리셋 기준으로 맞춰진다
#     (별도 로직 불필요).
#   - DESCRIPTION_PRESET_CLEAR_LABEL("🗑️ Clear")을 프리셋 목록 맨 끝에 추가.
#     이 버튼을 누르면 Description 칸을 통째로 비운다(Type은 유지).
#   - "toggle 형식은 필요 없다"는 요청에 따라, 프리셋을 처리한 직후 매번
#     desc_preset_select를 None으로 되돌려 버튼이 눌린 채로 남지 않게 함 —
#     매 탭이 하나의 독립된 "추가/지우기 동작"처럼 보이도록 함.
#   - Description은 원래도 일반 텍스트 입력칸이라 중간에 글자를 추가하거나
#     지우는 것은 이미 자유롭게 가능했음(별도 구현 불필요).
#   - [중요] 구현 중 실제 브라우저(Playwright) 테스트로 다음 문제를 발견하고
#     같이 수정함: Description 입력칸이 st.form("pami_input_form") "안"에
#     있으면, 폼의 특성상 "제출(Submit)" 버튼을 누르기 전까지는 타이핑한
#     내용이 서버(session_state)에 반영되지 않는다. 그 상태에서 폼 밖에 있는
#     프리셋 버튼을 누르면, 서버 입장에서는 Description이 아직 비어있는
#     것으로 보여서 "타이핑한 내용 뒤에 이어붙이기"가 아니라 그냥 프리셋
#     문구로 덮어써지는 결과가 나왔음(실제 테스트로 재현 확인).
#   - 해결: Description 입력칸을 st.form 밖으로 옮겨서, 프리셋 버튼과 마찬가지로
#     타이핑 직후(포커스 아웃 시) 바로 session_state에 반영되게 함. Process
#     Name/Type/Score/Remark/제출 버튼은 이 문제와 무관하므로 그대로 폼 안에
#     둠 — 다만 화면상 순서가 Description이 Process Name보다 먼저 보이도록
#     살짝 바뀜(Description Preset 바로 아래에 위치).
#
# [v2.18.0 변경사항 - 프리셋 목록 정리 및 제조 흐름 기준 순서 재배치]
#   - "forklifting 빼고, Pick&Place보다 Feeding으로 하고 Shipping은 빼도 될
#     것 같은데, Stamping 다음에 Piecing 넣어주고, 제조업 시작과 끝을 생각해서
#     순서를 조금 바꿔줄래"라는 요청에 따라 추가.
#   - Forklifting, Shipping 삭제. "Pick & Place" → "Feeding"으로 교체(이름만
#     변경, Type "MH"는 그대로).
#   - Stamping 바로 뒤에 "Piecing" 신규 추가. 정확히 어떤 공정인지, Type을
#     무엇으로 할지 사용자에게 확인 질문을 드렸으나 순서 조정 답변만 받고
#     Type에 대한 명시적 답은 없어, Stamping(P) 바로 뒤에 이어지는 생산
#     공정이라는 문맥상 Type "P"(생산)로 지정함. 실제와 다르면 프리셋 선택
#     후 Type 라디오 버튼에서 바로 고쳐서 쓰거나, 이 상수를 직접 수정하면 됨.
#   - 전체 순서를 "자재 투입 → 가공 → 조립/용접 → 도장 → 마무리/품질 → 포장"
#     흐름으로 재배치. 추가로 "Unloading(입고 하역)은 맨 앞, Loading(출하
#     상차)은 Packaging 바로 뒤 맨 끝"이라는 요청에 따라 두 항목을 각각 맨
#     앞/맨 뒤로 이동(입고 시 트럭에서 내리는 것=Unloading, 출하 시 트럭에
#     싣는 것=Loading이라는 의미로 해석함).
#
# [v2.17.0 변경사항 - 도장 공정 영문 용어 재검증 및 수정(하도 Primer 추가)]
#   - "상도가 그게 아니라 Primer 뭐 이런건데, 하도는 Clear, 중도는 Spray
#     아닌가?"라는 질문에 따라, 추측으로 답하지 않고 웹 검색으로 사실관계를
#     다시 확인한 뒤 반영함.
#   - 검색 결과(출처):
#     · 하도 = Primer / Undercoat (첫 번째 도장층, 방청+부착력)
#       https://m.cafe.daum.net/carcolor1/6bbj/64
#     · 중도 = Intermediate Coat (하도와 상도 사이 중간층, Surfacer라고도 함)
#       https://www.korea-autonews.com/entry/289-중도Intermediate-Coat-자동차-용어-도장페인트
#     · 상도 = Topcoat (마지막 색상/광택층)
#       https://m.cafe.daum.net/carcolor1/6bbj/64
#     · 자동차 OEM 특허 문서(전착→중도(프라이머/서페이서)→베이스코트→클리어코트
#       순서 명시): https://patents.google.com/patent/KR20120077825A/ko
#     · "상도=Primer, 하도=Clear"처럼 순서가 뒤바뀐 표기는 검색으로 확인한
#       어떤 자료에서도 근거를 찾지 못함. "Spray"는 층 이름이 아니라 하도를
#       칠하는 방식(분사) 중 하나를 가리키는 말로 확인됨.
#   - 결론: 기존 순서(전처리→상도→중도→오븐)와 "Mid Coat" 표기가 부정확했음.
#     이번 버전에서 "하도(Primer)"를 새로 추가하고, "Mid Coat"를 더 정확한
#     표준 용어 "Intermediate Coat"로 수정, 순서도 실제 도장 공정 흐름대로
#     Pretreatment → Primer → Intermediate Coat → Top Coat → Oven으로 바로잡음.
#
# [v2.16.0 변경사항 - 가공(Milling/Turning) + 도장(Paint) 공정 5개 프리셋 추가]
#   - "가공 중에 밀링이 있고 선반이 있고, 이거랑 Paint 상도/중도/오븐/전처리
#     이런거 넣어줄래"라는 요청에 따라 추가.
#   - "선반"을 영어로 어떻게 표기할지(Turning vs Lathe) 확인 질문을 드렸고,
#     "Turning(추천)"으로 결정.
#   - DESCRIPTION_PRESETS_WITH_TYPE(파일 상단 상수)에 아래 5개를 추가해
#     총 20개 → 25개로 늘림:
#       · Milling, Turning → 기존 가공 그룹(Molding, Trimming) 바로 뒤에 배치
#       · Pretreatment(전처리), Top Coat(상도), Mid Coat(중도), Oven(오븐,
#         도장 후 건조/경화 공정) → Welding 바로 뒤에 도장 공정 순서대로 배치
#         (전처리 → 상도 → 중도 → 오븐 순은 실제 도장 공정 흐름과 유사)
#   - 5개 전부 실제 생산 공정이므로 Type은 모두 "P"로 지정. 프리셋을 고르면
#     기존과 동일하게 Description과 Type이 함께 자동으로 채워짐.
#
# [v2.15.0 변경사항 - 프리셋 표기를 대문자 → 첫 글자만 대문자로 변경]
#   - "이게 너무 대문자로 쓰여있어서 좀 그런데"라는 피드백에 따라 추가.
#   - DESCRIPTION_PRESETS_WITH_TYPE(파일 상단 상수)의 공정명 표기를
#     "STORAGING" → "Storaging"처럼 첫 글자만 대문자로 수정. ("Pick & Place",
#     "Heat Treatment", "Labeling/Printing"처럼 단어가 여러 개인 경우는 각
#     단어 첫 글자를 대문자로 함)
#   - 이 목록은 프리셋 버튼(pills)에 보이는 글자이자 Description 칸에 실제로
#     들어가는 글자이기도 해서, 여기 한 곳만 고치면 화면 표시와 저장되는
#     내용이 함께 바뀜. Type 매핑 및 순서는 이전과 동일.
#
# [v2.14.0 변경사항 - Description 프리셋을 타이핑 없는 탭 방식(pills)으로 변경]
#   - "이 프리셋은 타이핑이 필요 없는데 셀렉만 할 수 있게 바꿀 수 있을까?
#     타이핑이 나오니 모바일로 하기 불편하다"는 피드백에 따라 추가.
#   - 원인: st.selectbox는 화면에는 드롭다운처럼 보이지만 내부적으로 검색용
#     텍스트 입력창이 함께 있는 컴포넌트라, 모바일에서 탭하면 항상 키보드가
#     함께 올라오고, 입력한 글자와 일치하는 옵션이 없으면 "No results"가 뜸.
#   - st.pills(선택 항목들을 알약 모양 버튼으로 늘어놓고 탭만으로 고르는
#     위젯)로 교체. 텍스트 입력창 자체가 없어 키보드가 뜨지 않고, 20개 항목이
#     화면 너비에 맞게 자동으로 줄바꿈되어 표시됨.
#   - st.pills는 선택 안 한 상태를 문자열이 아니라 파이썬 None으로 표현하므로
#     apply_description_preset()의 판별 조건을 이에 맞게 수정. Description·
#     Type 자동 채움 동작(v2.13.0) 자체는 그대로 유지.
#   - 이미 선택한 알약을 다시 탭하면 선택이 해제됨(그래도 Description 칸에
#     이미 채워진 글자는 지워지지 않고 그대로 남음).
#
# [v2.13.0 변경사항 - Description 프리셋을 실제 20개 공정 + Type 매핑으로 교체]
#   - 사용자가 준 실제 공정 목록(20개, 각 공정마다 MH/Production/WIP Type 지정)
#     대로 업데이트해달라는 요청에 따라 추가.
#   - "프리셋을 고르면 Type(MH/P/WIP)도 같이 자동 선택되게 할지" 확인 질문에
#     대해 "프리셋으로 셀렉이 되게 하되, 이후에 직접 바꾸는 것도 가능해야
#     한다"고 답변하셔서, 자동 선택은 하되 잠그지는 않는 방식으로 구현.
#   - DESCRIPTION_PRESETS_WITH_TYPE(파일 상단 상수)에 (공정명, Type) 쌍으로
#     20개를 저장. "Production"은 Type 값 체계(MH/P/WIP)에 맞춰 "P"로 매핑.
#   - apply_description_preset() 함수를 확장: 프리셋을 고르면 기존처럼
#     Description 칸을 그 공정명으로 채우고, 추가로 그 공정에 매핑된 Type을
#     찾아 Type 라디오 버튼도 함께 선택되도록 함.
#   - Type은 일반 라디오 버튼이라 자동 선택 후에도 비활성화(disable)되지
#     않으므로, 실제 상황이 표에 있는 것과 다르면 그대로 클릭해서 바꿀 수
#     있음(요청하신 "변경도 가능해야 함" 조건 충족).
#
# [v2.12.0 변경사항 - 기본값 3단계로 복귀 + 사람(기기)별 기억 기능은 보류]
#   - "3단계로 하고, 디폴트를 사람에 따라 바꿀 수 없냐"는 요청에 따라 작업.
#   - v2.11.1에서 코드 기본값을 2단계로 바꿨던 것을 되돌려 다시 3단계로 고정
#     (모든 사람에게 공통으로 보이는 "최초" 기본값은 3단계). 이 부분은 반영 완료.
#   - "사람(기기)마다 마지막 선택값을 자동으로 기억했다가 다음에 새로 접속할
#     때 그 값으로 시작하게" 하는 기능도 브라우저 localStorage를 이용해
#     시도했으나, 실제로 Playwright(자동화 브라우저)로 테스트한 결과 다음과
#     같은 이유로 "완전 자동 복원"은 정상 동작하지 않아 이번 버전에는
#     포함하지 않음:
#       · localStorage에 값을 "저장"하는 것은 성공하지만, 저장된 값으로
#         화면을 자동으로 되돌리려면(=새 접속 시 자동 새로고침) 페이지를
#         이동(navigate)시켜야 하는데, Streamlit이 내부적으로 만드는 컴포넌트
#         iframe은 보안상 "부모 화면을 직접 이동시키는 권한(top-navigation)"이
#         막혀 있어(브라우저 콘솔에 "sandboxed... allow-top-navigation... not
#         set" 오류 발생) 자동 새로고침이 불가능함을 확인함.
#   - 이 문제를 우회하려면 별도의 작은 프론트엔드 파일(정적 index.html 등)을
#     추가로 만들어 Streamlit의 "양방향 커스텀 컴포넌트" 방식으로 다시 구현해야
#     하는데, 이 경우 지금처럼 .py 파일 하나만 복사해서 붙여넣는 방식이 아니라
#     파일을 2개(폴더 구조 포함) 함께 배포해야 해서, "전체를 복사/붙여넣기
#     하기 쉽게" 만들어달라는 기존 요청과 상충됨. 이 트레이드오프를 사용자에게
#     안내하고 방향을 확인받은 뒤 다음 버전에서 반영할 예정.
#
# [v2.11.1 변경사항 - 신규 접속 시 글자 크기 기본값을 2단계로 변경]
#   - "기본값이 계속 3단계로 남는 거냐, 2단계가 더 나은데 2단계로 하면 다시
#     3단계로 바뀌는 거냐"는 질문에 따라 추가.
#   - FONT_ZOOM_DEFAULT_INDEX는 URL에 ?zoom= 값이 아예 없는 "새 접속"일 때만
#     쓰이는 값. 사용자가 -/+ 버튼을 한 번이라도 누르면 그 즉시 선택한 단계가
#     URL 쿼리 파라미터(?zoom=단계번호)에 저장되고, 그 다음부터는 화면 전환은
#     물론 브라우저를 새로고침(F5)해도 항상 그 저장된 값을 읽어와 그대로
#     유지됨 — FONT_ZOOM_DEFAULT_INDEX는 더 이상 참조되지 않으므로 3단계로
#     "되돌아가는" 일은 없음(v2.6.0부터 있던 동작과 동일).
#   - 다만 "새로 여는 화면"의 시작 값 자체는 2단계가 더 낫다는 의견에 따라
#     FONT_ZOOM_DEFAULT_INDEX를 2(3단계)에서 1(2단계, 15px)로 변경.
#
# [v2.11.0 변경사항 - 글자 크기 조절을 줌인/줌아웃 5단계로 변경]
#   - "zoom in/out을 5단계로 해서 더 키우자. 가장 작은 사이즈는 더 줄일
#     필요는 없다"는 요청에 따라 추가.
#   - Small/Medium/Large 3단계(13/16/20px) 라디오 버튼을 없애고, "−" 버튼 /
#     현재 크기의 "A" 미리보기 / "+" 버튼으로 구성된 줌 컨트롤로 변경.
#   - 5단계 값은 13/15/17/20/24px. 가장 작은 값(13px)은 기존 Small과
#     동일하게 유지했고, 가장 큰 값은 기존 Large(20px)보다 더 키운 24px로
#     설정. 기본값은 3단계(17px, 기존 Medium과 비슷한 수준).
#   - 선택지가 3개일 때는 라디오처럼 바로 고르는 방식이 더 간편했지만,
#     5단계로 늘어나면서 "−"/"+"로 오가는 줌 컨트롤이 더 단순하고 화면
#     공간도 덜 차지한다고 판단.
#   - 새로고침(F5)해도 유지되도록 URL 쿼리 파라미터(?zoom=단계번호)에
#     저장하는 방식(v2.6.0)은 그대로 유지.
#
# [v2.10.0 변경사항 - Description 프리셋 20개 확장 + Insert 버튼 제거]
#   - "20개로 늘려주고, Insert 버튼은 더 귀찮으니 빼달라"는 요청에 따라 추가.
#   - 기존 10개에 Receiving/Storage/Cutting/Drilling/Grinding/Molding/
#     Stamping/Soldering/Cleaning/Testing을 더해 총 20개로 확장. 입고/보관
#     → 자재 이동 → 절삭/성형/가공 → 접합 → 표면처리 → 품질 → 포장 순으로
#     배치해 제조 공정 흐름을 따라가며 고를 수 있게 함.
#   - "Insert" 버튼을 없애고, 드롭다운에서 고르는 즉시(on_change) Description
#     칸에 반영되도록 되돌림. 다만 v2.7.0 때와 달리 드롭다운을 다시 안내
#     문구로 리셋하지는 않음 — 그 리셋 때문에 "선택이 안 먹힌다"는 오해가
#     있었으므로(v2.8.0 참고), 이번엔 고른 값이 드롭다운에 그대로 남아있게
#     해서 지금 뭐가 적용됐는지 눈으로 바로 확인할 수 있게 함.
#
# [v2.9.0 변경사항 - Description 프리셋 목록을 제조업 공정에 맞게 확장]
#   - "제조업 프로세스에 맞게 간단하고 단순하게 바꿔달라, 나머지는 직접
#     입력(key-in)하면 된다"는 요청에 따라 추가.
#   - 기존 4개(Moving/Feeding/Assembly/Welding)에 Loading/Unloading/
#     Machining/Painting/Inspection/Packaging을 더해 총 10개로 구성.
#     자재 이동 → 가공/조립 → 품질/포장 순으로 배치해 실제 공정 흐름과
#     비슷하게 훑어볼 수 있도록 함.
#   - 목록은 여전히 공정 "이름"만 담은 단순한 구성이며, 세부 설명은 Insert
#     버튼으로 채운 뒤 이어서 직접 타이핑하는 기존 방식 그대로 사용.
#
# [v2.8.0 변경사항 - Description 프리셋 동작 방식 개선]
#   - "테스트 해봤는데 셀렉트가 안 된다"는 피드백에 따라 추가.
#   - 추정 원인: 이전 버전은 드롭다운에서 고르는 즉시(on_change) 자동으로
#     Description에 반영하고, 드롭다운 자체는 다시 "-- Select a preset --"
#     안내 문구로 리셋했음. 방금 고른 항목이 화면에서 바로 사라져 보이기
#     때문에, 실제로는 반영이 됐어도 "선택이 안 먹힌다"고 오해하기 쉬웠음.
#   - 개선: 드롭다운(고른 값 그대로 유지) + "➕ Insert" 버튼의 2단계 방식으로
#     변경. 버튼을 눌러야만 Description 칸에 반영되므로, 언제 무엇이
#     적용됐는지 훨씬 명확함.
#   - Description 프리셋 목록을 예시 문구 대신 실제 요청하신 내용
#     (Moving / Feeding / Assembly / Welding)으로 교체.
#
# [v2.7.0 변경사항 - Description 프리셋 추가]
#   - "Description에 predefined 내용을 먼저 넣어두고, 그 뒤에 추가로 입력할
#     수 있게 해달라"는 요청에 따라 추가.
#   - Description 입력칸 위에 프리셋 선택 드롭다운(Description Preset)을
#     추가. 프리셋을 고르면 Description 칸이 그 문구로 채워지고, 사용자는
#     이어서 타이핑해 내용을 덧붙이거나, 전부 지우고 새로 쓸 수도 있음.
#   - 프리셋 드롭다운은 st.form 밖에 배치함 — form 안의 위젯은 "Save/Update"
#     버튼을 눌러야만 값이 반영되므로, 고르자마자 Description 칸에 바로
#     채워지게 하려면 폼 바깥에 있어야 함.
#   - DESCRIPTION_PRESETS 목록(파일 상단 상수)은 실제 현장 문구를 몰라서
#     넣어둔 예시(placeholder)이므로, 회사에서 실제로 자주 쓰는 문구로
#     직접 교체해서 사용할 것.
#
# [v2.6.0 변경사항 - 글자 크기, 새로고침해도 유지되도록 개선]
#   - "Large로 바꾸고 새로고침을 하면 다시 Medium으로 바뀐다"는 피드백에 따라 추가.
#   - 원인: st.session_state는 브라우저를 새로고침(F5)하면 완전히 새로운
#     세션으로 취급되어 통째로 초기화됨. (같은 화면 안에서 버튼을 눌러
#     발생하는 "rerun"과는 다른 상황 — rerun에서는 session_state가 유지됨)
#   - 해결: 글자 크기 선택값을 session_state뿐 아니라 URL 쿼리 파라미터
#     (예: ?text_size=Large)에도 함께 저장. 새로고침해도 URL은 그대로
#     남아있으므로, 다음 로딩 시 session_state 대신 쿼리 파라미터에서
#     마지막 선택값을 읽어와 그대로 복원함.
#
# [v2.5.0 변경사항 - 글자 크기 UI를 라디오 버튼으로 되돌림]
#   - "휴대폰으로 열었더니 버튼 3개가 세로로 나와서 보기 불편하다"는 피드백에
#     따라, v2.3.1에서 도입했던 아이콘 버튼(A/A/A)을 다시 라디오 버튼으로 변경.
#     라디오는 좁은 화면에서도 옵션 3개가 가로 한 줄로 유지됨.
#   - "예전 라디오 버전은 화면 전환 시 선택값이 사라지는 것 같았다"는 피드백도
#     함께 해결: v2.3.0에서는 st.radio(index=1, key="font_size_choice")처럼
#     index와 key를 동시에 넘겼는데, 이 조합이 화면이 다시 그려질 때 선택값을
#     index 기본값으로 되돌리는 원인으로 보여, index는 제거하고 session_state
#     초기화만으로 기본값을 잡도록 수정 (Streamlit 공식 권장 방식).
#   - 라디오 옵션 앞의 "A" 글자를 작게/중간/크게 실제 크기로 다르게 표시하는
#     것은 그대로 유지 (CSS :nth-of-type으로 옵션별 스타일 지정).
#
# [v2.4.0 변경사항 - 오프라인 대응 강화]
#   - "인터넷이 안 되면 작동을 멈춘다"는 피드백에 따라 추가.
#   - 문제 원인: 구글 API 호출에 타임아웃이 없어, 인터넷이 끊기면 응답이
#     올 때까지 화면이 무한 대기(hang)하며 "멈춘 것처럼" 보였음.
#   - has_internet() 함수로 실제 API를 부르기 전에 www.googleapis.com:443 접속을
#     짧게(최대 2.5초) 시도해 인터넷 여부를 먼저 판단 → 오프라인이면
#     클라우드 시도 자체를 건너뛰고 즉시 로컬 저장만 진행 (화면 멈춤 없음)
#   - socket.setdefaulttimeout()으로 8초 상한을 걸어, 혹시 연결은 되지만
#     응답이 느린 경우에도 무한 대기하지 않도록 안전장치 추가
#   - Step 2 화면에 "☁️ Cloud sync: connected" / "📴 No internet connection"
#     상태 문구를 추가해, 지금 로컬에만 저장 중인지 클라우드까지 저장되고
#     있는지 사용자가 바로 확인 가능
#   - 자동 동기화(로컬→클라우드)를 "세션당 1회"에서 "1분 간격으로 재시도"로
#     변경 → 같은 세션을 계속 켜둔 채로 인터넷이 나중에 복구돼도, 이후
#     아무 저장 동작(프로세스 추가/수정 등) 한 번만 있으면 자동으로 클라우드에
#     반영됨 (페이지 새로고침 불필요)
#
# [v2.3.1 변경사항 - 글자 크기 UI 개선]
#   - 글자 크기 선택을 라디오 버튼에서 3개의 아이콘 버튼(Small/Medium/Large)으로 변경
#   - 버튼 안의 "A" 글자 크기 자체를 작게/중간/크게 다르게 표시해서
#     텍스트 설명 없이도 크기 차이를 한눈에 알 수 있도록 구성
#   - 현재 선택된 크기는 버튼 색상(primary 강조색) + 체크(✓) 표시로 명확히 구분
#
# [v2.3.0 변경사항 - UI 영어화 + 글자 크기 선택]
#   - 화면에 보이는 라벨/버튼/안내·경고·에러 메시지를 영어로 변경
#     (내부 로그 메시지(logger.*)와 코드 주석은 요청에 따라 한글 그대로 유지)
#   - "글자가 작아서 안 보인다"는 피드백에 따라, 메인 화면 최상단에
#     Small / Medium / Large 글자 크기 선택 UI 추가
#     → 선택 즉시 앱 전체(라벨/버튼/표/안내문 등)에 CSS로 일괄 적용, 기본값 Medium
#
# [v2.2.0 변경사항 - Fix 1 재설계]
#
# ▶ 저장 로직
#   - 항상 로컬 파일 + 클라우드 동시 저장 시도
#   - 인터넷 없으면 로컬 파일에만 저장 (클라우드 실패해도 로컬은 항상 저장)
#
# ▶ 복구 목록 표시 기준 (로컬/클라우드 timestamp 비교)
#   - 클라우드 연결 불가 → 로컬만 표시
#   - 클라우드 연결 가능 + 로컬이 클라우드보다 10초 초과 최신
#     → 로컬이 더 최신 데이터이므로 로컬만 표시
#   - 클라우드 연결 가능 + 클라우드가 최신(또는 10초 이내 차이)
#     → 클라우드만 표시 (정상 상태)
#
# ▶ 자동 동기화 (하루 1회)
#   - 로컬 timestamp가 클라우드보다 10초 이상 앞서면
#     로컬 데이터를 클라우드에 덮어써서 동기화
#   - 동기화 완료 후 복구 목록은 클라우드만 표시
#
# [v2.1.0 변경사항 - Fix 2]
#   - Google Sheets 14일 초과 행 자동 삭제 (세션 시작 시 1회 실행)
#   - 앱 휴지기 후 wake-up 시에도 만료 데이터 정리됨
# =============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import json
import os
import glob
import time
import logging
import io
import socket  # [v2.4.0] 인터넷 연결 여부 확인 및 소켓 타임아웃 설정용
# [v2.12.0] 글자 크기를 브라우저 localStorage로 기기별 자동 기억하려고
# streamlit.components.v1을 시도했으나, 아래 FONT_ZOOM_DEFAULT_INDEX 근처의
# 주석 및 파일 상단 [v2.12.0 변경사항]에 적은 이유로 이번 버전엔 포함하지
# 않아 이 import도 사용하지 않음(참고용으로 주석만 남김).
# import streamlit.components.v1 as components

# =====================================================================
# 로깅 설정
# =====================================================================
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# =====================================================================
# 구글 API 라이브러리 임포트
# =====================================================================
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    HAS_GOOGLE_LIBS = True
except ImportError:
    HAS_GOOGLE_LIBS = False

# 브라우저 탭 아이콘 및 제목
st.set_page_config(page_title="Supplier OAMI", page_icon="📝", layout="centered")
st.markdown("### 📝 Supplier OAMI Evaluation App")

# =====================================================================
# [v2.3.0] 글자 크기 선택 (Small / Medium / Large)
# [v2.3.1] 라디오 버튼 → 크기별 아이콘 버튼(A/A/A)으로 변경
# [v2.5.0] 아이콘 버튼 → 다시 라디오 버튼으로 되돌림 (휴대폰 좁은 화면 대응 +
#          index/key 동시 사용으로 인한 "선택값이 사라지는" 문제 해결)
# [v2.6.0] URL 쿼리 파라미터에 저장해 새로고침 후에도 선택값 유지
# [v2.11.0] Small/Medium/Large 3단계 라디오 → "−"/"+" 줌인·줌아웃 5단계로 변경
#   - "zoom in/out을 5단계로 해서 더 키우자. 젤 작은 사이즈는 더 줄일 필요는
#     없다"는 요청에 따라 변경. 3단계(13/16/20px)에서 5단계(13/15/17/20/24px)로
#     확장. 가장 작은 값(13px)은 기존 그대로 유지하고, 가장 큰 값은 기존
#     Large(20px)보다 더 키움(24px).
#   - 선택지가 3개일 때는 직접 고르는 라디오가 더 간편했지만, 5단계로
#     늘어나면서 한 줄에 다 늘어놓기보다 "-"/"+"로 단계를 오가는 줌 컨트롤이
#     더 간단하고 화면도 덜 차지함.
#   - 가운데에는 현재 단계의 실제 크기로 "A"를 표시해서, 지금이 몇 단계이고
#     얼마나 커지는지 눈으로 바로 확인 가능.
# "글자가 작아서 안 보인다"는 피드백에 따라 추가.
# 메인 화면 최상단에 배치하고, 선택값은 세션 동안 유지되며 새로고침해도
# URL 쿼리 파라미터를 통해 유지된다. 앱 전체 텍스트(라벨/버튼/표/안내문 등)에
# CSS로 즉시 적용된다.
# =====================================================================
# [v2.11.0] 1단계(가장 작음, 13px) ~ 5단계(가장 큼, 24px). 1단계 값은 기존
# Small과 동일하게 유지, 5단계는 기존 Large(20px)보다 더 크게 설정.
FONT_ZOOM_LEVELS = [13, 15, 17, 20, 24]  # px 단위, 인덱스 0~4 = 1~5단계
# [v2.12.0] "코드 상 기본값은 3단계로 두고, 대신 사람(기기)마다 마지막으로
# 고른 값을 기억하게 해달라"는 요청에 따라 v2.11.1(기본값을 2단계로 변경)을
# 되돌리고 다시 3단계로 고정. 개인별 기본값은 아래 sync_zoom_with_local_storage()의
# 브라우저 localStorage 기억 기능으로 처리한다.
FONT_ZOOM_DEFAULT_INDEX = 2  # 이 앱을 처음 접속하는 모든 사람에게 공통으로 보이는 기본값 = 3단계(17px)

# [v2.6.0] "Large로 바꾸고 새로고침(F5)하면 다시 Medium으로 돌아간다"는
# 피드백에 따라 추가 (session_state는 새로고침 시 초기화되므로, 새로고침에도
# 남는 URL 쿼리 파라미터에 값을 함께 저장해두고 거기서 복원한다).
# [v2.11.0] 저장 형식을 문구(Small/Medium/Large) 대신 단계 번호(0~4)로 변경.
_qp_zoom = st.query_params.get("zoom")
try:
    _qp_zoom_index = int(_qp_zoom) if _qp_zoom is not None else FONT_ZOOM_DEFAULT_INDEX
except (TypeError, ValueError):
    _qp_zoom_index = FONT_ZOOM_DEFAULT_INDEX
if not (0 <= _qp_zoom_index < len(FONT_ZOOM_LEVELS)):
    _qp_zoom_index = FONT_ZOOM_DEFAULT_INDEX

if "font_zoom_index" not in st.session_state:
    st.session_state.font_zoom_index = _qp_zoom_index


def apply_font_size(base_px):
    """선택된 글자 크기(px)를 앱 전역 CSS로 적용."""
    st.markdown(f"""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"] {{
        font-size: {base_px}px !important;
    }}
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div,
    .stText, .stCaption, [data-testid="stCaptionContainer"],
    .stAlert, .stAlert p, .stAlert div,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"],
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] div,
    .stButton button p, .stButton button div,
    .stDownloadButton button p, .stDownloadButton button div,
    .stTextInput input, .stTextArea textarea,
    .stRadio label p, .stRadio div[role="radiogroup"] label p,
    .stCheckbox label p,
    .stSelectbox div, .stSelectbox span,
    .stExpander summary p, .stExpander summary span, .stExpander div,
    table, table td, table th,
    code, pre,
    .stTabs [data-baseweb="tab"] {{
        font-size: {base_px}px !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def zoom_font_out():
    """[v2.11.0] 글자 크기를 한 단계 줄인다 (1단계보다 더 줄어들지 않음)."""
    if st.session_state.font_zoom_index > 0:
        st.session_state.font_zoom_index -= 1


def zoom_font_in():
    """[v2.11.0] 글자 크기를 한 단계 키운다 (5단계보다 더 커지지 않음)."""
    if st.session_state.font_zoom_index < len(FONT_ZOOM_LEVELS) - 1:
        st.session_state.font_zoom_index += 1


def render_font_zoom_control():
    """
    [v2.11.0] "−" / 현재 크기 미리보기(A) / "+" 줌인·줌아웃 컨트롤 렌더링.
    - "-"를 누르면 zoom_font_out(), "+"를 누르면 zoom_font_in()이 실행되어
      단계를 하나씩 조절한다. 맨 끝 단계에서는 해당 버튼이 비활성화된다.
    - 가운데 "A"는 현재 단계의 실제 글자 크기로 표시해, 지금 크기가 어느
      정도인지 텍스트 설명 없이도 바로 확인할 수 있다.
    - [v2.6.0]부터 이어온 대로, 선택값을 URL 쿼리 파라미터(?zoom=...)에도
      함께 저장해서 새로고침(F5)해도 유지되도록 한다.
    """
    idx = st.session_state.font_zoom_index
    current_px = FONT_ZOOM_LEVELS[idx]

    st.write("**🔠 Text Size**")
    z_c1, z_c2, z_c3 = st.columns([1, 2, 1])
    with z_c1:
        st.button("➖", key="font_zoom_out_btn", on_click=zoom_font_out,
                   disabled=(idx == 0), use_container_width=True,
                   help="Make text smaller")
    with z_c2:
        st.markdown(
            f"<div style='text-align:center;'>"
            f"<span style='font-size:{current_px}px; font-weight:bold;'>A</span> "
            f"<span style='font-size:13px; color:#888;'>({idx + 1}/{len(FONT_ZOOM_LEVELS)})</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    with z_c3:
        st.button("➕", key="font_zoom_in_btn", on_click=zoom_font_in,
                   disabled=(idx == len(FONT_ZOOM_LEVELS) - 1), use_container_width=True,
                   help="Make text bigger")

    # [v2.6.0, v2.11.0] 새로고침 후에도 유지되도록 현재 단계를 URL에 동기화
    st.query_params["zoom"] = str(st.session_state.font_zoom_index)


render_font_zoom_control()
apply_font_size(FONT_ZOOM_LEVELS[st.session_state.font_zoom_index])
st.write("")

# 로컬 백업 폴더
BACKUP_DIR = "oami_backups"
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# 유효값 상수
VALID_TYPES  = {"MH", "P", "WIP"}
VALID_SCORES = {1, 2, 3, 4, 5}

# =====================================================================
# [v2.7.0] Description 프리셋(predefined) 목록
# "Description 칸에 미리 정의된 문구를 먼저 넣어두고, 그 뒤에 이어서 추가로
# 입력할 수 있게 해달라"는 요청에 따라 추가.
# [v2.8.0] 목록을 실제 요청하신 문구(Moving/Feeding/Assembly/Welding)로 교체.
# [v2.9.0] "제조업 프로세스에 맞게, 간단하고 단순하게" 요청에 따라 자재
# 이동(Moving/Feeding/Loading/Unloading) → 가공/조립(Assembly/Welding/
# Machining/Painting) → 품질/포장(Inspection/Packaging) 순서로 자주 쓰이는
# 기본 공정 단어 위주로 구성.
# [v2.10.0] "20개로 늘려달라"는 요청에 따라 10개 추가 → 총 20개.
# 입고/보관 → 자재 이동 → 절삭/성형/가공 → 접합 → 표면처리 → 품질 →
# 포장 순서로, 제조 공정 흐름을 따라가며 훑어볼 수 있게 배치.
# 세부 내용은 프리셋 적용 후 이어서 직접 타이핑(key-in)하면 됨.
# [v2.13.0] 실제 현장에서 쓰는 20개 공정 목록(사용자 제공)으로 전면 교체.
# 이번엔 각 공정마다 Type(MH/Production/WIP)도 같이 지정되어 있어서, (공정명,
# Type) 쌍의 리스트로 저장한다. "Production"은 이 앱의 Type 값 체계(MH/P/WIP)에
# 맞춰 "P"로 변환해서 저장함. 프리셋을 고르면 Description뿐 아니라 Type도
# 자동으로 함께 선택된다(자세한 내용은 apply_description_preset() 참고). Type은
# 자동 선택 후에도 잠기지 않으므로 실제와 다르면 직접 클릭해서 바꿀 수 있다.
# [v2.15.0] "대문자로만 쓰여있어서 보기 좀 그렇다"는 피드백에 따라 공정명
# 표기를 전부 대문자(STORAGING 등)에서 첫 글자만 대문자인 표기(Storaging 등)로
# 변경. 버튼에 보이는 글자와 Description 칸에 실제로 채워지는 글자가 항상
# 같으므로 여기 한 곳만 고치면 둘 다 같이 바뀐다.
# [v2.16.0] "가공 중에 밀링/선반이 있고, 도장(Paint)에 상도/중도/오븐/전처리도
# 있다"는 요청에 따라 5개 추가(총 25개). 가공(Molding/Trimming) 뒤에
# Milling(밀링)·Turning(선반, 선삭 공정)을 추가하고, Welding 뒤에 도장 관련
# 공정 Pretreatment(전처리)·Top Coat(상도)·Mid Coat(중도)·Oven(오븐, 도장 후
# 건조/경화)을 순서대로 추가함. "선반"의 영문 표기는 사용자 확인을 거쳐
# "Turning"으로 결정. 전부 실제 생산 공정이므로 Type은 전부 "P"로 지정.
# [v2.17.0] "상도/중도/하도 영문 표기가 맞는지" 질문에 따라 웹 검색으로 재검증
# (출처는 파일 상단 [v2.17.0 변경사항] 참고). 하도=Primer, 중도=Intermediate
# Coat, 상도=Topcoat가 맞는 표준 용어로 확인되어, 빠져있던 "하도(Primer)"를
# 추가하고 "Mid Coat"를 "Intermediate Coat"로 수정. 순서도 실제 도장 공정
# 흐름대로 Pretreatment → Primer → Intermediate Coat → Top Coat → Oven으로
# 바로잡음.
# [v2.18.0] Forklifting·Shipping 삭제, "Pick & Place"→"Feeding" 교체, Stamping
# 뒤에 "Piecing"(Type: P, 자세한 사유는 파일 상단 [v2.18.0 변경사항] 참고)
# 추가. 전체 순서를 "자재 투입 → 가공 → 조립/용접 → 도장 → 마무리/품질 →
# 포장" 흐름으로 재배치하고, Unloading(입고 하역)은 맨 앞, Loading(출하
# 상차)은 Packaging 바로 뒤 맨 끝으로 이동.
#
# 목록은 아래에 (공정명, Type) 형태로 한 줄에 하나씩 적으면 됩니다.
# Type은 반드시 "MH" / "P" / "WIP" 셋 중 하나로 적어야 합니다.
# 필요하면 자유롭게 추가/삭제/수정해서 쓰세요.
# =====================================================================
DESCRIPTION_PRESETS_WITH_TYPE = [
    ("Unloading", "MH"),
    ("Storaging", "MH"),
    ("Feeding", "MH"),
    ("Replenishing", "MH"),
    ("Molding", "P"),
    ("Trimming", "P"),
    ("Milling", "P"),
    ("Turning", "P"),
    ("Stamping", "P"),
    ("Piecing", "P"),
    ("Remove", "WIP"),
    ("Conveyor", "WIP"),
    ("Heat Treatment", "P"),
    ("Assembly", "P"),
    ("Welding", "P"),
    ("Pretreatment", "P"),
    ("Primer", "P"),
    ("Intermediate Coat", "P"),
    ("Top Coat", "P"),
    ("Oven", "P"),
    ("Labeling/Printing", "P"),
    ("Deburring", "P"),
    ("Finishing", "P"),
    ("Inspection", "P"),
    ("Packaging", "P"),
    ("Loading", "MH"),
]
# 기존 코드(selectbox 등)와의 호환을 위해 이름만 뽑은 리스트도 함께 준비
DESCRIPTION_PRESETS = [name for name, _ in DESCRIPTION_PRESETS_WITH_TYPE]
# 공정명 → Type 조회용 딕셔너리 (apply_description_preset()에서 사용)
DESCRIPTION_PRESET_TYPE_MAP = dict(DESCRIPTION_PRESETS_WITH_TYPE)
# [v2.14.0] "아무것도 안 고른 상태"를 나타내던 안내 문구용 상수였으나,
# st.selectbox → st.pills로 바꾸면서 더 이상 필요 없어짐(pills는 선택 안 한
# 상태를 문자열이 아니라 파이썬 None으로 표현하기 때문). 과거 버전과 코드
# 흐름을 추적하기 쉽도록 상수 자체는 남겨두되, 위젯/콜백에서는 사용하지 않음.
DESCRIPTION_PRESET_PLACEHOLDER = "-- Select a preset (optional) --"

# [v2.19.0] "프리셋을 누르면 토글처럼 선택 상태로 남지 말고, 누를 때마다 그냥
# Description 칸 뒤에 글자가 타이핑되듯 추가되게 해달라"는 요청에 따라 추가.
# 처음엔 프리셋 버튼들(pills) 맨 끝에 이 항목을 하나 더 붙여서 사용했으나,
# [v2.20.0] "Clear를 프리셋 안에 넣지 말고 Description 옆에 별도 버튼으로
# 만들어달라"는 요청에 따라 pills 옵션에서는 빼고, Description 입력칸 바로
# 옆의 독립된 st.button 라벨로만 사용한다(자세한 내용은
# clear_description_field() 참고).
DESCRIPTION_PRESET_CLEAR_LABEL = "🗑️ Clear Description"

# 백업 보관 기간 (일)
BACKUP_RETENTION_DAYS = 14

# 로컬/클라우드 시간 차이 임계값 (초) — 이 값 초과 시 로컬이 더 최신으로 판단
# 정상 상태에서 로컬→클라우드 저장 시간차는 1~3초이므로
# 30초를 초과하면 오프라인 중 작업한 것으로 판단
TS_DIFF_THRESHOLD_SEC = 30

# =====================================================================
# [v2.4.0] 네트워크 연결 확인 & 타임아웃 설정
# "인터넷이 안 되면 앱이 멈춘다"는 피드백에 따라 추가.
# - 소켓 기본 타임아웃을 지정해 구글 API 호출이 무한 대기하지 않도록 방지
#   (연결은 되는데 응답만 느린 경우에 대한 안전장치)
# - 실제 클라우드 API를 부르기 전에 www.googleapis.com:443 접속을 짧게 시도해서
#   인터넷 연결 여부를 먼저 빠르게 판단 (최대 2.5초) → 오프라인이면
#   클라우드 시도 자체를 건너뛰어 화면이 멈추지 않고 즉시 로컬 저장만 진행
# - 판단 결과는 10초간 캐시하여, 반복 호출 시마다 매번 다시 확인하느라
#   생기는 불필요한 지연을 방지
# =====================================================================
NETWORK_TIMEOUT_SEC = 8           # 구글 API 호출 자체의 최대 대기 시간(초)
INTERNET_CHECK_TIMEOUT_SEC = 2.5  # 인터넷 연결 여부 사전 확인 시 최대 대기 시간(초)

socket.setdefaulttimeout(NETWORK_TIMEOUT_SEC)


@st.cache_data(ttl=10)
def has_internet():
    """
    인터넷(정확히는 Google API 서버) 연결 여부를 빠르게 확인. 10초간 결과 캐시.

    [v2.4.0] 처음엔 8.8.8.8:53(구글 DNS)로 확인했으나, 회사/보안 네트워크처럼
    53번(DNS) 포트는 막고 443번(HTTPS)만 허용하는 환경에서는 실제로는 인터넷이
    되는데도 "오프라인"으로 잘못 판단하는 문제가 있어, 실제로 사용하는 Google
    Sheets API 서버(www.googleapis.com)의 443번(HTTPS) 포트로 직접 확인하도록 변경.
    """
    try:
        socket.create_connection(("www.googleapis.com", 443), timeout=INTERNET_CHECK_TIMEOUT_SEC)
        return True
    except OSError:
        return False


# =====================================================================
# Google Sheets 헬퍼 함수
# =====================================================================
def get_sheets_service():
    """Google Sheets API 서비스 객체와 sheet_id 반환. 실패 시 (None, None)."""
    if not HAS_GOOGLE_LIBS or "google_drive" not in st.secrets:
        return None, None
    # [v2.4.0] 인터넷이 끊긴 상태면 API 호출 자체를 시도하지 않고 바로 포기
    # → 무한 대기(행업) 없이 즉시 로컬 전용 모드로 동작
    if not has_internet():
        return None, None
    try:
        credentials_info = dict(st.secrets["google_drive"])
        sheet_id = credentials_info.pop("sheet_id", None)
        credentials_info.pop("folder_id", None)
        if "private_key" in credentials_info:
            credentials_info["private_key"] = credentials_info["private_key"].replace("\\n", "\n")
        creds = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)
        return service, sheet_id
    except Exception as e:
        logger.error(f"Google Sheets 인증 실패: {e}")
        return None, None


def _get_all_rows(service, sheet_id):
    """Sheets A:C 전체 행 반환."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="A:C"
        ).execute()
        return result.get("values", [])
    except Exception as e:
        logger.error(f"Google Sheets 읽기 실패: {e}")
        return []


def _find_row_index(rows, filename):
    """파일명으로 행 인덱스(1-based) 탐색. 없으면 -1."""
    base_name = os.path.basename(filename)
    for i, row in enumerate(rows):
        if len(row) > 0 and row[0] == base_name:
            return i + 1
    return -1


def upload_or_update_gsheet(filename, content_dict):
    """Sheets에 백업 데이터 업로드(신규) 또는 갱신(기존 행). 성공 True, 실패 False."""
    service, sheet_id = get_sheets_service()
    if not service or not sheet_id:
        return False
    base_name  = os.path.basename(filename)
    json_data  = json.dumps(content_dict, ensure_ascii=False)
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        rows    = _get_all_rows(service, sheet_id)
        row_idx = _find_row_index(rows, filename)
        new_row = [[base_name, json_data, timestamp]]
        if row_idx > 0:
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"A{row_idx}:C{row_idx}",
                valueInputOption="RAW",
                body={"values": new_row}
            ).execute()
        else:
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range="A:C",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": new_row}
            ).execute()
        return True
    except Exception as e:
        logger.error(f"Google Sheets 업로드 실패 ({base_name}): {e}")
        return False


def delete_gsheet_row_if_exists(filename):
    """Sheets에서 해당 파일명 행을 빈 값으로 덮어써 삭제 처리."""
    service, sheet_id = get_sheets_service()
    if not service or not sheet_id:
        return False
    try:
        rows    = _get_all_rows(service, sheet_id)
        row_idx = _find_row_index(rows, filename)
        if row_idx > 0:
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"A{row_idx}:C{row_idx}",
                valueInputOption="RAW",
                body={"values": [["", "", ""]]}
            ).execute()
        return True
    except Exception as e:
        logger.error(f"Google Sheets 삭제 실패: {e}")
        return False


def get_gsheet_cloud_timestamp(filename):
    """
    Sheets에서 해당 파일명 행의 timestamp 문자열 반환.
    없거나 실패 시 None.
    """
    service, sheet_id = get_sheets_service()
    if not service or not sheet_id:
        return None
    try:
        rows    = _get_all_rows(service, sheet_id)
        row_idx = _find_row_index(rows, filename)
        if row_idx > 0:
            row = rows[row_idx - 1]
            return row[2] if len(row) >= 3 else None
        return None
    except Exception as e:
        logger.error(f"Sheets timestamp 조회 실패: {e}")
        return None


def get_gsheet_backup_list():
    """Sheets에서 유효한 백업 목록 반환. {label: data} 딕트."""
    service, sheet_id = get_sheets_service()
    options = {}
    if not service or not sheet_id:
        return options
    try:
        rows = _get_all_rows(service, sheet_id)
        for row in rows:
            if len(row) >= 2 and row[0] and row[1]:
                try:
                    data  = json.loads(row[1])
                    ts    = row[2] if len(row) >= 3 else "unknown"
                    label = (
                        f"[☁️ Cloud] {data['info']['supplier']} "
                        f"by {data['info']['evaluator']} ({ts})"
                    )
                    options[label] = data
                except (json.JSONDecodeError, KeyError):
                    continue
    except Exception as e:
        logger.error(f"Google Sheets 백업 목록 로딩 실패: {e}")
    return options


# =====================================================================
# [Fix 2] Google Sheets 14일 초과 행 자동 삭제
# 앱 세션 시작(wake-up 포함) 시 1회 실행.
# timestamp(C열)를 파싱해 14일 초과 행을 빈 행으로 덮어씀.
# =====================================================================
def cleanup_old_gsheet_backups():
    """Sheets에서 14일 초과 백업 행을 삭제. 세션당 1회."""
    if st.session_state.get("_gsheet_cleanup_done", False):
        return
    service, sheet_id = get_sheets_service()
    if not service or not sheet_id:
        st.session_state._gsheet_cleanup_done = True
        return
    try:
        rows   = _get_all_rows(service, sheet_id)
        cutoff = datetime.now() - timedelta(days=BACKUP_RETENTION_DAYS)
        for i, row in enumerate(rows):
            row_num = i + 1
            if len(row) < 3 or not row[0]:
                continue
            try:
                ts = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
                if ts < cutoff:
                    service.spreadsheets().values().update(
                        spreadsheetId=sheet_id,
                        range=f"A{row_num}:C{row_num}",
                        valueInputOption="RAW",
                        body={"values": [["", "", ""]]}
                    ).execute()
                    logger.warning(f"[GSheet Cleanup] 만료 행 삭제: row {row_num}, ts={row[2]}")
            except ValueError:
                continue
    except Exception as e:
        logger.error(f"Google Sheets 만료 정리 실패: {e}")
    st.session_state._gsheet_cleanup_done = True


# =====================================================================
# 파일명 생성 함수
# =====================================================================
def get_backup_filename(supplier, evaluator):
    """supplier + evaluator 조합으로 로컬 백업 파일 경로 생성."""
    safe_sup  = "".join(c for c in supplier  if c.isalnum() or c in " _-").strip().replace(" ", "_")
    safe_eval = "".join(c for c in evaluator if c.isalnum() or c in " _-").strip().replace(" ", "_")
    return os.path.join(BACKUP_DIR, f"{safe_sup}_{safe_eval}.json")


# =====================================================================
# 로컬 파일 만료 정리 (서버 측, 세션당 1회)
# =====================================================================
def cleanup_old_local_backups():
    """로컬 백업 파일 중 14일 초과분 삭제. 세션당 1회."""
    if st.session_state.get("_local_cleanup_done", False):
        return
    now = time.time()
    for f in glob.glob(os.path.join(BACKUP_DIR, "*.json")):
        try:
            if os.stat(f).st_mtime < now - (BACKUP_RETENTION_DAYS * 86400):
                os.remove(f)
        except Exception as e:
            logger.warning(f"로컬 백업 파일 정리 실패 ({f}): {e}")
    st.session_state._local_cleanup_done = True


# =====================================================================
# [v2.2.0] timestamp 차이 계산 유틸
# =====================================================================
def ts_diff_seconds(local_ts_str, cloud_ts_str):
    """
    로컬 - 클라우드 timestamp 차이(초) 반환.
    양수 = 로컬이 더 최신, 음수 = 클라우드가 더 최신.
    파싱 실패 시 0 반환.
    """
    try:
        fmt      = "%Y-%m-%d %H:%M:%S"
        local_ts = datetime.strptime(local_ts_str, fmt)
        cloud_ts = datetime.strptime(cloud_ts_str, fmt)
        return (local_ts - cloud_ts).total_seconds()
    except Exception:
        return 0


# =====================================================================
# [v2.2.0] 저장: 로컬 + 클라우드 항상 동시 저장
#
# - 로컬은 인터넷 유무와 관계없이 항상 저장 (오프라인 대비)
# - 클라우드는 가능할 때만 저장 (실패해도 로컬이 유지됨)
# =====================================================================
def _build_backup_payload_with_draft():
    """[v2.25.0] save_temp_backup()과 save_draft_local_only()가 공통으로 쓰는
    백업 데이터 생성 로직을 하나로 모음(같은 draft 규칙을 두 곳에 따로
    적어두면 나중에 한쪽만 고치는 실수가 생기기 쉬워서 함수로 분리).
    (supplier, evaluator, fname, backup_data) 튜플을 반환하고, supplier/
    evaluator가 비어있으면 (None, None, None, None)을 반환한다."""
    supplier  = st.session_state.master_info.get("supplier", "")
    evaluator = st.session_state.master_info.get("evaluator", "")
    if not supplier or not evaluator:
        return None, None, None, None

    # [v2.24.0] 새 항목을 입력하는 중(is_inserting=True)일 때만 draft를
    # 남긴다. 기존 항목을 수정하는 중(is_inserting=False)일 때는 원본
    # 데이터가 이미 process_list에 안전하게 들어있고, 수정 중인 위치(인덱스)가
    # 세션 재시작 후 어긋날 수 있어 draft 복원 대상에서는 제외한다.
    draft = None
    if st.session_state.get("is_inserting", False):
        draft = {
            "name":   st.session_state.get("p_name_input", "") or "",
            "desc":   st.session_state.get("p_desc_input", "") or "",
            "type":   st.session_state.get("p_type_input"),
            "score":  st.session_state.get("p_score_input"),
            "remark": st.session_state.get("p_remark_input", "") or "",
        }
        # 다섯 칸이 전부 비어있으면 저장할 draft가 없는 것과 같음
        if not any(draft.values()):
            draft = None

    backup_data = {
        "info":         st.session_state.master_info,
        "list":         st.session_state.process_list,
        "draft":        draft,  # [v2.24.0] 저장 전 타이핑 중이던 새 항목 내용
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    fname = get_backup_filename(supplier, evaluator)
    return supplier, evaluator, fname, backup_data


def save_temp_backup():
    """항상 로컬 저장 + 클라우드 저장 시도. stop_backup 시 동작 안 함.

    [v2.24.0] "타이핑을 하다가 한참 아무것도 안 하면 처음으로 돌아가는 경우가
    있다"는 피드백에 따라, 아직 Save 버튼을 누르지 않은 새 항목 입력 내용
    (Process Name/Description/Type/Score/Remark)도 "draft"로 함께 백업한다.
    이유: 이 문제의 실제 원인은 Streamlit의 세션 상태가 브라우저-서버 연결에
    묶여 있어서, (모바일에서 화면을 오래 꺼두거나 다른 앱으로 오래 전환하는
    등으로) 그 연결이 끊기면 서버가 기존 세션을 비우고 완전히 새 세션으로
    시작해버리는 데 있다 — 이건 앱 코드로 "연결 끊김 자체"를 막을 수 있는
    부분이 아니다. 대신, 지금까지는 process_list에 실제로 "저장(Save New
    Process)"된 항목만 백업되고 있어서, 저장 전 타이핑 중이던 내용은 세션이
    끊기면 통째로 사라지는 문제가 있었다. 세션이 끊겨도 "Restore Selected
    Session"으로 복구하면, 이전에 저장해둔 항목들 뿐 아니라 마지막으로
    타이핑하던 draft까지 함께 돌아온다(복원 로직은 아래 "Restore Selected
    Session" 버튼 콜백 참고).

    [v2.25.0] 이 함수는 실제 저장(Save New Process/Update Process/Delete
    /Go Evaluation/Restore)처럼 "확실히 클라우드까지 바로 반영하고 싶은"
    시점에만 호출한다. Description 등 입력칸에서 타이핑할 때마다 걸리는
    draft 자동 저장은 아래 save_draft_local_only()로 옮겼다 — 이유는 그
    함수 주석 참고."""
    if st.session_state.get("stop_backup", False):
        return
    supplier, evaluator, fname, backup_data = _build_backup_payload_with_draft()
    if supplier is None:
        return

    # ① 로컬 파일 저장 — 인터넷 없어도 항상 실행
    try:
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"로컬 백업 저장 실패: {e}")

    # ② 클라우드 저장 — 실패해도 로컬이 유지되므로 문제없음
    upload_or_update_gsheet(fname, backup_data)


def save_draft_local_only():
    """[v2.25.0] Process Name/Description/Type/Score/Remark의 on_change로
    걸리는 draft 자동 저장 전용 함수. save_temp_backup()과 달리 클라우드
    저장은 시도하지 않고 로컬 파일 저장만 한다.

    이유: "인터넷이 안 되거나 중간에 잠깐 끊기면 문제가 생기지 않을까?"라는
    질문에 대한 대응. v2.24.0에서는 이 다섯 칸 모두에 save_temp_backup()을
    직접 걸었는데, 그 함수는 매번 클라우드 저장까지 시도한다. 오프라인이거나
    네트워크가 불안정할 때는 그때마다 has_internet()의 사전 연결 확인(캐시가
    만료된 경우 최대 INTERNET_CHECK_TIMEOUT_SEC초)이나, 어쩌다 연결은 됐는데
    도중에 끊기는 경우의 API 호출 자체(최대 NETWORK_TIMEOUT_SEC초)만큼 그
    칸을 벗어나는 순간 화면이 잠깐씩 멎어 보일 수 있다 — 필드가 5개나 되니
    체감상 예전(제출 버튼 누를 때 딱 한 번)보다 훨씬 자주 이런 지연이 생길
    수 있다는 우려가 타당했다.
    draft는 세션이 끊겼을 때를 대비한 임시 보호장치일 뿐 최종 제출이
    아니므로, 굳이 매번 클라우드까지 확인할 필요가 없다. 그래서 이 함수는
    로컬 파일 저장만 즉시 하고 끝낸다 — 로컬 저장은 네트워크를 전혀 타지
    않으므로 인터넷 상태와 무관하게 항상 빠르게 끝난다. 클라우드 반영은 이미
    있던 sync_local_to_cloud_if_needed()(평가 중일 때 매 rerun마다 확인하되
    SYNC_RECHECK_INTERVAL_SEC=60초 간격으로만 재시도)가 맡아서, 온라인
    상태가 되면 늦어도 다음 화면 갱신 시점에 자동으로 클라우드에도 반영된다.
    (기기가 완전히 꺼지는 등 로컬 저장 자체가 안 되는 경우는 애초에 이
    함수가 아니라 기기 문제이므로 이 함수의 책임 범위 밖이다.)"""
    if st.session_state.get("stop_backup", False):
        return
    supplier, evaluator, fname, backup_data = _build_backup_payload_with_draft()
    if supplier is None:
        return

    # 로컬 파일 저장만 — 클라우드 시도는 하지 않음(위 설명 참고)
    try:
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"로컬 draft 백업 저장 실패: {e}")


# =====================================================================
# [v2.2.0] 자동 동기화: 하루 1회
# 로컬 timestamp가 클라우드보다 TS_DIFF_THRESHOLD_SEC 초 이상 앞서면
# 로컬 → 클라우드 덮어쓰기.
# 오프라인 중 작업했던 내용이 다음날 앱 접속 시 자동으로 클라우드에 반영됨.
#
# [v2.4.0] "세션당 1회" → "SYNC_RECHECK_INTERVAL_SEC초 간격으로 재시도"로 변경.
# 기존에는 세션 시작 시 한 번 확인하고 나면(_sync_done=True) 그 세션 동안은
# 다시는 확인하지 않아서, 같은 세션을 계속 켜둔 채로 인터넷이 중간에 복구돼도
# 자동으로 클라우드에 반영되지 않는 문제가 있었음. 이제는 마지막 확인 후
# 일정 시간이 지나면 다시 확인하므로, 인터넷이 돌아온 뒤 아무 저장 동작
# (프로세스 추가/수정 등으로 화면이 다시 그려지는 시점)이 한 번만 있으면
# 자동으로 클라우드에 반영된다.
# =====================================================================
SYNC_RECHECK_INTERVAL_SEC = 60  # 이 시간(초)마다 로컬→클라우드 동기화 필요 여부 재확인


def sync_local_to_cloud_if_needed():
    """로컬이 더 최신이면 클라우드에 덮어씀. 마지막 확인 후 SYNC_RECHECK_INTERVAL_SEC초가
    지나기 전까지는 다시 확인하지 않음 (매번 재시도하며 불필요하게 지연되는 것 방지)."""
    last_check = st.session_state.get("_last_sync_check_ts", 0)
    if time.time() - last_check < SYNC_RECHECK_INTERVAL_SEC:
        return
    st.session_state._last_sync_check_ts = time.time()  # 먼저 기록 (오류 나도 중복 실행 방지)

    supplier  = st.session_state.master_info.get("supplier", "")
    evaluator = st.session_state.master_info.get("evaluator", "")
    if not supplier or not evaluator:
        return

    fname = get_backup_filename(supplier, evaluator)
    if not os.path.exists(fname):
        return  # 로컬 파일 없으면 동기화 불필요

    # 로컬 timestamp 읽기
    try:
        with open(fname, "r", encoding="utf-8") as f:
            local_data = json.load(f)
        local_ts = local_data.get("last_updated", "")
    except Exception:
        return

    # 클라우드 timestamp 읽기
    cloud_ts = get_gsheet_cloud_timestamp(fname)

    if cloud_ts is None:
        # [v2.4.0] 클라우드에 없는 것인지, 아니면 그냥 오프라인이라 못 읽어온 것인지 구분
        # → 오프라인이면 이번엔 조용히 넘어가고, 다음 재시도 때 다시 확인
        if not has_internet():
            return
        # 온라인인데도 클라우드에 없으면 로컬을 업로드
        upload_or_update_gsheet(fname, local_data)
        logger.warning("[Sync] 클라우드에 없음 → 로컬 업로드 완료")
        return

    diff = ts_diff_seconds(local_ts, cloud_ts)
    if diff > TS_DIFF_THRESHOLD_SEC:
        # 로컬이 더 최신 → 클라우드에 덮어씀
        upload_or_update_gsheet(fname, local_data)
        logger.warning(f"[Sync] 로컬이 {diff:.0f}초 최신 → 클라우드 덮어쓰기 완료")


# =====================================================================
# [v2.2.0] 복구 목록 빌드
#
# 판단 기준 (파일별로 개별 비교):
#   1. 클라우드 연결 불가 → 로컬만 표시
#   2. 클라우드 연결 가능 + 로컬이 10초 초과 최신
#      → 로컬이 더 최신 데이터이므로 로컬만 표시
#   3. 클라우드 연결 가능 + 클라우드가 최신(혹은 10초 이내 차이)
#      → 클라우드만 표시
# =====================================================================
def build_backup_options():
    """
    {label: data} 딕트 반환. 라벨 prefix로 출처 구분:
      [☁️ Cloud] — 클라우드 데이터
      [🖥️ Local] — 로컬 데이터 (클라우드보다 최신인 경우만)
    """
    options     = {}
    cloud_avail = get_sheets_service()[0] is not None  # 클라우드 연결 가능 여부

    # 로컬 파일 목록 스캔
    local_files = {}
    for bf in glob.glob(os.path.join(BACKUP_DIR, "*.json")):
        try:
            with open(bf, "r", encoding="utf-8") as f:
                data = json.load(f)
            local_files[bf] = data
        except Exception as e:
            logger.warning(f"로컬 백업 파일 읽기 실패 ({bf}): {e}")

    if not cloud_avail:
        # 케이스 1: 클라우드 연결 불가 → 로컬만 표시
        for bf, data in local_files.items():
            try:
                ts    = data.get("last_updated", "unknown")
                label = (
                    f"[🖥️ Local] {data['info']['supplier']} "
                    f"by {data['info']['evaluator']} ({ts})"
                )
                options[label] = data
            except KeyError:
                continue
        return options

    # 클라우드 연결 가능: 파일별로 timestamp 비교 후 표시 출처 결정
    # 먼저 클라우드 전체 목록을 한 번만 읽어서 캐싱
    service, sheet_id = get_sheets_service()
    cloud_rows = _get_all_rows(service, sheet_id) if service and sheet_id else []

    def get_cloud_data_for_file(fname):
        """cloud_rows에서 fname에 해당하는 (data, ts) 반환. 없으면 (None, None)."""
        base = os.path.basename(fname)
        for row in cloud_rows:
            if len(row) >= 2 and row[0] == base:
                try:
                    d  = json.loads(row[1])
                    ts = row[2] if len(row) >= 3 else None
                    return d, ts
                except Exception:
                    return None, None
        return None, None

    # 로컬 파일과 클라우드를 비교해 표시 출처 결정
    handled_bases = set()
    for bf, local_data in local_files.items():
        base = os.path.basename(bf)
        handled_bases.add(base)
        local_ts             = local_data.get("last_updated", "")
        cloud_data, cloud_ts = get_cloud_data_for_file(bf)

        if cloud_ts is None:
            # 클라우드에 없는 파일 → 로컬 표시
            try:
                label = (
                    f"[🖥️ Local] {local_data['info']['supplier']} "
                    f"by {local_data['info']['evaluator']} ({local_ts})"
                )
                options[label] = local_data
            except KeyError:
                continue
        else:
            diff = ts_diff_seconds(local_ts, cloud_ts)
            if diff > TS_DIFF_THRESHOLD_SEC:
                # 케이스 2: 로컬이 10초 초과 최신 → 로컬만 표시
                try:
                    label = (
                        f"[🖥️ Local] {local_data['info']['supplier']} "
                        f"by {local_data['info']['evaluator']} ({local_ts})"
                    )
                    options[label] = local_data
                except KeyError:
                    continue
            else:
                # 케이스 3: 클라우드가 최신(혹은 동일) → 클라우드만 표시
                try:
                    label = (
                        f"[☁️ Cloud] {cloud_data['info']['supplier']} "
                        f"by {cloud_data['info']['evaluator']} ({cloud_ts})"
                    )
                    options[label] = cloud_data
                except (KeyError, TypeError):
                    continue

    # 로컬에 없고 클라우드에만 있는 항목 추가
    for row in cloud_rows:
        if len(row) >= 2 and row[0] and row[0] not in handled_bases:
            try:
                data  = json.loads(row[1])
                ts    = row[2] if len(row) >= 3 else "unknown"
                label = (
                    f"[☁️ Cloud] {data['info']['supplier']} "
                    f"by {data['info']['evaluator']} ({ts})"
                )
                options[label] = data
            except (json.JSONDecodeError, KeyError):
                continue

    return options


# 다운로드 콜백
def handle_download():
    if st.session_state.get("delete_backup_checkbox", True):
        st.session_state.stop_backup = True
        supplier  = st.session_state.master_info.get("supplier", "")
        evaluator = st.session_state.master_info.get("evaluator", "")
        if supplier and evaluator:
            fname = get_backup_filename(supplier, evaluator)
            delete_gsheet_row_if_exists(fname)
            if os.path.exists(fname):
                try:
                    os.remove(fname)
                except Exception as e:
                    logger.warning(f"로컬 백업 삭제 실패: {e}")
        st.session_state.download_action_status = "deleted"
    else:
        st.session_state.stop_backup = False
        st.session_state.download_action_status = "kept"


def reindex_processes():
    for i, p in enumerate(st.session_state.process_list):
        p["No."] = i + 1


# =====================================================================
# 폼 네비게이션 및 상태 동기화
# =====================================================================
def sync_form_with_state():
    if st.session_state.is_inserting:
        st.session_state.p_name_input  = ""
        st.session_state.p_desc_input  = ""
        st.session_state.p_type_input  = None
        st.session_state.p_score_input = None
        st.session_state.p_remark_input = ""
    else:
        plist = st.session_state.process_list
        idx   = st.session_state.nav_index
        if len(plist) > 0 and 0 <= idx < len(plist):
            p = plist[idx]
            st.session_state.p_name_input   = p["Process"] if p["Process"] != "N/A" else ""
            st.session_state.p_desc_input   = p["Description"]
            st.session_state.p_type_input   = p["Type"]
            st.session_state.p_score_input  = p["PAMI"]
            st.session_state.p_remark_input = p["Remark"]
        else:
            st.session_state.is_inserting   = True
            st.session_state.nav_index      = max(len(plist) - 1, -1)
            st.session_state.p_name_input   = ""
            st.session_state.p_desc_input   = ""
            st.session_state.p_type_input   = None
            st.session_state.p_score_input  = None
            st.session_state.p_remark_input = ""
    st.session_state.show_delete_confirm = False
    st.session_state.pami_form_error     = ""


# =====================================================================
# 순환 네비게이션
# Prev: 첫 번째에서 누르면 → 마지막으로
# Next: 마지막에서 누르면 → 첫 번째로
# =====================================================================
def nav_prev():
    plist = st.session_state.process_list
    if len(plist) == 0:
        return
    if st.session_state.is_inserting:
        st.session_state.is_inserting = False
    elif st.session_state.nav_index > 0:
        st.session_state.nav_index -= 1
    else:
        st.session_state.nav_index = len(plist) - 1
    sync_form_with_state()


def nav_next():
    plist = st.session_state.process_list
    if len(plist) == 0:
        return
    if st.session_state.is_inserting:
        return
    if st.session_state.nav_index < len(plist) - 1:
        st.session_state.nav_index += 1
    else:
        st.session_state.nav_index = 0
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
            st.session_state.nav_index    = -1
            st.session_state.is_inserting = True
        elif idx >= len(st.session_state.process_list):
            st.session_state.nav_index    = len(st.session_state.process_list) - 1
            st.session_state.is_inserting = False
        else:
            st.session_state.is_inserting = False
        save_temp_backup()
    sync_form_with_state()


# =====================================================================
# [v2.7.0] Description 프리셋 적용
# [v2.8.0] "셀렉트가 안 된다"는 피드백에 따라, 자동 적용(on_change) 대신
# 드롭다운 + "Insert" 버튼의 2단계 방식으로 변경했었음.
# [v2.10.0] "Insert 버튼이 오히려 더 번거롭다"는 피드백에 따라 다시 되돌림.
# 다만 v2.7.0 때와 달리, 이번엔 고른 뒤 드롭다운을 안내 문구로 리셋하지
# 않는다 — 그 "자동 리셋"이 방금 고른 선택지가 화면에서 바로 사라져 보이게
# 만들어 "선택이 안 먹힌다"는 오해를 낳았던 원인으로 보이기 때문. 이번엔
# 드롭다운에 고른 값이 그대로 남아있으면서, 고르는 즉시 Description 칸에도
# 반영되므로 버튼 없이도 지금 뭐가 적용됐는지 바로 확인할 수 있다.
# 프리셋 드롭다운은 st.form 밖에 있어야 선택 즉시 화면이 갱신되고
# Description 칸에 반영된다 (form 안의 위젯은 제출 전까지 값이 반영되지
# 않으므로, 폼 바깥에 둔다).
# =====================================================================
def apply_description_preset():
    """프리셋(알약 버튼)을 탭하면 즉시 Description 입력칸을 그 문구로 채운다.
    사용자는 이후 이어서 타이핑하거나, 전부 지우고 새로 쓸 수 있다.
    [v2.13.0] 추가: 고른 공정에 매핑된 Type(MH/P/WIP)이 있으면 Type 라디오
    버튼도 함께 자동 선택한다. Type은 일반 라디오 버튼이라 자동 선택 후에도
    잠기지 않으므로, 실제 상황이 다르면 그대로 클릭해서 바꿀 수 있다.
    [v2.14.0] 위젯을 st.selectbox → st.pills로 바꾸면서, 값이 없을 때
    "플레이스홀더 문자열"이 아니라 파이썬 None으로 오도록 로직 변경.

    [v2.19.0] 동작을 "하나만 고르는 선택(toggle)" 방식에서 "누를 때마다
    Description 칸 뒤에 이어붙이는(append) 방식"으로 전면 변경.
    - 이미 입력되어 있던 내용(직접 타이핑한 것이든, 이전에 다른 프리셋을 눌러
      추가된 것이든) 뒤에 콤마(, )로 구분해서 새로 고른 프리셋 문구를 이어
      붙인다. 예: "Unloading" 상태에서 "Storaging"을 누르면
      "Unloading, Storaging"이 된다.
    - Type은 매번 "가장 최근에 누른 프리셋"의 매핑값으로 갱신되므로, 결과적으로
      마지막으로 누른 프리셋 기준으로 Type이 맞춰진다.
    - 매번 처리가 끝나면 pills 자신의 선택 상태(desc_preset_select)를 다시
      None으로 되돌려, 버튼이 눌린 채로 "선택된 것처럼" 남아있지 않고 다음
      탭을 위한 중립 상태로 돌아가게 한다("toggle 형식은 필요 없다"는 요청
      반영). 위젯 자기 자신의 on_change 콜백 안에서 자기 자신의
      session_state를 되돌리는 것은 Streamlit에서 허용되는 패턴이다(다음
      rerun에서 위젯이 다시 그려지기 전에 실행되기 때문).
    [v2.20.0] "Clear를 프리셋 안에 넣지 말고 Description 옆에 별도 버튼으로
    만들어달라"는 요청에 따라, 전체 지우기 기능은 이 함수에서 분리해
    clear_description_field()로 옮김 — 이 함수는 이제 "프리셋 추가"만 담당.

    [v2.26.0] "Preset으로 Description 글을 넣을 때는 저장이 안 되는 것 같다"
    는 피드백에 따라 함수 끝에 save_draft_local_only() 호출을 추가했다.
    원인: v2.24.0~v2.25.0에서 draft 자동 저장은 Description 입력칸 자체의
    on_change에 걸려 있었는데, on_change는 "사용자가 그 위젯을 직접
    조작했을 때"만 호출된다. 프리셋(pills)을 탭하면 이 함수가 p_desc_input/
    p_type_input 값을 프로그램적으로 바꾸는 것이지, Description 입력칸을
    직접 조작하는 게 아니라서 그 위젯의 on_change는 호출되지 않았다 — 그래서
    프리셋으로만 채운 내용은 draft에 반영되지 않는 사각지대가 있었다. 이제
    프리셋을 탭해 내용을 바꾼 바로 그 시점에 이 함수 스스로 draft를
    저장하도록 해서, Description 입력칸을 직접 타이핑하든 프리셋을 탭하든
    항상 draft가 최신 상태로 남게 했다."""
    selected = st.session_state.get("desc_preset_select")
    if selected:
        # [v2.19.0] 기존 내용 뒤에 이어붙이기. 끝에 남아있을 수 있는 콤마/
        # 공백은 정리한 뒤 ", "로 구분해서 붙인다.
        current = (st.session_state.get("p_desc_input") or "").rstrip()
        if current.endswith(","):
            current = current[:-1].rstrip()
        st.session_state.p_desc_input = f"{current}, {selected}" if current else selected
        # [v2.13.0] 프리셋에 매핑된 Type이 있으면 같이 자동 선택
        # [v2.19.0] 여러 번 누르면 "가장 최근에 누른" 프리셋 기준으로 갱신됨
        mapped_type = DESCRIPTION_PRESET_TYPE_MAP.get(selected)
        if mapped_type in VALID_TYPES:
            st.session_state.p_type_input = mapped_type
        # [v2.19.0] 버튼을 누른 채로("선택된 상태로") 남지 않도록 매번 중립
        # 상태(None)로 되돌림 — toggle처럼 보이지 않게 하기 위함
        st.session_state.desc_preset_select = None
        # [v2.26.0] 프리셋으로 바뀐 내용을 즉시 draft로 저장(위 설명 참고)
        save_draft_local_only()


def clear_description_field():
    """[v2.20.0] "Clear 버튼을 프리셋 목록이 아니라 Description 옆에 따로
    만들어달라"는 요청에 따라 apply_description_preset()에서 분리한 전체
    지우기 동작. Description 칸만 비우고 Process Name/Type/Score/Remark는
    건드리지 않는다(지우고 싶은 건 문구지 이미 골라둔 다른 값들이 아닐 수
    있으므로).

    [v2.26.0] apply_description_preset()과 같은 이유로, Clear 버튼도
    Description 입력칸의 on_change를 거치지 않고 값을 직접 비우기 때문에
    draft가 갱신되지 않는 사각지대가 있었다. Clear를 누른 직후에도 draft가
    "비어있는 최신 상태"로 남도록 save_draft_local_only()를 호출한다."""
    st.session_state.p_desc_input = ""
    # [v2.26.0] Description을 비운 상태도 즉시 draft로 반영(위 설명 참고)
    save_draft_local_only()


def process_form_submit():
    p_name   = st.session_state.p_name_input
    p_desc   = st.session_state.p_desc_input
    p_type   = st.session_state.p_type_input
    p_score  = st.session_state.p_score_input
    p_remark = st.session_state.p_remark_input

    if not p_desc or p_type is None or p_score is None:
        st.session_state.pami_form_error = "🚨 Fill in Description, Type, and Score."
        return

    st.session_state.pami_form_error = ""

    if st.session_state.is_inserting:
        target_idx        = st.session_state.nav_index + 1
        is_appending_at_end = (target_idx == len(st.session_state.process_list))
        new_process = {
            "Supplier":   st.session_state.master_info["supplier"],
            "Evaluator":  st.session_state.master_info["evaluator"],
            "No.":        0,
            "Process":    p_name if p_name else "N/A",
            "Type":       p_type,
            "Description": p_desc,
            "PAMI":       p_score,
            "Remark":     p_remark if p_remark else "",
            "Time":       datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.process_list.insert(target_idx, new_process)
        reindex_processes()
        st.session_state.nav_index    = target_idx
        st.session_state.is_inserting = is_appending_at_end
        st.session_state.success_toast = f"Added successfully as No. {target_idx + 1}"
    else:
        idx = st.session_state.nav_index
        p   = st.session_state.process_list[idx]
        p["Process"]     = p_name if p_name else "N/A"
        p["Description"] = p_desc
        p["Type"]        = p_type
        p["PAMI"]        = p_score
        p["Remark"]      = p_remark if p_remark else ""
        p["Time"]        = datetime.now().strftime("%H:%M:%S")
        st.session_state.success_toast = f"Updated No. {idx + 1}"

    save_temp_backup()
    sync_form_with_state()


# =====================================================================
# 앱 시작 시 정리 작업 (세션당 1회)
# =====================================================================
cleanup_old_local_backups()
cleanup_old_gsheet_backups()

# =====================================================================
# 세션 상태 초기화
# =====================================================================
if 'master_info'           not in st.session_state:
    st.session_state.master_info           = {"supplier": "", "evaluator": ""}
if 'process_list'          not in st.session_state:
    st.session_state.process_list          = []
if 'is_evaluating'         not in st.session_state:
    st.session_state.is_evaluating         = False
if 'stop_backup'           not in st.session_state:
    st.session_state.stop_backup           = False
if 'download_action_status' not in st.session_state:
    st.session_state.download_action_status = None
if 'show_confirm_clear'    not in st.session_state:
    st.session_state.show_confirm_clear    = False
if 'pami_form_error'       not in st.session_state:
    st.session_state.pami_form_error       = ""
if 'success_toast'         not in st.session_state:
    st.session_state.success_toast         = ""
if 'show_delete_confirm'   not in st.session_state:
    st.session_state.show_delete_confirm   = False
if 'nav_index'             not in st.session_state:
    st.session_state.nav_index             = -1
if 'is_inserting'          not in st.session_state:
    st.session_state.is_inserting          = True

# 평가 중일 때 동기화 시도 (하루 1회)
if st.session_state.is_evaluating:
    sync_local_to_cloud_if_needed()

# 토스트 메시지 출력
if st.session_state.success_toast:
    st.toast(st.session_state.success_toast)
    st.session_state.success_toast = ""

# =====================================================================
# Step 1: Supplier & Evaluator Info
# =====================================================================
with st.expander("📌 Step 1: Supplier & Evaluator Info", expanded=not st.session_state.is_evaluating):

    if not st.session_state.is_evaluating:
        # [v2.2.0] 복구 목록: 로컬/클라우드 timestamp 비교 후 단일 출처만 표시
        backup_options = build_backup_options()

        if backup_options:
            st.markdown(f"**Check Backup History (Past {BACKUP_RETENTION_DAYS} Days)**")
            selected_backup = st.selectbox(
                "Restore previous session",
                options=["-- Select a backup --"] + list(backup_options.keys())
            )
            if selected_backup != "-- Select a backup --":
                if st.button("Restore Selected Session"):
                    restored_data = backup_options[selected_backup]
                    st.session_state.master_info  = restored_data['info']
                    st.session_state.process_list = restored_data['list']
                    st.session_state.is_evaluating         = True
                    st.session_state.stop_backup           = False
                    st.session_state.download_action_status = None
                    st.session_state.nav_index    = len(st.session_state.process_list) - 1
                    st.session_state.is_inserting = True
                    sync_form_with_state()
                    # [v2.24.0] Save 버튼을 누르기 전에 타이핑 중이던 draft가
                    # 함께 백업되어 있으면 복원. sync_form_with_state()가 새
                    # 항목 입력칸을 빈 값으로 초기화한 "다음"에 덮어써야
                    # draft 내용이 지워지지 않는다.
                    draft = restored_data.get('draft')
                    if draft:
                        st.session_state.p_name_input   = draft.get("name", "") or ""
                        st.session_state.p_desc_input   = draft.get("desc", "") or ""
                        st.session_state.p_type_input   = draft.get("type")
                        st.session_state.p_score_input  = draft.get("score")
                        st.session_state.p_remark_input = draft.get("remark", "") or ""
                    st.rerun()
            st.write("---")

    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        supplier_input = st.text_input(
            "Supplier Name - Required*",
            value=st.session_state.master_info["supplier"],
            disabled=st.session_state.is_evaluating
        )
    with sub_col2:
        evaluator_input = st.text_input(
            "Evaluator Name - Required*",
            value=st.session_state.master_info["evaluator"],
            disabled=st.session_state.is_evaluating
        )

    if not st.session_state.is_evaluating:
        if st.button("Go Evaluation"):
            if not supplier_input or not evaluator_input:
                st.error("🚨 Please enter both Supplier Name and Evaluator Name.")
            else:
                st.session_state.master_info["supplier"]  = supplier_input
                st.session_state.master_info["evaluator"] = evaluator_input
                st.session_state.is_evaluating = True
                save_temp_backup()
                st.rerun()

# =====================================================================
# Step 2: PAMI Input
# =====================================================================
if st.session_state.is_evaluating:
    st.info(
        f"📍 Supplier: **{st.session_state.master_info['supplier']}** | "
        f"Evaluator: **{st.session_state.master_info['evaluator']}**"
    )

    # [v2.4.0] 온라인/오프라인 상태 표시
    # 인터넷이 끊겨도 앱이 멈추지 않고 로컬 저장만으로 계속 진행되는데,
    # 지금 클라우드까지 저장되고 있는지 사용자가 바로 알 수 있도록 안내.
    if has_internet():
        st.caption("☁️ Cloud sync: connected — your data is backed up locally and to the cloud.")
    else:
        st.caption(
            "📴 No internet connection — your data is still being saved locally. "
            "It will sync to the cloud automatically once you're back online."
        )

    if st.session_state.stop_backup:
        st.warning("⚠️ CSV downloaded. Automatic backup is now disabled for this session.")

    # =====================================================================
    # Bulk Upload via Excel
    # [v2.3.0] 안내문/에러/경고 메시지를 영어로 변경 (화면 표시용 텍스트만 대상)
    # =====================================================================
    with st.expander("📂 Bulk Upload via Excel", expanded=False):
        st.markdown("**Use the Excel template below to register multiple processes at once.**")

        template_df = pd.DataFrame({
            "Process Name": ["Assembly 1", "Testing"],
            "Description":  ["Engine assembly", "Final check"],
            "Type":         ["MH", "P"],
            "Score":        [4, 5],
            "Remark":       ["Routine check", "Critical step"]
        })
        towrite = io.BytesIO()
        template_df.to_excel(towrite, index=False, engine='openpyxl')
        towrite.seek(0)

        st.download_button(
            label="📥 Download Excel Template",
            data=towrite,
            file_name="OAMI_Bulk_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download the template, fill it in, then upload it below."
        )

        uploaded_file = st.file_uploader("Upload filled Excel template", type=["xlsx", "xls"])
        if uploaded_file is not None:
            if st.button("🚀 Upload & Apply Data"):
                try:
                    df_uploaded   = pd.read_excel(uploaded_file)
                    required_cols = ["Description", "Type", "Score"]
                    if not all(col in df_uploaded.columns for col in required_cols):
                        st.error(
                            f"🚨 Invalid Excel template. "
                            f"The following columns are required: {', '.join(required_cols)}"
                        )
                    else:
                        added_count = 0
                        skipped_rows = []
                        for row_idx, row in df_uploaded.iterrows():
                            desc = row.get("Description")
                            if pd.isna(desc) or str(desc).strip() == "":
                                continue
                            raw_type = str(row.get("Type", "")).strip().upper()
                            if raw_type not in VALID_TYPES:
                                skipped_rows.append(
                                    f"Row {row_idx + 2}: Type '{row.get('Type')}' is invalid (MH/P/WIP only)"
                                )
                                continue
                            try:
                                raw_score = int(row.get("Score", 0))
                            except (ValueError, TypeError):
                                raw_score = 0
                            if raw_score not in VALID_SCORES:
                                skipped_rows.append(
                                    f"Row {row_idx + 2}: Score '{row.get('Score')}' is invalid (1~5 only)"
                                )
                                continue
                            new_process = {
                                "Supplier":    st.session_state.master_info["supplier"],
                                "Evaluator":   st.session_state.master_info["evaluator"],
                                "No.":         0,
                                "Process":     str(row.get("Process Name", "N/A")) if pd.notna(row.get("Process Name")) else "N/A",
                                "Type":        raw_type,
                                "Description": str(desc).strip(),
                                "PAMI":        raw_score,
                                "Remark":      str(row.get("Remark", "")) if pd.notna(row.get("Remark")) else "",
                                "Time":        datetime.now().strftime("%H:%M:%S")
                            }
                            st.session_state.process_list.append(new_process)
                            added_count += 1

                        if added_count > 0:
                            reindex_processes()
                            save_temp_backup()
                            st.session_state.is_inserting = True
                            st.session_state.nav_index    = len(st.session_state.process_list) - 1
                            sync_form_with_state()
                            st.success(f"✅ {added_count} process(es) were successfully registered in bulk!")
                        if skipped_rows:
                            st.warning(
                                f"⚠️ {len(skipped_rows)} row(s) were skipped because they are invalid:\n\n"
                                + "\n".join(skipped_rows)
                            )
                        if added_count == 0 and not skipped_rows:
                            st.warning("⚠️ No valid process data found in the Excel file to register.")
                        if added_count > 0:
                            time.sleep(1)
                            st.rerun()
                except Exception as e:
                    st.error(f"🚨 An error occurred while reading the file: {e}")

    st.write("---")

    # =====================================================================
    # 네비게이션 버튼 - 순환 방식
    # =====================================================================
    if st.session_state.process_list or st.session_state.is_inserting:
        nav_c1, nav_c2, nav_c3 = st.columns(3)
        with nav_c1:
            st.button("⬅️ Prev", on_click=nav_prev,
                      disabled=len(st.session_state.process_list) == 0,
                      use_container_width=True)
        with nav_c2:
            st.button("Next ➡️", on_click=nav_next,
                      disabled=st.session_state.is_inserting or len(st.session_state.process_list) == 0,
                      use_container_width=True)
        with nav_c3:
            st.button("➕ New", on_click=nav_new,
                      disabled=st.session_state.is_inserting,
                      use_container_width=True)
        st.write("")

        if st.session_state.is_inserting:
            st.markdown(
                f"<div style='text-align:center; font-weight:bold; color:#0d6efd;'>"
                f"✨ Add New Process as No. {st.session_state.nav_index + 2}</div>",
                unsafe_allow_html=True
            )
        else:
            total       = len(st.session_state.process_list)
            current_num = st.session_state.nav_index + 1
            current_desc = st.session_state.process_list[st.session_state.nav_index].get('Description', '')
            st.markdown(
                f"<div style='text-align:center; font-weight:bold; color:#198754;'>"
                f"✏️ Editing No. {current_num} / {total} : {current_desc}</div>",
                unsafe_allow_html=True
            )

    # =====================================================================
    # [v2.7.0] Description 프리셋 선택
    # [v2.8.0] 드롭다운 + "Insert" 버튼의 2단계 방식으로 변경했었음.
    # [v2.10.0] "Insert 버튼이 더 번거롭다"는 피드백에 따라 버튼 제거,
    # 드롭다운에서 고르는 즉시(on_change) Description 칸에 반영되도록 변경.
    # (자세한 이유는 apply_description_preset() 함수 주석 참고)
    # st.form 밖에 있어야 선택 즉시 반영되므로, 폼 시작 전에 배치한다.
    # =====================================================================
    # [v2.14.0] "타이핑이 필요없이 셀렉만 되게, 모바일에서 키보드가 뜨는게
    # 불편하다"는 피드백에 따라 st.selectbox(검색용 텍스트 입력이 딸려있는
    # 드롭다운) → st.pills(탭만으로 고르는 알약 모양 버튼들)로 변경. 키보드가
    # 뜰 일이 아예 없고, 20개 항목이 화면 너비에 맞춰 자동으로 줄바꿈되어
    # 표시된다.
    # [v2.19.0] "누르면 토글처럼 선택 상태로 남지 말고, 누를 때마다 Description
    # 뒤에 이어붙여달라(예: Unloading 누르고 Storaging 누르면 둘 다 나오게).
    # 직접 타이핑한 글자 뒤에 프리셋을 눌러도 이어붙게 하고, Type은 마지막에
    # 누른 프리셋 기준으로 맞춰달라"는 요청에 따라 동작을 전면 변경. 자세한
    # 동작은 apply_description_preset() 참고.
    # [v2.20.0] "Clear를 프리셋 안에 넣지 말고 Description 옆에 별도 버튼으로
    # 만들어달라, Description은 Process Name 아래에 위치하게 해달라"는 요청에
    # 따라 v2.19.0에서 프리셋 목록 맨 끝에 있던 DESCRIPTION_PRESET_CLEAR_LABEL
    # ("🗑️ Clear")을 프리셋 옵션에서 빼고, Description 입력칸 바로 옆의 독립된
    # 버튼(clear_description_field() 콜백)으로 옮김. 자세한 내용은 파일 상단
    # [v2.20.0 변경사항] 참고.
    # =====================================================================
    # [v2.19.0] Description 입력칸을 st.form 밖으로 이동.
    # 이유: st.form 안의 위젯은 "제출(Submit)" 버튼을 누르기 전까지는 직접
    # 타이핑한 값이 session_state에 반영되지 않는다(프리셋 버튼처럼 폼 밖에
    # 있는 위젯과는 다르게, 폼 안 위젯은 블러/Tab을 해도 서버로 값이 전송되지
    # 않고 브라우저 안에서만 임시로 보관됨). 그래서 예전처럼 Description이
    # 폼 안에 있으면 "직접 타이핑 후 프리셋을 눌러서 이어붙이기" 기능이
    # 타이핑한 내용을 못 보고 그냥 덮어써 버리는 문제가 실제로 있었음(직접
    # 브라우저 테스트로 재현/확인함). 프리셋 픽커가 원래 폼 밖에 있는 것과
    # 같은 이유로, Description도 폼 밖으로 옮겨서 타이핑한 즉시(블러 시)
    # session_state에 반영되게 함.
    # [v2.20.0] "Description을 Process Name 아래에 위치시켜달라"는 요청에
    # 따라 Process Name도 함께 폼 밖으로 옮겨서 Description 바로 위에 배치.
    # Process Name은 이 append 문제와 무관하지만, 폼 밖 위젯끼리는 순서를
    # 자유롭게 배치할 수 있으므로 이렇게 옮겨서 원래 있던 순서(Process Name
    # → Description)를 그대로 되살렸다. Type/Score/Remark/제출 버튼만 폼 안에
    # 남음.
    # [v2.21.0] "Process Name/Description이 Type/Score/Remark/Save와 같은
    # 테두리 박스 안에 있어야 한다"는 스크린샷 피드백에 따라, st.form 자체를
    # st.container(border=True)로 교체하고 그 안에 Process Name부터 Save
    # 버튼까지 전부 배치했다. Description Preset pills는 사용자 확정에 따라
    # 계속 이 박스 밖(위)에 남는다. 자세한 내용은 파일 상단 [v2.21.0 변경사항]
    # 참고.
    # =====================================================================
    st.markdown("**📝 Step 2: PAMI Input per Process**")
    if st.session_state.pami_form_error:
        st.error(st.session_state.pami_form_error)

    st.pills(
        "📋 Description Preset (optional)",
        options=DESCRIPTION_PRESETS,
        selection_mode="single",
        key="desc_preset_select",
        on_change=apply_description_preset,
        help="Tap a preset to add it to the end of the Description field below "
             "(you can tap several in a row, or type your own text first)."
    )

    # =====================================================================
    # [v2.21.0] Process Name ~ Save 버튼까지를 테두리 박스 하나로 통합.
    # 예전 st.form(...) 대신 st.container(border=True)를 사용 — form이
    # 아니므로 st.form_submit_button 대신 일반 st.button을 쓴다. Description
    # Preset pills는 사용자 확정에 따라 이 박스 밖(위)에 그대로 둔다.
    # =====================================================================
    with st.container(border=True):
        # [v2.24.0] Process Name/Description/Type/Score/Remark 다섯 칸 모두에
        # on_change를 걸어, 이 칸에서 포커스가 벗어날 때마다(라디오는 선택
        # 즉시) 지금까지 입력한 내용을 draft로 자동 백업한다. 세션이 중간에
        # 끊겨도 Restore로 복구하면 이 draft까지 함께 돌아온다.
        # [v2.25.0] "인터넷이 안 되거나 중간에 잠깐 끊기면 문제가 생기지
        # 않을까?"라는 질문에 따라, on_change 대상을 save_temp_backup(로컬+
        # 클라우드 동시 시도)에서 save_draft_local_only(로컬만 즉시 저장)로
        # 변경. 다섯 칸 모두에서 매번 클라우드까지 확인하면 오프라인/불안정한
        # 네트워크에서 칸을 옮길 때마다 짧게 멈춰 보일 수 있어서, draft
        # 저장은 네트워크와 무관하게 항상 즉시 끝나도록 하고 클라우드 반영은
        # 기존 sync_local_to_cloud_if_needed()에 맡겼다. 자세한 이유는
        # save_draft_local_only() 함수 주석과 파일 상단 [v2.25.0 변경사항]
        # 참고.
        st.text_input("Process Name (Optional)", key="p_name_input", on_change=save_draft_local_only)
        # [v2.22.0] "Clear Description 버튼이 너무 커서 실수로 누를 것 같다"는
        # 피드백에 따라, Description 아래에 있던 가로로 긴 버튼(글자+아이콘)을
        # 없애고 휴지통 아이콘만 있는 작은 버튼으로 교체(처음엔 st.columns로
        # Description 오른쪽 같은 줄에 배치 시도).
        # [v2.23.0] "모바일로 보니 (좁은 화면에서 컬럼이 자동으로 줄바꿈되어)
        # 무조건 한 줄 아래로 내려가더라, 그럼 차라리 한 줄 내리고 오른쪽으로
        # 보내달라"는 피드백에 따라 방식 변경. st.columns([6,1])는 화면 폭에
        # 따라 "PC에서는 같은 줄, 좁은 화면에서는 왼쪽 정렬로 줄바꿈"이라는
        # 일관되지 않은 결과를 냈었다(직접 브라우저 테스트로 확인). 이를
        # 화면 크기와 무관하게 "Description 아래 자기만의 줄 + 그 줄의 오른쪽
        # 끝"으로 통일하기 위해, 컬럼 대신 st.container(key=...)로 버튼 전용
        # 줄을 만들고, 그 컨테이너에 CSS(align-items:flex-end)를 적용해 안의
        # 버튼을 항상 오른쪽으로 붙였다. st.container에 key를 주면 Streamlit이
        # 해당 블록에 "st-key-<key>" CSS 클래스를 자동으로 붙여주는 점을
        # 이용함(별도 컬럼 분할이 없으므로 좁은 화면에서도 줄바꿈으로 인한
        # 위치 흔들림이 없다).
        st.text_input("Description - Required*", placeholder="Enter details, or pick a preset above...", key="p_desc_input", on_change=save_draft_local_only)
        with st.container(key="clear_desc_row"):
            st.button("🗑️", key="clear_desc_icon_btn", on_click=clear_description_field,
                      help=f"{DESCRIPTION_PRESET_CLEAR_LABEL} (Process Name/Type/Score/Remark are not affected).")
        st.markdown(
            "<style>div.st-key-clear_desc_row{display:flex; align-items:flex-end;}</style>",
            unsafe_allow_html=True
        )

        st.write("Type - Required*")
        st.radio("Type", options=["MH", "P", "WIP"], index=None, horizontal=True,
                 label_visibility="collapsed", key="p_type_input", on_change=save_draft_local_only)
        st.write("Score (1~5) - Required*")
        st.radio("Score", options=[1, 2, 3, 4, 5], index=None, horizontal=True,
                 label_visibility="collapsed", key="p_score_input", on_change=save_draft_local_only)
        st.text_input("Remark (Optional)", key="p_remark_input", on_change=save_draft_local_only)
        btn_text = "Save New Process" if st.session_state.is_inserting else "Update Process"
        st.button(btn_text, on_click=process_form_submit)

    # =====================================================================
    # Cancel / Delete 버튼
    # =====================================================================
    if st.session_state.process_list or st.session_state.is_inserting:
        act_c1, act_c2 = st.columns(2)
        with act_c1:
            st.button("🚫 Cancel", on_click=nav_cancel,
                      disabled=(not st.session_state.is_inserting) or (len(st.session_state.process_list) == 0),
                      use_container_width=True)
        with act_c2:
            st.button("🗑️ Delete", on_click=set_delete_confirm,
                      disabled=st.session_state.is_inserting,
                      use_container_width=True)

        if st.session_state.show_delete_confirm and not st.session_state.is_inserting:
            st.error(f"⚠️ Are you sure you want to delete Process **No. {st.session_state.nav_index + 1}**?")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.button("✔️ Yes, Delete", on_click=delete_current_process, use_container_width=True)
            with d_col2:
                st.button("❌ Cancel", on_click=cancel_delete, use_container_width=True)

    # =====================================================================
    # Evaluation Summary & Export
    # =====================================================================
    if st.session_state.process_list:
        st.write("---")
        st.markdown("**📊 Evaluation Summary**")

        df   = pd.DataFrame(st.session_state.process_list)
        cols = ["Supplier", "Evaluator", "No.", "Process", "Type", "Description", "PAMI", "Remark", "Time"]
        df   = df[cols]

        oami_avg        = df["PAMI"].mean()
        total_processes = len(df)

        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric(label="Total Processes", value=f"{total_processes}")
        with m_col2:
            st.metric(label="Total OAMI Average", value=f"{oami_avg:.2f} / 5.0")

        raw_text = (
            f"Supplier: {st.session_state.master_info['supplier']} | "
            f"Evaluator: {st.session_state.master_info['evaluator']} | "
            f"Processes: {total_processes} | Avg OAMI: {oami_avg:.2f}\n"
        )
        # [v2.2.1] 컬럼 순서 변경: No. > Process > Description > Type > PAMI > Remark > Time
        raw_text += "No.|Process|Description|Type|PAMI|Remark|Time\n"
        for _, row in df.iterrows():
            raw_text += (
                f"{row['No.']}|{row['Process']}|{row['Description']}|"
                f"{row['Type']}|{row['PAMI']}|{row['Remark']}|{row['Time']}\n"
            )

        tab_mobile, tab_pc = st.tabs(["📱 1. Mobile (Text)", "🖥️ 2. PC (Table)"])

        with tab_mobile:
            st.info(
                "💡 **Tip:** Click the button below to copy the text, "
                "or use the 'Open Outlook Mail App' button to auto-fill your email body."
            )
            safe_raw_text  = json.dumps(raw_text)
            copy_text_html = f"""
            <button id="btn-copy-text" onclick="copyToClipboard()" style="width:100%; height:40px; background-color:#0d6efd; color:white; border:none; border-radius:5px; font-weight:bold; font-size:14px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.1);">
                📋 Copy Text for Outlook
            </button>
            <script>
            function copyToClipboard() {{
                var textToCopy = {safe_raw_text};
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(textToCopy).then(showSuccess).catch(function() {{ fallbackCopy(textToCopy); }});
                }} else {{ fallbackCopy(textToCopy); }}
                function fallbackCopy(text) {{
                    var ta = document.createElement("textarea");
                    ta.value = text;
                    ta.style.cssText = "position:fixed;top:0;left:0;opacity:0;";
                    document.body.appendChild(ta);
                    ta.focus(); ta.select();
                    try {{ document.execCommand('copy') ? showSuccess() : alert("Copy failed."); }}
                    catch(e) {{ alert("Copy failed."); }}
                    document.body.removeChild(ta);
                }}
                function showSuccess() {{
                    var btn = document.getElementById('btn-copy-text');
                    btn.innerText = '✅ Copied!';
                    btn.style.backgroundColor = '#198754';
                    setTimeout(function() {{ btn.innerText='📋 Copy Text for Outlook'; btn.style.backgroundColor='#0d6efd'; }}, 2000);
                }}
            }}
            </script>
            """
            st.html(copy_text_html)
            st.code(raw_text, language="text")

        with tab_pc:
            st.info(
                "💡 Wide and clean table copy optimized for PC environments. "
                "**Note:** Tables cannot be auto-filled in the Mail App. "
                "You must copy and paste this table manually."
            )
            # [v2.2.1] 컬럼 순서 변경: Description을 Type 앞으로
            export_cols = ["No.", "Process", "Description", "Type", "PAMI", "Remark", "Time"]
            html_table  = df[export_cols].to_html(index=False).replace(
                '<table border="1" class="dataframe">',
                '<table border="1" cellpadding="8" style="border-collapse:collapse; text-align:left; font-family:Arial; width:100%;">'
            )
            email_html = (
                f"<div id='pc-email-content' style='background:#f8f9fa; padding:15px;'>"
                f"<strong>OAMI Report: {st.session_state.master_info['supplier']}</strong><br><br>"
                f"<strong>Total Processes:</strong> {total_processes}<br>"
                f"<strong>Average OAMI: <span style='color:blue;'>{oami_avg:.2f} / 5.0</span></strong>"
                f"<br><br>{html_table}</div>"
            )
            copy_table_html = f"""
            <button id="btn-copy-table" onclick='copyPCTable()' style='width:100%; height:40px; background-color:#28a745; color:white; border:none; border-radius:5px; font-weight:bold; font-size:14px; cursor:pointer; margin-bottom:10px; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>
                📋 Copy Table for Outlook
            </button>
            <script>
            function copyPCTable() {{
                var body  = document.getElementById('pc-email-content');
                var range = document.createRange();
                range.selectNode(body);
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                try {{
                    document.execCommand('copy');
                    var btn = document.getElementById('btn-copy-table');
                    btn.innerText='✅ Copied!'; btn.style.backgroundColor='#198754';
                    setTimeout(function() {{ btn.innerText='📋 Copy Table for Outlook'; btn.style.backgroundColor='#28a745'; }}, 2000);
                }} catch(e) {{ alert('Copy failed.'); }}
                window.getSelection().removeAllRanges();
            }}
            </script>
            """
            st.html(f"<div style='max-height:450px; overflow-y:auto;'>{copy_table_html}{email_html}</div>")

        st.write("")

        subject      = f"OAMI Evaluation - {st.session_state.master_info['supplier']} OAMI - {oami_avg:.2f}"
        body_encoded = urllib.parse.quote(raw_text)
        mail_link    = f"mailto:?subject={urllib.parse.quote(subject)}&body={body_encoded}"
        st.markdown(
            f'<a href="{mail_link}" target="_blank" style="text-decoration:none;">'
            f'<button style="width:100%; height:45px; border-radius:5px; border:none; cursor:pointer; background-color:#0078D4; color:white; font-weight:bold; font-size:14px;">'
            f'📨 Open Outlook Mail App (Auto-fill Text)</button></a>',
            unsafe_allow_html=True
        )

        st.write("---")
        st.warning(
            "⚠️ **Warning:** System backups are temporary and can be deleted at any time. "
            "**You must download the CSV file to keep your data permanently.**"
        )
        st.checkbox(
            "🗑️ Delete system backup file after download (Recommended for security)",
            value=True,
            key="delete_backup_checkbox"
        )

        summary_line  = (
            f"# Supplier: {st.session_state.master_info['supplier']} | "
            f"Evaluator: {st.session_state.master_info['evaluator']} | "
            f"Processes: {total_processes} | Avg OAMI: {oami_avg:.2f}\n"
        )
        # [v2.2.1] CSV 컬럼 순서 변경: Description을 Type 앞으로
        export_df     = df[["No.", "Process", "Description", "Type", "PAMI", "Remark", "Time"]]
        csv_data_bytes = (summary_line + export_df.to_csv(index=False)).encode('utf-8-sig')

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

        # 데이터 초기화
        if not st.session_state.show_confirm_clear:
            if st.button("🚨 Clear All Data (Start New)", use_container_width=True):
                st.session_state.show_confirm_clear = True
                st.rerun()
        else:
            st.error("⚠️ Are you sure? This will delete all current progress.")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("✔️ Yes, Clear Data", use_container_width=True):
                    supplier  = st.session_state.master_info.get("supplier", "")
                    evaluator = st.session_state.master_info.get("evaluator", "")
                    if supplier and evaluator:
                        fname = get_backup_filename(supplier, evaluator)
                        delete_gsheet_row_if_exists(fname)
                        if os.path.exists(fname):
                            try:
                                os.remove(fname)
                            except Exception as e:
                                logger.warning(f"초기화 중 백업 삭제 실패: {e}")
                    for key in ['master_info', 'process_list', 'is_evaluating', 'stop_backup',
                                'download_action_status', 'show_confirm_clear', 'nav_index',
                                'is_inserting', 'show_delete_confirm',
                                'p_name_input', 'p_desc_input', 'p_type_input',
                                'p_score_input', 'p_remark_input',
                                '_last_sync_check_ts']:  # [v2.4.0] _sync_done → _last_sync_check_ts
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            with col_no:
                if st.button("❌ No, Cancel", use_container_width=True):
                    st.session_state.show_confirm_clear = False
                    st.rerun()

# =====================================================================
# Footer - README 링크 (앱 최하단, 항상 표시)
# =====================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#aaa; font-size:13px; padding:4px 0 8px 0;'>"
    "📖 How to use &nbsp;→&nbsp; "
    "<a href='https://github.com/kim2140/oami#readme' target='_blank' style='color:#0d6efd; text-decoration:none;'>English</a>"
    " &nbsp;/&nbsp; "
    "<a href='https://github.com/kim2140/oami/blob/main/README_KO.md' target='_blank' style='color:#0d6efd; text-decoration:none;'>한국어</a>"
    "</div>",
    unsafe_allow_html=True
)