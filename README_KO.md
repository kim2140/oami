> 🇺🇸 [View in English](README.md)

# 📝 Supplier OAMI Evaluation App (공급사 OAMI 평가 앱)

현장 심사자가 공급사의 공정별 **OAMI**(공정 품질) 평가 — Line Type + Type(MH/OP/WIP) + PAMI 점수(1~5) + 설명/비고 — 를 기록하기 위한 웹 앱입니다. **로컬 + 클라우드** 이중 백업이 자동으로 이루어져, 기기 문제나 통신 두절이 생겨도 작업 내용이 사라지지 않습니다.

*(이 문서는 앱 버전 **2.29.0** 기준으로 확인/작성되었습니다.)*

이 안내서는 앱을 처음 쓰는 분도 순서대로 따라 하기만 하면 되도록 작성했습니다.

---

## 🔗 앱 접속하기

별도 설치 없이 브라우저에서 바로 열면 됩니다.

**👉 https://oamigmscore.streamlit.app/**

PC와 모바일 브라우저 모두에서 사용할 수 있습니다. 아래 내용은 이 사이트를 연 뒤 사용하는 방법을 설명합니다.

---

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| 이중 백업 | 변경할 때마다 로컬 백업에 자동 저장되고, 온라인 상태일 때는 클라우드에도 자동으로 백업됩니다. |
| 오프라인 대응 | 인터넷이 끊겨도 앱은 멈추지 않고 로컬 저장만으로 계속 진행되며, 다시 연결되면 자동으로 클라우드와 동기화됩니다 — 어느 쪽이든 데이터 손실은 없습니다. |
| 타이핑 중 자동 저장 | **Save New Process**를 누르기 전, 입력하는 중에도 내용이 draft로 자동 저장되므로 브라우저 탭이 중간에 초기화돼도 처음부터 다시 입력할 필요 없이 "Restore Selected Session"에서 이어서 작성할 수 있습니다. |
| 글자 크기 조절 | 화면 상단의 5단계 −/+ 줌 컨트롤로 전체 글자 크기를 키우거나 줄일 수 있고, 선택값은 세션 동안(주소창 URL을 통해) 유지되어 새로고침해도 초기화되지 않습니다. |
| 탭으로 설명 작성 | 제조 흐름 순서(자재 투입 → 가공 → 조립/용접 → 도장 → 마무리 → 품질 → 포장/출하)로 정리된 22개의 프리셋 버튼을 탭하면 Description 입력칸 뒤에 이어붙여지며, 직접 타이핑한 내용과도 함께 조합할 수 있습니다. |
| Type 자동 제안 | Description 프리셋을 선택하면 해당 공정에 맞는 Type(MH/OP/WIP)도 함께 채워지며, 이후에도 수동으로 자유롭게 바꿀 수 있습니다. |
| Line Type + Program(s) Supported | 각 공정마다 공용라인(Shared Line)인지 전용라인(Dedicated Line)인지 기록합니다. 전용라인을 고르면 어떤 프로그램(들)의 라인인지 적을 수 있습니다. 마지막에 고른 값이 다음 새 공정의 기본값으로 자동으로 이어지므로 매번 다시 고를 필요가 없습니다. |
| 대량 업로드 | Excel 템플릿을 내려받아 채운 뒤 업로드하면 여러 공정을 한 번에 등록할 수 있습니다. |
| 이어서 작업 | 보관 기간 내의 로컬 또는 클라우드 백업(둘 중 더 최신 것) 중에서 골라 복구하면, 중단했던 지점부터 그대로 이어서 작업할 수 있습니다. |
| 모바일/PC 내보내기 | 이메일용으로 텍스트 요약(모바일에 적합) 또는 HTML 표(PC에 적합)를 복사하거나, 클릭 한 번으로 Outlook 초안을 자동 작성할 수 있습니다. |
| CSV 내보내기 | 언제든 전체 평가 결과를 CSV 파일로 내려받을 수 있습니다. |

---

## 🧭 사용 방법

### Step 0 — 글자 크기 조절 (선택)

앱 최상단의 **🔠 Text Size** 컨트롤(`−` / `A` / `+`)로 5단계 중 원하는 크기를 선택할 수 있습니다. 가운데 "A"는 현재 단계(예: `3/5`)를 실제 크기로 보여주므로 바로 효과를 확인할 수 있으며, 선택한 크기는 세션 내내 유지됩니다.

### Step 1 — 공급사 및 평가자 정보

![Step 1 화면: 글자 크기 조절 컨트롤과, Supplier Name/Evaluator Name 입력칸 위에 있는 이전 세션 복구용 드롭다운](screenshots/01_step1_start.png)

1. 최근 14일 이내의 백업(로컬 또는 클라우드 중 더 최신인 것)이 있으면 **"Restore Selected Session"**으로 이어서 진행할 수 있는 옵션이 나타납니다 — 세션이 중단됐을 때 타이핑 중이던 내용까지 포함해서 복구됩니다.
2. **Supplier Name**과 **Evaluator Name**을 입력합니다(둘 다 필수).

   ![Supplier Name과 Evaluator Name을 입력해 Go Evaluation을 누를 준비가 된 화면](screenshots/02_step1_filled.png)

3. **Go Evaluation**을 눌러 시작합니다. 둘 중 하나라도 비어 있으면 *"🚨 Please enter both Supplier Name and Evaluator Name."* 메시지가 표시됩니다.

평가가 시작되면 클라우드 연결 상태를 알려주는 안내 문구가 표시됩니다.
- **☁️ Cloud sync: connected** — 로컬과 클라우드 양쪽에 정상적으로 백업되고 있습니다.
- **📴 No internet connection** — 인터넷이 끊긴 상태이며, 데이터는 로컬에는 계속 저장되고 있고, 다시 연결되면 자동으로 클라우드와 동기화됩니다.

### Step 2 — (선택) Excel로 대량 업로드

**📂 Bulk Upload via Excel**을 펼쳐서 여러 공정을 한 번에 등록할 수 있습니다.

![Bulk Upload via Excel을 펼친 화면: Download Excel Template 버튼과 파일 업로드 박스](screenshots/03_step2_bulk_upload.png)

1. **📥 Download Excel Template**을 클릭합니다 — `Process Name / Description / Type / Score / Remark` 컬럼의 예시 행이 포함되어 있습니다.
2. 내용을 채운 뒤 **Upload filled Excel template**으로 업로드합니다.
3. **🚀 Upload & Apply Data**를 클릭합니다. `Description`, `Type`, `Score`는 필수 컬럼이며(`Type`은 `MH`/`OP`/`WIP` 중 하나), Type이나 Score가 유효하지 않은 행은 경고와 함께 건너뛰고 나머지 행은 정상적으로 반영됩니다.

   > 참고: 대량 업로드로 등록한 행에는 아직 Line Type / Program(s) Supported가 함께 들어가지 않습니다. 필요하면 아래 Step 3처럼 해당 항목으로 이동해 직접 입력한 것과 동일하게 나중에 채워 넣으면 됩니다.

### Step 3 — 공정별 입력

먼저 **Description Preset** — 입력 박스 위에 있는 22개의 프리셋 버튼 중 하나를 탭하면 아래 Description 입력칸 뒤에 해당 공정명이 이어붙습니다(여러 번 연속으로 탭할 수 있습니다 — 예: *Unloading*을 탭한 뒤 *Storaging*을 탭하면 `"Unloading, Storaging"`이 됩니다). 프리셋을 탭하면 해당 공정에 맞는 **Type**(MH/OP/WIP)도 함께 채워지며, *가장 마지막에 탭한* 프리셋 기준으로 갱신됩니다. 이후에도 Type은 수동으로 자유롭게 바꿀 수 있습니다.

![Description Preset 버튼들과, 그 아래 비어있는 입력 박스: Process Name, Line Type, Description, Type, Score, Remark, Save New Process](screenshots/04_step3_presets.png)

그 다음, 테두리 박스 안에서 아래 항목을 채웁니다.

1. **Process Name** (선택) — 공정/설비를 나타내는 자유 텍스트 라벨입니다.
2. **Line Type** (필수) — **Shared Line**(공용라인) 또는 **Dedicated Line**(전용라인) 중 선택합니다.

   ![Shared Line을 선택하고, 프리셋으로 채운 Description과 Type/Score까지 고른 화면](screenshots/05_step3_shared_line.png)

   **Dedicated Line**을 선택하면 바로 아래에 **Program(s) Supported** 입력칸이 나타나 어떤 프로그램(들)의 전용라인인지 적을 수 있습니다(선택 입력).

   ![Dedicated Line을 선택해 그 아래 Program(s) Supported 텍스트 입력칸이 나타난 화면](screenshots/06_step3_dedicated_line.png)

   여기서 고른 값(공용/전용 여부, 그리고 입력한 프로그램명)은 *다음* 새 공정을 추가할 때 기본값으로 자동으로 이어지므로 매번 다시 고를 필요가 없습니다 — 물론 실제로 값이 다르면 언제든 바꿀 수 있습니다.
3. **Description** (필수) — 직접 입력하거나 프리셋으로 채워진 내용을 자유롭게 편집할 수 있으며, 입력칸 옆의 작은 **🗑️** 버튼으로 이 내용만 지울 수 있습니다(Process Name/Line Type/Type/Score/Remark는 영향받지 않습니다).
4. **Type** (필수) — `MH`(자재 취급) / `OP`(생산/공정) / `WIP`(공정 중 재공); 마지막으로 탭한 프리셋에 따라 자동으로 채워지지만 자유롭게 변경 가능합니다.
5. **Score (1~5)** (필수) — 해당 공정의 PAMI 점수입니다.
6. **Remark** (선택) — 추가로 남길 비고입니다.
7. **Save New Process**(기존 항목을 수정 중이면 **Update Process**)를 클릭해 저장합니다.

작성 중인 내용을 취소하려면 **🚫 Cancel**을, 저장된 공정을 삭제하려면 **🗑️ Delete**를 사용합니다(삭제 전에 **✔️ Yes, Delete** / **❌ Cancel** 확인 단계가 나타납니다).

### Step 4 — 평가 요약 및 내보내기

공정이 하나 이상 저장되면 입력 박스 아래에 **📊 Evaluation Summary**가 나타납니다.

- **Total Processes**와 **Total OAMI Average**(5.0 만점) 지표.
- **📱 1. Mobile (Text)** 탭 — **📋 Copy Text for Outlook**으로 복사할 수 있는 텍스트 요약(수동 붙여넣기도 가능).

  ![Mobile 탭에 표시된 텍스트 요약: Program(s) Supported 컬럼에 "Shared" 또는 입력한 프로그램명이 나타남](screenshots/07_step4_summary_mobile.png)

- **🖥️ 2. PC (Table)** 탭 — 이메일에 표 형태로 붙여넣기 위한 **📋 Copy Table for Outlook** 기능이 포함된 HTML 표. 두 내보내기 화면 모두 Line Type과 Program(s) Supported를 하나의 **Program(s) Supported** 컬럼으로 합쳐서 보여줍니다 — 공용라인이면 **"Shared"**, 전용라인이면 입력한 프로그램명이 그대로 나타나서, 엑셀의 한 컬럼에 그대로 옮겨 붙일 수 있습니다.

  ![PC 탭에 동일한 데이터가 정리된 표로 표시된 화면](screenshots/08_step4_summary_pc.png)

- **📨 Open Outlook Mail App** — 모바일 텍스트 요약이 본문에 자동으로 채워진 새 메일 초안을 엽니다.
- **📥 Download CSV Backup** — 전체 평가 결과를 CSV 파일로 내려받습니다. 기본값으로 체크되어 있는 체크박스를 통해 다운로드 후 임시 시스템 백업 파일을 함께 삭제할 수도 있습니다 — **CSV 파일만이 유일한 영구 보관본**이며, 시스템 백업은 임시 저장분으로 언제든 삭제될 수 있습니다.
- **🚨 Clear All Data (Start New)** — 확인 절차를 거친 뒤 앱을 초기화하여 새로운 평가를 시작합니다. 이때 현재 공급사의 임시 백업도 함께 제거됩니다.

  ![CSV 다운로드 버튼, 백업 삭제 체크박스, Clear All Data 버튼이 있는 화면](screenshots/09_step4_csv_download.png)

---

## 💾 백업 및 데이터 정책

| | 로컬 백업 | Google Sheets 백업 | CSV 다운로드 |
|---|---|---|---|
| 저장 시점 | 변경할 때마다 자동(타이핑 중인 draft 포함) | 온라인 상태일 때 자동(최선 노력) | 필요할 때 수동 |
| 보관 기간 | 임시 — 보관 기간 내 유지, 삭제 가능 | 임시 — 보관 기간 내 유지, 삭제 가능 | **영구** — 장기적으로 신뢰할 수 있는 유일한 보관본 |
| 인터넷 필요 여부 | 불필요 | 필요 | 불필요 |

이전 세션을 복구할 때(Step 1)는 로컬과 클라우드 백업 중 더 최근에 업데이트된 쪽을 항상 사용하므로, 어느 쪽이 마지막으로 온라인 상태였는지와 관계없이 진행 상황을 잃지 않습니다.

---

## 🏷️ Type 정의

| Type | 의미 |
|---|---|
| `MH` | Material Handling(자재 취급) — 자재를 이동/보관/취급하는 공정 (예: Unloading, Moving, Storaging, Feeding, Loading) |
| `OP` | Operation/Process(생산/공정) — 부가가치를 더하는 제조 공정 (예: Molding, Stamping, Welding, 도장, Inspection, Packaging) |
| `WIP` | Work In Process(공정 중 재공) — 공정 중간에 부품을 취급하는 단계 (예: Remove, Conveyor) |

## 🏭 Line Type 정의

| Line Type | 의미 |
|---|---|
| Shared Line (공용라인) | 여러 프로그램/제품이 함께 쓰는 라인 — 별도로 적을 프로그램명이 없습니다. |
| Dedicated Line (전용라인) | 특정 프로그램(들) 전용 라인 — **Program(s) Supported**에 어떤 프로그램인지 적습니다. |

---

## ❓ 자주 묻는 질문

**Q: 데이터 입력 중에 인터넷이 끊기면 어떻게 되나요?**
A: 데이터는 손실되지 않습니다. 앱은 평소처럼 로컬 백업에 계속 저장되며 "📴 No internet connection" 안내가 표시되고, 다시 연결되면 자동으로 Google Sheets 동기화를 재개합니다.

**Q: 한동안 타이핑을 멈췄더니 화면이 초기화된 것 같아요.**
A: 새 공정을 입력하던 중이었다면, 그 내용은 입력하는 동안 계속 로컬 draft로 자동 저장됩니다(Save 버튼을 누르기 전에도). **Step 1 → Restore Selected Session**에서 가장 최근 백업을 골라 복구하면 중단했던 지점부터 그대로 이어서 작성할 수 있습니다.

**Q: 앱을 사용하려면 Google Sheets 설정이 반드시 필요한가요?**
A: 아닙니다. 클라우드 백업은 선택 사항이며, 설정하지 않아도 로컬 백업만으로 앱이 정상적으로 동작합니다.

**Q: CSV를 다운로드했는데 시스템 백업이 사라졌나요?**
A: **"Delete system backup file after download"** 체크박스가 체크된 상태로 다운로드한 경우에만 삭제됩니다(기본값은 체크됨). 어느 경우든 다운로드한 CSV 파일이 이후의 영구 기록이 됩니다.

**Q: 저장한 공정을 나중에 수정할 수 있나요?**
A: 네 — 해당 항목으로 이동해 항목을 수정한 뒤 **Update Process**를 클릭하면 됩니다. 삭제하려면 **🗑️ Delete**를 사용하세요.

**Q: 내보내기 결과에는 왜 Line Type과 Program(s) Supported가 따로 안 나오고 "Program(s) Supported" 한 컬럼만 나오나요?**
A: 엑셀의 한 컬럼에 그대로 옮겨 붙일 수 있도록 하기 위해서입니다 — 공용라인이면 **"Shared"**, 전용라인이면 입력한 프로그램명이 나타납니다. Step 3의 입력 화면에서는 Line Type과 Program(s) Supported를 여전히 따로 입력하며, 내보내기 요약에서만 하나로 합쳐집니다.

---

## 🔒 보안 관련 안내

- 사이트 화면에는 자격 증명이나 설정 관련 정보가 전혀 표시되지 않으며, 오직 본인이 입력한 평가 데이터만 보입니다.
- 로컬/클라우드 백업은 세션을 이어서 진행하기 위한 임시 작업본이지 영구 보관용이 아닙니다(위 표 참고). 영구적으로 보관하고 싶은 결과는 CSV로 다운로드해두세요.
- CSV 파일은 다운로드를 누르는 시점에 즉석에서 생성되며, 본인이 내려받은 파일 외에는 앱 어디에도 별도로 저장되지 않습니다.

---

## 📄 라이선스

MIT License.