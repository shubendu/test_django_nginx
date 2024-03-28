import json
from re import sub
from config_app.utils import get_domain, get_protocol
from inspections.models import InspectionItem
from inspections.models import InspectionItemType


def snake_case(s):
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                s.replace('-', ' '))).split()).lower()


trailer_details = {
    "type": {
        "id": "trailer",
        "label": "Trailer",
        "icon": "./assets/icon/trailer.svg",
        "url": "http://18.234.9.101:8000/api/item-types/2/",
        "ref_field": "ministry_no"
    },
    "ref": "MINISTRY_NO",
    "ministry_no": "MINISTRY_NO",
    "year": "2017-04-14T14:46:14.664+05:30",
    "chassis_no": "CHESIS_NO",
    "make": "CHECKMAKE_DAF",
    "model": "CHECK_MODEL",
    "description": "this is a test description for test vehicle",
    "fleet_no": "001",
    "dvsa_id": "9090400",
    "body_type": "HEAVY BODY",
    "operator_name": "test_operator name",
    "mot_exp": "2022-05-15T14:46:04.551+05:30",
    "axles": [
        # {"doubleWheel": false},
        # {"doubleWheel": false},
        # {"doubleWheel": true}
    ],
    "spares": 2
}

powered_vehicle_details = {
    "type": {
        "id": "powered-vehicle",
        "label": "Powered Vehicle",
        "icon": "./assets/icon/truck-moving.svg",
        "url": "http://18.234.9.101:8000/api/item-types/1/",
        "ref_field": "registration_no"
    },
    "ref": "REG NO",
    "registration_no": "REG NO",
    "make": "CKECK MAKE POW VEH",
    "model": "MODEL CHECK",
    "description": "some dec here",
    "tacho_2yr": "tachography 2 ",
    "tacho_6yr": "tachography 6",
    "fleet_no": "fleet number ",
    "operator_name": "opeator name",
    "year": "2014-04-18T11:51:27.545+05:30",
    "mot_exp": "2019-04-18T11:51:27.625+05:30",
    "axles": [
        # {"doubleWheel": true},
        # {"doubleWheel": true},
        # {"doubleWheel": true},
        # {"doubleWheel": true},
        # {"doubleWheel": true}
    ],
    # "spares": 3
}


def check_excel_file_extension(file):
    """ Check if the file is an excel file """
    if file.name.endswith('.xlsx'):
        return True
    else:
        return False


def get_vehicle_json(request, vehicle_details):
    """ Get vehicle json """

    vehicle_type = vehicle_details["type"]
    protocol = get_protocol(request)
    domain = get_domain(request)
    vehicle_json_details = {}
    vehicle_type_dict = {}
    ref = ""
    red_flag = False
    error_dict = dict()
    row_number = vehicle_details["row_number"]
    if vehicle_type == "Trailer":
        vehicle_type_dict = {
            "id": "trailer",
            "label": "Trailer",
            "icon": "./assets/icon/trailer.svg",
            "url": f"{protocol}://{domain}/api/item-types/2/",
            "ref_field": "ministry_no"
        }
        ministry_no = vehicle_details["ministry_number"]
        if ministry_no is None:
            red_flag = True
            error_dict[f"row_{row_number}_ministry"] = "Ministry no is required"
        ref = ministry_no
        vehicle_json_details["ministry_no"] = ministry_no
    elif vehicle_type == "Powered Vehicle":
        vehicle_type_dict = {
            "id": "powered-vehicle",
            "label": "Powered Vehicle",
            "icon": "./assets/icon/truck-moving.svg",
            "url": f"{protocol}://{domain}/api/item-types/1/",
            "ref_field": "registration_no"
        }
        registration_no = vehicle_details["registration_number"]
        if registration_no is None:
            red_flag = True
            error_dict[f"row_{row_number}_registration"] = "Registration no is required"
        ref = registration_no
        vehicle_json_details["registration_no"] = registration_no
    chassis_no = vehicle_details["chassis_number"]
    make = vehicle_details["make"]
    model = vehicle_details["model"]
    year = vehicle_details["year"]
    description = vehicle_details["description"]
    fleet_no = vehicle_details["fleet_number"]
    dvsa_id = vehicle_details["dvsa_id_number"]
    body_type = vehicle_details["body_type"]
    operator_name = vehicle_details["operator_name"]
    mot_exp = vehicle_details["mot_expiry"]
    vehicle_json_details.update({
        "type": vehicle_type_dict,
        "ref": ref,
        "chassis_no": chassis_no,
        "make": make,
        "model": model,
        "year": year,
        "description": description,
        "fleet_no": fleet_no,
        "dvsa_id": dvsa_id,
        "body_type": body_type,
        "operator_name": operator_name,
        "mot_exp": mot_exp
    })
    if make is None:
        red_flag = True
        error_dict[f"row_{row_number}_make"] = "Make is required"
    if model is None:
        red_flag = True
        error_dict[f"row_{row_number}_model"] = "Model is required"
    if year is None:
        red_flag = True
        error_dict[f"row_{row_number}_year"] = "Year is required"
    if operator_name is None:
        red_flag = True
        error_dict[f"row_{row_number}_operator_name"] = "operator_name is required"
    ref_exists = InspectionItem.objects.filter(ref=ref).exists()
    if ref_exists:
        red_flag = True
        error_dict[f"row_{row_number}"] = "Ministry/Registration number already exists"
    if red_flag:
        return False, error_dict

    return True, vehicle_json_details


def create_instances_from_excel_data(request, headings, excel_data):
    """ Create instances from excel data """
    headings = [snake_case(heading) for heading in headings]
    bulk_item_list = list()
    for row in excel_data:
        row = [None if item == "None" else item for item in row]
        vehicle_details = dict(zip(headings, row))
        vehicle_type = vehicle_details["type"]
        if vehicle_type is None:
            continue
        is_valid, validated_data = get_vehicle_json(request, vehicle_details)
        if not is_valid:
            return is_valid, validated_data
        else:
            vehicle_json = validated_data
            vehicle_type = vehicle_json["type"]["label"]
            item_type = InspectionItemType.objects.get(name=vehicle_type)
            bulk_item_list.append(
                InspectionItem(
                    created_by=request.user,
                    ref=vehicle_json["ref"],
                    item_json=json.dumps(vehicle_json),
                    item_type=item_type,
                )
            )
    InspectionItem.objects.bulk_create(bulk_item_list)
    return True, None
