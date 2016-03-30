from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from celery.result import AsyncResult, result_from_tuple
from django.conf import settings
from django.core.cache import cache
from misirlou.tasks import import_manifest


class StatusView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        if not task_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        celery_task = AsyncResult(task_id)
        task_result = celery_task.result if celery_task.result else {}
        count, succeeded, failed = 0, 0, 0
        completed = False
        import pdb
        pdb.set_trace()
        # Return the task result if all sub-processes have finished
        if task_result.get('status') == settings.SUCCESS:
            return Response(task_result)

        # # Otherwise, count how many sub-processes have finished.
        #
        # elif celery_task.children:
        #     for res in celery_task.children:
        #         if res.ready():
        #             count += 1
        #     task_result['count'] = count
        #     if count == celery_task.result['total']:
        #         completed = True
        #
        # # If all sub-processes have finished, compose results.
        # if completed:
        #     task_result['status'] = settings.SUCCESS
        #     task_result['succeeded'] = {}
        #     task_result['failed'] = {}
        #     for res in celery_task.children:
        #         task_stat, man_id, rem_url, errors, warnings = res.result
        #         if res.result[0] == 0:
        #             succeeded += 1
        #             d = {'status': task_stat,
        #                  'uuid': man_id,
        #                  'url': '/manifests/{}'.format(man_id),
        #                  'warnings': warnings}
        #             task_result['succeeded'][res.result[2]] = d
        #         else:
        #             d = {'errors': errors,
        #                  'warnings': warnings,
        #                  'status': task_stat,
        #                  'uuid': man_id}
        #             failed += 1
        #             task_result['failed'][res.result[2]] = d
        #
        #         res.forget()
        #
        #     meta = celery_task._get_task_meta()
        #     meta['result'] = task_result
        #     meta['status'] = settings.SUCCESS
        #     del meta['children']
        #
        #     import_manifest.update_state(task_id=task_id,
        #                                  meta=meta)
        #     return Response(task_result)



        if celery_task.status == "PENDING":
            return Response(status=status.HTTP_404_NOT_FOUND)

        if task_result.get('status') in [settings.ERROR, settings.SUCCESS]:
            return Response(task_result)

        if task_result.get('status') == settings.PROGRESS:
            return Response({'status': settings.PROGRESS, 'progress': count,
                             'total': task_result['total']})

        if celery_task.traceback:
            data = {'status': settings.ERROR,
                    'error': "server error",
                    'error_type':  task_result['exc_type']}
            return Response(data)

        return Response({'status': settings.PROGRESS})
