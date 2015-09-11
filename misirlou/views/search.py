from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(('GET',))
def search(request):
    if request.GET.get('q'):
        return Response({'q': request.GET.get('q')})
    else:
        return Response({'error': 'Did not provide query (q).'},
                        status=status.HTTP_400_BAD_REQUEST)
