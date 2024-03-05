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
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="apple-touch-icon" href="/favicon.ico">
  </head>
  <body>
{containers}
  </body>
</html>
"""

NAV_ITEM_TEMPLATE = """
            <a href="#{year}" id="nav-{year}"><h3 class="{_class}"><span>{year}</span></h3></a>"""

CONTAINER_TEMPLATE = """
      <div id="{year}" class="container {_class}">
        <div class="column right">
          <h1>UNDEREXPOSED</h1><br>
          <p>Hi there! I'm Nicola, a PhD student from UC Santa Barbara. <br><br>I recently picked up the hobby of photography. This page is a place to collect my latest photos.</p><br><br>
          <nav>
  {nav_items}
          </nav>
        <!-- END DIV COLUMN RIGHT -->
        </div>

        <div class="column left">
          <div class="container-spacing"></div>
{photos}
        <!-- END DIV COLUMN LEFT -->
        </div>
      <!-- END CONTAINER {year} -->
      </div>
"""

PHOTO_TEMPLATE = """
          <div class="image-container">
            <img src="./{path}" width="2048" height="1365" loading="lazy">
            <p class="image-label">{date}. {dof}mm f/{f} {shutter}s ISO {iso}.</p><br><br>
          </div>
"""


all_photos = glob("archive/**/**.jpg", recursive=True)

containers = defaultdict(list)

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

    containers[int(year)].append((exif["DateTimeOriginal"], photo_html))

containers_html = ""
for year in sorted(containers, reverse=True):
    containers[year] = [s[1] for s in sorted(containers[year], key=lambda e: e[0], reverse=True)]
    navs_html = "".join([NAV_ITEM_TEMPLATE.format(year=y, _class="active" if y==year else "") for y in sorted(containers, reverse=True)])
    containers_html += CONTAINER_TEMPLATE.format(year=year, _class="", nav_items=navs_html, photos=''.join(containers[year]))

# duplicate most recent year as fallback (shown by default on page load)
fallback_year = max(containers)  
navs_html = "".join([NAV_ITEM_TEMPLATE.format(year=y, _class="active" if y==fallback_year else "") for y in sorted(containers, reverse=True)])
containers_html += CONTAINER_TEMPLATE.format(year=fallback_year, _class="fallback", nav_items=navs_html, photos=''.join(containers[fallback_year]))

template = TEMPLATE.format(containers=containers_html)

with open("./index.html", "w") as f:
    f.write(template)

