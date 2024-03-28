from django.contrib import messages
from users.models import Profile
from django.contrib.auth import login
from users.mixins import UserTypeMixin
from config_app.choices import UserTypes


def check_user_is_contractor(user, request):
    # @ todo : check if user is contractor
    user_type_obj = UserTypeMixin()
    user_type = user_type_obj.get_user_type(user, request)
    if "contractor_admin" in user_type:
        profile = Profile.objects.get(user=user)
        return True, profile.contractor
    else:
        return False, None


def check_contractor_login(request, user):
    if not user:
        messages.error(request, "Invalid username or password.")
        return False
    elif not user.is_active:
        messages.error(request, "This user is inactive.")
        return False

    user_type_obj = UserTypeMixin()
    user_type = user_type_obj.get_user_type(user, request)

    if any(x in user_type for x in [UserTypes.contractor_admin, UserTypes.viewer, UserTypes.inspector]):
        login(request, user)
        request.session['user_type'] = user_type
        request.session['contractor_id'] = user.profile.contractor.id
        return True
    else:
        messages.error(request, "This user is not a contractor admin.")
        return False
    return False
