# 📝 공급사 OAMI 평가 앱

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://oamigmscore.streamlit.app/)

공급사 현장 평가를 위한 OAMI(Operation Assessment & Management Index) 입력 도구입니다.  
모바일/PC 모두 지원하며, 클라우드 자동 백업과 Outlook 이메일 내보내기 기능을 제공합니다.

---

## 🚀 앱 바로가기

**https://oamigmscore.streamlit.app/**

---

## 📋 주요 기능

| 기능 | 설명 |
|---|---|
| **실시간 자동 백업** | 입력 즉시 Google Sheets 클라우드 저장 |
| **세션 복원** | 이전 작업 이어서 진행 가능 |
| **엑셀 일괄 등록** | 여러 프로세스를 한 번에 업로드 |
| **순환 네비게이션** | Prev/Next로 항목 간 자유롭게 이동 |
| **모바일 텍스트 복사** | Outlook 앱에 한 번에 붙여넣기 |
| **PC 테이블 복사** | HTML 표 형식으로 복사 |
| **CSV 다운로드** | 영구 보관용 파일 저장 |

---

## 🛠️ 사용 방법

### Step 1 — Supplier & Evaluator 정보 입력

1. 앱 접속 후 **📌 Step 1: Supplier & Evaluator Info** 섹션 확인
2. **Supplier Name** 입력 (필수)
3. **Evaluator Name** 입력 (필수)
4. **Go Evaluation** 버튼 클릭 → Step 2로 이동

> ⚠️ 두 항목 모두 입력해야 다음 단계로 진행됩니다.

---

### Step 2 — 이전 세션 복원 (선택)

이전에 작업한 내용이 있으면 자동으로 백업 목록이 표시됩니다.

1. **Restore previous session** 드롭다운에서 항목 선택
   - `[☁️ Cloud]` — Google Sheets 클라우드 백업
   - `[🖥️ Local]` — 서버 로컬 백업 (최근 14일)
2. **Restore Selected Session** 클릭 → 이전 작업 내용 불러오기

> 💡 복원 후 마지막 항목에서 이어서 입력할 수 있습니다.

---

### Step 3 — 프로세스 입력 (개별 등록)

#### 3-1. 새 항목 추가

| 필드 | 필수 여부 | 설명 |
|---|---|---|
| **Process Name** | 선택 | 공정명 (미입력 시 N/A 자동 기입) |
| **Description** | **필수** | 공정 상세 내용 |
| **Type** | **필수** | `MH` / `P` / `WIP` 중 선택 |
| **Score (1~5)** | **필수** | OAMI 점수 (1=최하, 5=최상) |
| **Remark** | 선택 | 비고 |

1. 폼 작성 후 **Save New Process** 클릭
2. 저장 완료 시 상단에 토스트 메시지 표시
3. 다음 항목 자동 대기 상태로 전환

#### 3-2. 기존 항목 수정

1. **⬅️ Prev** / **Next ➡️** 버튼으로 항목 이동
2. 수정할 항목으로 이동하면 폼에 기존 값 자동 표시
3. 내용 수정 후 **Update Process** 클릭

#### 3-3. 항목 삭제

1. 삭제할 항목으로 이동
2. **🗑️ Delete** 클릭
3. 확인 메시지에서 **✔️ Yes, Delete** 클릭

> ⚠️ 삭제 후 번호(No.)가 자동으로 재정렬됩니다.

#### 3-4. 네비게이션 버튼

| 버튼 | 동작 |
|---|---|
| **⬅️ Prev** | 이전 항목 이동 (첫 번째에서 누르면 마지막으로 순환) |
| **Next ➡️** | 다음 항목 이동 (마지막에서 누르면 첫 번째로 순환) |
| **➕ New** | 새 항목 추가 모드 전환 |
| **🚫 Cancel** | 새 항목 추가 취소 (기존 목록으로 복귀) |

---

### Step 4 — 엑셀 일괄 등록 (선택)

여러 프로세스를 한 번에 등록할 때 사용합니다.

1. **📂 Bulk Upload via Excel** 섹션 펼치기
2. **📥 Download Excel Template** 클릭 → 양식 다운로드
3. 양식에 데이터 입력 후 저장

| 컬럼 | 필수 여부 | 허용값 |
|---|---|---|
| Process Name | 선택 | 텍스트 |
| Description | **필수** | 텍스트 |
| Type | **필수** | `MH` / `P` / `WIP` |
| Score | **필수** | `1` ~ `5` 정수 |
| Remark | 선택 | 텍스트 |

4. **Upload filled Excel template** → 파일 선택
5. **🚀 Upload & Apply Data** 클릭

> ⚠️ Type/Score 값이 올바르지 않은 행은 자동으로 건너뜁니다. 건너뛴 항목은 경고 메시지로 확인 가능합니다.

---

### Step 5 — 결과 확인 및 내보내기

프로세스가 1개 이상 등록되면 **📊 Evaluation Summary** 섹션이 표시됩니다.

#### 지표 확인

| 지표 | 설명 |
|---|---|
| **Total Processes** | 등록된 공정 수 |
| **Total OAMI Average** | 전체 평균 점수 (/ 5.0) |

#### 📱 모바일 — 텍스트 복사

1. **📱 1. Mobile (Text)** 탭 선택
2. **📋 Copy Text for Outlook** 클릭 → 클립보드 복사
3. Outlook 앱 열기 → 본문에 붙여넣기
4. 또는 **📨 Open Outlook Mail App** 클릭 → 제목/본문 자동 입력

#### 🖥️ PC — 테이블 복사

1. **🖥️ 2. PC (Table)** 탭 선택
2. **📋 Copy Table for Outlook** 클릭 → HTML 표 복사
3. Outlook 데스크톱 앱 본문에 붙여넣기

> ⚠️ PC 테이블은 Mail 앱 자동 연결을 지원하지 않습니다. 수동으로 복사하세요.

#### 📥 CSV 다운로드 (영구 보관)

1. **🗑️ Delete system backup file after download** 체크박스 확인
   - ✅ 체크됨 (권장): 다운로드 후 서버 백업 자동 삭제
   - ☐ 해제: 서버 백업 유지
2. **📥 Download CSV Backup** 클릭
3. 파일명: `OAMI_{Supplier명}_{날짜}.csv`

---

### Step 6 — 초기화 (새 평가 시작)

1. **🚨 Clear All Data (Start New)** 클릭
2. 확인 메시지에서 **✔️ Yes, Clear Data** 클릭
3. 모든 데이터 및 백업 삭제 후 Step 1으로 초기화

> ⚠️ 초기화 전 반드시 CSV를 다운로드하세요. 복구가 불가능합니다.

---

## 💾 백업 정책

| 구분 | 저장 위치 | 보관 기간 |
|---|---|---|
| 자동 백업 | Google Sheets (클라우드) | 수동 삭제 전까지 |
| 로컬 백업 | 서버 임시 저장 | **14일** |
| CSV 다운로드 | 사용자 기기 | 영구 보관 |

> ⚠️ 로컬 백업은 **14일 후 자동 삭제**됩니다. 중요한 데이터는 반드시 CSV로 저장하세요.

---

## 📎 Type 정의

| Type | 의미 |
|---|---|
| **MH** | Man-Hour (인력 투입 작업) |
| **P** | Process (공정) |
| **WIP** | Work In Progress (진행 중 작업) |

---

## ❓ FAQ

**Q. 입력 중 앱이 꺼졌어요.**  
A. 재접속 후 Step 1에서 동일한 Supplier/Evaluator로 진행하면 백업 목록에 이전 작업이 표시됩니다.

**Q. 엑셀 업로드 후 일부 행이 등록되지 않았어요.**  
A. Type(MH/P/WIP)과 Score(1~5) 값이 올바른지 확인하세요. 잘못된 행은 자동으로 건너뜁니다.

**Q. 같은 Supplier를 다시 평가하고 싶어요.**  
A. 이전 데이터를 CSV로 저장 후 **Clear All Data**로 초기화하고 새로 시작하세요.

**Q. PC에서 테이블을 이메일에 붙여넣으면 표 형식이 깨져요.**  
A. Outlook 데스크톱 앱(웹 버전 아님)에서 붙여넣기 하면 표 형식이 유지됩니다.

---

## 🔒 보안 안내

- 민감한 자격증명 정보는 앱 내에 저장되지 않습니다
- 백업 데이터는 CSV 다운로드 후 서버에서 삭제를 권장합니다
- Google Sheets 백업은 서비스 계정 전용 시트에만 저장됩니다

---

## 📄 License

MIT License
