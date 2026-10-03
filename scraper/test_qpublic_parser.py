"""Parser tests for parse_qpublic_owner in scraper/fetch.py.

Fixtures:
  - Clayton County GA (12238D A008, 13107C C002): classic four-column-blocks
    template, kept as a regression.
  - Cherokee County GA (15N24T 065, 15N14C 001): newer Beacon "Owners"
    template (markup shape from the indexed live report and a 2026-01-27
    printed report); plus the password-protected variant that must degrade
    to ("", []).
Run:  python3 scraper/test_qpublic_parser.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch import parse_qpublic_owner

TPL = """<html><body><main id="maincontent">
<section id="ctlBodyPane_ctl05_mSection" class="avoid-page-break">
<header id="ctlBodyPane_ctl05_divHeader" class="module-header" moduleid="45861">
<a class="toggle-collapse"><div id="ctlBodyPane_ctl05_lblName" class="title" role="heading" aria-level="2">Owner</div></a>
</header>
<div class="module-content">
<div class="block-row">
<div class="four-column-blocks">
<span id="ctlBodyPane_ctl05_ctl01_sprLblOwnerTitle_lblSuppressed"></span>
{BODY}
<span id="ctlBodyPane_ctl05_ctl01_lblAddress1"><br>{A1}</span>
<span id="ctlBodyPane_ctl05_ctl01_lblAddress2">{A2}</span>
<span id="ctlBodyPane_ctl05_ctl01_lblCityStZip"><br>{CSZ}</span>
</div>
<div class="four-column-blocks"><span id="ctlBodyPane_ctl05_ctl01_sprLblOwnerMultiple_lblSuppressed"></span></div>
<div class="four-column-blocks"><span id="ctlBodyPane_ctl05_ctl01_sprLblJanuaryOwner_lblSuppressed"></span></div>
</div></div></section></main></body></html>"""


def test_parcel_span_form():
    body = ('<span id="ctlBodyPane_ctl05_ctl01_sprLnkOwnerName1_lnkUpmSearchLinkSuppressed_lblSearch">'
            'ABBOTT REBECCA LYNN, SMITH BRENDA JEAN</span>\n'
            '<span id="ctlBodyPane_ctl05_ctl01_sprLblOwnerName2_lblSuppressed">'
            '<br>OR THARP BRANDON LEE</span>')
    owner, mail = parse_qpublic_owner(
        TPL.format(BODY=body, A1="2024 SLATE RD", A2="",
                   CSZ="ELLENWOOD GA 30294 2213"))
    assert owner == "ABBOTT REBECCA LYNN, SMITH BRENDA JEAN, OR THARP BRANDON LEE", owner
    assert mail == ["2024 SLATE RD", "ELLENWOOD GA 30294 2213"], mail


def test_parcel_anchor_form():
    body = ('<a id="ctlBodyPane_ctl05_ctl01_sprLnkOwnerName1_lnkUpmSearchLinkSuppressed_lnkSearch" '
            'href="javascript:__doPostBack(\'x\',\'\')">JOHNSON BOBBY Q</a>\n'
            '<span id="ctlBodyPane_ctl05_ctl01_sprLblOwnerName2_lblSuppressed"></span>')
    owner, mail = parse_qpublic_owner(
        TPL.format(BODY=body, A1="302 HILLCREST CIRCLE", A2="",
                   CSZ="ANDERSON SC 29624 "))
    assert owner == "JOHNSON BOBBY Q", owner
    assert mail == ["302 HILLCREST CIRCLE", "ANDERSON SC 29624"], mail


def test_no_owner_section():
    assert parse_qpublic_owner("<html><body><p>nothing here</p></body></html>") == ("", [])


def test_blank_owner_block():
    owner, mail = parse_qpublic_owner(
        TPL.format(BODY="", A1="", A2="", CSZ=""))
    assert (owner, mail) == ("", [])


# Cherokee County's Beacon template: a newer Beacon layout whose section
# header is "Owners" (plural) with plain text lines under module-content.
# Markup shape verified 2026-10-03 from the indexed live Cherokee report for
# parcel 15N24T 065 and the printed report for parcel 15N14C 001 (owner
# LESTER LANELLE MOORE, 4281 PINETREE DR, POWDER SPRINGS, GA 30127).
CHEROKEE_TPL = """<html><body><main id="maincontent">
<section id="ctlBodyPane_ctl07_mSection">
<header class="module-header">
<div id="ctlBodyPane_ctl07_lblName" class="title">Owners</div>
</header>
<div class="module-content">
<div class="block-row">
<div class="four-column-blocks">
<span>LESTER LANELLE MOORE</span><br>
<span>4281 PINETREE DR</span><br>
<span>POWDER SPRINGS, GA 30127</span>
</div>
</div></div></section></main></body></html>"""


def test_cherokee_owners_template():
    owner, mail = parse_qpublic_owner(CHEROKEE_TPL)
    assert owner == "LESTER LANELLE MOORE", owner
    assert mail == ["4281 PINETREE DR", "POWDER SPRINGS, GA 30127"], mail


def test_cherokee_owners_password_protected():
    # Anonymous viewers currently see only this notice in the Owners module;
    # the parser must degrade to ("", []) rather than picking it up as data.
    html = """<html><body><main id="maincontent">
<section id="ctlBodyPane_ctl07_mSection">
<header class="module-header">
<div class="title">Owners</div>
</header>
<div class="module-content">
This Owners information is password protected.
</div></section></main></body></html>"""
    assert parse_qpublic_owner(html) == ("", [])


if __name__ == "__main__":
    test_parcel_span_form()
    test_parcel_anchor_form()
    test_no_owner_section()
    test_blank_owner_block()
    test_cherokee_owners_template()
    test_cherokee_owners_password_protected()
    print("ALL QPARSER TESTS PASSED")
