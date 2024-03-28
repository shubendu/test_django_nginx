from django.template.defaulttags import register
from dateutil.parser import parse


@register.filter
def get(dict, key):
    return dict.get(key)


@register.filter
def jsondate(datestring):
    return parse(datestring)


@register.filter
def findTread(wheels, options):
    # return wheels[0]['side']
    [side, position, treadPosition] = options.split()
    tread = [wheel['tread'] for wheel in wheels if (
        wheel['side'] == side and wheel['position'] == position)]
    if not tread or not tread[0] or not tread[0][treadPosition]:
        return '-'
    return '{} mm'.format(tread[0][treadPosition])


@register.filter
def findPressure(wheels, options):
    # return wheels[0]['side']
    [side, position, units] = options.split()
    tread = [wheel['pressure'] for wheel in wheels if (
        wheel['side'] == side and wheel['position'] == position)]
    if not tread or not tread[0] or not tread[0][units]:
        return '-'
    return '{}'.format(tread[0][units])


category_ids = [
    "cab",
    "groundLevel",
    "underVehicle",
    "underTrailer",
    "trailerSuspension",
    "drawbarTrailers",
    "trailerBrakes",
    "brakingSystem",
    "trailerLampsReflectors",
    "aService",
    "engineService"
]


@register.filter
def failedItems(categories):
    rectificationsFail = []
    for id in category_ids:
        if id not in categories:
            continue
        category = categories[id]
        for question in category['questions']:
            if 'value' in question and question['value'] == 'failed':
                rectificationsFail.append(question)
    return rectificationsFail


@register.filter
def monitoredItems(categories):
    rectificationsMonitor = []
    for id in category_ids:
        if id not in categories:
            continue
        category = categories[id]
        for question in category['questions']:
            if 'value' in question and question['value'] == 'monitor':
                rectificationsMonitor.append(question)
    return rectificationsMonitor


@register.filter
def camel_case(label):
    # Remove spaces from the label
    label = label.replace(' ', '')

    # Split the label into words
    words = label.split('_')

    # Capitalize the first letter of each word (except the first word)
    camel_case_words = [words[0]] + [word.capitalize() for word in words[1:]]

    # Join the words together without spaces
    camel_case_string = ''.join(camel_case_words)

    return camel_case_string
