from djchoices import ChoiceItem
from djchoices import DjangoChoices


class UserTypes(DjangoChoices):
    super_admin = ChoiceItem('super_admin', 'super_admin')
    contractor_admin = ChoiceItem('contractor_admin', 'contractor_admin')
    inspector = ChoiceItem('inspector', 'inspector')
    viewer = ChoiceItem('viewer', 'viewer')


class VehicleTypes(DjangoChoices):
    trailer = ChoiceItem('trailer', 'trailer')
    powered_vehicle = ChoiceItem('powered_vehicle', 'powered_vehicle')
