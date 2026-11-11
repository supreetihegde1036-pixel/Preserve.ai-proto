import streamlit as st
import sqlite3, json, uuid, hashlib
from pathlib import Path
from datetime import date, datetime
from io import BytesIO
import numpy as np
from PIL import Image

ROOT = Path(__file__).parent
DATA = ROOT / "preserve_data"
UPLOADS = DATA / "uploads"
UPLOADS.mkdir(parents=True, exist_ok=True)
DB = DATA / "cases.sqlite"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)
CARIES_MODEL = MODEL_DIR / "dental_caries_best.pt"

st.set_page_config(page_title="PRESERVE AI", page_icon="🦷", layout="wide")
DISCLAIMER = ("Research demonstration only — not a diagnostic device. This lightweight build does not run a trained AI model, "
              "detect caries automatically, see through crowns, establish tooth vitality, or prescribe treatment. "
              "A qualified dentist must interpret all findings with clinical examination and appropriate tests.")

with sqlite3.connect(DB) as con:
    con.execute("""CREATE TABLE IF NOT EXISTS cases (
      id TEXT PRIMARY KEY, created TEXT, case_code TEXT, tooth TEXT, restoration TEXT,
      exam_date TEXT, symptoms TEXT, xray_path TEXT, scan_path TEXT, report TEXT)""")

def inspect_mesh_geometry(file_bytes, filename):
    """Basic mesh-file integrity/geometry checks; deliberately not a trained AI."""
    import trimesh
    ext = Path(filename).suffix.lower().lstrip(".")
    mesh = trimesh.load(BytesIO(file_bytes), file_type=ext, force="mesh")
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    if mesh is None or len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("No usable triangular mesh was found.")
    return {
        "vertices": int(len(mesh.vertices)),
        "triangular_faces": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "surface_area": round(float(mesh.area), 2),
        "bounding_dimensions": [round(float(v), 2) for v in mesh.extents],
        "units": "Not inferred; depends on the source scanner/export settings"
    }


def save_upload(f, cid, tag):
    if not f: return None
    ext = Path(f.name).suffix.lower()
    p = UPLOADS / f"{cid}_{tag}{ext}"
    p.write_bytes(f.getbuffer())
    return str(p.relative_to(ROOT))

def preview_mesh(f):
    try:
        import trimesh, plotly.graph_objects as go
        mesh = trimesh.load(BytesIO(f.getvalue()), file_type=Path(f.name).suffix.lower()[1:], force="mesh")
        v, faces = np.asarray(mesh.vertices), np.asarray(mesh.faces)
        if len(faces) > 100000:
            faces = faces[np.linspace(0, len(faces)-1, 100000).astype(int)]
        fig = go.Figure(go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2],
                                  i=faces[:,0], j=faces[:,1], k=faces[:,2]))
        fig.update_layout(scene=dict(aspectmode="data"), height=450, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.caption("3D preview only — no automatic surface or margin analysis.")
    except Exception as e:
        st.info(f"Mesh preview unavailable for this file ({e}). The file can still be saved.")

st.title("🦷 PRESERVE AI")
st.subheader("Multimodal restorative assessment | Lightweight guide demonstration")
st.warning(DISCLAIMER)

with st.sidebar:
    st.header("Prototype status")
    st.success("Case intake • radiograph upload • IOS upload • tooth-level linking • structured report")
    st.info("Guide demonstration build: case intake, 2D/3D uploads, tooth-level association and structured reporting.")
    st.caption("No trained diagnostic AI model is bundled or running in this lightweight version. IOS checks are technical mesh checks only.")
    st.caption("Use de-identified case codes only. Do not upload names or identifiable patient records.")

new, saved, about = st.tabs(["➕ New case", "🗂 Saved cases", "ℹ️ About"])

with new:
    st.markdown("### 1. Case details")
    c1,c2,c3 = st.columns(3)
    with c1:
        code = st.text_input("De-identified case code", placeholder="PAI-001")
        tooth = st.selectbox("FDI tooth number", [str(i) for i in
            [11,12,13,14,15,16,17,18,21,22,23,24,25,26,27,28,
             31,32,33,34,35,36,37,38,41,42,43,44,45,46,47,48]])
    with c2:
        restoration = st.selectbox("Indirect restoration", ["Crown","Inlay","Onlay","Overlay","Other"])
        exam = st.date_input("Examination date", date.today())
    with c3:
        symptoms = st.text_area("Symptoms / concerns", placeholder="Optional, de-identified")

    st.markdown("### 2. Upload imaging")
    l,r = st.columns(2)
    with l:
        st.markdown("**Conventional 2D radiograph**")
        xray = st.file_uploader("Bitewing or periapical image", ["png","jpg","jpeg"], key="xray")
        if xray:
            st.image(Image.open(xray), caption="Radiograph preview", use_container_width=True)
    with r:
        st.markdown("**3D intraoral scan**")
        scan = st.file_uploader("IOS mesh file", ["stl","ply","obj"], key="scan")
        if scan:
            st.write(f"{scan.name} · {len(scan.getvalue())/1024:.1f} KB")
            preview_mesh(scan)
            with st.expander("3D scan technical checks (not AI diagnosis)"):
                try:
                    mesh_info = inspect_mesh_geometry(scan.getvalue(), scan.name)
                    st.json(mesh_info)
                    st.caption("These checks describe the mesh file only. They do not detect defective margins, cracks, recurrent caries or biological tooth health.")
                    st.session_state["ios_mesh_checks"] = mesh_info
                    st.session_state["ios_mesh_hash"] = hashlib.sha256(scan.getvalue()).hexdigest()
                except Exception as e:
                    st.warning(f"Could not inspect mesh geometry: {e}")

    st.markdown("### 3. AI module status")
    st.info(
        "This lightweight guide-demo version demonstrates the multimodal workflow and report structure. "
        "A trained radiograph model and a trained IOS diagnostic model are not installed or active. "
        "No automatic image diagnosis is performed."
    )
    st.caption(
        "Future integration: a separately evaluated radiograph model and an IOS surface-analysis model, "
        "with findings associated by case code, tooth number and examination date."
    )

    st.markdown("### 4. Enter observations")
    st.caption("Manual observations only. These are not AI detections.")
    a,b = st.columns(2)
    with a:
        st.markdown("**Radiograph observations**")
        rf = st.multiselect("Select if observed", [
            "Radiolucency adjacent to restoration margin — suspicious, not confirmed",
            "Possible recurrent caries appearance — requires clinical correlation",
            "Visible marginal discrepancy",
            "Periapical change requiring clinical correlation",
            "Image overlap/quality limits interpretation",
            "No obvious abnormality noted"
        ])
        rn = st.text_area("Radiograph notes")
    with b:
        st.markdown("**IOS surface observations**")
        sf = st.multiselect("Select if observed", [
            "Accessible margin irregularity",
            "Possible marginal gap/step on scanned surface",
            "Contour discrepancy",
            "Surface wear or roughness",
            "Visible restoration chip/fracture",
            "Incomplete margin capture / scan artefact",
            "No obvious surface abnormality noted"
        ])
        sn = st.text_area("IOS notes")
    cn = st.text_area("Clinical examination / other test notes",
                      placeholder="e.g. sensibility testing, percussion, bite test, periodontal findings…")

    if st.button("Generate and save case report", type="primary", use_container_width=True):
        if not code.strip():
            st.error("Enter a de-identified case code.")
        elif not xray and not scan:
            st.error("Upload at least one modality.")
        else:
            cid = str(uuid.uuid4())[:8].upper()
            xp, sp = save_upload(xray,cid,"radiograph"), save_upload(scan,cid,"ios")
            prompts = []
            if any("radiolucency" in x.lower() or "caries" in x.lower() for x in rf):
                prompts.append("Review the radiographic area and correlate with clinical examination; do not treat the radiographic appearance alone as confirmation.")
            if any(any(k in x.lower() for k in ["margin","contour","surface"]) for x in sf):
                prompts.append("Inspect the accessible restoration margin/contour clinically and determine whether the surface finding is significant.")
            if any(any(k in x.lower() for k in ["fracture","chip"]) for x in rf+sf):
                prompts.append("Assess restoration integrity and remaining tooth structure clinically.")
            if symptoms.strip():
                prompts.append("Correlate symptoms with history and appropriate clinical tests, including pulp sensibility testing where indicated.")
            if not prompts:
                prompts.append("Complete clinical examination and record any additional tests required before diagnosis.")
            integration = ("Both modalities have observations and are linked by case code, tooth number and date. "
                "This is metadata-level association, not geometric registration.") if rf and sf else (
                "Only one or neither modality has observations. Assessment is incomplete; add the other modality when available.")
            report = {
                "case_id":cid, "case_code":code.strip(), "tooth":tooth, "restoration":restoration,
                "exam_date":exam.isoformat(), "status":"Clinician review required",
                "radiograph_observations":rf, "radiograph_notes":rn or "Not recorded",
                "ios_observations":sf, "ios_notes":sn or "Not recorded",
                "symptoms":symptoms or "Not recorded", "clinical_notes":cn or "Not recorded",
                "tooth_level_integration":integration, "further_assessment_prompts":prompts,
                "radiograph_ai_findings": "No trained radiograph AI model is installed in this lightweight guide-demo build.",
                "ios_mesh_technical_checks": (st.session_state.get("ios_mesh_checks")
                    if scan and st.session_state.get("ios_mesh_hash") == hashlib.sha256(scan.getvalue()).hexdigest()
                    else "No mesh checks recorded"),
                "ai_status":"No trained diagnostic AI model is active in this lightweight guide-demo build. IOS output is limited to technical mesh checks. The report is a workflow demonstration, not a diagnosis.",
                "limitations":[
                    "IOS cannot see through opaque crowns or directly reveal hidden caries.",
                    "A 2D radiograph is a projection and may be affected by overlap, angulation and image quality.",
                    "Imaging alone cannot establish complete biological tooth health or pulp vitality.",
                    "No automated diagnosis, treatment recommendation or future-failure prediction is performed."
                ],
                "disclaimer":DISCLAIMER
            }
            with sqlite3.connect(DB) as con:
                con.execute("INSERT INTO cases VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (cid,datetime.now().isoformat(timespec="seconds"),code.strip(),tooth,restoration,
                     exam.isoformat(),symptoms,xp,sp,json.dumps(report)))
            st.session_state["report"] = report
            st.success(f"Saved case {cid} locally.")

    if "report" in st.session_state:
        rep = st.session_state["report"]
        st.markdown("---")
        st.markdown(f"## Case report — {rep['case_id']}")
        st.write(f"**{rep['case_code']}** · Tooth **{rep['tooth']}** · {rep['restoration']} · {rep['exam_date']}")
        st.info(rep["status"])
        st.markdown("**Radiograph observations**")
        st.write(rep["radiograph_observations"] or "None entered")
        st.markdown("**IOS observations**")
        st.write(rep["ios_observations"] or "None entered")
        st.markdown("**Radiograph AI findings**")
        st.write(rep.get("radiograph_ai_findings", "Not available"))
        st.markdown("**IOS technical checks**")
        st.write(rep.get("ios_mesh_technical_checks", "Not available"))
        st.markdown("**Tooth-level integration**")
        st.write(rep["tooth_level_integration"])
        st.markdown("**Further assessment prompts**")
        for p in rep["further_assessment_prompts"]: st.write("• " + p)
        st.error(rep["ai_status"])
        st.download_button("Download report (JSON)", json.dumps(rep,indent=2),
                           file_name=f"PRESERVE_AI_{rep['case_id']}.json", mime="application/json")

with saved:
    st.markdown("### Saved local cases")
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT id,created,case_code,tooth,restoration,exam_date FROM cases ORDER BY created DESC").fetchall()
    if not rows:
        st.info("No cases saved yet.")
    else:
        import pandas as pd
        st.dataframe(pd.DataFrame(rows,columns=["ID","Created","Case code","Tooth","Restoration","Exam date"]),
                     use_container_width=True,hide_index=True)
        choice = st.selectbox("View report", [x[0] for x in rows])
        with sqlite3.connect(DB) as con:
            data = con.execute("SELECT report FROM cases WHERE id=?",(choice,)).fetchone()
        if data: st.json(json.loads(data[0]))

with about:
    st.markdown("""
### What this version does
- Accepts conventional 2D radiographs (PNG/JPG) and IOS meshes (STL/PLY/OBJ).
- Previews the radiograph and, where possible, the 3D scan.
- Links files at tooth level using case code, FDI tooth number and date.
- Records clinician-entered observations and produces a structured report.
- Accepts and previews conventional 2D radiographs and 3D IOS mesh files.
- Associates the uploaded modalities using case code, FDI tooth number and examination date.
- Records clinician-entered observations and creates a structured case report.
- Performs basic IOS mesh file integrity/geometry checks; these are not diagnostic AI.
- Saves cases locally in SQLite.

### AI development status in this lightweight guide-demo
- No trained radiograph AI model is bundled or active.
- No trained IOS diagnostic AI model is bundled or active.
- No automated caries, gap, crack or restoration-failure detection is performed.
- No exact 2D-to-3D geometric registration is implemented.
- No autonomous diagnosis, treatment advice or future-risk prediction is performed.
- Current multimodal association is metadata-level only.

### Development roadmap
1. Test intake and pairing with synthetic or approved de-identified records.
2. Create clinician annotation rules and a reference standard.
3. Develop and validate radiograph analysis separately.
4. Develop IOS surface analysis separately.
5. Fuse independently evaluated outputs with uncertainty reporting.
6. Validate prospectively before any clinical use.

**Privacy:** Data stays on the computer running this app. Do not host publicly or use identifiable patient data. Obtain institutional approval and consent/permissions as applicable.
""")

st.divider()
st.caption("PRESERVE AI · Early research prototype · Not for autonomous clinical diagnosis or treatment")
