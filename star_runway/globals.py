
from django.conf import settings
from db_interface.queries import *
from db_interface.execute import *
from django.views.decorators.csrf import csrf_exempt
from utilities.constants import *
import json,re,os
from django.http import JsonResponse
import base64
import smtplib
import random
from django.http import JsonResponse
from django.conf import settings
import pytz
from datetime import datetime
import humanize
import requests
from django.core.files.storage import default_storage
from .settings import MEDIA_ROOT
from django.core.files.base import ContentFile


# This function is used to check the authorization 
def authorize(auth_token,access_token):
    msg = ''
    state = True
    response = ''

    #To check the Authorization token
    if auth_token != 'Th45Dc@g9K3gaFuWlaLV901Ds2':
        msg = {'status': 400, 'message': 'Authorization Failed'}
        state = False

    #To check the access token from user master table
    user_validation = """ SELECT * from user_master where access_token =  '{access_token}' """
    sql = user_validation.format(access_token=access_token)
    response = search_all(sql)
    if len(response) == 0 :
       msg = {
                'status':400,
                'action_status': 'Error',
                'message': 'User Access Denied'
       }
       state = False


    return state,msg,response
       

# This API is to check the validity of the access token
@csrf_exempt
def valid_token(request):

    """
    API for Validate User Access Token for Validating the token by checking into the user_master table.
    """
    try:
        if request.method != 'GET':
            message =   {
                            'status':400,
                            'action_status':'failed',
                            'message': 'Wrong Request'
                                
                        }
            return JsonResponse(message, safe=False)
        
        elif request.method == 'GET': 
            try:

                # checking the Authorization token
                request_header = request.headers
                if request_header['Authorization'] != 'Th45Dc@g9K3gaFuWlaLV901Ds2':
                    resp = {'status':400,'message':'Authorization Failed'}
                    return JsonResponse(resp, safe=False)
                else:

                    # Validating the user data
                    user_token= request.GET.get('user_token')  
                    user_validation = """ SELECT * from users_login_table where access_token =  '{access_token}' """

                    sql = user_validation.format(access_token=user_token) 
                    records=search_all(sql) 
                    if len(records) != 0 : 
                        user_id = records[0]['ref_user_id']
                        get_user_dts = """ select * from user_master where data_uniq_id = '{user_id}' and active_status = 1 ;""".format(user_id = user_id)
                        user_dtls = search_all(get_user_dts)

                        if len(user_dtls) != 0:
                            user_name = user_dtls[0]['user_name']
                            user_type = user_dtls[0]['user_type']
                            first_name = user_dtls[0]['first_name']
                            email = user_dtls[0]['email']
                            mobile = user_dtls[0]['mobile']
                            message = {                                
                                'action':'success',
                                'user_type':int(user_type),
                                'access_token':user_token,
                                'user_data':{
                                'user_name':user_name,
                                'user_id':base64_operation(user_id,'encode'),
                                'access_token':user_token,'user_type':user_type,'first_name':first_name,'email':email,'mobile':mobile,
                                }
                            }
                            return JsonResponse(message, safe=False,status = 200)
                        else:
                            message = {
                    
                                'action':'error',
                                'message': 'This Account is Inactivated by Admin. Please Contact the admin!!' 
                            }
                        return JsonResponse(message, safe=False,status = 600)
                    else:
                        message = {                                
                                'action':'error',
                                'message': 'Invalid Token' 
                            }
                        return JsonResponse(message, safe=False,status = 200)
                
            except Exception as Err:
                response_exception(Err)
                return JsonResponse(Err, safe=False)
        else:
            message = {                                
                    'action':'error',
                    'message': 'Wrong Request'                                
                    }
            return JsonResponse(message, safe=False, status = 400)

    except Exception as Err:
        response_exception(Err)
        return JsonResponse(Err, safe=False)



#This function is created to decode and encode the data    
@csrf_exempt
def base64_operation(input_str, operation='encode'):
    # Encode string to bytes
    input_str = str(input_str)
    string_bytes = input_str.encode('utf-8')
    
    # Perform the operation based on the input
    if operation == 'encode':
        # Encode bytes to base64
        base64_bytes = base64.b64encode(string_bytes)
        # Convert bytes to string
        output_str = base64_bytes.decode('utf-8')
        # Remove padding character and unwanted characters
        output_str = output_str.replace('=', '').replace('-', '').replace('_', '')
    elif operation == 'decode':
        # Add padding character as needed
        input_str = input_str + '=' * (4 - len(input_str) % 4)
        # Convert string to bytes
        base64_bytes = input_str.encode('utf-8')
        # Decode base64 bytes to bytes
        string_bytes = base64.b64decode(base64_bytes)
        # Convert bytes to string
        output_str = string_bytes.decode('utf-8')
    else:
        raise ValueError("Invalid operation specified. Please use 'encode' or 'decode'.")
    
    return output_str

def web_data_format(data,page_number,index):
    created_date = data["CreatedAt"]
    modified_date = data["UpdatedAt"]

    data['s_no'] = ((int(page_number) - 1) * 10 ) + index + 1
    data['formatted_created_date'] = convert_to_user_timezone(data['CreatedAt'])
    data['formatted_modified_date'] = convert_to_user_timezone(data['UpdatedAt'])
   
    calculated_time = format_time_difference (created_date)
    calculated_time = format_time_difference (modified_date)
    data['readable_created_date'] = calculated_time
    data['readable_modified_date'] = calculated_time



#To generate the four digit otp number
def generate_otp():
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # Generates a 6-digit OTP
    return otp
    

#This function is created to validate password 
def password_validation(password,field_name):
    msg = ''
    state = True
    
    if len(password)<8:
        state = False
        msg = "Password must be 8 characters long"
    elif not re.search("[A-Z]",password):
        state = False
        msg = "Password must have one capital Letter"
    elif not re.search("[0-9]",password):
        state = False
        msg = "Password must have numbers"
    elif not re.search("[@$!%*?&]",password):
        state = False
        msg = "Password must have one special character"

    msg = {
        'status':400,
        'action': 'error',
        "message" : {
            field_name: msg  # Using 'mobile' as the key
        }
    }

    return state,msg


# This function is used to check the authorization for multiple login 
def check_authorization_key(auth_token):
    msg = ''
    state = True
    response = ''
    if auth_token != 'Th45Dc@g9K3gaFuWlaLV901Ds2':
        msg = {'status': 400, 'action': 'error', 'message': 'Authorization Failed'}
        state = False

    return state,msg,response


# This function is used to check the authorization for multiple login 
def authorization(auth_token,access_token):
    msg = ''
    state = True
    response = ''
    if auth_token != 'Th45Dc@g9K3gaFuWlaLV901Ds2':
        msg = {'status': 400, 'message': 'Authorization Failed'}
        state = False

    user_validation = """ SELECT * from users_login_table where access_token =  '{access_token}' """
    # return JsonResponse(user_validation,safe=False)
    sql = user_validation.format(access_token=access_token)
    response = search_all(sql)
    if len(response) == 0 :
       msg = {
                'status':400,
                'action': 'error',
                'message': 'User access denied'
       }
       state = False

    return state,msg,response

# # To store utc time using mysql db(created_date)       
def convert_to_user_timezone(utc_time, user_time_zone='Asia/Kolkata'):
    # Parse the UTC time string to a datetime object
    # utc_datetime = datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')

    # Define the user's time zone using pytz
    user_tz = pytz.timezone(user_time_zone)

    # Convert the UTC datetime to the user's time zone
    user_datetime = utc_time.replace(tzinfo=pytz.utc).astimezone(user_tz)

    # Format the user_datetime as per your requirement
    formatted_datetime = user_datetime.strftime('%b %d, %Y | %I:%M %p')

    return formatted_datetime



#This API is created to decode and encode the data    
@csrf_exempt
def decode_encode(request):

    """
    API just for decoding and encoding.
    """
    try:
        if request.method == 'GET':
            try:

                # Checking Authorization key
                request_header = request.headers
                if request_header['Authorization'] != "Th45Dc@g9K3gaFuWlaLV901Ds2":
                    resp = {'status':400,'message':'Authorization Failed'}
                    return JsonResponse(resp, safe=False)
                else:
                    type_of = request.GET['type']
                    string = request.GET['string']
                    string_decode = base64_operation(string,type_of)
                    print(string_decode)
                    return JsonResponse(string_decode, safe=False)
            except:
                response_exception(Err)
                return JsonResponse(Err, safe=False)
        else:
            message = {
                            'status':400,
                            'action_status':'Error',
                            'message':'Wrong Request'
                        }
            return JsonResponse(message,safe=False)
    except Exception as Err:
        response_exception(Err)
        return JsonResponse(Err, safe=False)
    
#This function is created to validate the data    
def validate_data(data,errors):
    phone_number_pattern =  r'^\d{10}$'
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    ifsc_pattern = r"^[A-Z]{4}0[A-Z0-9]{6}$"
    pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    time_pattern = r'^\d{2}:\d{2}:\d{2}$'
    datetime_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$'
    aadhar_pattern = r"^\d{4}\s?\d{4}\s?\d{4}$"
    gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
    # Two digits
    # Five uppercase alphabetic characters
    # Four digits
    # One uppercase alphabetic character
    # One character, either a digit from 1 to 9 or an uppercase alphabetic character
    # One uppercase 'Z' 
    # One character, which can be either a digit (0-9) or an uppercase alphabetic character


    validation_errors = {}
    for field, error_message in errors.items():
        if field not in data or data[field] == "":
            validation_errors[field] = error_message['req_msg']
        else:
            if error_message['type'] == 'string' and (not isinstance(data[field], str) or not data[field].strip()):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'mobile' and ( not re.match(phone_number_pattern, data[field])):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'email' and ( not re.match(email_pattern, data[field])):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'ifsc' and ( not re.match(ifsc_pattern, data[field])):
                validation_errors[field] = error_message['val_msg'] 
            if error_message['type'] == 'pan' and ( not re.match(pan_pattern, data[field])):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'date' and ( not re.match(date_pattern, data[field])):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'time' and ( not re.match(time_pattern, data[field])):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'datetime' and ( not re.match(datetime_pattern, data[field])):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'pincode' and (requests.get(f"https://api.postalpincode.in/pincode/{data[field]}").json()[0].get('Status') != 'Success'):                
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'int' and ( not data[field].isdigit() ):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'float' and ( not float(data[field]) ):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'aadhar' and ( not re.match(aadhar_pattern, data[field])):
                validation_errors[field] = error_message['val_msg']
            if error_message['type'] == 'gst' and ( not re.match(gst_pattern, data[field])):
                validation_errors[field] = error_message['val_msg']
               
    return validation_errors


def data_validation(data,error):
    aadhar_pattern = r"^\d{4}\s?\d{4}\s?\d{4}$"
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    validation_errors = {}

    for field, error_message in error.items():
        if error_message['type'] == 'date' and ( not re.match(date_pattern, data[field])):
            validation_errors[field] = error_message['val_msg']
        if error_message['type'] == 'aadhar' and ( not re.match(aadhar_pattern, data[field])):
                validation_errors[field] = error_message['val_msg']

    return validation_errors



#This function is created to format the date from the get data    
def format_time_difference(past_time):
    current_time = datetime.now()
    time_difference = current_time - past_time
    return humanize.naturaldelta(time_difference) + ' ago'

#This function is created to filter the get data    
def data_filter(request,table_name=None):

    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date',None)
    has_limit = request.GET.get('has_limit',1)
    page_number = int(request.GET.get('page', 1))
    items_per_page = int(request.GET.get('items_per_page', 10))
    active_status = request.GET.get('active_status', None)
    order_field = request.GET.get('order_field', f'{table_name}.CreatedAt')
    order_type = request.GET.get('order_type', 'DESC')
    data_uniq_id = request.GET.get('data_uniq_id', None)

    search_join = ""

    if data_uniq_id:                            
        data_uniq_id = base64_operation(data_uniq_id,'decode')  
        search_join += "AND {table_name}.data_uniq_id = '{data_uniq_id}' ".format(data_uniq_id=data_uniq_id,table_name=table_name)
    if active_status :
        search_join += " and {table_name}.active_status = {active_status}".format(active_status=active_status,table_name=table_name)
    if from_date :  
        search_join += " and {table_name}.CreatedAt >= '{from_date}' ".format(from_date=from_date+" 00:00:00",table_name=table_name)
    if to_date:
        search_join += "  and {table_name}.CreatedAt <= '{to_date}'".format(to_date=to_date+ " 23:59:59",table_name=table_name)
    if int(has_limit) == 1:
        limit_offset = f" LIMIT {items_per_page} OFFSET {(page_number - 1) * items_per_page}"
    else:
        limit_offset = ""
    order_by = " order by {order_field} {order_type} ".format(order_field=order_field,order_type=order_type)  
    
    return limit_offset,search_join,items_per_page,page_number,order_by
    
#This function is created to format the get data
def data_format(data,page_number,index):
    created_date = data["CreatedAt"]
    modified_date = data["UpdatedAt"]

    data['s_no'] = ((int(page_number) - 1) * 10 ) + index + 1
    data['formatted_created_date'] = convert_to_user_timezone(data['CreatedAt'])
    data['formatted_modified_date'] = convert_to_user_timezone(data['UpdatedAt'])
   
    calculated_time = format_time_difference (created_date)
    calculated_time = format_time_difference (modified_date)
    data['readable_created_date'] = calculated_time
    data['readable_modified_date'] = calculated_time

#This function is created to format the get data
def data_formats(data,page_number,index):
    created_date = data["created_date"]
    modified_date = data["modified_date"]

    data['s_no'] = ((int(page_number) - 1) * 10 ) + index + 1
    data['formatted_created_date'] = convert_to_user_timezone(data['created_date'])
    data['formatted_modified_date'] = convert_to_user_timezone(data['modified_date'])
   
    calculated_time = format_time_difference (created_date)
    calculated_time = format_time_difference (modified_date)
    data['readable_created_date'] = calculated_time
    data['readable_modified_date'] = calculated_time

# #Function to upload file as json data
# def save_file(file_data, file_name, media_folder):
#     if not os.path.exists(media_folder):
#         os.makedirs(media_folder)
#     file_content = base64.b64decode(file_data)
#     file_path = os.path.join(media_folder, os.path.basename(file_name))
#     with open(file_path, 'wb') as f:
#         f.write(file_content)
#     return file_path

def save_file(file_data, file_name, media_folder):
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    if cloud_name and api_key and api_secret:
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
            file_content = base64.b64decode(file_data)
            folder = media_folder.strip('/').replace('media/', '')
            public_id = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}-{os.path.splitext(file_name)[0]}"
            result = cloudinary.uploader.upload(
                file_content,
                folder=folder,
                public_id=public_id,
                resource_type='auto'
            )
            return result['secure_url']
        except Exception as e:
            print(f"Cloudinary upload failed: {e}")

    if not os.path.exists(media_folder):
        os.makedirs(media_folder)
    file_content = base64.b64decode(file_data)
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_file_name = f"{current_datetime}-{file_name}"
    file_path = os.path.join(media_folder, new_file_name)
    with open(file_path, 'wb') as f:
        f.write(file_content)
    return file_path


#Function to upload file as form data
def upload_file_formdata(media_folder, uploaded_file, folder_name):
    utc_time = datetime.utcnow()

    if not os.path.exists(media_folder):
        os.makedirs(media_folder)
                
    img_ext = uploaded_file.name.split('.')[-1]
    image_name = uploaded_file.name.split('.')[0]
    formatted_utc_time = utc_time.strftime('%d%b%y-%H%M%S').lower()
    image_file_path = os.path.join(folder_name, f"{image_name}-{formatted_utc_time}.{img_ext}")
    image_file = default_storage.save(image_file_path, ContentFile(uploaded_file.read()))
    img_path = default_storage.url(image_file)

    return img_path


def check_existing_value(field_value, field_name, table_name, data_uniq_id=None):
    is_exist = False
    msg = ''
    exist_query = ''

    if data_uniq_id:
        exist_query = f" and data_uniq_id != '{data_uniq_id}'"

    # Check for existing field value
    if search_all(f"SELECT * FROM {table_name} WHERE {field_name} = '{field_value}' {exist_query}"):
        is_exist = True
        msg = f"{field_name.replace('_', ' ').capitalize()} already exists"
        
    message = {
        field_name: msg
    }
    return is_exist, message

#Function to check the existing value for string fields
def check_existing_value_2(field_value, field_name, table_field_name, table_name, id_name=None, id_name_value=None):
    is_exist = False
    msg = ''
    exist_query = ''

    if id_name:
        exist_query = f" and {id_name} != '{id_name_value}'"

    # Check for existing field value
    if search_all(f"SELECT * FROM {table_name} WHERE {table_field_name} = '{field_value}' {exist_query}"):
        is_exist = True
        msg = f"{field_name.replace('_', ' ').capitalize()} already exists"
        
    message = {
        field_name: msg
    }
    return is_exist, message



