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
        Inject the data into the context object under its own key, "view_data"

        This is similar to what happens in generic Django API views with
        context_object_name. Django Rest Framework may provide a more ergonomic
        way to do this in the future.

        See https://github.com/tomchristie/django-rest-framework/issues/1673
        """
        context = super().resolve_context(data, request, response)
        context.update({
            'view_data': data,
            'JSPM_USE_UNBUNDLED': settings.JSPM_USE_UNBUNDLED
        })
        return context
