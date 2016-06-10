import tqdm
import ujson as json
import requests
import csv
import scorched

from django.conf import settings
from django.core.management.base import BaseCommand

UPLOAD_POLL_WAIT_SECS = 0.25
UPLOAD_PROGRESS_STEP = 5


class Command(BaseCommand):
    """Import a csv file into solr omr core"""
    help = "Import a csv file into the solr omr core."

    def add_arguments(self, parser):
        parser.add_argument("id", nargs=1, help="UUID of document in database"
                                                " to attach OMR data to.")
        parser.add_argument("csv_path", nargs=1, help="CSV file containing OMR data.")

    def handle(self, *args, **options):
        path = options['csv_path'][0]
        pk = options['id'][0]

        uri = settings.SOLR_SERVER + 'manifest/?q=' + pk
        resp = requests.get(uri).json()
        if resp['response']['numFound'] != 1:
            raise ValueError("Could not deference given ID in solr.")
        man = json.loads(resp['response']['docs'][0]['manifest'])
        seq = man['sequences'][0]['canvases']

        # Salzinnes specific mapping
        label_map = make_label_map(seq, "cdn-hsmu-m2149l4")
        upload_to_solr(path, pk, label_map)


def make_label_map(canvas_list, document):
    """Create map of folio labels to IIIF image urls."""
    label_map = {}
    if document == "cdn-hsmu-m2149l4":
        for can in canvas_list:
            label = can['label'].split(" ")[-1]
            label_map[label] = can['images'][0]['resource']['service']['@id']
    return label_map


def upload_to_solr(filename, document_id, label_map):
    """Commit a CSV file to solr"""
    solr_con = scorched.SolrInterface(settings.SOLR_OCR)
    num_lines = sum(1 for line in open(filename))

    last_folio = None
    last_url = None
    page = 0
    doc_lst = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in tqdm.tqdm(reader, total=num_lines):
            if row['folio'] != last_folio:
                last_folio = row['folio']
                solr_con.add(doc_lst)
                solr_con.commit()
                doc_lst = []
                page += 1
                last_url = label_map[last_folio]
            row['document_id'] = document_id
            row['image_url'] = last_url
            row['pagen'] = page
            # More salzinne specific commands.
            del row['siglum_slug']
            del row['folio']
            del row['type']
            doc_lst.append(row)
