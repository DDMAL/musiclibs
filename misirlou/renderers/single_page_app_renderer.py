from django.conf import settings
from rest_framework.renderers import TemplateHTMLRenderer
import copy

class SinglePageAppRenderer (TemplateHTMLRenderer):
    """
    Renderer to display the single page app with the appropriate bootstrapped
    data
    """

    template_name = 'single_page_app.html'

    def resolve_context(self, data, request, response):
        """
        Inject the data into the context object under its own key, "view_data"

        This is similar to what happens in generic Django API views with
        context_object_name. Django Rest Framework may provide a more ergonomic
        way to do this in the future.

        See https://github.com/tomchristie/django-rest-framework/issues/1673
        """
        context = super().resolve_context(data, request, response)
        """
        This was causing infinite recursion in the new restframework version,
        which appears to be fixed by making a copy of the data dict rather
        than simply referencing it. I don't have a deep understanding of this
        issue, so please feel free to correct to a more graceful solution if
        one exists. -AP
        """
        context.update({
            'view_data': copy.copy(data),
            'JSPM_USE_UNBUNDLED': settings.JSPM_USE_UNBUNDLED
        })
        return context
