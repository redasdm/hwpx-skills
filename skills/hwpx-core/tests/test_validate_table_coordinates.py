#!/usr/bin/env python3
"""Regression tests for Hancom-editable table coordinate validation."""

from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path


_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
_SPEC = importlib.util.spec_from_file_location(
    "validate", _SCRIPTS_DIR / "validate.py"
)
assert _SPEC and _SPEC.loader
_validate = importlib.util.module_from_spec(_SPEC)
sys.modules["validate"] = _validate
_SPEC.loader.exec_module(_validate)


def _table_xml(*, last_row_addr: int = 1) -> str:
    rows = []
    for row_index, row_address in enumerate((0, last_row_addr)):
        cells = []
        for col_index in range(2):
            cells.append(
                f'<hp:tc><hp:subList><hp:p><hp:run><hp:t/></hp:run>'
                f'</hp:p></hp:subList><hp:cellAddr colAddr="{col_index}" '
                f'rowAddr="{row_address}"/><hp:cellSpan colSpan="1" '
                f'rowSpan="1"/><hp:cellSz width="1000" height="1000"/>'
                f'<hp:cellMargin left="0" right="0" top="0" bottom="0"/>'
                f'</hp:tc>'
            )
        rows.append(f'<hp:tr>{"".join(cells)}</hp:tr>')
    return (
        '<hp:tbl id="100" rowCnt="2" colCnt="2">'
        f'{"".join(rows)}</hp:tbl>'
    )


def _section_xml(*, last_row_addr: int = 1) -> bytes:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<hs:sec xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
        'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph">'
        '<hp:p><hp:run>'
        f'{_table_xml(last_row_addr=last_row_addr)}'
        '</hp:run></hp:p></hs:sec>'
    ).encode("utf-8")


def _write_hwpx(path: Path, section: bytes) -> Path:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as zf:
        zf.writestr("mimetype", "application/hwp+zip")
        zf.writestr("Contents/content.hpf", b"<hpf:package xmlns:hpf=\"urn:test\"/>")
        zf.writestr("Contents/header.xml", b"<hh:head xmlns:hh=\"urn:test\"/>")
        zf.writestr("Contents/section0.xml", section)
    return path


def test_validate_accepts_consistent_table_grid(tmp_path: Path):
    path = _write_hwpx(tmp_path / "valid.hwpx", _section_xml())

    errors, _warnings = _validate.validate(str(path))

    assert errors == []


def test_validate_rejects_skipped_out_of_range_row_address(tmp_path: Path):
    path = _write_hwpx(
        tmp_path / "bad-row-address.hwpx",
        _section_xml(last_row_addr=5),
    )

    errors, _warnings = _validate.validate(str(path))

    assert any("Table 100" in error and "rowAddr=5" in error for error in errors)