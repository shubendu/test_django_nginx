import base64
from django import template

register = template.Library()


@register.filter
def get_image_file_as_base64_data(CONTRACTOR_LOGO):
    """
    This template tag takes a image object and returns a base64 encoded string.
    """
    image_bytes = CONTRACTOR_LOGO.read()
    base64_bytes = base64.b64encode(image_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string
