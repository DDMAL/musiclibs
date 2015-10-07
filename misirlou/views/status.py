from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from celery.result import AsyncResult
from rest_framework.reverse import reverse
from django.conf import settings

class StatusView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        if not task_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        celery_task = AsyncResult(task_id)
        task_result = celery_task.result if celery_task.result else {}

        if celery_task.status == "PENDING":
            return Response(status=status.HTTP_404_NOT_FOUND)

        if task_result.get('status') == settings.ERROR:
            return Response({'status': settings.ERROR,
                             'error': task_result.get('error')})

        if task_result.get('status') == settings.SUCCESS:
            manifest_url = reverse('manifest-detail', request=request,
                                   args=[task_result.get('uuid')])
            response = {'status': settings.SUCCESS, 'location': manifest_url}
            if task_result.get('warnings'):
                response['warnings'] = task_result.get('warnings')
            return Response(response, status=status.HTTP_303_SEE_OTHER,
                            headers={'Location': manifest_url})

        data = {'status': settings.PROGRESS}
        if celery_task.traceback:
            data['status'] = settings.ERROR
            data['trace'] = celery_task.traceback
        if celery_task.result:
            data.update(celery_task.result)
        return Response(data)
