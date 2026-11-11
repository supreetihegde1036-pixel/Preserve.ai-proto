# PRESERVE AI — Lightweight Guide Demonstration

## Purpose
This is a lightweight, shareable demonstration of the proposed PRESERVE AI workflow for assessment of indirect restorations.

## What it does
- Accepts conventional 2D dental radiographs (PNG/JPG).
- Accepts 3D intraoral scan meshes (STL/PLY/OBJ).
- Previews uploaded images and, where supported, the 3D mesh.
- Links records using de-identified case code, FDI tooth number and examination date.
- Records manual observations from the radiograph and IOS.
- Performs basic mesh-file geometry/integrity checks.
- Produces and saves a structured case report locally.

## What it does NOT do
- This lightweight build does not contain or run a trained diagnostic AI model.
- It does not automatically detect recurrent caries, defective margins, cracks or restoration failure.
- IOS mesh checks are technical file checks, not clinical interpretation.
- It does not establish pulp vitality or overall biological tooth health.
- It does not perform exact 2D-to-3D geometric registration or validated multimodal diagnostic fusion.
- It does not provide autonomous diagnosis or treatment recommendations.

## Run on Windows
1. Install 64-bit Python (Python 3.11 or 3.12 recommended).
2. Extract this ZIP.
3. Open the extracted folder.
4. Click the File Explorer address bar, type `cmd`, and press Enter.
5. Run:
   `python -m venv .venv`
6. Activate:
   `.venv\\Scripts\\activate`
7. Install the lightweight dependencies:
   `python -m pip install -r requirements.txt`
8. Launch:
   `streamlit run app.py`
9. Open the local URL shown in Command Prompt (usually http://localhost:8501).

## Privacy and research use
Use only synthetic or appropriately consented and de-identified records. Do not upload identifiable patient data. Obtain institutional approval and permissions as applicable. This is a research demonstration and must not be used for clinical decision-making.

## Proposed next development
1. Identify and assess suitable public dental datasets.
2. Evaluate a pretrained radiograph model on an appropriate held-out dataset.
3. Develop an IOS surface-analysis module.
4. Associate independently evaluated outputs at tooth level.
5. Obtain expert review and clinical validation before making diagnostic claims.
