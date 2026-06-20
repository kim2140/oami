> 🇰🇷 [한국어 README 보기](README_KO.md)

# 📝 Supplier OAMI Evaluation App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://oamigmscore.streamlit.app/)

A field evaluation tool for supplier audits based on the OAMI (Operation Assessment & Management Index).  
Supports both mobile and PC, with automatic cloud backup and Outlook email export.

---

## 🚀 Launch App

**https://oamigmscore.streamlit.app/**

---

## 📋 Key Features

| Feature | Description |
|---|---|
| **Auto Cloud Backup** | Saves to Google Sheets instantly as you input |
| **Session Restore** | Resume previous evaluation sessions |
| **Excel Bulk Upload** | Register multiple processes at once |
| **Circular Navigation** | Move freely between entries with Prev/Next |
| **Mobile Text Copy** | One-tap copy for Outlook mobile app |
| **PC Table Copy** | Copy as formatted HTML table |
| **CSV Download** | Permanent local file export |

---

## 🛠️ How to Use

### Step 1 — Enter Supplier & Evaluator Info

1. Open the app and locate **📌 Step 1: Supplier & Evaluator Info**
2. Enter **Supplier Name** (required)
3. Enter **Evaluator Name** (required)
4. Click **Go Evaluation** → proceed to Step 2

> ⚠️ Both fields are required to continue.

---

### Step 2 — Restore Previous Session (Optional)

If you have previously saved work, a backup list will appear automatically.

1. Select an entry from the **Restore previous session** dropdown
   - `[☁️ Cloud]` — Google Sheets cloud backup
   - `[🖥️ Local]` — Server local backup (last 14 days)
2. Click **Restore Selected Session** → load previous data

> 💡 After restoring, you can continue from where you left off.

---

### Step 3 — Enter Processes (Individual)

#### 3-1. Add a New Entry

| Field | Required | Description |
|---|---|---|
| **Process Name** | Optional | Process label (defaults to N/A if blank) |
| **Description** | **Required** | Detailed description of the process |
| **Type** | **Required** | Select `MH` / `P` / `WIP` |
| **Score (1~5)** | **Required** | OAMI score (1 = lowest, 5 = highest) |
| **Remark** | Optional | Additional notes |

1. Fill in the form and click **Save New Process**
2. A toast message confirms the save
3. The form resets and waits for the next entry

#### 3-2. Edit an Existing Entry

1. Navigate to the target entry using **⬅️ Prev** / **Next ➡️**
2. The form auto-fills with existing values
3. Make changes and click **Update Process**

#### 3-3. Delete an Entry

1. Navigate to the entry you want to delete
2. Click **🗑️ Delete**
3. Confirm by clicking **✔️ Yes, Delete**

> ⚠️ Entry numbers (No.) are automatically reordered after deletion.

#### 3-4. Navigation Buttons

| Button | Action |
|---|---|
| **⬅️ Prev** | Go to previous entry (wraps to last from first) |
| **Next ➡️** | Go to next entry (wraps to first from last) |
| **➕ New** | Switch to new entry mode |
| **🚫 Cancel** | Cancel new entry and return to current list |

---

### Step 4 — Bulk Upload via Excel (Optional)

Use this when you need to register many processes at once.

1. Expand the **📂 Bulk Upload via Excel** section
2. Click **📥 Download Excel Template** and save the file
3. Fill in the template:

| Column | Required | Allowed Values |
|---|---|---|
| Process Name | Optional | Any text |
| Description | **Required** | Any text |
| Type | **Required** | `MH` / `P` / `WIP` |
| Score | **Required** | Integer `1` ~ `5` |
| Remark | Optional | Any text |

4. Upload the completed file under **Upload filled Excel template**
5. Click **🚀 Upload & Apply Data**

> ⚠️ Rows with invalid Type or Score values are skipped automatically. A warning message lists which rows were skipped.

---

### Step 5 — Review Results & Export

Once at least one process is saved, the **📊 Evaluation Summary** section appears.

#### Summary Metrics

| Metric | Description |
|---|---|
| **Total Processes** | Number of registered processes |
| **Total OAMI Average** | Overall average score (out of 5.0) |

#### 📱 Mobile — Copy as Text

1. Select the **📱 1. Mobile (Text)** tab
2. Click **📋 Copy Text for Outlook** → copied to clipboard
3. Open Outlook app → paste into email body
4. Or click **📨 Open Outlook Mail App** → subject and body auto-filled

#### 🖥️ PC — Copy as Table

1. Select the **🖥️ 2. PC (Table)** tab
2. Click **📋 Copy Table for Outlook** → HTML table copied
3. Paste into Outlook desktop app body

> ⚠️ The PC table does not support auto-fill in the Mail app. Paste manually.

#### 📥 Download CSV (Permanent Storage)

1. Check the **🗑️ Delete system backup file after download** checkbox
   - ✅ Checked (recommended): server backup deleted after download
   - ☐ Unchecked: server backup retained
2. Click **📥 Download CSV Backup**
3. File name format: `OAMI_{SupplierName}_{Date}.csv`

---

### Step 6 — Reset (Start New Evaluation)

1. Click **🚨 Clear All Data (Start New)**
2. Confirm by clicking **✔️ Yes, Clear Data**
3. All data and backups are deleted — returns to Step 1

> ⚠️ Download your CSV before resetting. This action cannot be undone.

---

## 💾 Backup Policy

| Type | Storage | Retention |
|---|---|---|
| Auto Backup | Google Sheets (Cloud) | Until manually deleted |
| Local Backup | Server temporary storage | **14 days** |
| CSV Download | User's device | Permanent |

> ⚠️ Local backups are **automatically deleted after 14 days**. Always download the CSV to keep your data permanently.

---

## 📎 Type Definitions

| Type | Meaning |
|---|---|
| **MH** | Man-Hour (labor-intensive operation) |
| **P** | Process (standard process step) |
| **WIP** | Work In Progress (ongoing operation) |

---

## ❓ FAQ

**Q. The app closed while I was entering data.**  
A. Reopen the app and enter the same Supplier/Evaluator in Step 1. Your previous session will appear in the backup list.

**Q. Some rows were not imported after Excel upload.**  
A. Check that Type values are MH/P/WIP and Score values are integers between 1 and 5. Invalid rows are skipped automatically.

**Q. I want to evaluate the same supplier again.**  
A. Download the CSV first, then click **Clear All Data** to reset and start a new session.

**Q. The table formatting breaks when I paste it into email.**  
A. Use the Outlook desktop app (not the web version) to preserve the HTML table format.

---

## 🔒 Security

- No sensitive credentials are stored within the app
- It is recommended to delete server backups after downloading the CSV
- Google Sheets backups are saved only to a dedicated service account sheet

---

## 📄 License

MIT License
