"""
====================================================================================
File                :   login.py
Description         :   This file contains code related to the logout API.
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
from star_runway.globals import *
from django.http import JsonResponse
from star_runway.settings import *

@csrf_exempt
def user_logout(request):
    """
    Log out the user by clearing their access_token.

    Args:
        request (HttpRequest): The HTTP request object representing the user's request to log out.

    Returns:
        JsonResponse: A JSON response indicating the result of the logout operation.
                     
    """
    try:
        if request.method == 'GET': 
            request_header = request.headers
            if request_header.get('Authorization') != 'Th45Dc@g9K3gaFuWlaLV901Ds2':
                resp = {'status':400,'message':'Authorization Failed'}
                return JsonResponse(resp, safe=False)
            else:
                # Checking the Authorization of the request
                access_token = request.GET['access_token']                
                get_user_data_query = """ select * from users_login_table where access_token = '{access_token}'""".format(access_token=access_token)
                get_user_data = search_all(get_user_data_query)                
                if len(get_user_data) == 0:
                    message = {
                    'action': 'error',
                    'message': 'User access denied'
                    }                    
                    return JsonResponse(message, safe=False,status = 400)                
                else:                    
                    # Updating the user_master table  
                    delete_user_data = """ delete from users_login_table where access_token = '{access_token}';"""
                    sql = delete_user_data.format(access_token=access_token)
                    response = django_execute_query(sql)
                    if response != 0:
                        message = {
                            'action': 'success',
                            'message': 'Logged out successfully'
                        }
                        return JsonResponse(message, safe=False,status = 200)
                    else:
                        message = {
                            'action': 'error',
                            'message': 'Failed to logout successfully'
                        }
                        return JsonResponse(message, safe=False,status = 400)
        else:
            message = {
                'action': 'error',
                'message': 'Wrong Request'
            }
            return JsonResponse(message, safe=False,status = 400)

    except Exception as Err:
        response_exception(Err)
        return JsonResponse(str(Err), safe=False)