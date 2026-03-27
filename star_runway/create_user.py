"""
====================================================================================
File                :   create_user.py
Description         :   This file contains code related to the create user API.
Author              :   Haritha sree S
Date Created        :   April 1st 2024
Last Modified BY    :   Haritha sree S
Date Modified       :   April 1st 2024
====================================================================================
"""

from django.conf import settings
from db_interface.queries import *
from db_interface.execute import *
from django.views.decorators.csrf import csrf_exempt
from utilities.constants import *
from datetime import datetime
from star_runway.globals import *
import json,uuid,math
from django.contrib.auth.hashers import make_password


def existing_user(user_name, mobile, email,data_uniq_id=None):
    is_exist = False
    msg = ''
    exist_query = ''
    message = ''


    if data_uniq_id:
        exist_query = """ and data_uniq_id != '{data_uniq_id}' ;""".format(data_uniq_id=data_uniq_id)

    # Check for existing user_name
    if search_all(f"SELECT * FROM user_master WHERE user_name = '{user_name}' {exist_query}"):
        is_exist = True
        msg = "User name already exists"
        message = {
            'user_name': msg  # Using 'mobile' as the key
        }

    # Check for existing mobile
    elif search_all(f"SELECT * FROM user_master WHERE mobile = '{mobile}' {exist_query}"):
        is_exist = True
        msg = "Mobile number already exists"
        message = {
            'mobile': msg  # Using 'mobile' as the key
        }
    # Check for existing email
    elif search_all(f"SELECT * FROM user_master WHERE email = '{email}' {exist_query}"):
        is_exist = True
        msg = "Email already exists"
        message = {
            'email': msg  # Using 'mobile' as the key
        }
    message = {
        'status': 400,
        'action': 'error',
        'message': message
    }
    return is_exist, message


@csrf_exempt
def create_user(request):
    """
    Inserts datas into the master.

    Args:
        request (HttpRequest): The HTTP request object containing the data to be inserted.

    Returns:
        JsonResponse: A JSON response indicating the result of the data insertion.

    The `create_user` API is responsible for adding new records to the database.
    It expects an HTTP request object containing the data to be inserted. The data should be in a
    specific format, such as JSON, and must include the necessary fields required by the database.
    """
    # try:
    if request.method in ["POST","PUT","DELETE"]:
        data = json.loads(request.body)
        utc_time = datetime.utcnow()
        request_header = request.headers
        auth_token = request_header["Authorization"]
        access_token = data["access_token"]
        
        #To verify the authorization
        state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
        if not state:
            return JsonResponse(msg, safe=False)
        
        user_id = user[0]["ref_user_id"]
        #To create the data
        if request.method == "POST":
            #To throw an required error message
            errors = {
                'user_name': {'req_msg': 'User name is required','val_msg': '', 'type': ''},
                'show_password': {'req_msg': 'Password is required','val_msg': '', 'type': ''},
                'email': {'req_msg': 'Email is required','val_msg': 'Invalid email', 'type': 'email'},
                'mobile': {'req_msg': 'Mobile number is required','val_msg': 'Invalid mobile number', 'type': 'mobile'},
                'first_name': {'req_msg': 'First name is required','val_msg': '', 'type': ''},

            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)

            data_uniq_id = str(uuid.uuid4())
            first_name = data["first_name"]
            user_name = data["user_name"]
            email = data["email"]
            mobile = data["mobile"]              
            show_password = data["show_password"]
            user_type = data.get("user_type","2")
            is_exist,message = existing_user(user_name,mobile,email)
            if is_exist:
                return JsonResponse(message, safe=False)
            state,msg = password_validation(show_password,"show_password")
            if state == False:                                                                    
                return JsonResponse(msg, safe=False)
            password = make_password(show_password)
                        
            query = """insert into user_master (data_uniq_id,first_name,user_name,email,mobile,show_password,password,created_date,modified_date,user_type,created_by,modified_by) 
            values ('{data_uniq_id}','{first_name}','{user_name}','{email}','{mobile}','{show_password}',
            '{psw}','{created_date}','{modified_date}','{user_type}','{created_by}','{modified_by}');""".format(data_uniq_id=data_uniq_id,first_name=first_name,user_name=user_name,email=email,mobile=mobile,show_password=show_password,psw= password,created_date=utc_time,modified_date=utc_time,user_type=user_type,created_by=user_id,modified_by=user_id)
            success_message = "Data created successfully"                                            
            error_message = "Failed to create data"
    
        #To modify the data
        elif request.method == "PUT":
            errors = {
                'user_name': {'req_msg': 'User name is required','val_msg': '', 'type': ''},
                'show_password': {'req_msg': 'Password is required','val_msg': '', 'type': ''},
                'email': {'req_msg': 'Email is required','val_msg': 'Invalid email', 'type': 'email'},
                'mobile': {'req_msg': 'Mobile number is required','val_msg': 'Invalid mobile number', 'type': 'mobile'},
                'first_name': {'req_msg': 'First name is required','val_msg': '', 'type': ''},

            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)

            data_uniq_id = base64_operation(data["data_uniq_id"],'decode')  
            first_name = data["first_name"]
            user_name = data["user_name"]  
            email = data["email"]
            mobile = data["mobile"]
            show_password = data["show_password"]
            user_type = data.get("user_type","2")
            
            is_exist,message = existing_user(user_name,mobile,email,data_uniq_id)
            if is_exist:
                return JsonResponse(message, safe=False)
            state,msg = password_validation(show_password,field_name=show_password)
            if state == False:                                                                    
                return JsonResponse(msg, safe=False)
            password = make_password(show_password)  
            
            query = """update user_master set first_name = '{first_name}',user_name= '{user_name}',email='{email}',mobile='{mobile}', show_password='{show_password}',modified_date = '{now}',created_by = '{created_by}',modified_by = '{modified_by}',user_type = '{user_type}' where data_uniq_id = '{data_uniq_id}';""".format(data_uniq_id=data_uniq_id,first_name=first_name,user_name=user_name,email=email,mobile=mobile,show_password=show_password,now=utc_time,utc=utc_time,created_by=user_id,modified_by=user_id,user_type=user_type)
            success_message = "Data updated successfully"
            error_message = "Failed to update data"            
        
        #To delete the data
        elif request.method == "DELETE":
            data_uniq_id = base64_operation(data["data_uniq_id"],'decode')  
            query = """DELETE FROM user_master where data_uniq_id = '{data_uniq_id}';""".format(data_uniq_id=data_uniq_id)
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
    # except Exception as Err:
    #     response_exception(Err)
    #     return JsonResponse(str(Err), safe=False)
        
@csrf_exempt
def user_get(request):

    """
    Retrieves data from the database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `user_get` API is responsible for fetching data from the database
    based on the parameters provided in the HTTP request. The request may include filters, sorting
    criteria, or other parameters to customize the query.
    """
    try:
        
        if request.method == "GET": 
            utc_time = datetime.utcnow()

            request_header = request.headers
            auth_token = request_header["Authorization"]
            access_token = request.GET["access_token"]
            table_name = 'user_master'

            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if state == False:
                return JsonResponse(msg, safe=False)
            
            else:            
                search_input = request.GET.get('search_input',None)
                user_type = request.GET.get('search_input',None)
                
                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_input = search_input.strip() 
                    search_join += " AND ({table_name}.user_name REGEXP '{inp}' or {table_name}.email REGEXP '{inp}' or {table_name}.mobile REGEXP '{inp}' ) ".format(inp=search_input,table_name=table_name)
                    
                #Query to make the count of data
                count_query = """ SELECT count(*) as count
                FROM {table_name}
                WHERE 1=1 and user_type!= 1 {search_join};""".format(search_join=search_join,table_name=table_name)
                get_count = search_all(count_query)

                #Query to fetch all the data 
                fetch_data_query = """ SELECT *, DATE_FORMAT(user_master.created_date, '%b %d, %Y | %l:%i %p') as created_f_date
                FROM user_master
                WHERE 1=1 and user_type!= 1 {search_join} {order_by} {limit};""".format(search_join=search_join,order_by=order_by,limit=limit_offset,user_type=user_type) 
                                    
                get_all_data = search_all(fetch_data_query)
                
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

                    data_formats(data=i,page_number=page_number,index=index)
                                        
                message = {
                        'action':'success',
                        'data':get_all_data,  
                        'page_number': page_number,
                        'items_per_page': items_per_page,
                        'total_pages': total_pages,
                        'total_items': count                                                                                   
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
    

@csrf_exempt
def user_status(request):
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
                'data_ids': {'req_msg': 'User is required','val_msg': '', 'type': ''}, 
                'active_status': {'req_msg': 'Active status is required','val_msg': '', 'type': ''}, 
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            data_uniq_id_list = data['data_ids']
            for data_uniq_id in data_uniq_id_list:
                data_uniq_id_en = base64_operation(data_uniq_id,'decode')  
                
                active_status = data["active_status"]                                                             
                query = """
                UPDATE user_master 
                SET active_status = {active_status}, modified_date = '{modified_date}', modified_by = '{modified_by}' 
                WHERE data_uniq_id = '{data_uniq_id}';
                """.format(data_uniq_id=data_uniq_id_en, active_status=active_status, modified_date=utc_time, modified_by=user_id)
                
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
def user_delete(request):
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
                'data_ids': {'req_msg': 'User is required','val_msg': '', 'type': ''}, 
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            data_uniq_id_list = data['data_ids']
            for data_uniq_id in data_uniq_id_list:
                data_uniq_id_en = base64_operation(data_uniq_id,'decode')  
                                                                           
                query = """delete from user_master where data_uniq_id = '{data_uniq_id}';""".format(data_uniq_id=data_uniq_id_en)                
                execute = django_execute_query(query)
            success_message = "Data deleted successfully"
            error_message = "Failed to delete data"
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
    
