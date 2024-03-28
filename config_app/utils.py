from django.contrib.sites.shortcuts import get_current_site


def get_domain(request):
    return get_current_site(request).domain


def get_protocol(request):
    return 'https' if request.is_secure() else 'http'
