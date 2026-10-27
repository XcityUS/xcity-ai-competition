#!/usr/bin/env python3
"""Refresh the official stage-one ZIP from the single issued boundary source.
Run update_site_boundary.py and practice-brief/build_maps.py first.
Keeps pilot-layer files and the current README; replaces every boundary exchange.
"""
from pathlib import Path
import json, zipfile, tempfile, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parents[1];B=R/'brief/site-package/boundaries';AS=R/'scripts/practice-brief/assets/en';Z=R/'brief/design-practice-stage1-data.zip';prefix='XCITY_design_practice_stage1_data/'
with tempfile.TemporaryDirectory() as tmp:
 t=Path(tmp)
 with zipfile.ZipFile(Z) as z:z.extractall(t)
 root=t/prefix;shp=root/'shp'
 for name in ['xcity_site_boundary.kml','xcity_site_boundary.kmz']:shutil.copyfile(B/name,root/name)
 for p in (B/'exchange').iterdir():shutil.copyfile(p,shp/p.name if p.suffix!='.dxf' else root/p.name)
 for name in ['parcels_9_13.geojson','scope_9_13.geojson','boundary-revision.json']:shutil.copyfile(B/name,root/name)
 (root/'BOUNDARY_README.txt').write_text((B/'README.md').read_text())
 # Replace the old README that explicitly described leaving narrow slivers unclosed.
 from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
 from reportlab.lib.styles import getSampleStyleSheet
 styles=getSampleStyleSheet(); story=[]
 for title,text in [
 ('Site data — read me','XCITY Design Practice Call | Issued boundary seam-closure revision'),
 ('Files','KMZ/KML: WGS 84 Google Earth polygons for the site, both parcels and fixed pilots. GeoJSON: WGS 84 longitude/latitude. DXF: UTM zone 19S, metres. All four shapefiles: UTM zone 19S (EPSG:32719), UTF-8. xcity_site_maps.pdf: seven screening/reference map pages. boundary-revision.json: reproducible change record and hashes.'),
 ('Boundary revision','The two enclosed gaps between the supplied parcels are closed. The exact existing external outline is retained. Parcel A remains unchanged; Parcel B receives the internal seam land and its overlap with A is removed. New site geometry: 1,656.684229 km²; nominal project area: 1,656 km². Added internal seam: 0.304419 km². No external land was added. This is an organiser-authorised competition-data topology correction, not a cadastral certification.'),
 ('Fixed pilot areas','Agrivoltaic fields: approximately 13.9 km² of outline. Living area, phase one: approximately 2.48 km². Both are issued fixed conditions; their original geometry is unchanged.'),
 ('Screening limitations','Terrain and water maps are preliminary screening. Flood-sensitive areas are not verified design-flood boundaries, lakes or automatic permanent no-build areas. The added seam has terrain coverage but hydrological classification has not been reconstructed: do not treat it as confirmed non-flood-sensitive or developable land.'),
 ('Read together','Use the current Design Brief and site-package evidence index for sources, intended uses and missing inputs. The archive records earlier geometry only; it must not override the current issued revision. Contact: competition@xcity.ai.')]:
  story.extend([Paragraph(title,styles['Heading1' if not story else 'Heading2']),Paragraph(text,styles['BodyText']),Spacer(1,8)])
 SimpleDocTemplate(str(root/'README.pdf'),pagesize=(595.28,841.89),rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=38).build(story)
 # Re-render the map appendix from exactly the same source maps as the Design Brief.
 c=canvas.Canvas(str(root/'xcity_site_maps.pdf'),pagesize=(841.89,595.28));c.setTitle('XCITY issued site maps — seam-closure revision')
 for filename,title in [('site-context.png','Competition boundary and terrain'),('lead-zone.png','Fixed pilot fields and living area'),('elevation.png','Elevation'),('slope.png','Slope screening'),('drainage.png','DEM-derived drainage'),('flood-screen.png','Flood-sensitive screening (not a verified flood boundary)'),('buildable-screen.png','Low-slope screening; added seam hydrology remains unclassified')]:
  c.setFillColorRGB(.97,.96,.94);c.rect(0,0,842,596,fill=1,stroke=0);c.setFillColorRGB(.18,.18,.17);c.setFont('Helvetica',16);c.drawString(28,565,title)
  c.drawImage(str(AS/filename),100,38,width=642,height=507,preserveAspectRatio=True,anchor='c',mask='auto');c.setFont('Helvetica',8);c.drawString(28,20,'XCITY | Single issued geometry: '+json.loads((B/'boundary-revision.json').read_text())['revision']);c.showPage()
 c.save()
 with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(t)))
print(Z)
