import openpyxl
from django.shortcuts import render
from django.contrib import messages

from vehicle.utils import check_excel_file_extension
from vehicle.utils import create_instances_from_excel_data


def upload_vehicle_page(request):
    if request.method == "POST":
        excel_file = request.FILES["excel_file"]
        # check if the file is an excel file
        if not check_excel_file_extension(excel_file):
            messages.error(request, 'Please upload excel file only.')
            return render(request, 'vehicle/upload_vehicle_page.html')
        wb = openpyxl.load_workbook(excel_file)
        # getting a particular sheet by name out of many sheets
        worksheet = wb["Sheet1"]
        excel_data = list()
        context = {}
        count = 0
        headings = []
        # iterating over the rows and
        # getting value from each cell in row
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            if count == 0:
                headings = row_data
                headings.append("row_number")
                count += 1
            else:
                row_data.append(count)  # append row number to the row data
                count += 1
                excel_data.append(row_data)
        created, response = create_instances_from_excel_data(request, headings, excel_data)
        context["excel_data"] = excel_data
        if not created:
            errors = response
            context["errors"] = errors
            messages.error(request, "Please check errors in the excel file")
        else:
            messages.success(request, "Vehicles uploaded successfully")
        return render(request, 'vehicle/upload_vehicle_page.html', context)
    return render(request, 'vehicle/upload_vehicle_page.html')
