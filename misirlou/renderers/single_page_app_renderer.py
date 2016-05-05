from django.conf import settings
from rest_framework.renderers import TemplateHTMLRenderer

class SinglePageAppRenderer (TemplateHTMLRenderer):
    """
    Renderer to display the single page app with the appropriate bootstrapped
    data
    """

    template_name = 'single_page_app.html'

    def resolve_context(self, data, request, response):
        """
        Pass the data into the context object under a key, `view_data`,
        and pass in the client-side debug configuration.
        """
        view_data = super().resolve_context(data, request, response)

        return {
            'view_data': view_data,
            'DEBUG_CLIENT_SIDE': settings.DEBUG_CLIENT_SIDE
        }
