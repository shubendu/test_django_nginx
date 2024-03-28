from django.core.management.base import BaseCommand
from users.models import Contractor
from inspection_template.models import (
    InspectionTemplateProfile,
    Template,
    Category,
    Question,
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


class Command(BaseCommand):
    help = 'Create default templates for Powered vehicle and Trailer'

    def create_template(self, vehicle_type, context):
        category_ids = []
        sort_order = 1
        for model_attribute, question_im_array in context.items():
            category_id_label = category_id_label_map(model_attribute)
            category_id = category_id_label.get('id')
            category_label = category_id_label.get('label')
            category_obj = Category.objects.create(
                category_id=category_id,
                label=category_label,
                sort_order=sort_order)
            question_ids = []
            for question in question_im_array:
                label = question['label']
                im_array = question.get('im', 0)
                question_obj = Question.objects.create(
                    question=label,
                    im_array=im_array,
                )
                question_ids.append(question_obj.id)
            category_obj.questions.add(*question_ids)
            category_ids.append(category_obj.id)
            sort_order += 1
        template_obj = Template.objects.create(
            name=f"Default {vehicle_type} Template")
        template_obj.category.add(*category_ids)
        return template_obj

    def handle(self, *args, **options):
        powered_vehicle_attributes = {
            'cabQuestions': cabQuestions,
            'underVehicleQuestions': underVehicleQuestions,
            'groundLevelQuestions': groundLevelQuestions,
            'brakingSystemQuestions': brakingSystemQuestions,
            'engineServiceQuestions': engineServiceQuestions,
            'aServiceQuestions': aServiceQuestions,
            'otherQuestions': otherQuestions,
        }
        trailer_attributes = {
            'underTrailerQuestions': underTrailerQuestions,
            'trailerSuspension': trailerSuspension,
            'drawbarTrailers': drawbarTrailers,
            'trailerBrakes': trailerBrakes,
            'brakingSystemQuestions': brakingSystemQuestions,
            'trailerLampsReflectors': trailerLampsReflectors,
            'aServiceQuestions': aServiceQuestions,
            'trailerTyreQuestions': trailerTyreQuestions,
            'otherQuestions': otherQuestions,
        }
        vehicle_types = ["Trailer", "Powered Vehicle"]
        default_profiles = []

        for vehicle_type in vehicle_types:
            if vehicle_type == "Trailer":
                template_obj = self.create_template(
                    vehicle_type, trailer_attributes)
                trailer_obj = InspectionTemplateProfile.objects.create(
                    name="Default Trailer Profile",
                    vehicle_type="trailer",
                    template=template_obj
                )
                self.stdout.write(
                    self.style.SUCCESS("Created default Trailer profile")
                )
                default_profiles.append(trailer_obj.id)
            else:
                template_obj = self.create_template(
                    vehicle_type, powered_vehicle_attributes)
                powered_vehicle_obj = InspectionTemplateProfile.objects.create(
                    name="Default Powered Vehicle Profile",
                    vehicle_type="powered_vehicle",
                    template=template_obj
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        "Created default Powered Vehicle profile")
                )
                default_profiles.append(powered_vehicle_obj.id)
        contractors = Contractor.objects.all()
        for contractor in contractors:
            contractor.inspection_template.add(*default_profiles)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Added default profiles to {contractor.name}")
            )

