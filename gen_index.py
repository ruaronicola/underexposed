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
    <title>UNDEREXPOSED</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
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
  <script type="text/javascript" src="js/main.js"></script>
</html>

"""

NAV_ITEM_TEMPLATE = """
          <a href="#{year}" id="nav-{year}"><h3><span>{year}</span></h3></a>
"""

SECTION_TEMPLATE = """
        <section id="{year}">
          <div class="section-spacing"></div>
          <h2><span>{year}</span></h2>
{photos}
        <!-- END SECTION {year} -->
        </section>
"""

PHOTO_TEMPLATE = """
          <div class="image-container">
            <img src="./{path}">
            <p class="image-label">{date}. {dof}mm f/{f} 1/{shutter}s ISO {iso}.</p><br><br>
          </div>
"""


all_photos = glob("archive/**/**.jpg", recursive=True)

sections = defaultdict(list)

for path in all_photos:
    exif = {
        ExifTags.TAGS[k]: v
        for k, v in Image.open(path)._getexif().items()
        if k in ExifTags.TAGS
    }

    year, month, day = exif["DateTimeOriginal"].split()[0].split(":")
    date = f"{MONTHS[int(month)]} {day}, {year}"

    dof = int(round(exif["FocalLength"]))

    f = exif["FNumber"]

    shutter = f"{1/exif['ExposureTime']}"

    iso = exif["ISOSpeedRatings"]

    photo_html = PHOTO_TEMPLATE.format(path=path, date=date, dof=dof, f=f, shutter=shutter, iso=iso)

    sections[int(year)].append((exif["DateTimeOriginal"], photo_html))

navs_html = ""
sections_html = ""
for year in sorted(sections, reverse=True):
    sections[year] = [s[1] for s in sorted(sections[year], key=lambda e: e[0], reverse=True)]

    navs_html += NAV_ITEM_TEMPLATE.format(year=year)
    sections_html += SECTION_TEMPLATE.format(year=year, photos=''.join(sections[year]))

navs_html += NAV_ITEM_TEMPLATE.format(year=min(sections)-1)
sections_html += SECTION_TEMPLATE.format(year=min(sections)-1, photos='')

template = TEMPLATE.format(nav_items=navs_html, sections=sections_html)

print(template)
