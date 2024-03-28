from re import sub
from inspection_template.models import Category, Template, Question
from inspection_template.serializers import QuestionSerializer
from django.core.exceptions import ObjectDoesNotExist


def extract_str_ids(data, string):
    """
    Extracts the 'string-id' values from a dictionary.

    :param data: A dictionary containing key-value pairs.
    :type data: dict
    :return: A list of 'string-id' values extracted from the dictionary keys.
    :rtype: list
    """
    str_ids = [key for key in data.keys() if key.startswith(f"{string}")]
    return str_ids


def extract_ids(cat_ids):
    """
    Extracts id list of 'cat-id' strings.

    :param cat_ids: A list of 'cat-id' strings.
    :type cat_ids: list
    :return: A list of ids extracted from the 'cat-id' strings.
    :rtype: list
    """
    ids = [int(cat_id.split('-')[1]) for cat_id in cat_ids]
    return ids


def camel_case(s):
    """
    Converts a string to camel case.

    :param s: The input string.
    :type s: str
    :return: The camel-cased version of the string.
    :rtype: str
    """
    # Remove underscores and hyphens, then split into words, title case them, and join
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    # Check if the resulting string is empty before proceeding
    if not s:
        return s
    # Convert the first character to lowercase and leave the rest as-is
    return s[0].lower() + s[1:]


def vehicle_type(vehicle_type):
    if vehicle_type == 'p':
        return 'Powered Vehicle'
    elif vehicle_type == 't':
        return 'Trailer'
    else:
        return 'Unknown'


def create_new_questions(data, cat_ids):
    """
    Create new questions and associate them with categories based on provided data.

    Args:
    - data (dict): A dictionary where each key is a category id (as a string)
                   and its value is a list of questions. Each question is represented
                   as a string, combining the question text and an image array,
                   separated by a '$'.
    - cat_ids (list): A list of category ids (integers) for which to create questions.

    The function creates all the new questions in bulk for each category and then
    associates them with the respective categories in the database.
    """

    # Loop over each category ID provided
    for cat_id in cat_ids:
        questions_to_create = []  # Temporary list to hold Question objects for bulk creation

        # Retrieve the list of questions for the category from the data dictionary
        questions = data.get(str(cat_id))
        if not questions:
            continue  # Skip this category ID if no questions are provided

        for question in questions:
            question_text, im_array = question.split('$', 1)  # Split each question into text and image array
            questions_to_create.append(Question(
                question=question_text,
                im_array=im_array,
                is_enabled=True  # Assume new questions should be enabled by default
            ))

        # Bulk create questions to reduce database queries
        new_questions = Question.objects.bulk_create(questions_to_create)

        # No need to manually add question IDs to categories since Django handles M2M relationships
        # However, fetching the category object outside the loop and using it directly to add questions can be optimized
        try:
            # Fetch the category object once and reuse it for adding questions
            category_obj = Category.objects.get(id=cat_id)
            # Directly add question objects to the category, leveraging Django's ManyToMany relationship handling
            category_obj.questions.add(*new_questions)  # Pass question instances directly
        except ObjectDoesNotExist:
            # Handle the case where the category ID does not exist in the database
            print(f"Category with id {cat_id} does not exist.")  # Logging or handling the error as needed


def update_category_data(template_obj, data):
    cat_ids = extract_str_ids(data, "cat-")
    ids = extract_ids(cat_ids)
    cats_to_update = []
    for id in ids:
        label = data.get(f'cat-{id}')
        cat_id = camel_case(label)
        sort_order = data.get(f'sort_order-{id}') or 0
        cat_obj = Category(pk=id, label=label, sort_order=sort_order, category_id=cat_id)
        cats_to_update.append(cat_obj)
    Category.objects.bulk_update(cats_to_update, ['label', 'sort_order', 'category_id'])
    
    # create new categories and questions -- start
    data = dict(data)
    new_cats = extract_str_ids(data, "newCat")
    for cat_id in new_cats:
        cat_data = data.get(cat_id)
        cat_name = cat_data[0]
        sort_order = cat_data[1] or 0
        category_id = camel_case(cat_name)  
        # this category id is for frontend representation
        # it is not used in backend. TODO: need to remove this
        # and create dynamic category id from label
        cat_obj = Category.objects.create(
            label=cat_name,
            sort_order=sort_order,
            category_id=category_id
        )
        questions = cat_data[2:]
        for question in questions:
            question_text, im_array = question.split('$')
            ques_obj = Question.objects.create(
                question=question_text,
                im_array=im_array,
                # is_enabled=True
            )
            cat_obj.questions.add(ques_obj)
        template_obj.category.add(cat_obj)
    return True


def update_question_data(template_obj, data):
    existing_questions_ids = list(
        Question.objects.filter(category__template__id=template_obj.id)
        .values_list('id', flat=True)
        .distinct()
    )
    questions_to_update = []
    question_ids = []
    for question_id, value in data.items():
        try:
            question_id = int(question_id)
        except ValueError:
            # only select questions id
            continue
        value = value[0]
        question_text, im_array = value.split('$')
        ques_obj = Question(
            pk=question_id,
            question=question_text,
            im_array=im_array,
            is_enabled=True
        )
        questions_to_update.append(ques_obj)
        question_ids.append(question_id)
    Question.objects.bulk_update(
        questions_to_update, ['question', 'im_array', 'is_enabled'])
    questions_to_exclude = list(
        set(existing_questions_ids) - set(question_ids))
    probable_cat_ids = list(
        set(question_ids) - set(existing_questions_ids))
    cat_ids = list(
        Category.objects.filter(id__in=probable_cat_ids)
        .values_list('id', flat=True)
        .distinct()
    )  # doing this we can filter only existing cat ids
    if any(cat_ids):
        create_new_questions(data, cat_ids)
    
    Question.objects.filter(
        id__in=questions_to_exclude).update(is_enabled=False)
    return True


def fetch_questions(template_profile_obj):
    result = []
    template_obj = template_profile_obj.template
    categories = template_obj.category.all()
    for category in categories:
        cat_result = {}
        cat_result['id'] = category.category_id
        cat_result['category_label'] = category.label
        cat_result['sort_order'] = category.sort_order
        questions = category.questions.filter(is_enabled=True)
        question_list = []
        for question in questions:
            data = QuestionSerializer(question).data
            question_list.append(data)
        cat_result['questions'] = question_list
        result.append(cat_result)
    return result


def update_template_name(template_obj, data):
    name = data.get('name')
    include_tyre_brake_section = bool(data.get('tyre_brake_section', False))
    template_obj.name = name
    template_obj.include_tyre_break_section = include_tyre_brake_section
    template_obj.save()
    return True
