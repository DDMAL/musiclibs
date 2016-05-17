import requests

from rest_framework import generics
from rest_framework import status
from django.http import HttpResponse


class ImageProxy(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        """Return the image at a given url."""
        img_url = request.GET.get('img')
        if not img_url:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        referer = "{0}://{1}".format(request.scheme, request.get_host())
        r = requests.get(img_url, stream=True, headers={'referer': referer})

        # 404 if the mime-type is not some kind of image.
        if 'image' not in r.headers['content-type']:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

        if 200 <= r.status_code < 300:
            return HttpResponse(r.iter_content(2048), content_type=r.headers['content-type'])
        else:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)