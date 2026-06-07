from __future__ import annotations

import argparse
import copy
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


NS = {
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hp10": "http://www.hancom.co.kr/hwpml/2016/paragraph",
    "ha": "http://www.hancom.co.kr/hwpml/2011/app",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    "hhs": "http://www.hancom.co.kr/hwpml/2011/history",
    "hm": "http://www.hancom.co.kr/hwpml/2011/master-page",
    "hpf": "http://www.hancom.co.kr/schema/2011/hpf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf/",
    "ooxmlchart": "http://www.hancom.co.kr/hwpml/2016/ooxmlchart",
    "hwpunitchar": "http://www.hancom.co.kr/hwpml/2016/HwpUnitChar",
    "epub": "http://www.idpf.org/2007/ops",
    "config": "urn:oasis:names:tc:opendocument:xmlns:config:1.0",
}

for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

HP = f"{{{NS['hp']}}}"
DEFAULT_TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "education_sw_plan_template.hwpx"


def hp(tag: str) -> str:
    return HP + tag


def read_section_xml(template: Path) -> bytes:
    with zipfile.ZipFile(template, "r") as zf:
        return zf.read("Contents/section0.xml")


def text_nodes(el: ET.Element) -> list[ET.Element]:
    return el.findall(".//hp:t", NS)


def replace_first_text_containing(el: ET.Element, needle: str, value: str) -> bool:
    for node in text_nodes(el):
        if needle in (node.text or ""):
            node.text = value
            return True
    return False


def clear_paragraph_runs(p: ET.Element) -> ET.Element | None:
    line_seg = None
    for child in list(p):
        if child.tag == hp("linesegarray"):
            line_seg = copy.deepcopy(child)
        if child.tag in {hp("run"), hp("linesegarray")}:
            p.remove(child)
    return line_seg


def set_paragraph_runs(p: ET.Element, runs: list[tuple[str, str]]) -> ET.Element:
    line_seg = clear_paragraph_runs(p)
    for char_pr, text in runs:
        run = ET.Element(hp("run"), {"charPrIDRef": char_pr})
        if text:
            t = ET.SubElement(run, hp("t"))
            t.text = text
        p.append(run)
    if line_seg is not None:
        p.append(line_seg)
    return p


def paragraph_from(template: ET.Element, runs: list[tuple[str, str]]) -> ET.Element:
    p = copy.deepcopy(template)
    return set_paragraph_runs(p, runs)


def set_cell_text(tc: ET.Element, value: str) -> None:
    p = tc.find(".//hp:p", NS)
    if p is None:
        return
    first_run = p.find("hp:run", NS)
    char_pr = first_run.get("charPrIDRef") if first_run is not None else "12"
    set_paragraph_runs(p, [(char_pr, value)])


def update_cover(cover: ET.Element, title: str, subtitle: str, dept: str, date: str) -> ET.Element:
    out = copy.deepcopy(cover)
    replace_first_text_containing(out, "교육용 SW 지원사업", title)
    replace_first_text_containing(out, "계약 개선 계획(안)", subtitle)
    replace_first_text_containing(out, "미래교육과 에듀테크팀", f"{date} / {dept}")
    return out


def make_section_header(template: ET.Element, roman: str, title: str, table_id: int) -> ET.Element:
    out = copy.deepcopy(template)
    tbl = out.find(".//hp:tbl", NS)
    if tbl is not None:
        tbl.set("id", str(table_id))
    old_texts = [node.text or "" for node in text_nodes(out)]
    for node in text_nodes(out):
        txt = node.text or ""
        if re.fullmatch(r"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+", txt.strip()):
            node.text = roman
            break
    for old in old_texts:
        stripped = old.strip()
        if stripped and not re.fullmatch(r"[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ◤]+", stripped):
            replace_first_text_containing(out, stripped, " " + title)
            break
    return out


def make_blank(template: ET.Element) -> ET.Element:
    return paragraph_from(template, [("10", "")])


def parse_source_text(source_text: Path) -> tuple[str, str, str, str, list[tuple[str, str, list[str]]]]:
    lines = [line.rstrip() for line in source_text.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in lines if line.strip()]
    if len(lines) < 5:
        raise ValueError("Source text must include title, subtitle, metadata, and at least one section.")

    title = lines[0].strip()
    subtitle = lines[1].strip()
    date = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("작성일:")), "")
    dept = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("보고부서:")), "")

    sections: list[tuple[str, str, list[str]]] = []
    current: tuple[str, str, list[str]] | None = None
    sec_re = re.compile(r"^([ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+)\.\s*(.+)$")
    for line in lines[4:]:
        match = sec_re.match(line)
        if match:
            if current:
                sections.append(current)
            current = (match.group(1), match.group(2).strip(), [])
        elif current:
            current[2].append(line)
    if current:
        sections.append(current)
    if not sections:
        raise ValueError("No Roman-numeral sections found in source text.")
    return title, subtitle, date, dept, sections


def normalize_symbol_outline(content: list[str]) -> list[str]:
    normalized: list[str] = []
    after_number_heading = False
    after_square_heading = False
    i = 0
    while i < len(content):
        line = content[i].strip()
        if line == "단계" and content[i : i + 4] == ["단계", "일정", "주요 과업", "기대 산출물"]:
            normalized.extend(content[i:])
            break

        number_match = re.match(r"^\d+\.\s*(.+)$", line)
        if number_match:
            normalized.append("□ " + number_match.group(1).strip())
            after_number_heading = True
            after_square_heading = False
        elif line.startswith("□"):
            body = line[1:].strip()
            if after_number_heading:
                normalized.append("❍ " + body)
                after_square_heading = True
            else:
                normalized.append("□ " + body)
                after_square_heading = False
        elif line.startswith("❍"):
            body = line[1:].strip()
            if after_square_heading:
                normalized.append("- " + body)
            else:
                normalized.append("❍ " + body)
        elif line.startswith("-"):
            normalized.append("- " + line[1:].strip())
        else:
            normalized.append("❍ " + line)
        i += 1
    return normalized


def make_roadmap_table(template_p: ET.Element, raw_lines: list[str], table_id: int) -> ET.Element:
    rows = [raw_lines[i : i + 4] for i in range(0, len(raw_lines), 4)]
    out = copy.deepcopy(template_p)
    tbl = out.find(".//hp:tbl", NS)
    if tbl is None:
        return out
    tbl.set("id", str(table_id))

    trs = tbl.findall("hp:tr", NS)
    target_count = len(rows)
    for tr in trs[target_count:]:
        tbl.remove(tr)
    tbl.set("rowCnt", str(target_count))

    for row, tr in zip(rows, tbl.findall("hp:tr", NS)):
        for value, tc in zip(row, tr.findall("hp:tc", NS)):
            set_cell_text(tc, value)
    return out


def build_document(template: Path, source_text: Path) -> ET.ElementTree:
    title, subtitle, date, dept, sections = parse_source_text(source_text)
    root = ET.fromstring(read_section_xml(template))
    children = list(root)
    if len(children) < 50:
        raise ValueError("Template does not match the expected Education SW plan-style structure.")

    cover_template = children[0]
    section_template = children[1]
    heading_template = children[10]
    body_template = children[31]
    long_body_template = children[43]
    blank_template = children[35]
    table4_template = children[49]

    new_children: list[ET.Element] = [update_cover(cover_template, title, subtitle, dept, date)]
    next_table_id = 2200000000

    for roman, sec_title, content in sections:
        new_children.append(make_section_header(section_template, roman, sec_title, next_table_id))
        next_table_id += 1
        content = normalize_symbol_outline(content)
        i = 0
        while i < len(content):
            line = content[i].strip()
            if line == "단계" and content[i : i + 4] == ["단계", "일정", "주요 과업", "기대 산출물"]:
                new_children.append(make_roadmap_table(table4_template, content[i:], next_table_id))
                next_table_id += 1
                break
            if line.startswith("□"):
                new_children.append(paragraph_from(heading_template, [("13", line)]))
            else:
                template_p = long_body_template if len(line) > 75 else body_template
                new_children.append(paragraph_from(template_p, [("12", line)]))
            i += 1
        new_children.append(make_blank(blank_template))

    for child in list(root):
        root.remove(child)
    for child in new_children:
        root.append(child)
    return ET.ElementTree(root)


def write_output(template: Path, output: Path, tree: ET.ElementTree) -> None:
    section_bytes = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(template, "r") as src, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data = src.read(info.filename)
            if info.filename == "Contents/section0.xml":
                data = section_bytes
            dst.writestr(info, data)


def refresh_line_layout(output: Path) -> None:
    cell_writer = Path.home() / ".codex" / "skills" / "hwpx-core" / "scripts" / "cell_writer.py"
    if not cell_writer.is_file():
        print(f"WARNING: line-layout refresh skipped; missing {cell_writer}", file=sys.stderr)
        return
    subprocess.run(
        [
            sys.executable,
            str(cell_writer),
            "--hwpx",
            str(output),
            "--body-width",
            "48190",
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an Education SW plan-style HWPX from a template and source text.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Template HWPX path. Defaults to the bundled skill asset.")
    parser.add_argument("--source-text", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--refresh-line-layout", action="store_true", help="Regenerate linesegarray for automatic visual wrapping.")
    args = parser.parse_args()

    if not args.template.is_file():
        raise SystemExit(f"Template HWPX not found: {args.template}")
    write_output(args.template, args.output, build_document(args.template, args.source_text))
    if args.refresh_line_layout:
        refresh_line_layout(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
