#!/usr/bin/python
# -*- coding: UTF-8 -*-
""" Script for creating a IIIF manifest from the cantus Salzinmes files.

Requires the factory module from
https://github.com/IIIF/presentation-api/tree/master/implementations/manifest-factory

Make sure to set the EXPORT_DIR to something sensible before running.
"""
import sys
try:
    import factory
except ImportError as e:
    print("You need the manifest factory module from"\
    " https://github.com/IIIF/presentation-api/tree/master/implementations/manifest-factory\n")
    raise


BASE_METADATA_URI = "http://dev-cantus.simssa.ca/manuscript/133/"
BASE_IMAGE_URI = "http://dev-cantus.simssa.ca/iiif/image/srv/images/cantus/cdn-hsmu-m2149l4/"

EXPORT_DIR = "/home/lexpar/Documents/DDMAL/salzinnes_man"

fac = factory.ManifestFactory()
fac.set_base_metadata_uri(BASE_METADATA_URI)
fac.set_base_metadata_dir(EXPORT_DIR)
fac.set_base_image_uri(BASE_IMAGE_URI)
fac.set_iiif_image_info(2.0, 2)
fac.set_debug("error")

manifest = fac.manifest(label="Salzinnes, CDN-Hsmu M2149.L4")
manifest.description = """Cistercian antiphonal from the Abbey of Salzinnes, Namur, in the Diocese of Liège. Manuscript produced on vellum and completed in 1554 and 1555. Square notation on red, 4-line staves. Monastic cursus. 238 folios with two lacunae (Volume I, f.125 and Volume II, f.32) and several inserted folios with full-page illuminations (between ff.45 and 46, ff. 50 and 51, and ff.117 and 118). 61.5 x 39.5 x 14.5 cm.
Liturgical Occasions “at a glance” (refer to the index for complete contents):
    Volume I: Ff. 1r-126v: Winter Temporale. 1r, Saturday before the first Sunday of Advent; 1v, Advent; 28r, Great “O” Antiphons; 29r, Nativity; 45v, Epiphany; 55r, Ferial Office; 69v, Septuagesima; 101v, Lent; 121r, Holy Saturday.
    122v, Te Deum; 123v, Te decet laus; 123v, Responsory tones; 124v, Vigil for Easter; 125r, Lacuna; 126r, full-page illumination of The Resurrection; 126v, full-page illumination of Christ in Majesty.
    127r-198v: Winter Sanctorale (except for the addition of several antiphons for Roch and Hubert). 127r, Andrew; 134r, Conception or Birth of Mary; 142v, Stephen; 147v, John the Evangelist; 152v, Holy Innocents; 157r, Agnes; 162r, Conversion of Paul; 168v, Purification of the Virgin; 174r, Agatha; 179r, Chair of Peter; 185r, Benedict; 191v, Annunciation of Mary; 197v, Roch; 198r, Hubert.
    198v, empty staves.
    Volume II: Ff. 1r-24v: Common of Saints. 1r, Common of Apostles; 5v, Common of Two Apostles; 7v, Feast of the Evangeslists; 14r, Canticles; 17r, Common of one Martyr; 23v, Feast of several Martyrs; 29r, Feast of one Confessor who is a Pope; 32r-32v, Lacuna; 34v, Feast of one Confessor not a Pope; 35r, Common of several Confessors; 35r, Feast of one Virgin.
    40v, Colophon.
The colophon on f.40v in Volume II reads: “Che libure feist faire Dame Julienne de glymes prieuse de Salsines Jadit grande chantre de ce lieu. Pryes dieu pour elle.” The date of 1554 appears on ff.122r and 197r in Volume I, and on f.16v in Volume II. The date of 1555 appears at the end of Volume I on f.197v and the end of Volume II on f.40v. According to the colophon the book was commissioned by Dame Julienne de Glymes, prioress and former cantrix of the Cistercian Abbey of Salzinnes, Namur, in present day Belgium, likely with parts of it completed in 1554 and the rest in 1555. Founded in 1196-97 by Philip the Noble Count of Namur, the Abbey was incorporated in the Cistercian Order in 1204 under the Diocese of Liège. It was destroyed by the French Revolutionary armies in 1795.
The Salzinnes Antiphonal was likely acquired in the 1840s or 1850s in France by Bishop William Walsh, the first Archbishop for the Diocese of Halifax. It was donated to the Patrick Power Library, Saint Mary’s University by Archbishop James M. Hayes in 1975.
Painted in a bright palette in gouache, the Salzinnes Antiphonal contains six full-page illuminations and six historiated initials and includes several scenes depicting multiple narratives from the Bible. The most significant feature of the Antiphonal is the full-length portraits of thirty-four nuns with their names in cursive and block script, some with patrons’ coats-of-arms. In addition, three different religious orders are represented: Cistercians, Carmelites and Benedictines, in honour of the de Glymes family.
Selected Bibliography
Dietz, Judith. Centuries of Silence: The Discovery of the Salzinnes Antiphonal. MA thesis, Saint Mary’s University, Halifax 2006.
Indexed by Judy Dietz, on behalf of Saint Mary’s University, aided in liturgical and musical matters by Jennifer Bain and Meredith Evans, Dalhousie University, Halifax, Nova Scotia, with editorial assistance from Debra Lacoste, The University of Western Ontario.
"""
manifest.set_metadata({
    'Date': "1554-5",
    'Provenance': 'Salzinnes',
    'Siglum': 'CDN-Hsmu M2149.L4'})

seq = manifest.sequence()
with open("salzinne_files") as files:
        for f in files:
            f=f.strip('\n')
            page = f.replace('cdn-hsmu-m2149l4_', '')
            page = page.replace('.jp2', '')
            print("Creating {}".format(page))
            cvs =  seq.canvas(label="Folio {}".format(page), ident='folio-{}'.format(page))
            cvs.set_image_annotation(f, iiif=True)

manifest.toFile()
canvases = manifest.sequences[0].canvases
for c in canvases:
    c.toFile()
