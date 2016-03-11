from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from celery.result import AsyncResult
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

        if task_result.get('status') in [settings.ERROR, settings.SUCCESS]:
            return Response(task_result)

        if celery_task.state == settings.PROGRESS:
            meta = celery_task._get_task_meta()
            return Response({'status': settings.PROGRESS, 'progress': meta['result']})

        if celery_task.traceback:
            data = {'status': settings.ERROR,
                    'error': "server error",
                    'error_type':  task_result['exc_type']}
            return Response(data)

        return Response({'status': settings.PROGRESS})
