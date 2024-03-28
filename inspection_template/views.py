import random

from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.views import View

from inspection_template.mixins import AjaxRequiredMixin
from inspection_template.models import (
    Question, Category, Template)
from inspection_template.utils import (
    camel_case,
    update_category_data,
    update_template_name,
    update_question_data
)
from inspection_template.questions import (
    aServiceQuestions,
    brakingSystemQuestions,
    cabQuestions,
    drawbarTrailers,
    engineServiceQuestions,
    groundLevelQuestions,
    otherQuestions,
    trailerBrakes,
    trailerLampsReflectors,
    trailerSuspension,
    trailerTyreQuestions,
    underTrailerQuestions,
    underVehicleQuestions,
    category_id_label_map
)


def choose_vehicle_type(request):
    """View for choosing vehicle type."""
    return render(request, 'inspection_template/choose_vehicle_type.html')


def create_custom_template(request):
    """View for creating custom template."""
    context = {
        'cabQuestions': cabQuestions,
        'groundLevelQuestions': groundLevelQuestions,
        'underVehicleQuestions': underVehicleQuestions,
        'brakingSystemQuestions': brakingSystemQuestions,
        'aServiceQuestions': aServiceQuestions,
        'engineServiceQuestions': engineServiceQuestions,
        'otherQuestions': otherQuestions,
        'underTrailerQuestions': underTrailerQuestions,
        'trailerSuspension': trailerSuspension,
        'drawbarTrailers': drawbarTrailers,
        'trailerBrakes': trailerBrakes,
        'trailerLampsReflectors': trailerLampsReflectors,
        'trailerTyreQuestions': trailerTyreQuestions,
    }
    vehicle_type = request.GET.get('vehicle_type')
    if vehicle_type:
        context['vehicle_type'] = vehicle_type

    if request.method == 'POST':
        exclude_keys = ['csrfmiddlewaretoken', 'name', 'sort_order', 'tyre_brake_section']
        data = request.POST
        name = data.get('name')
        include_tyre_brake_section = bool(data.get('tyre_brake_section', False))
        category_sort_order = data.getlist('sort_order')
        category_sort_order = list(filter(None, category_sort_order))
        category_ids = []
        db_category_label_id = {}  # use this to avoid duplicate category creation
        data = dict(data)  # convert QueryDict to dict
        for key, value in data.items():
            model_attribute = key.split('$')[0]
            category_id_label = category_id_label_map(model_attribute)
            if not category_id_label:
                category_id = camel_case(model_attribute)
                category_label = model_attribute
            else:
                category_id = category_id_label.get('id')
                category_label = category_id_label.get('label')
            if category_label in exclude_keys:
                continue
            if category_label in db_category_label_id.keys():
                category_obj = Category.objects.get(
                    id=db_category_label_id[category_label])
            else:
                category_obj = Category.objects.create(
                    category_id=category_id,
                    label=category_label,
                )
                db_category_label_id[category_label] = category_obj.id
                if category_sort_order:
                    category_obj.sort_order = category_sort_order.pop(0)
                    category_obj.save()
                category_ids.append(category_obj.id)
            question_ids = []
            if model_attribute not in exclude_keys:
                if value == '':
                    continue
                for val in value:
                    question_text, im_array = val.split('@')
                    im_array = None if im_array == '-' else im_array
                    obj = Question.objects.create(
                        question=question_text,
                        im_array=im_array,
                    )
                    question_ids.append(obj.id)
            category_obj.questions.add(*question_ids)
        obj = Template.objects.create(name=name, include_tyre_break_section=include_tyre_brake_section)
        obj.category.add(*category_ids)
        messages.success(
            request,
            'Template created successfully, please select from the dropdown'
        )
        return redirect('admin:inspection_template_inspectiontemplateprofile_add')
    return render(request, 'inspection_template/template_form.html', context)


class EditTemplateView(UserPassesTestMixin, View):
    """
    Class-based view for editing a template.

    GET: Display the template edit form.
    POST: Handle the form submission and update the template data.
    """

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        # When the user fails the test we redirect them to the login page
        return redirect('login')

    def get(self, request, template_id):
        """
        Handle GET requests and display the template edit form.

        Args:
            request (HttpRequest): The HTTP request object.
            template_id (int): The ID of the template to edit.

        Returns:
            HttpResponse: The rendered template edit form.
        """
        template_obj = get_object_or_404(Template, id=template_id)
        context = {
            'name': template_obj.name,
            'id': template_obj.id,
            'categories': template_obj.category.all(),
            'tyre_brake_section_enabled': template_obj.include_tyre_break_section,
        }
        return render(request, 'inspection_template/template_edit_form.html', context)

    def post(self, request, template_id):
        """
        Handle POST requests and update the template data.

        Args:
            request (HttpRequest): The HTTP request object.
            template_id (int): The ID of the template to edit.

        Returns:
            HttpResponseRedirect: A redirect to the template profile page if the template is updated successfully.
        """
        data = request.POST
        template_obj = get_object_or_404(Template, id=template_id)
        cats_updated = update_category_data(template_obj, data)
        template_updated = update_template_name(template_obj, data)
        questions_updated = update_question_data(template_obj, dict(data))
        if cats_updated or template_updated or questions_updated:
            messages.success(request, 'Template updated successfully.')

        redirect_url = "admin:inspection_template_inspectiontemplateprofile_changelist"
        return redirect(redirect_url)

class DeleteTemplateView(UserPassesTestMixin, View):
    """
    Class-based view for deleting a template.

    GET: Display the template delete confirmation page.
    POST: Handle the form submission and delete the template.
    """

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        # When the user fails the test we redirect them to the login page
        return redirect('login')

    def get(self, request, template_id):
        """
        Handle GET requests and display the template delete confirmation page.

        Args:
            request (HttpRequest): The HTTP request object.
            template_id (int): The ID of the template to delete.

        Returns:
            HttpResponse: The rendered template delete confirmation page.
        """
        template_obj = get_object_or_404(Template, id=template_id)
        template_obj.delete()
        messages.success(request, 'Template deleted successfully.')
        redirect_url = "admin:inspection_template_inspectiontemplateprofile_changelist"
        return redirect(redirect_url)


def custom_category_template(request):
    template_name = 'inspection_template/include/custom_category.html'
    context = {}
    context['id'] = request.GET.get('id', 0)
    if request.GET.get('type') == 'edit':
        # create a random number to avoid conflict with other categories
        random_number = random_number = random.randint(1, 1000)
        context['id'] = f"newCat{random_number}"
        template_name = 'inspection_template/include/custom_category_for_edit.html'
    return render(request, template_name, context)


def custom_question_template(request):
    template_name = 'inspection_template/include/custom_question.html'
    context = {
        'randomNumber': request.GET.get('randomNumber', 0),
        'rowId': request.GET.get('rowId', 0),
        'label': request.GET.get('label', 0)
    }
    if request.GET.get('type') == 'edit':
        template_name = 'inspection_template/include/custom_question_for_edit.html'
    return render(request, template_name, context)


class DeleteObjectView(AjaxRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        obj_id = request.GET.get('id')
        object_type = request.GET.get('type')
        
        # Mapping of types to their respective Django models
        model_map = {
            'question': Question,
            'category': Category,
        }

        # Get the model class based on the object_type parameter
        model_cls = model_map.get(object_type)
        if model_cls is None:
            return JsonResponse({'status': 'error', 'message': 'Invalid object type.'})

        # Attempt to delete the specified object
        try:
            obj = model_cls.objects.get(id=obj_id)
            obj.delete()
            return JsonResponse({'status': 'success', 'message': f'{object_type.capitalize()} deleted successfully.'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': f'{object_type.capitalize()} does not exist.'})
