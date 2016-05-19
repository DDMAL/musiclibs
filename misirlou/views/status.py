from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from celery.result import GroupResult, AsyncResult
from django.conf import settings

import scorched

class StatusView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        if not task_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        group_result = GroupResult.restore(task_id)

        if not group_result:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not group_result.ready():
            return Response({"status": settings.PROGRESS,
                             "progress": {"count": group_result.completed_count(),
                                          "total": len(group_result)}})
        else:
            commit_if_not_yet(group_result)
            succeeded = {}
            failed = {}
            failed_count = 0
            succeeded_count = 0

            if group_result.supports_native_join:
                results = group_result.join_native()
            else:
                results = group_result.join()

            for res in results:
                task_stat, man_id, rem_url, errors, warnings = res
                if task_stat == settings.SUCCESS:
                    succeeded_count += 1
                    succeeded[rem_url] = {'url': '/manifests/'+man_id,
                                          'warnings': warnings}
                else:
                    failed_count += 1
                    failed[rem_url] = {'errors': errors}

            d = {'succeeded': succeeded, 'succeeded_count': succeeded_count,
                 'failed': failed, 'failed_count': failed_count,
                 'total_count': len(group_result), 'status': settings.SUCCESS}
            return Response(d)

def commit_if_not_yet(group_result):
    """Commit results if they have not yet been commited."""
    for child in group_result.children:
        child = child.result
        if child[0] == 0:
            solr_conn = scorched.SolrInterface(settings.SOLR_SERVER)
            resp = solr_conn.query(id=child[1]).execute()
            if resp.result.numFound == 0:
                solr_conn.commit()
            return
