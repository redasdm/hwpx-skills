from __future__ import annotations

import argparse
import copy
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
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

HEADING_SYMBOLS = "□❐■▣"
BODY_SYMBOLS = "❍○◦•"
COVER_TITLE_ROW = "2"
COVER_FOOTER_ROW = "5"

# The Education SW asset predates the □/❍/- outline convention, so its example body content
# cannot be recognised by symbol; pin its slot paragraphs by position.
PINNED_SLOTS: dict[str, dict[str, int]] = {
    "education_sw_plan_template.hwpx": {
        "heading": 10,
        "body": 31,
        "long_body": 43,
        "blank": 35,
        "table4": 49,
    },
}


@dataclass(frozen=True)
class TextSlot:
    """A template paragraph reused for generated lines, plus the charPr of its text run."""

    template: ET.Element
    char_pr: str


@dataclass(frozen=True)
class TemplateSlots:
    cover: ET.Element
    section: ET.Element
    heading: TextSlot
    body: TextSlot
    long_body: TextSlot
    blank: TextSlot
    table4: ET.Element


def hp(tag: str) -> str:
    return HP + tag


def top_paragraphs(root: ET.Element) -> list[ET.Element]:
    return [child for child in root if child.tag == hp("p")]


def paragraph_text(p: ET.Element) -> str:
    return "".join(node.text or "" for node in p.iter(hp("t"))).strip()


def text_char_pr(p: ET.Element, default: str = "12") -> str:
    """charPr of the run carrying the paragraph text; falls back to the first run."""
    runs = p.findall("hp:run", NS)
    for run in reversed(runs):
        if any((node.text or "") for node in run.findall("hp:t", NS)):
            return run.get("charPrIDRef") or default
    for run in runs:
        if run.get("charPrIDRef"):
            return run.get("charPrIDRef")
    return default


def table_shape(p: ET.Element) -> tuple[int, int] | None:
    tbl = p.find(".//hp:tbl", NS)
    if tbl is None:
        return None
    return int(tbl.get("rowCnt")), int(tbl.get("colCnt"))


def discover_slots(root: ET.Element, template_name: str) -> TemplateSlots:
    """Locate the paragraphs the generator reuses, so any template of the layout family works."""
    tops = top_paragraphs(root)
    pinned = PINNED_SLOTS.get(template_name, {})
    missing = (
        "Template is missing {what}. A plan-layout template needs a 6x2 cover table, an 8x7 "
        f"section-header table, a '{HEADING_SYMBOLS[0]}' line, a '{BODY_SYMBOLS[0]}' line, an empty "
        "body paragraph, and a 4-column table."
    )

    def slot(role: str, find, what: str) -> ET.Element:
        if role in pinned:
            return tops[pinned[role]]
        found = find()
        if found is None:
            raise ValueError(missing.format(what=what))
        return found

    cover = slot("cover", lambda: next((p for p in tops if table_shape(p) == (6, 2)), None), "a 6x2 cover table")
    section = slot("section", lambda: next((p for p in tops if table_shape(p) == (8, 7)), None), "an 8x7 section-header table")
    heading = slot(
        "heading",
        lambda: next((p for p in tops if paragraph_text(p)[:1] in HEADING_SYMBOLS), None),
        f"a '{HEADING_SYMBOLS[0]}' heading line",
    )
    body = slot(
        "body",
        lambda: next((p for p in tops if paragraph_text(p)[:1] in BODY_SYMBOLS), None),
        f"a '{BODY_SYMBOLS[0]}' body line",
    )
    blank = slot("blank", lambda: next((p for p in tops if not paragraph_text(p)), None), "an empty body paragraph")
    table4 = slot(
        "table4",
        lambda: next((p for p in tops if (shape := table_shape(p)) and shape[1] == 4), None),
        "a 4-column table",
    )
    long_body = tops[pinned["long_body"]] if "long_body" in pinned else body

    return TemplateSlots(
        cover=cover,
        section=section,
        heading=TextSlot(heading, text_char_pr(heading)),
        body=TextSlot(body, text_char_pr(body)),
        long_body=TextSlot(long_body, text_char_pr(long_body)),
        blank=TextSlot(blank, text_char_pr(blank)),
        table4=table4,
    )


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


def cover_cell(cover: ET.Element, row_addr: str) -> ET.Element | None:
    tbl = cover.find(".//hp:tbl", NS)
    if tbl is None:
        return None
    for tc in tbl.iter(hp("tc")):
        addr = tc.find("hp:cellAddr", NS)
        if addr is not None and addr.get("rowAddr") == row_addr:
            return tc
    return None


def cover_text_nodes(cover: ET.Element, row_addr: str) -> list[ET.Element]:
    cell = cover_cell(cover, row_addr)
    if cell is None:
        return []
    return [node for node in cell.iter(hp("t")) if (node.text or "").strip()]


def update_cover(cover: ET.Element, title: str, subtitle: str, dept: str, date: str) -> ET.Element:
    """Fill the family cover: title (and subtitle when the template has a second line) plus footer."""
    out = copy.deepcopy(cover)
    title_nodes = cover_text_nodes(out, COVER_TITLE_ROW)
    if title_nodes:
        title_nodes[0].text = title
    if subtitle:
        if len(title_nodes) > 1:
            title_nodes[1].text = subtitle
        else:
            print(
                "NOTE: template cover has a single title line; the subtitle was not rendered.",
                file=sys.stderr,
            )
    footer = " / ".join(part for part in (date, dept) if part)
    footer_nodes = cover_text_nodes(out, COVER_FOOTER_ROW)
    if footer and footer_nodes:
        footer_nodes[0].text = footer
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


def make_blank(slot: TextSlot) -> ET.Element:
    return paragraph_from(slot.template, [(slot.char_pr, "")])


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
    slots = discover_slots(root, template.name)

    new_children: list[ET.Element] = [update_cover(slots.cover, title, subtitle, dept, date)]
    next_table_id = 2200000000

    for roman, sec_title, content in sections:
        new_children.append(make_section_header(slots.section, roman, sec_title, next_table_id))
        next_table_id += 1
        content = normalize_symbol_outline(content)
        i = 0
        while i < len(content):
            line = content[i].strip()
            if line == "단계" and content[i : i + 4] == ["단계", "일정", "주요 과업", "기대 산출물"]:
                new_children.append(make_roadmap_table(slots.table4, content[i:], next_table_id))
                next_table_id += 1
                break
            if line.startswith("□"):
                new_children.append(paragraph_from(slots.heading.template, [(slots.heading.char_pr, line)]))
            else:
                slot = slots.long_body if len(line) > 75 else slots.body
                new_children.append(paragraph_from(slot.template, [(slot.char_pr, line)]))
            i += 1
        new_children.append(make_blank(slots.blank))

    for child in list(root):
        root.remove(child)
    for child in new_children:
        root.append(child)
    return ET.ElementTree(root)


def serialize_section_xml(root: ET.Element, template_section: bytes) -> bytes:
    """Serialize like 한/글 does: template declaration/root namespaces, no newlines."""
    body = ET.tostring(root, encoding="utf-8", xml_declaration=False).decode("utf-8")
    body = body.replace("\r\n", "").replace("\n", "")
    body_open = body.find("<hs:sec")
    body_start = body.find(">", body_open) + 1
    template_text = template_section.decode("utf-8")
    template_open = template_text.find("<hs:sec")
    template_start = template_text.find(">", template_open) + 1
    return (template_text[:template_start] + body[body_start:]).encode("utf-8")


def write_output(template: Path, output: Path, tree: ET.ElementTree) -> None:
    section_bytes = serialize_section_xml(tree.getroot(), read_section_xml(template))
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
    parser = argparse.ArgumentParser(description="Build a plan-layout HWPX from a template and source text.")
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="Template HWPX path. Defaults to the bundled Education SW asset; the bundled AIEP and "
        "체험센터 보고자료 assets work too, and any document of the same layout family.",
    )
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
