"""
====================================================================================
File                :   model_master.py
Description         :   This file contains code related to the model master API.
Author              :   Haritha sree S
Date Created        :   May 12th 2024
Last Modified BY    :   Haritha sree S
Date Modified       :   May 12th 2024
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

@csrf_exempt
def model_master(request):
    """
    Inserts datas into the master.

    Args:
        request (HttpRequest): The HTTP request object containing the data to be inserted.

    Returns:
        JsonResponse: A JSON response indicating the result of the data insertion.

    The `model_master` API is responsible for adding new records to the master database.
    It expects an HTTP request object containing the data to be inserted. The data should be in a
    specific format, such as JSON, and must include the necessary fields required by the master database.
    """
    try:
        
        if request.method in ["POST","PUT","DELETE"]:
            data = json.loads(request.body)
            utc_time = datetime.utcnow()
            request_header = request.headers
            auth_token = request_header["Authorization"]
            access_token = data["access_token"]
            table_name = "model_master"
            
            #To verify the authorization
            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if not state:
                return JsonResponse(msg, safe=False)
            
            user_id = user[0]["ref_user_id"]
            #To create the data
            if request.method == "POST":
                #To throw an required error message
                errors = {
                    'model': {'req_msg': 'Model is required','val_msg': '', 'type': ''}  
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)
            
                data_uniq_id = str(uuid.uuid4())
                model = data["model"]  
                is_exist, message = check_existing_value(model, "model", table_name)
                
                if is_exist:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False)

                query = """insert into model_master (data_uniq_id,model,created_date,modified_date,created_by,modified_by) values ('{data_uniq_id}','{model}', '{created_date}', '{modified_date}','{created_by}','{modified_by}');""".format(data_uniq_id=data_uniq_id,model=model,created_date=utc_time,modified_date=utc_time,created_by=user_id,modified_by=user_id)
                success_message = "Data created successfully"
                error_message = "Failed to create data"
            
            #To modify the data
            elif request.method == "PUT":
                #To throw an required error message
                errors = {
                    'model': {'req_msg': 'Model is required','val_msg': '', 'type': ''} ,
                    'data_uniq_id': {'req_msg': 'model ID is required','val_msg': '', 'type': ''}   
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)
            
                data_uniq_id = base64_operation(data["data_uniq_id"],'decode')  
                model = data["model"]  

                is_exist, message = check_existing_value(model, "model", table_name, data_uniq_id)
                
                if is_exist:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False)
 
                query = """update model_master set model = '{model}',modified_date = '{now}',modified_by = '{modified_by}' where data_uniq_id = '{data_uniq_id}';""".format(data_uniq_id=data_uniq_id,model=model,now=utc_time,modified_by=user_id)
                success_message = "Data updated successfully"
                error_message = "Failed to update data"            
           
            #To delete the data
            elif request.method == "DELETE":
                data_uniq_id = base64_operation(data["data_uniq_id"],'decode')  
                query = """DELETE FROM model_master where data_uniq_id = '{data_uniq_id}';""".format(data_uniq_id=data_uniq_id)
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
def model_master_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `model_master_get` API is responsible for fetching data from the master database
    based on the parameters provided in the HTTP request. The request may include filters, sorting
    criteria, or other parameters to customize the query.
    """
    try:
        
        if request.method == "GET": 
            utc_time = datetime.utcnow()

            request_header = request.headers
            auth_token = request_header["Authorization"]
            access_token = request.GET["access_token"]
            table_name = 'model_master'

            state,msg,response = authorization(auth_token=auth_token,access_token=access_token)
            if not state:
                return JsonResponse(msg, safe=False)  
            
            else:            
                search_input = request.GET.get('search_input',None)
                
                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_input = search_input.strip() 
                    search_join += " AND  {table_name}.model REGEXP '{inp}' ".format(inp=search_input,table_name=table_name)

                #Query to make the count of data
                count_query = """ SELECT count(*) as count
                FROM {table_name}
                WHERE 1=1 {search_join};""".format(search_join=search_join,table_name=table_name)
                get_count = search_all(count_query)

                #Query to fetch all the data 
                fetch_data_query = """ SELECT *, DATE_FORMAT(model_master.created_date, '%b %d, %Y | %l:%i %p') as created_f_date,
                (select user_name from user_master where user_master.data_uniq_id = model_master.created_by) as created_user FROM model_master
                WHERE 1=1  {search_join} {order_by} {limit};""".format(search_join=search_join,order_by=order_by,limit=limit_offset) 
                                    
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
                    
                    #To get encoded data_uniq_id,serial number,formatted,readable created and modified_date 
                    data_formats(data=i,page_number=page_number,index=index)
                                        
                message = {
                        'action':'success',
                        'data':get_all_data,  
                        'page_number': page_number,
                        'items_per_page': items_per_page,
                        'total_pages': total_pages,
                        'total_items': count,
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
    
@csrf_exempt
def model_master_web_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `model_master_get` API is responsible for fetching data from the master database
    based on the parameters provided in the HTTP request. The request may include filters, sorting
    criteria, or other parameters to customize the query.
    """
    try:
        
        if request.method == "GET": 
            utc_time = datetime.utcnow()

            request_header = request.headers
            auth_token = request_header["Authorization"]
            
            table_name = 'model_master'

            state,msg,response = check_authorization_key(auth_token=auth_token)
            if not state:
                return JsonResponse(msg, safe=False)  
            
            else:            
                search_input = request.GET.get('search_input',None)
                
                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_input = search_input.strip() 
                    search_join += " AND  {table_name}.model REGEXP '{inp}' ".format(inp=search_input,table_name=table_name)

                #Query to make the count of data
                count_query = """ SELECT count(*) as count
                FROM {table_name}
                WHERE 1=1 {search_join};""".format(search_join=search_join,table_name=table_name)
                get_count = search_all(count_query)

                #Query to fetch all the data 
                fetch_data_query = """ SELECT *, DATE_FORMAT(model_master.created_date, '%b %d, %Y | %l:%i %p') as created_f_date,
                (select user_name from user_master where user_master.data_uniq_id = model_master.created_by) as created_user FROM model_master
                WHERE 1=1  {search_join} {order_by} {limit};""".format(search_join=search_join,order_by=order_by,limit=limit_offset) 
                                    
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
                    # i['data_uniq_id'] = base64_operation(i['data_uniq_id'],'encode')
                    
                    #To get encoded data_uniq_id,serial number,formatted,readable created and modified_date 
                    data_formats(data=i,page_number=page_number,index=index)
                                        
                message = {
                        'action':'success',
                        'data':get_all_data,  
                        'page_number': page_number,
                        'items_per_page': items_per_page,
                        'total_pages': total_pages,
                        'total_items': count,
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
    

@csrf_exempt
def model_master_status(request):
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
                'data_ids': {'req_msg': 'Model ID is required','val_msg': '', 'type': ''}, 
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
                UPDATE model_master 
                SET active_status = '{active_status}', modified_date = '{modified_date}', modified_by = '{modified_by}' 
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
def model_master_delete(request):
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
                'data_ids': {'req_msg': 'Model ID is required','val_msg': '', 'type': ''}, 
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            data_uniq_id_list = data['data_ids']
            for data_uniq_id in data_uniq_id_list:
                data_uniq_id_en = base64_operation(data_uniq_id,'decode')  
                                                                           
                query = """delete from model_master where data_uniq_id = '{data_uniq_id}';""".format(data_uniq_id=data_uniq_id_en)                
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
    