import factory
import IPython

BASE_METADATA_URI = "https://images.simssa.ca/iiif/manuscripts/liber/"
BASE_IMAGE_URI = "https://images.simssa.ca/iiif/image/liber/"

EXPORT_DIR = "/home/lexpar/Documents/DDMAL/salzinnes_man"

fac = factory.ManifestFactory()
fac.set_base_metadata_uri(BASE_METADATA_URI)
fac.set_base_metadata_dir(EXPORT_DIR)
fac.set_base_image_uri(BASE_IMAGE_URI)
fac.set_iiif_image_info(2.0, 2)
fac.set_debug("error")

manifest = fac.manifest(label="The Liber Usualis")
manifest.description = """A compendium of the most common chants used by the Catholic Church.
This document has had experimental Optical Music and Text Recognition applied to it
to make it's contents searchable."""
manifest.related = "http://ddmal.music.mcgill.ca/research/omr/Search_the_Liber_Usualis"
manifest.metadata = {"Date": "1961", "Location": "Belgium"}

seq = manifest.sequence()
for num in range(1,2341):
    num = "{0:04d}".format(num)
    page = "liber_{}".format(num)
    print("Creating {}".format(page))
    cvs =  seq.canvas(label="Page {}".format(num), ident='page-{}'.format(num))
    cvs.set_image_annotation(page+".tif", iiif=True)

manifest.toFile()
canvases = manifest.sequences[0].canvases
for c in canvases:
    c.toFile()