"""
====================================================================================
File                :   change_password.py
Description         :   This file contains code related to the change password API.
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
from django.http import JsonResponse
from star_runway.settings import *
from django.contrib.auth.hashers import make_password



@csrf_exempt
def password_change(request):
    """
    change the password of the user.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating the result of the successful updation of new password.
    """
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            request_header = request.headers
            auth_token = request_header["Authorization"]
            access_token = data["access_token"]
            
            #To verify the authorization
            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if not state:
                return JsonResponse(msg, safe=False)
                        
            #To throw an required error message
            errors = {
                'current_password': {'req_msg': 'Current password is required','val_msg': '', 'type': ''},
                'new_password': {'req_msg': 'New password is required','val_msg': '', 'type': ''},
                'confirm_password': {'req_msg': 'Confirm password is required','val_msg': '', 'type': ''},
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False)              
            else:                
                user_id = user[0]['ref_user_id']
                current_password = data["current_password"]
                search_password = """select * from user_master where data_uniq_id = '{user_id}';""".format(user_id = user_id)
                get_password = search_all(search_password)
                if len(get_password)!=0:
                    existing_password = get_password[0]["show_password"]
                    
                    if current_password == existing_password:
                        new_password = data["new_password"]
                        confirm_password = data["confirm_password"]
                        state,msg = password_validation(new_password,"new_password")                    
                        if state == False:
                            return JsonResponse(msg, safe=False)
                        else:
                            pass

                        if new_password == confirm_password:
                            password = make_password(confirm_password)
                            update_query = """update user_master set show_password = '{show_password}',password = '{password}' where data_uniq_id = '{user_id}';""".format(show_password=confirm_password,password=password,user_id=user_id)
                            execute = django_execute_query(update_query)
                            if execute !=0:
                                response = {
                                    'action':'success',
                                    'message':'Password changed',
                                }
                                return JsonResponse(response, safe=False,status=200)                            
                            else:
                                response = {
                                        'action':"error",
                                        'message':'Failed to change password',
                                        }
                            return JsonResponse(response, safe=False)                        
                        else:
                            response = {
                                'action':'error',
                                'new_password':'New password and Confirm password does not match',
                                }
                            return JsonResponse({'status': 400, 'action': 'error', 'message': response}, safe=False)
                    else:
                        response = {                                    
                            'action':'error',
                            'current_password':'Current password does not match',
                            }
                        return JsonResponse({'status': 400, 'action': 'error', 'message': response}, safe=False)
                    
                else:
                    response = {                                    
                        'action':'error',
                        'current_password':'Current password does not exist',
                        }
                    return JsonResponse({'status': 400, 'action': 'error', 'message': response}, safe=False)
        else:
            message = {
                'action': 'error',
                'message': 'Wrong Request'
                }
            return JsonResponse(message, safe=False,status=400)        

    except Exception as Err:
        response_exception(Err)
        return JsonResponse(str(Err), safe=False)