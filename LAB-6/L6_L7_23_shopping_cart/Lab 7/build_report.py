"""Build transparent browser screenshots of recorded output, then the PDF."""
import html
import json
import re
import subprocess
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EVIDENCE = HERE / "evidence"
CHROME = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")


def screenshot(stem, title, excerpt=None):
    data = json.loads((EVIDENCE / (stem + ".json")).read_text(encoding="utf-8"))
    output = data["stdout"] + data["stderr"]
    if excerpt is not None:
        output = excerpt(output)
    inputs = data["stdin"]
    command = " ".join(data["command"])
    body = f"""<!doctype html><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>body{{margin:32px;background:#f4f6fa;color:#15243a;font:18px Arial}}
h1{{font-size:28px;margin:0 0 12px}} .meta{{font-size:16px;margin-bottom:15px}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:white;border:1px solid #bbc6d4;
border-radius:8px;padding:22px;font:16px/1.45 Consolas,monospace;margin:12px 0}}
small{{font-size:15px;color:#41536c}}</style>
<h1>{html.escape(title)}</h1><div class="meta">Recorded subprocess output | exit code: {data['exit_code']}</div>
<small>Command</small><pre>{html.escape(command)}</pre>
{('<small>Supplied standard input (one value per line)</small><pre>' + html.escape(inputs) + '</pre>') if inputs is not None else ''}
<small>{'Output excerpts; full unedited log supplied separately' if excerpt else 'Captured stdout and stderr'}</small>
<pre>{html.escape(output)}</pre>"""
    page = EVIDENCE / (stem + ".html")
    page.write_text(body, encoding="utf-8")
    png = EVIDENCE / (stem + ".png")
    run = subprocess.run([str(CHROME), "--headless", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", "--hide-scrollbars", "--allow-file-access-from-files",
        "--user-data-dir=" + str(ROOT / "tmp" / "lab7-chrome"),
        "--window-size=1280,1100", "--screenshot=" + str(png), page.as_uri()],
        capture_output=True, timeout=45)
    if not png.exists():
        raise RuntimeError(run.stderr.decode(errors="replace"))
    return png


def failure_excerpt(output):
    lines = output.splitlines()
    picks = [lines[0], ""]
    # Copy genuine minimized examples and errors verbatim from the saved log.
    for name in ("cart_total", "promo_percent", "delivery_zone"):
        picks.append("Function: " + name)
        section = output.split("test_" + name + "_no_crash", 1)[1]
        if name != "delivery_zone":
            next_name = "promo_percent" if name == "cart_total" else "delivery_zone"
            section = section.split("test_" + next_name + "_no_crash", 1)[0]
        section_lines = section.splitlines()
        for index, line in enumerate(section_lines):
            if "s=None" in line:
                picks.extend(section_lines[max(0, index - 2):index + 2])
                break
        picks.append("")
    picks.extend(lines[-5:])
    return "\n".join(picks)


def passing_excerpt(output):
    lines = output.splitlines()
    selected = [line for line in lines if "collected 3" in line or ("PASSED" in line and ("no_crash" in line or "valid" in line or "whitespace" in line))]
    selected.extend(["", "[All three repository test functions are shown above.]", ""])
    selected.extend(line for line in lines if "passing, 0 failing" in line)
    selected.extend(["", lines[-1]])
    return "\n".join(selected)


def build():
    images = {}
    for stem, title, excerpt in [
        ("before_application", "Step 2 - Original application", None),
        ("before_tests", "Step 4 - Fuzz tests before fixes", failure_excerpt),
        ("after_application", "Step 5 - Fixed application, invalid input", None),
        ("after_tests", "Step 6 - All tests pass after fixes", passing_excerpt),
        ("after_valid_application", "Fixed application, valid input", None),
    ]:
        images[stem] = screenshot(stem, title, excerpt)

    output = ROOT / "DELIVERABLES" / "FUZZ_TESTING_PES2UG24CS152_LAB-7.pdf"
    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#18385a")
    styles["Heading1"].textColor = colors.HexColor("#18385a")
    styles["BodyText"].fontSize = 10.5
    styles["BodyText"].leading = 15
    story = []

    def para(text, style="BodyText"):
        story.append(Paragraph(text, styles[style]))
        story.append(Spacer(1, 9))

    para("LAB 7: FUZZ TESTING", "Title")
    para("Shopping Cart - Input Validation", "Heading1")
    para("SRN: PES2UG24CS152 | Date: 13 November 2026")
    para("Objective", "Heading2")
    para("Use Hypothesis to expose input-validation failures in three parsers, harden the implementation, and rerun only the three fuzz-test functions supplied by the repository.")
    para("Assigned files and provenance", "Heading2")
    para('The assignment sheet links to <link href="https://github.com/SETAPESU26/L6_L7_23_shopping_cart/tree/main/Lab%207">SETAPESU26/L6_L7_23_shopping_cart, Lab 7</link>. The assigned filenames are shopping_cart.py and test_shopping_cart.py; these correspond to processor.py and test_processor.py in the generic handout. The original instructor files are preserved in original/.')
    para("Environment and method", "Heading2")
    para("Windows, Python 3.14.7, pytest 9.2.0, Hypothesis 6.170.15. Only the three original repository test functions are used. Each retains the original @given(st.text() | st.none()) strategy; its empty body is completed by calling the corresponding function. Any unhandled exception fails the test. No extra test functions, strategies, assertions or custom Hypothesis settings are added.")
    para("Measured results", "Heading2")
    para("Before fixes: all 3 original fuzz-test functions failed. After fixes: the same 3 functions passed. Hypothesis statistics are retained in the raw output; generated inputs are distinct from the three collected pytest tests.")
    para("Evidence format", "Heading2")
    para("The following pages contain browser screenshots of actual recorded subprocess output. Inputs, commands and exit codes are shown explicitly. These are output-viewer screenshots, not interactive terminal captures. Excerpts are labeled; full unedited stdout/stderr and JSON metadata are supplied in evidence/. No passing output was fabricated.")

    captions = [
        ("before_application", "Step 2 - Run the original application", "Input 'bad' cannot be split into name:pricexqty. The unhandled ValueError terminates the application with exit code 1 before the promo and pincode prompts."),
        ("before_tests", "Step 4 - Run the fuzz tests before fixing", "All three required no-crash properties fail. Hypothesis minimizes inputs to examples such as None and empty text. The screenshot shows minimized None cases and the actual failure summary; full tracebacks are retained in evidence/before_tests.txt."),
        ("after_application", "Step 5 - Run the fixed application", "The same supplied inputs (bad, OFF101, 5) now produce 0, 0 and Unknown. All three prompts complete and the process exits normally. Invalid carts are rejected as a whole."),
        ("after_tests", "Step 6 - Rerun the completed test suite", "All 3 original no-crash tests pass. Each uses only st.text() | st.none(), as in the repository. The application examples on the adjacent pages are separate command-line demonstrations, not additional pytest tests. Full per-test output and Hypothesis statistics are saved in evidence/after_tests.txt."),
        ("after_valid_application", "Valid-input confirmation", "The supplied example remains correct: pen:10x2,book:250x1 totals 270; OFF20 returns 20; 560085 maps to South. This check confirms that hardening preserves useful application behavior."),
    ]
    for stem, heading, caption in captions:
        story.append(PageBreak())
        para(heading, "Heading1")
        para(caption)
        story.append(Image(str(images[stem]), width=499, height=429))

    story.append(PageBreak())
    para("Bug analysis and fixes", "Heading1")
    rows = [["Function", "Original defect", "Fix / chosen policy"],
        ["cart_total", "Unchecked split/unpacking; invalid integer conversion; negative values accepted.", "Validate whole item grammar and types; price >= 0, qty > 0; reject whole invalid cart with 0."],
        ["promo_percent", "Missing OFF crashes; prefix/suffix fragments and invalid ranges accepted.", "Match entire case-insensitive OFF code; accept 0-100 only; invalid input returns 0."],
        ["delivery_zone", "Empty input indexes fail; absent keys raise KeyError; no length/digit check.", "Require six ASCII digits; safely look up the supplied prefix table; otherwise Unknown."]]
    table = Table([[Paragraph(html.escape(cell), styles["BodyText"]) for cell in row] for row in rows], colWidths=[110, 185, 204])
    table.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0),colors.HexColor("#e5edf5")), ("VALIGN",(0,0),(-1,-1),"TOP"), ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#b5c3d2")), ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8), ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    story.append(table)
    story.append(Spacer(1, 14))
    para("Reproduce from the Lab 7 folder", "Heading2")
    for command in ["python -m pip install -r requirements.txt", "python shopping_cart.py", "python -m pytest test_shopping_cart.py -v --hypothesis-show-statistics"]:
        para(html.escape(command), "Code")
    para("Design choices and limits", "Heading2")
    para("The starter specifies no crashes but does not define invalid-input return values. Zero and Unknown are documented choices. Zero does not distinguish invalid input from a valid zero result; a production API should expose validation status separately. Prefix 9 is unsupported by the supplied table, not declared invalid in real postal systems. No input-size or denial-of-service guarantee is claimed. The original tests check only for unhandled exceptions on text and None. They do not verify result values or every input type. Passing these tests cannot prove the absence of every defect.")
    para("Submission contents", "Heading2")
    para("This PDF, the fixed shopping_cart.py, and the completed test_shopping_cart.py. Source files, originals, raw logs, screenshot images and reproducible commands are available in the Lab 7 folder. Review the report before submission.")

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#52657a"))
        canvas.drawString(48, 28, "PES2UG24CS152 | Lab 7 - Fuzz Testing")
        canvas.drawRightString(A4[0] - 48, 28, str(doc.page))

    SimpleDocTemplate(str(output), pagesize=A4, rightMargin=48, leftMargin=48,
        topMargin=42, bottomMargin=45, title="Lab 7 - Shopping Cart Fuzz Testing", author="PES2UG24CS152").build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    build()
