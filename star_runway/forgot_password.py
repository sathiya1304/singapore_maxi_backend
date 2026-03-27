
"""
====================================================================================
File                :   forgot_password.py
Description         :   This file contains code related to the forgot password API.
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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.hashers import make_password



@csrf_exempt
def send_otp(request):
    """
    Send an otp to the user.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating that the otp has been sent successfully .
    """
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            request_header = request.headers
            auth_token = request_header["Authorization"]
            state,msg,user = check_authorization_key(auth_token=auth_token)
            if not state:
                return JsonResponse(msg, safe=False)

            #To throw an required error message
            errors = {
                'username': {'req_msg': 'User name is required','val_msg': '', 'type': ''},

            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False) 
                      
            else:
                user_name = data["username"]
                                  
                select_user_query = """ select * from user_master where user_name = '{user_name}';""".format(user_name=user_name) 
                get_user_name = search_all(select_user_query)
                if len(get_user_name) != 0 :
                    email = get_user_name[0]["email"]
                    user_id = get_user_name[0]["data_uniq_id"]
                    otp = generate_otp()                        
                    subject = 'OTP Verification'
                    from_email = 'dev.hugeitsolutions@gmail.com'
                    text_content = f'Your OTP is: {otp}'
                    
                    # Compose the email
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
                    try:
                        msg.send()
                        query = """insert into otp_table (otp,ref_user_id) values ('{otp_number}','{user_id}');""".format(otp_number=otp,user_id=user_id)
                        execute = django_execute_query(query)
                        if execute!=0:
                            msg = {
                            'action':'success',
                            'message': "Email sent successfully"                                    
                            }
                            return JsonResponse(msg, safe=False,status=200)
                        else:
                            msg = {
                            'action':'error',
                            'message': 'Failed to send email'                                    
                            }
                            return JsonResponse(msg, safe=False,status=400)
                        
                    except Exception as e:
                        msg = {
                        'action': 'error',
                        'message': 'Failed to send email'
                        }
                        return JsonResponse(msg,safe=False,status=400)                                           
                else:
                    msg = {
                    'action': 'error',
                    'user_name': 'User not found'
                    }                        
                    return JsonResponse({'status': 400, 'action': 'error', 'message': msg}, safe=False)                 
        else:
            message = {
                    'action': 'error',
                    'message': 'Wrong Request'
                }
            return JsonResponse(message, safe=False,status=400)
    except Exception as Err:
        response_exception(Err)
        return JsonResponse(str(Err), safe=False)
    

@csrf_exempt
def verify_otp(request):
    """
    verification of the otp.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating the result of the successful otp verification.
    """
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            request_header = request.headers
            auth_token = request_header["Authorization"]
            state,msg,user = check_authorization_key(auth_token=auth_token)
            if not state:
                return JsonResponse(msg, safe=False)

            #To throw an required error message
            errors = {
                'username': {'req_msg': 'User name is required','val_msg': '', 'type': ''},
                'otp_number': {'req_msg': 'OTP is required','val_msg': '', 'type': ''},
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False) 
                      
            else:
                user_name = data["username"]
                otp_number = data["otp_number"]

                select_user_id = """select data_uniq_id from user_master where user_name = '{user_name}'""".format(user_name=user_name)
                get_id = search_all(select_user_id)

                user_id = get_id[0]["data_uniq_id"]
                   
                search_otp = """select * from otp_table where ref_user_id = '{user_id}';""".format(user_id=user_id)
                get_otp = search_all(search_otp)                        
                existing_otp = get_otp[0]["otp"]
                
                if existing_otp == otp_number:
                    delete_otp_query = f"DELETE FROM otp_table where ref_user_id = '{user_id}';""".format(user_id=user_id)
                    execute = django_execute_query(delete_otp_query)
                    if execute != 0 :
                        response = {                        
                                'otp_number':'OTP verified'
                                }
                        return JsonResponse({'status': 200, 'action': 'success', 'message': response}, safe=False)
                    else:
                        response = {
                                'otp_number':'Invalid OTP',
                                }
                        return JsonResponse({'status': 400, 'action': 'error', 'message': response}, safe=False) 
                else:
                    response = {                                
                                'otp_number':'OTP does not match',
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
    

@csrf_exempt
def update_password(request):
    """
    updation of the password.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating the result of the updation of the password.
    """
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            request_header = request.headers
            auth_token = request_header["Authorization"]
            state,msg,user = check_authorization_key(auth_token=auth_token)
            if not state:
                return JsonResponse(msg, safe=False)
            
            #To throw an required error message
            errors = {
                'username': {'req_msg': 'User name is required','val_msg': '', 'type': ''},
                'new_password': {'req_msg': 'New password is required','val_msg': '', 'type': ''},
                'confirm_password': {'req_msg': 'Confirm password is required','val_msg': '', 'type': ''},
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors}, safe=False) 
                      
            else:                              
                user_name = data["username"]
                new_password = data["new_password"]
                confirm_password = data["confirm_password"]
                state,msg = password_validation(new_password,"new_password")                    
                if state == False:
                    return JsonResponse(msg, safe=False)                    
                else:
                    
                    if new_password == confirm_password:
                        password = make_password(confirm_password)
                        update_query = """update user_master set show_password = '{show_password}', password = '{password}' where user_name = '{user_name}';""".format(show_password=new_password,password=password,user_name=user_name)
                        # return JsonResponse(update_query,safe=False)
                        execute = django_execute_query(update_query)
                        if execute !=0:
                            response = {
                                        'action':'success',
                                        'message':'Password updated',
                                        }
                            return JsonResponse(response, safe=False,status=200)                            
                        else:
                            response = {
                                    'action':"error",
                                    'message':'Updation failed',
                                    }
                        return JsonResponse(response, safe=False,status=400)                        
                    else:
                        response = {
                                'action':'error',
                                'new_password':' New password and Confirm password does not match',
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