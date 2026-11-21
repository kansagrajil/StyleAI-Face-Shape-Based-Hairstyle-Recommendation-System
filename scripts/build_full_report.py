"""
Master Report Generator for Atmiya University
Assembles all 11 chapters, Front Pages, References, and Appendices.
Sets up standard A4 university formatting with 1.25" left margin for binding.
Generates the final Word document and verifies exact page count.
"""

import os
import sys
import subprocess

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from scripts.report_helpers import OUTPUT_FILE
from scripts.report_sections_part1 import build_front_matter, build_chapter_1
from scripts.report_sections_part2 import build_chapter_2, build_chapter_3
from scripts.report_sections_part3 import build_chapter_4, build_chapter_5, build_chapter_6
from scripts.report_sections_part4 import build_chapter_7, build_chapter_8
from scripts.report_sections_part5 import (
    build_chapter_9, build_chapter_10, build_chapter_11, build_references_and_appendix
)

def add_page_number_to_run(run):
    """Inserts a dynamic Word PAGE field into the specified run element."""
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def create_document():
    doc = Document()

    # Configure Default Section Dimensions (A4 with 1.25" Left margin for university binding)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.9)
    section.bottom_margin = Inches(0.9)
    section.left_margin = Inches(1.25)
    section.right_margin = Inches(0.9)

    # Configure Running Header & Footer
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hrun = hp.add_run("StyleAI — Face Shape Based Hairstyle Recommendation System")
    hrun.font.name = 'Times New Roman'
    hrun.font.size = Pt(8.5)
    hrun.italic = True
    hrun.font.color.rgb = RGBColor(100, 116, 139)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    frun1 = fp.add_run("Atmiya University, Rajkot — Department of Computer Engineering          Page ")
    frun1.font.name = 'Times New Roman'
    frun1.font.size = Pt(8.5)
    frun1.font.color.rgb = RGBColor(100, 116, 139)
    
    frun2 = fp.add_run()
    frun2.font.name = 'Times New Roman'
    frun2.font.size = Pt(8.5)
    frun2.bold = True
    frun2.font.color.rgb = RGBColor(30, 41, 59)
    add_page_number_to_run(frun2)

    # Set default Normal style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)

    print("Building Front Pages (Cover, Declaration, Certificates, Ack, Abstract, TOC, Lists)...")
    build_front_matter(doc)

    print("Building Chapter 1 (Introduction)...")
    build_chapter_1(doc)

    print("Building Chapter 2 (Literature Survey - 10+ Pages)...")
    build_chapter_2(doc)

    print("Building Chapter 3 (Project Planning)...")
    build_chapter_3(doc)

    print("Building Chapter 4 (Requirement Analysis)...")
    build_chapter_4(doc)

    print("Building Chapter 5 (System Analysis)...")
    build_chapter_5(doc)

    print("Building Chapter 6 (System Design)...")
    build_chapter_6(doc)

    print("Building Chapter 7 (System Implementation)...")
    build_chapter_7(doc)

    print("Building Chapter 8 (Testing)...")
    build_chapter_8(doc)

    print("Building Chapter 9 (Results and Discussion)...")
    build_chapter_9(doc)

    print("Building Chapter 10 (User Manual)...")
    build_chapter_10(doc)

    print("Building Chapter 11 (Conclusion)...")
    build_chapter_11(doc)

    print("Building References (IEEE Format) and Appendices...")
    build_references_and_appendix(doc)

    doc.save(OUTPUT_FILE)
    print(f"Report saved successfully to: {OUTPUT_FILE}")

def check_word_page_count(docx_path):
    ps_script = f"""
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    try {{
        $doc = $word.Documents.Open('{docx_path}')
        # wdStatisticPages = 2
        $pages = $doc.ComputeStatistics(2)
        Write-Output "PAGE_COUNT:$pages"
        $doc.Close([ref]$false)
    }} finally {{
        $word.Quit()
    }}
    """
    try:
        result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if "PAGE_COUNT:" in line:
                return int(line.split("PAGE_COUNT:")[1].strip())
    except Exception as e:
        print(f"Error checking page count: {e}")
    return None

if __name__ == '__main__':
    create_document()
    pages = check_word_page_count(OUTPUT_FILE)
    if pages:
        print(f"Verified Word Document Page Count: {pages} pages")
    else:
        print("Could not query Word COM page count.")
