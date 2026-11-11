# PRESERVE AI — Guide Review Summary

**Project title:** PRESERVE AI: An AI-Assisted Multimodal Framework Integrating Conventional 2D Dental Radiographs and 3D Intraoral Scans for the Assessment of Indirect Restorations.

**Current deliverable:** Lightweight working interface demonstrating case intake, 2D radiograph upload, 3D intraoral scan upload, tooth-level metadata association, manual observation capture, basic 3D mesh technical checks and structured report generation.

**Research concept:** The proposed system will investigate whether information from conventional radiographs and IOS surface scans can be brought together at tooth level to support a more structured assessment of indirect restorations.

**Current implementation status:** This build is a workflow demonstrator. It does not contain a trained diagnostic AI model. The 3D module performs file geometry/integrity checks only. No validated multimodal diagnostic fusion is implemented.

**Scientific boundaries:** IOS cannot reveal decay beneath an opaque crown. Conventional 2D radiographs are projection images and may be limited by overlap, angulation and image quality. Imaging alone cannot establish pulp vitality or complete biological tooth health. All findings require qualified clinical interpretation.

**Proposed next steps:** Evaluate suitable public datasets and pretrained models; develop radiograph and IOS modules independently; associate outputs using tooth number and examination date; conduct expert review and validation before clinical claims.

**Research ethics:** Use only synthetic or properly consented and de-identified records, with institutional approval and data permissions as applicable.
