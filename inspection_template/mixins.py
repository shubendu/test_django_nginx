from django.http import JsonResponse


class AjaxRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            return JsonResponse({'status': 'error', 'message': 'Invalid request type.'})
        return super().dispatch(request, *args, **kwargs)
