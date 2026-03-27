
"""
====================================================================================
File                :   login.py
Description         :   This file contains code related to the login API.
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
import json
from star_runway.globals import *
import random
import string
from django.http import JsonResponse
from star_runway.settings import *
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password



@csrf_exempt
def user_login(request):
    """
    Logs into the application.

    Args:
        request (HttpRequest): The HTTP request object containing login credentials and other necessary information.

    Returns:
        JsonResponse: A JSON response indicating the result of the login attempt. The response
        includes details such as success or failure, error messages, and user information
        if the login is successful.
    """
    if request.method == "POST":
        try:
            request_header = request.headers
            if request_header.get('Authorization') != 'Th45Dc@g9K3gaFuWlaLV901Ds2':
                resp = {'status':400,'message':'Authorization Failed'}
                return JsonResponse(resp, safe=False)
            else:
                data = json.loads(request.body)
                user_name = data["user_name"]                
                show_password = data["show_password"]
                
                get_user_query = """ select * from user_master where user_name = '{user_name}' or email = '{user_name}' """.format(user_name=user_name)
                response = search_all(get_user_query)
                
                if len(response)  == 0:
                    return JsonResponse({'status': 400, 'action': 'error',"message": "Incorrect username/password"}, safe=False)
                
                existing_password = response[0]["password"] 
                stage = check_password(show_password,existing_password)

                if not stage :
                    return JsonResponse({'status': 400, 'action': 'error',"message": "Incorrect username/password"}, safe=False)
                elif response[0]['active_status'] == 0 or response[0]['active_status'] == '0':
                    return JsonResponse({"message": "This user is temporarily suspended. Please contact the admin"}, safe=False)    
                else:
                    user_id = response[0]['data_uniq_id']
                    user_type = response[0]["user_type"]
                    access_token = ''.join(random.choice(string.ascii_letters) for i in range(50))
                    
                    query = """insert into users_login_table (access_token,ref_user_id,user_name,ref_user_type) values ('{access_token}','{ref_data_uniq_id}','{user_name}','{user_type}')""".format(access_token=access_token,ref_data_uniq_id=user_id,user_name=user_name,user_type=user_type)                    
                    result = django_execute_query(query)
                    if result != 0:
                        del response[0]["password"]
                        del response[0]["show_password"]
                        message = {
                            'action':'success',
                            'message': "Logged in Successfully",
                            'user_id':user_id,
                            'access_token':access_token,
                            'user_data':response,
                            'user_type':user_type
                            }
                        return JsonResponse(message, safe=False,status = 200)                                                
                    else:
                        message = {
                        'action':'error',
                        'message': "Login Failed",
                        }                        
                    return JsonResponse(message, safe=False,status = 400)          
        except Exception as Err:
            response_exception(Err)
            return JsonResponse(str(Err), safe=False)
    else:
        message = {
            'action': 'error',
            'message': 'Wrong Request'
        }
        return JsonResponse(message, safe=False,status = 400)
    



