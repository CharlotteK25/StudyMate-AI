"""Upload Notes - dropzone + recent uploads table."""

import re
import zipfile
from xml.etree import ElementTree

import streamlit as st

from services import firebase_service as fb
from services import gemini_service as gem
from utils.state import new_id, today_str
from utils.theme import flat, icon, pill, section_title, card, PRIMARY_DARK

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
try:
    import docx
except ImportError:
    docx = None

FORMAT_COLORS = {
    "PDF":  ("#fef2f2", "#dc2626"),
    "DOCX": ("#eff6ff", "#2563eb"),
    "TXT":  ("#f0fdf4", "#16a34a"),
    "PPTX": ("#fff7ed", "#ea580c"),
}

DROPZONE_CSS = """
<style>
.st-key-dropzone {
    background: #ffffff; border: 2px dashed #dfe4e2; border-radius: 18px;
    padding: 38px 20px 30px 20px; text-align: center; margin-bottom: 26px;
}
/* Fold Streamlit's own uploader chrome into our dashed box */
.st-key-dropzone [data-testid="stFileUploaderDropzone"] {
    background: transparent !important; border: none !important;
    min-height: auto !important; padding: 0 !important; justify-content: center !important;
}
.st-key-dropzone [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
.st-key-dropzone [data-testid="stFileUploaderDropzone"] button {
    background: #f0fdf4 !important; color: #15803d !important;
    border: 1px solid #a7f3c8 !important; border-radius: 10px !important;
    font-weight: 600 !important; padding: 10px 26px !important; box-shadow: none !important;
}
.st-key-dropzone [data-testid="stFileUploaderDropzone"] button:hover { background: #dcfce7 !important; }
/* text-align on the container does not reach these - stMarkdown blocks
   are separate flex children, so centre them explicitly */
.st-key-dropzone .stMarkdown { text-align: center !important; width: 100%; }
.sm-drop-title { font-size: 15px !important; font-weight: 600 !important; color: #111827;
                 margin: 0 !important; text-align: center !important; }
.sm-drop-sub   { font-size: 13.5px !important; color: #9ca3af;
                 margin: 6px 0 18px 0 !important; text-align: center !important; }
.st-key-dropzone [data-testid="stFileUploaderDropzone"] section,
.st-key-dropzone [data-testid="stFileUploader"] { width: 100%; }
</style>
"""


def _pptx_text(f) -> str:
    # a pptx is a zip - slide text lives in ppt/slides/slideN.xml as <a:t> tags
    tag = "{http://schemas.openxmlformats.org/drawingml/2006/main}t"
    slides_out = []
    with zipfile.ZipFile(f) as z:
        slides = [n for n in z.namelist()
                  if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
        # sort numerically, otherwise slide10 comes before slide2
        slides.sort(key=lambda n: int(re.search(r"slide(\d+)\.xml", n).group(1)))
        for name in slides:
            root = ElementTree.fromstring(z.read(name))
            texts = [t.text for t in root.iter(tag) if t.text and t.text.strip()]
            if texts:
                slides_out.append("\n".join(texts))
    return "\n\n".join(slides_out)


def _extract_text(f) -> str:
    name = f.name.lower()
    try:
        if name.endswith(".txt"):
            return f.read().decode("utf-8", errors="ignore")
        if name.endswith(".pdf") and PyPDF2:
            return "\n".join((p.extract_text() or "") for p in PyPDF2.PdfReader(f).pages)
        if name.endswith(".docx") and docx:
            return "\n".join(p.text for p in docx.Document(f).paragraphs)
        if name.endswith(".pptx"):
            return _pptx_text(f)
    except Exception:
        return ""
    return ""


def render_notes():
    uid = st.session_state.user["uid"]
    st.markdown(DROPZONE_CSS, unsafe_allow_html=True)

    st.markdown('<p class="sm-title">Upload Notes</p>', unsafe_allow_html=True)
    st.markdown('<p class="sm-subtitle">Upload your study files and generate AI-powered '
                'summaries instantly</p>', unsafe_allow_html=True)
    st.write("")

    with st.container(key="dropzone"):
        st.markdown(flat(f'<div class="sm-drop-icon">{icon("upload", PRIMARY_DARK, 26)}</div>'),
                    unsafe_allow_html=True)
        st.markdown('<p class="sm-drop-title">Drag-and-drop or select your notes</p>',
                    unsafe_allow_html=True)
        st.markdown('<p class="sm-drop-sub">Supports PDF, DOCX, TXT, PPTX &middot; '
                    'Max 50 MB per file</p>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload", type=["pdf", "docx", "txt", "pptx"],
            accept_multiple_files=True, key="notes_uploader", label_visibility="collapsed",
        )

    if uploaded:
        existing = {n["name"] for n in fb.get_notes(uid)}
        added = 0
        for f in uploaded:
            base = f.name.rsplit(".", 1)[0]
            if base in existing:
                continue
            ext = f.name.rsplit(".", 1)[-1].upper() if "." in f.name else "TXT"
            kb = f.size / 1024
            fb.save_note(uid, {
                "id": new_id(), "name": base,
                "format": ext if ext in FORMAT_COLORS else "TXT",
                "size": f"{kb/1024:.1f} MB" if kb >= 1024 else f"{kb:.0f} KB",
                "date": today_str(), "status": "ready",
                "text": _extract_text(f), "summary": "", "keywords": [],
            })
            added += 1
        if added:
            st.rerun()

    notes = fb.get_notes(uid)
    done = len([n for n in notes if n.get("status") == "done"])

    with card("uploads"):
        section_title("Recent Uploads", f"{len(notes)} files",
                      right_html=pill(f"{done} summarised"))

        if not notes:
            st.markdown('<p style="color:#9ca3af;font-size:14px;padding:26px 0;text-align:center;">'
                        'No files yet. Drop one above to get started.</p>', unsafe_allow_html=True)
            return

        st.markdown(flat('<div class="sm-thead">'
                         '<div style="flex:3.4;">File name</div>'
                         '<div style="flex:1;">Format</div>'
                         '<div style="flex:1.3;">Uploaded</div>'
                         '<div style="flex:1.7;">Action</div></div>'), unsafe_allow_html=True)

        with st.container(key="notes_table"):
            for note in sorted(notes, key=lambda n: n.get("date", ""), reverse=True):
                bg, fg = FORMAT_COLORS.get(note["format"], ("#f3f4f6", "#374151"))
                c = st.columns([0.5, 2.9, 1, 1.3, 1.7, 0.4], vertical_alignment="center")

                c[0].markdown(flat(f'<div class="sm-file-icon" style="background:{bg};">'
                                   f'{icon("file", fg, 16)}</div>'), unsafe_allow_html=True)
                c[1].markdown(flat(f'<p class="sm-file-name">{note["name"]}</p>'
                                   f'<p class="sm-file-size">{note["size"]}</p>'),
                              unsafe_allow_html=True)
                c[2].markdown(pill(note["format"], bg, fg), unsafe_allow_html=True)
                c[3].markdown(f'<p class="sm-file-size">{note["date"]}</p>', unsafe_allow_html=True)

                with c[4]:
                    if note.get("status") == "done":
                        with st.container(key=f"btn_green_view_{note['id']}"):
                            if st.button("Summary Ready", key=f"view_{note['id']}",
                                         width="stretch", icon=":material/check_circle:"):
                                st.session_state[f"show_{note['id']}"] = \
                                    not st.session_state.get(f"show_{note['id']}", False)
                                st.rerun()
                    elif not note.get("text"):
                        st.markdown('<p class="sm-file-size">No text found</p>', unsafe_allow_html=True)
                    else:
                        with st.container(key=f"btn_dark_sum_{note['id']}"):
                            if st.button("Generate Summary", key=f"sum_{note['id']}",
                                         width="stretch", icon=":material/auto_awesome:"):
                                with st.spinner("Generating summary..."):
                                    r = gem.generate_summary(note["text"])
                                fb.update_note(uid, note["id"], {
                                    "status": "done", "summary": r.get("summary", ""),
                                    "keywords": r.get("keywords", []),
                                })
                                st.rerun()

                with c[5]:
                    if st.button("", key=f"del_{note['id']}", icon=":material/delete:",
                                 help="Delete this file"):
                        fb.delete_note(uid, note["id"])
                        st.rerun()

                if st.session_state.get(f"show_{note['id']}"):
                    st.markdown(f'<div style="padding:6px 0 14px 0;font-size:13.5px;color:#4b5563;'
                                f'line-height:1.65;">{note.get("summary","No summary.")}</div>',
                                unsafe_allow_html=True)
                    if note.get("keywords"):
                        st.markdown(" ".join(pill(k, "#f1f5f9", "#475569")
                                             for k in note["keywords"][:8]), unsafe_allow_html=True)
