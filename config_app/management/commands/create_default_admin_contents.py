from django.core.management.base import BaseCommand
from config_app.models import AdminContent


class Command(BaseCommand):
    help = 'Create contents for admin'

    def handle(self, *args, **options):
        terms = AdminContent.objects.filter(title='terms&conditions')
        if not terms:
            terms = AdminContent(
                title='terms&conditions',
                content='Please use admin panel to update Terms and Conditions.'
            )
            terms.save()
            print("Terms and conditions created.")
        else:
            print("Terms and conditions exist.")
        privacy = AdminContent.objects.filter(title='privacypolicy')
        if not privacy:
            privacy = AdminContent(
                title='privacypolicy',
                content='Please use admin panel to update Privacy policy.'
            )
            privacy.save()
            print("Privacy policy created.")
        else:
            print("Privacy policy exist.")
        pdf_note = AdminContent.objects.filter(title='pdfnote')
        if not pdf_note:
            pdf_note = AdminContent(
                title='pdfnote',
                content=(
                    "NOTE: IT IS ALWAYS THE RESPONSIBILITY OF "
                    "THE OPERATOR THAT THE VEHICLE IS IN A ROADWORTHY "
                    "CONDITION BEFORE BEING USED ON THE ROAD"))
            pdf_note.save()
            print("PDF note created.")
        else:
            print("PDF note exist.")
