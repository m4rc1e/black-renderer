import io
from typing import NamedTuple
from fontTools.misc.arrayTools import (
    scaleRect,
    offsetRect,
    intRect,
    unionRect,
    insetRect,
)
import uharfbuzz as hb
from .font import BlackRendererFont
from .backends import getSurface


def renderText(
    fontPath,
    textString,
    outputPath,
    *,
    fontSize=250,
    margin=20,
    features=None,
    variations=None
):
    font = BlackRendererFont(fontPath)
    glyphNames = font.glyphNames

    scaleFactor = fontSize / font.hbFont.face.upem

    buf = hb.Buffer()
    buf.add_str(textString)
    buf.guess_segment_properties()

    if variations:
        font.setLocation(variations)

    hb.shape(font.hbFont, buf, features)

    infos = buf.glyph_infos
    positions = buf.glyph_positions
    glyphLine = []
    for info, pos in zip(infos, positions):
        g = GlyphInfo(
            name=glyphNames[info.codepoint],
            gid=info.codepoint,
            xAdvance=pos.x_advance,
            yAdvance=pos.y_advance,
            xOffset=pos.x_offset,
            yOffset=pos.y_offset,
        )
        glyphLine.append(g)
    bounds = calcBounds(font, glyphLine, scaleFactor)
    bounds = insetRect(bounds, -margin, -margin)
    bounds = intRect(bounds)
    if outputPath is None or outputPath.suffix == ".svg":
        surfaceFactory = getSurface("svg")
    else:
        surfaceFactory = getSurface("skia")  # XXX switch backend
    xMin, yMin, xMax, yMax = bounds
    width = xMax - xMin
    surface = surfaceFactory(xMin, yMin, xMax - xMin, yMax - yMin)
    backend = surface.backend
    backend.transform((scaleFactor, 0, 0, scaleFactor, 0, 0))
    for glyph in glyphLine:
        with backend.savedState():
            backend.transform((1, 0, 0, 1, glyph.xOffset, glyph.yOffset))
            font.drawGlyph(glyph.name, backend)
        backend.transform((1, 0, 0, 1, glyph.xAdvance, glyph.yAdvance))
    if outputPath is not None:
        surface.saveImage(outputPath)
    else:
        stream = io.BytesIO()
        surface.saveImage(stream)
        print(stream.getvalue().decode("utf-8").rstrip())


def calcBounds(font, glyphLine, scaleFactor):
    bounds = None
    x, y = 0, 0
    for glyph in glyphLine:
        glyphBounds = font.getGlyphBounds(glyph.name)
        if glyphBounds is None:
            continue
        glyphBounds = offsetRect(glyphBounds, x + glyph.xOffset, y + glyph.yOffset)
        x += glyph.xAdvance
        y += glyph.yAdvance
        if bounds is None:
            bounds = glyphBounds
        else:
            bounds = unionRect(bounds, glyphBounds)
    return scaleRect(bounds, scaleFactor, scaleFactor)


class GlyphInfo(NamedTuple):
    name: str
    gid: int
    xAdvance: float
    yAdvance: float
    xOffset: float
    yOffset: float
