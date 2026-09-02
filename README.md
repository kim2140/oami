> 🇰🇷 [한국어 README 보기](README_KO.md)

# 📝 Supplier OAMI Evaluation App

A web app for auditors to record a supplier's per-process **OAMI** (process-quality) evaluations on-site — Type (MH / P / WIP) + PAMI score (1–5) + description/remark per process — with automatic **local + cloud** dual backup so no work is lost if your device or connection drops.

*(Documentation last verified against app version **2.21.0**.)*

---

## 🔗 Open the App

No installation needed — just open it in your browser:

**👉 https://oamigmscore.streamlit.app/**

It works on both PC and mobile browsers. Everything below describes how to use it once it's open.

---

## ✨ Features

| Feature | Description |
|---|---|
| Dual backup | Every change is saved automatically to a local backup, and mirrored to the cloud in the background whenever you're online. |
| Offline-safe | If the connection drops, the app keeps working and saving locally; it re-syncs to the cloud automatically once you're back online — no data is lost either way. |
| Adjustable text size | A 5-level −/+ zoom control at the top of the app makes all text bigger or smaller; the setting is remembered for the session (via the page URL) so a refresh doesn't reset it. |
| Tap-to-build description | 26 preset buttons, grouped by manufacturing flow (material handling → machining → assembly/welding → paint → finishing → quality → packaging/shipping), each tap appends its text to the Description field and can be combined with free typing. |
| Auto Type suggestion | Selecting a Description preset also fills in the matching Type (MH/P/WIP) for you — you can still change it manually afterward. |
| Bulk upload | Register many processes at once via an Excel template (download, fill in, upload). |
| Resume in progress | Restore a session from its local or cloud backup (whichever is newer) within the retention window, to continue exactly where you left off. |
| Mobile & PC export | Copy a plain-text summary (mobile-friendly) or an HTML table (PC-friendly) for email, or auto-fill an Outlook draft with one click. |
| CSV export | Download the full evaluation as a CSV file at any time. |

---

## 🧭 How to Use

### Step 0 — Adjust Text Size (optional)

At the very top of the app, use the **🔠 Text Size** control (`−` / `A` / `+`) to pick from 5 font sizes. The center "A" shows the current step (e.g. `3/5`) at its actual size, so you can see the effect immediately. Your choice stays applied for the rest of the session.

### Step 1 — Supplier & Evaluator Info

1. If a backup from the past 14 days exists (locally or in the cloud, whichever is newer), a **"Restore Selected Session"** option appears so you can pick it up where you left off.
2. Enter **Supplier Name** and **Evaluator Name** (both required).
3. Click **Go Evaluation** to start. If either field is empty, you'll see: *"🚨 Please enter both Supplier Name and Evaluator Name."*

Once evaluation starts, a status caption tells you whether the cloud connection is active:
- **☁️ Cloud sync: connected** — your data is backed up locally and to the cloud.
- **📴 No internet connection** — your data is still being saved locally, and will sync to the cloud automatically once you're back online.

### Step 2 — (Optional) Bulk Upload via Excel

Open **📂 Bulk Upload via Excel** to register several processes at once:

1. Click **📥 Download Excel Template** — it includes sample rows with the columns `Process Name / Description / Type / Score / Remark`.
2. Fill it in and upload it with **Upload filled Excel template**.
3. Click **🚀 Upload & Apply Data**. `Description`, `Type`, and `Score` are required columns; rows with an invalid Type or Score are skipped with a warning, and the rest are still applied.

### Step 3 — Enter Each Process

First, **Description Preset** — tap any of the 26 preset buttons (above the input box) to append that step's name to the Description field below (you can tap several in a row — e.g. tap *Unloading* then *Storaging* to get `"Unloading, Storaging"`). Tapping a preset also sets **Type** to match that preset's usual category (MH/P/WIP); the *last* preset you tap wins, and you can still change Type manually afterward.

Then, inside the input box, fill in:

1. **Process Name** (optional) — a free-text label for the process/station.
2. **Description** (required) — free-text; you can type here directly, edit around what the presets inserted, or clear it entirely with the **🗑️ Clear Description** button (this only clears Description — Process Name, Type, Score, and Remark are untouched).
3. **Type** (required) — `MH` (Material Handling) / `P` (Production/Process) / `WIP` (Work In Process); pre-filled by the last preset tapped, but freely changeable.
4. **Score (1–5)** (required) — the PAMI score for this process.
5. **Remark** (optional) — any additional note.
6. Click **Save New Process** (or **Update Process** if you're editing an existing entry).

Use **🚫 Cancel** to discard an in-progress edit, or **🗑️ Delete** to remove a saved process (a confirmation step — **✔️ Yes, Delete** / **❌ Cancel** — appears before anything is removed).

### Step 4 — Evaluation Summary & Export

Once you have at least one process saved:

- **Total Processes** and **Total OAMI Average** (out of 5.0) are shown as metrics.
- **📱 1. Mobile (Text)** tab — a plain-text summary you can copy with **📋 Copy Text for Outlook**, or paste manually.
- **🖥️ 2. PC (Table)** tab — a formatted HTML table you can copy with **📋 Copy Table for Outlook** for pasting into an email as a table.
- **📨 Open Outlook Mail App** — opens a new mail draft with the mobile text summary pre-filled in the body.
- **📥 Download CSV Backup** — downloads the full record as a CSV file. A checkbox (checked by default) lets you also delete the temporary system backup file after downloading, since **the CSV file is the only permanent copy** — system backups are temporary and can be cleared at any time.
- **🚨 Clear All Data (Start New)** — resets the app to start a fresh evaluation (with a confirmation step first). This also removes the current supplier's temporary backup.

---

## 💾 Backup & Data Policy

| | Local backup | Google Sheets backup | CSV download |
|---|---|---|---|
| When it's saved | Automatically, after every change | Automatically, whenever online (best-effort) | Manually, on demand |
| Persistence | Temporary — kept for the retention window, can be cleared | Temporary — kept for the retention window, can be cleared | **Permanent** — this is the only copy you should rely on long-term |
| Requires internet | No | Yes | No |

Restoring a past session (Step 1) always uses whichever of the local or cloud backup is more recently updated, so you never lose progress no matter which one was last online.

---

## 🏷️ Type Definitions

| Type | Meaning |
|---|---|
| `MH` | Material Handling — moving, storing, or handling material (e.g. Unloading, Storaging, Feeding, Loading) |
| `P` | Production/Process — a value-adding manufacturing step (e.g. Molding, Stamping, Welding, Painting, Inspection, Packaging) |
| `WIP` | Work In Process — intermediate handling of parts mid-process (e.g. Remove, Conveyor) |

---

## ❓ FAQ

**Q: What happens if I lose internet connection while entering data?**
A: Nothing is lost. The app keeps saving to the local backup as usual and shows a "📴 No internet connection" notice; once you're back online, it resumes syncing to Google Sheets automatically.

**Q: Do I need Google Sheets configured to use the app?**
A: No. Cloud backup is optional — without it configured, the app runs fully on local backups only.

**Q: I downloaded the CSV — is the system backup gone now?**
A: Only if you left the **"Delete system backup file after download"** checkbox checked (it's checked by default). Either way, the CSV file you downloaded is the permanent record going forward.

**Q: Can I edit a process after saving it?**
A: Yes — navigate to it and edit the fields, then click **Update Process**. Use **🗑️ Delete** to remove it instead.

---

## 🔒 Security Notes

- The site never shows any credentials or configuration details in the UI — you only ever see your own evaluation data.
- Backups (local + cloud) are temporary working copies for resuming a session, not a permanent archive — see the table above. Download the CSV whenever you want a permanent, personal copy of your results.
- The CSV file is generated on the spot when you click download and isn't stored anywhere else by the app — it only exists in your own download.

---

## 📄 License

MIT License.