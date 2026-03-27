"""
====================================================================================
File                :   enquiry.py
Description         :   This file contains code related to the enquiry API.
Author              :   Haritha sree S
Date Created        :   May 02th 2024
Last Modified BY    :   Haritha sree S
Date Modified       :   May 02th 2024
====================================================================================
"""

from django.conf import settings
from db_interface.queries import *
from db_interface.execute import *
from django.views.decorators.csrf import csrf_exempt
from utilities.constants import *
from datetime import datetime,timedelta
from star_runway.globals import *
import json,uuid,math
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@csrf_exempt
def enquiry(request):
    """
    Inserts datas into the master.

    Args:
        request (HttpRequest): The HTTP request object containing the data to be inserted.

    Returns:
        JsonResponse: A JSON response indicating the result of the data insertion.

    The `registration` API is responsible for adding new records to the master database.
    It expects an HTTP request object containing the data to be inserted. The data should be in a
    specific format, such as JSON, and must include the necessary fields required by the master database.
    """
    try:
        
        if request.method in ["POST","PUT","DELETE"] :
            data = json.loads(request.body)
            utc_time = datetime.utcnow()
            request_header = request.headers
            auth_token = request_header["Authorization"]
            state,msg,response = check_authorization_key(auth_token=auth_token)
            if not state:
                return JsonResponse(msg, safe=False)           
            
            #To create the data
            if request.method == "POST":
                errors = {
                'name': {'req_msg': 'Name is required','val_msg': '', 'type': ''},
                'contact_number': {'req_msg': 'Contact number is required','val_msg': '', 'type': ''}, 
                'pickup_loc': {'req_msg': 'Pick up location is required','val_msg': '', 'type': ''}, 
                'drop_loc': {'req_msg': 'Drop off location is required','val_msg': '', 'type': ''}, 
                'passengers': {'req_msg': 'Number of passengers is required','val_msg': '', 'type': ''}, 
                # 'date': {'req_msg': 'Date is required','val_msg': '', 'type': ''}, 
                # 'time': {'req_msg': 'Time is required','val_msg': '', 'type': ''},
                # 'ref_model_id': {'req_msg': 'Model is required','val_msg': '', 'type': ''}, 
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)
                booking_data = """SELECT booking_id FROM `enquiry_table` ORDER BY `enquiry_table`.`booking_id` DESC""" 
                get_data = search_all(booking_data)

                if get_data:
                    last_booking_id = get_data[0].get('booking_id') if isinstance(get_data[0], dict) else None
                else:
                    last_booking_id = None

                if last_booking_id:
                    match = re.match(r"EnNo(\d+)", last_booking_id)
                    if match:
                        number = int(match.group(1)) + 1
                        new_booking_id = f"EnNo{number:03d}"  
                else:
                    new_booking_id = "EnNo001"


                data_uniq_id = str(uuid.uuid4())
                
                name = data.get("name", "")
                contact_number = data.get("contact_number", "")
                pickup_loc = data.get("pickup_loc", "")
                drop_loc = data.get("drop_loc", "")
                passengers = data.get("passengers", "")
                date = data.get("date", None) 
                time = data.get("time", None)  
                ref_model_id = data.get("ref_model_id", "")
                # if ref_model_id != "" and ref_model_id != None :
                #     ref_model_id = base64_operation(ref_model_id, 'decode')  
                ref_model_name = data.get("ref_model_name", "")

                query = """INSERT INTO enquiry_table (data_uniq_id, booking_id, name, contact_number, pickup_loc, drop_loc, passengers, date, time, ref_model_id, ref_model_name,created_date,modified_date) VALUES ('{data_uniq_id}','{booking_id}', '{name}', '{contact_number}', '{pickup_loc}', '{drop_loc}', '{passengers}', '{date}', '{time}', '{ref_model_id}', '{ref_model_name}','{created_date}', '{modified_date}');""".format(data_uniq_id=data_uniq_id, booking_id=new_booking_id,name=name,contact_number=contact_number,pickup_loc=pickup_loc,drop_loc=drop_loc,passengers=passengers,date=date,time=time,ref_model_id=ref_model_id,ref_model_name=ref_model_name,created_date=utc_time,modified_date=utc_time)
                print(query,"queryjdfhjff")
                success_message = "Data created successfully"
                error_message = "Failed to create data"

            #To modify the data
            elif request.method == "PUT":  
                errors = {
                'name': {'req_msg': 'Name is required','val_msg': '', 'type': ''},
                'contact_number': {'req_msg': 'Contact number is required','val_msg': '', 'type': ''}, 
                'pickup_loc': {'req_msg': 'Pick up location is required','val_msg': '', 'type': ''}, 
                'drop_loc': {'req_msg': 'Drop off location is required','val_msg': '', 'type': ''}, 
                'passengers': {'req_msg': 'Number of passengers is required','val_msg': '', 'type': ''}, 
                # 'date': {'req_msg': 'Date is required','val_msg': '', 'type': ''}, 
                # 'time': {'req_msg': 'Time is required','val_msg': '', 'type': ''},
                # 'ref_model_id': {'req_msg': 'Model is required','val_msg': '', 'type': ''}, 
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)                
                
                data_uniq_id = base64_operation(data["data_uniq_id"],'decode')                  
                booking_id = data["booking_id"]
                name = data["name"]
                contact_number = data["contact_number"]
                pickup_loc = data["pickup_loc"]
                drop_loc = data["drop_loc"]
                passengers = data["passengers"]
                date = data["date"]
                time = data["time"]
                ref_model_id = data["ref_model_id"]
                if ref_model_id != "" and ref_model_id is not None:
                    ref_model_id = base64_operation(ref_model_id, 'decode')
                ref_model_name = data["ref_model_name"]

                query = """UPDATE enquiry_table SET name = '{name}',contact_number = '{contact_number}',pickup_loc = '{pickup_loc}',drop_loc = '{drop_loc}',passengers = '{passengers}',date = '{date}',time = '{time}',ref_model_id = '{ref_model_id}',ref_model_name = '{ref_model_name}', modified_date = '{modified_date}' WHERE data_uniq_id = '{data_uniq_id}';""".format(name=name,contact_number=contact_number,pickup_loc=pickup_loc,drop_loc=drop_loc,passengers=passengers,date=date,time=time,ref_model_id=ref_model_id,ref_model_name=ref_model_name,modified_date= utc_time,data_uniq_id=data_uniq_id)

                success_message = "Data updated successfully"
                error_message = "Failed to update data"
            
            #To delete the data
            elif request.method == "DELETE":
                data_uniq_id = base64_operation(data["data_uniq_id"],'decode')  
                query = """DELETE FROM enquiry_table where data_uniq_id = '{data_uniq_id}';""".format(data_uniq_id=data_uniq_id)
                success_message = "Data deleted successfully"
                error_message = "Failed to delete data"
            
            execute = django_execute_query(query)
            if execute!=0:
                message = {
                        'action':'success',
                        'message':success_message,
                        'data_uniq_id':data_uniq_id
                        }
                return JsonResponse(message, safe=False,status = 200)                    
            else:
                message = {                        
                        'action':'error',
                        'message': error_message
                        }
                return JsonResponse(message, safe=False, status = 400)  
        else:
            message = {
                    'action': 'error',
                    'message': 'Wrong Request'
                }
            return JsonResponse(message, safe=False, status = 405)
    except Exception as Err:
        response_exception(Err)
        return JsonResponse(str(Err), safe=False)
    

@csrf_exempt
def change_enquiry_status(request):
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            utc_time = datetime.utcnow()
            request_header = request.headers
            auth_token = request_header["Authorization"]
            access_token = data["access_token"]
            
            #To verify the authorization
            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if not state:
                return JsonResponse(msg, safe=False)
            
            #To throw an required error message
            errors = {
                'data_ids': {'req_msg': 'ID is required','val_msg': '', 'type': ''}, 
                'status': {'req_msg': 'Status is required','val_msg': '', 'type': ''}, 
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            data_uniq_id_list = data['data_ids']
            for data_uniq_id in data_uniq_id_list:
                data_uniq_id_en = base64_operation(data_uniq_id,'decode')  
                
                status = data["status"]                                                             
                query = """
                UPDATE enquiry_table 
                SET status = {status}, modified_date = '{modified_date}' 
                WHERE data_uniq_id = '{data_uniq_id}';
                """.format(data_uniq_id=data_uniq_id_en, status=status, modified_date=utc_time)
                execute = django_execute_query(query)
            success_message = "Data updated successfully"
            error_message = "Failed to update data"
            if execute!=0:
                message = {
                        'action':'success',
                        'message':success_message,
                        }
                return JsonResponse(message, safe=False,status = 200)                    
            else:
                message = {                        
                        'action':'error',
                        'message': error_message
                        }
                return JsonResponse(message, safe=False, status = 400)                         
        else:
            message = {
                    'action': 'error',
                    'message': 'Wrong Request'
                }
            return JsonResponse(message, safe=False, status = 405)
    except Exception as Err:
        response_exception(Err)
        return JsonResponse(Err, safe=False) 

@csrf_exempt
def enquiry_get(request):
    try:
        
        if request.method == "GET": 
            utc_time = datetime.utcnow()

            request_header = request.headers
            auth_token = request_header["Authorization"]
            access_token = request.GET["access_token"]
            table_name = 'enquiry_table'

            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if state == False:
                return JsonResponse(msg, safe=False)
            
            else:            
                search_input = request.GET.get('search_input',None)
                status = request.GET.get('status', None)
                unique_keyname = request.GET.get('unique_keyname', None)

                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_join += " AND  ({table_name}.name REGEXP '{inp}' OR {table_name}.booking_id REGEXP '{inp}' OR {table_name}.ref_model_name REGEXP '{inp}' )".format(inp=search_input,table_name=table_name)

                if status:                            
                    search_join += "AND {table_name}.status = '{status}' ".format(status=status,table_name=table_name)

                # if unique_keyname:
                #     unique_keyname = unique_keyname
                #     search_join += " AND {table_name}.UniquePageName = '{UniqueKeyName}' ".format(UniqueKeyName=unique_keyname,table_name=table_name)
                
                #Query to make the count of data
                count_query = """ SELECT count(*) as count
                FROM {table_name}
                WHERE 1=1 {search_join};""".format(search_join=search_join,table_name=table_name)
                get_count = search_all(count_query)

                #Query to fetch all the data 
                fetch_data_query = """ SELECT *, DATE_FORMAT(enquiry_table.created_date, '%b %d, %Y | %l:%i %p') as created_f_date FROM enquiry_table
                WHERE 1=1  {search_join} {order_by} {limit};""".format(search_join=search_join,order_by=order_by,limit=limit_offset) 
                                    
                get_all_data = search_all(fetch_data_query)

                # return JsonResponse(get_all_data,safe=False)
                
                if len(get_count)!=0:                        
                    count = get_count[0]['count']
                    total_pages = math.ceil(count / items_per_page)
                else:
                    message = {
                            'action':'error',
                            'message': "Failed to make the count"
                            }
                    return JsonResponse(message, safe=False,status = 400)
                
                for index,i in enumerate(get_all_data):
                    i['data_uniq_id'] = base64_operation(i['data_uniq_id'],'encode')
                    i['ref_model_id'] = base64_operation(i['ref_model_id'],'encode')

                    #To get encoded page_id,serial number,formatted,readable created and modified_date 
                    data_formats(data=i,page_number=page_number,index=index)
                                        
                message = {
                        'action':'success',
                        'data':get_all_data,  
                        'page_number': page_number,
                        'items_per_page': items_per_page,
                        'total_items': count,
                        "total_pages":total_pages,
                        'table_name':table_name                                                                                 
                        }
                return JsonResponse(message,safe=False,status = 200)                                                        
        else:
            message = {
                    'action': 'error',
                    'message': 'Wrong Request'
                }
            return JsonResponse(message, safe=False, status = 405)
 
    except Exception as Err:
        response_exception(Err)
        return JsonResponse(str(Err), safe=False)

