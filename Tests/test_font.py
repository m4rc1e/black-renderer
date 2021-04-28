import pathlib
from blackrenderer.font import BlackRendererFont
from blackrenderer.dumpCOLRv1Glyph import dumpCOLRv1Glyph


testDir = pathlib.Path(__file__).resolve().parent
testFont1 = testDir / "data" / "noto-glyf_colr_1.ttf"


def test_font():
    font = BlackRendererFont(testFont1)
    assert len(font.glyphNames) > len(font.colrGlyphNames)