from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from celery.result import AsyncResult
from rest_framework.reverse import reverse


class StatusView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        if not task_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        celery_task = AsyncResult(task_id)
        task_status = celery_task.status

        if task_status == 'PENDING':
            return Response(status.HTTP_404_NOT_FOUND)

        if task_status == 'SENT':
            return Response({'status': 'PROCESSING'})

        if task_status == 'SUCCESS':
            manifest_url = reverse('manifest-detail', request=request,
                                   args=[task_id])
            return Response({'Location': manifest_url, 'status': 'SUCCESS'},
                            status=status.HTTP_303_SEE_OTHER)

        data = {'status': task_status}
        if celery_task.traceback:
            data['trace'] = celery_task.traceback

        return Response(data)
