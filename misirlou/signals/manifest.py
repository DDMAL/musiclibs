from django.dispatch import Signal

manifest_imported = Signal(providing_args=['id', 'local_url'])
