from django.shortcuts import redirect
from django.templatetags.static import static
from django.views.generic import TemplateView
from users.mixins import UserTypeMixin


class IndexView(TemplateView, UserTypeMixin):
    template_name = 'pages/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_type'] = self.get_user_type(self.request.user)
        return context


def FaciconView(request):
    return redirect(static('pages/img/icon.png'))
