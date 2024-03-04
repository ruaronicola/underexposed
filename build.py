#!/usr/bin/env python3

from glob import glob
from PIL import Image, ExifTags
from collections import defaultdict


MONTHS = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

TEMPLATE = """
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>underexposed</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="css/main.css">
  </head>
  <body>
    <div class="container" autofocus>
      <div class="column right">
        <h1>UNDEREXPOSED</h1><br>
        <p>Hi there! I'm Nicola, a PhD student from UC Santa Barbara. <br><br>I recently picked up the hobby of photography. This page is a place to collect my latest photos.</p><br><br>
        <nav>
{nav_items}
        </nav>
      <!-- END DIV COLUMN RIGHT -->
      </div>

      <div class="column left">
{sections}
      <!-- END DIV COLUMN LEFT -->
      </div>

    <!-- END DIV CONTAINER -->
    </div>

  </body>
</html>

"""

NAV_ITEM_TEMPLATE = """
          <a href="#{year}" id="nav-{year}"><h3><span>{year}</span></h3></a>
"""

SECTION_TEMPLATE = """
        <section id="{year}" class="{_class}">
          <div class="section-spacing"></div>
          <h2><span>{year}</span></h2>
{photos}
        <!-- END SECTION {year} -->
        </section>
"""

PHOTO_TEMPLATE = """
          <div class="image-container">
            <img src="./{path}" width="2048" height="1365" loading="lazy">
            <p class="image-label">{date}. {dof}mm f/{f} {shutter}s ISO {iso}.</p><br><br>
          </div>
"""


all_photos = glob("archive/**/**.jpg", recursive=True)

sections = defaultdict(list)

for path in all_photos:
    if path.split("/")[-1].startswith("_"):
        print(f"ERROR: Found a filename starting with an \"_\". Please fix that: {path}")
        exit(1)

    exif = {
        ExifTags.TAGS[k]: v
        for k, v in Image.open(path)._getexif().items()
        if k in ExifTags.TAGS
    }

    year, month, day = exif["DateTimeOriginal"].split()[0].split(":")
    date = f"{MONTHS[int(month)]} {day}, {year}"

    dof = int(round(exif["FocalLength"]))

    f = exif["FNumber"]

    if exif['ExposureTime'] < 1:
        shutter = f"1/{1/exif['ExposureTime']}"
    else:
        shutter = int(round(exif["ExposureTime"]))

    iso = exif["ISOSpeedRatings"]

    photo_html = PHOTO_TEMPLATE.format(path=path, date=date, dof=dof, f=f, shutter=shutter, iso=iso)

    sections[int(year)].append((exif["DateTimeOriginal"], photo_html))

navs_html = ""
sections_html = ""
for year in sorted(sections, reverse=True):
    sections[year] = [s[1] for s in sorted(sections[year], key=lambda e: e[0], reverse=True)]

    navs_html += NAV_ITEM_TEMPLATE.format(year=year)
    sections_html += SECTION_TEMPLATE.format(year=year, _class="", photos=''.join(sections[year]))

# duplicate most recent year as fallback (shown by default on page load)
sections_html += SECTION_TEMPLATE.format(year=max(sections), _class="fallback", photos=''.join(sections[max(sections)]))

# navs_html += NAV_ITEM_TEMPLATE.format(year=min(sections)-1)
# sections_html += SECTION_TEMPLATE.format(year=min(sections)-1, photos='')

template = TEMPLATE.format(nav_items=navs_html, sections=sections_html)

with open("./index.html", "w") as f:
    f.write(template)

