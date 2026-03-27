"""
====================================================================================
File                :   pages.py
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
def sections(request):
    """
    Inserts data into the master.

    Args:
        request (HttpRequest): The HTTP request object containing the data to be inserted.

    Returns:
        JsonResponse: A JSON response indicating the result of the data insertion.

    The `sections` API is responsible for adding new records to the master database.
    It expects an HTTP request object containing the data to be inserted. The data should be in a
    specific format, such as JSON, and must include the necessary fields required by the master database.
    """
    # try:
        
    if request.method in ["POST","PUT","DELETE"]:
        data = json.loads(request.body)
        utc_time = datetime.utcnow()
        request_header = request.headers
        auth_token = request_header["Authorization"]
        access_token = data["access_token"]
        table_name = 'sections'
        
        # #To verify the authorization
        state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
        if not state:
            return JsonResponse(msg, safe=False)
        
        user_id = user[0]["ref_user_id"]
        #To create the data
        if request.method == "POST":
            # To throw an required error message
            errors = {
                'page_id': {'req_msg': 'Page is required','val_msg': '', 'type': ''},
                'section_name': {'req_msg': 'Section name is required','val_msg': '', 'type': ''},
                'unique_section_name': {'req_msg': 'Unique page name is required','val_msg': 'A unique name should not have any spaces between the words', 'type': 'key_format'},
                # 'slug': {'req_msg': 'Slug is required','val_msg': '', 'type': ''},   
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,'message_type':"specific"}, safe=False)
        
            section_id = str(uuid.uuid4())
            page_id = base64_operation(data["page_id"],'decode')  
            section_name = data["section_name"]
            unique_section_name = data["unique_section_name"]
            slug = data.get("slug","")
            image_name = data.get("image_name","")
            section_image = data.get("section_image","")
            description = data.get("description","")
            if description:
                description = base64_operation(description,'encode')
            media_folder = 'media/section_images/' 
            if image_name:
                image_path = save_file(section_image, image_name, media_folder)
            else:
                image_path = ""

            media_id = base64_operation(data.get("media_id",""),'decode')  
            position = data.get("position", 0)
            is_exist, message = check_existing_value_2(unique_section_name, "unique_section_name", "UniqueSectionName", table_name)
            
            if is_exist:
                return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False) 

            query = """insert into sections (SectionID,PageID,SectionName,UniqueSectionName,Slug,MediaID,Position,CreatedAt,UpdatedAt,SectionImage,Description) values ('{SectionID}','{PageID}','{SectionName}','{UniqueSectionName}','{Slug}','{MediaID}',{Position},'{CreatedAt}','{UpdatedAt}','{SectionImage}','{Description}');""".format(SectionID=section_id,PageID=page_id,SectionName=section_name,UniqueSectionName=unique_section_name,Slug=slug,MediaID=media_id,Position=position,CreatedAt=utc_time,UpdatedAt=utc_time,SectionImage=image_path,Description=description)
            success_message = "Data created successfully"
            error_message = "Failed to create data"
        
        #To modify the data
        elif request.method == "PUT":
            #To throw an required error message
            errors = {
                'page_id': {'req_msg': 'Page is required','val_msg': '', 'type': ''},
                'section_id': {'req_msg': 'Section is required','val_msg': '', 'type': ''},
                'section_name': {'req_msg': 'Section name is required','val_msg': '', 'type': ''},
                'unique_section_name': {'req_msg': 'Unique page name is required','val_msg': 'A unique name should not have any spaces between the words', 'type': 'key_format'},
                # 'slug': {'req_msg': 'Slug is required','val_msg': '', 'type': ''},   
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,'message_type':"specific"}, safe=False)
            
            section_id = base64_operation(data["section_id"],'decode')  
            page_id = base64_operation(data["page_id"],'decode')  
            section_name = data["section_name"]
            unique_section_name = data["unique_section_name"]
            slug = data.get("slug","")
            image_name = data.get("image_name","")
            section_image = data.get("section_image","")
            description = data.get("description","")
            if description:
                description = base64_operation(description,'encode')
            section_image_path = data.get("section_image_path","") # existing image
            media_folder = 'media/section_images/' 
            
            image_path = ""
            if section_image_path != "":
                image_path = section_image_path
            elif section_image !="" and section_image != None :
                image_path = save_file(section_image, image_name, media_folder)                    
        
            media_id = base64_operation(data.get("media_id",""),'decode')  
            position = data.get("position", 0)
            is_exist, message = check_existing_value_2(unique_section_name, "unique_section_name", "UniqueSectionName", table_name, "SectionID", section_id)

            if is_exist:
                return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False) 
            
            query = """UPDATE sections SET PageID = '{PageID}', SectionName = '{SectionName}', UniqueSectionName = '{UniqueSectionName}', Slug = '{Slug}', MediaID = '{MediaID}', Position = {Position},UpdatedAt = '{UpdatedAt}',SectionImage = '{SectionImage}',Description = '{Description}' WHERE SectionID = '{SectionID}';""".format(SectionID=section_id,PageID=page_id,SectionName=section_name,UniqueSectionName=unique_section_name,Slug=slug,MediaID=media_id,Position=position,UpdatedAt=utc_time,SectionImage=image_path,Description=description)

            success_message = "Data updated successfully"
            error_message = "Failed to update data"            
        
        #To delete the data
        elif request.method == "DELETE":
            section_id = base64_operation(data["section_id"],'decode')  
            query = """DELETE FROM sections where SectionID = '{SectionID}';""".format(SectionID=section_id)
            success_message = "Data deleted successfully"
            error_message = "Failed to delete data"
        
        execute = django_execute_query(query)

        if execute!=0:
            message = {
                    'action':'success',
                    'message':success_message,
                    'SectionID':section_id
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
def sections_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `sections_get` API is responsible for fetching data from the master database
    based on the parameters provided in the HTTP request. The request may include filters, sorting
    criteria, or other parameters to customize the query.
    """
    # try:
        
    if request.method == "GET": 
        utc_time = datetime.utcnow()

        request_header = request.headers
        auth_token = request_header["Authorization"]
        access_token = request.GET["access_token"]
        table_name = 'sections'

        protocol = request.META['SERVER_PROTOCOL']
        host = protocol[:protocol.index('/')].lower() + '://' + request.META['HTTP_HOST']

        state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
        if state == False:
            return JsonResponse(msg, safe=False)
        
        else:            
            search_input = request.GET.get('search_input',None)
            page_id = request.GET.get('page_id',None)
            media_id = request.GET.get('media_id',None)
            position = request.GET.get('position',None)
            data_uniq_id = request.GET.get('data_uniq_id', None)
            unique_keyname = request.GET.get('unique_keyname', None)

            #To filter using limit,from_date,to_date,active_status,order_type,order_field
            limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

            if search_input:
                search_join += " AND ({table_name}.SectionName REGEXP '{inp}' OR {table_name}.UniqueSectionName REGEXP '{inp}' OR {table_name}.Slug REGEXP '{inp}' )".format(inp=search_input,table_name=table_name)

            if page_id:
                page_id = base64_operation(page_id, 'decode').strip()
                search_join += " AND {table_name}.PageID = '{PageID}' ".format(PageID=page_id,table_name=table_name)

            if media_id:
                media_id = base64_operation(media_id, 'decode').strip()
                search_join += " AND {table_name}.MediaID = '{MediaID}' ".format(MediaID=media_id,table_name=table_name)

            if position:
                position = position
                search_join += " AND {table_name}.Position = {Position} ".format(Position=position,table_name=table_name)

            if data_uniq_id:                            
                data_uniq_id = base64_operation(data_uniq_id,'decode')  
                search_join += "AND {table_name}.SectionID = '{data_uniq_id}' ".format(data_uniq_id=data_uniq_id,table_name=table_name)

            if unique_keyname:
                unique_keyname = unique_keyname
                search_join += " AND {table_name}.UniqueSectionName = '{UniqueKeyName}' ".format(UniqueKeyName=unique_keyname,table_name=table_name)
            
            #Query to make the count of data
            count_query = """ SELECT count(*) as count
            FROM {table_name}
            WHERE 1=1 {search_join};""".format(search_join=search_join,table_name=table_name)
            get_count = search_all(count_query)

            #Query to fetch all the data 
            fetch_data_query = """ SELECT *, DATE_FORMAT(sections.CreatedAt, '%b %d, %Y | %l:%i %p') as created_f_date,(select PageName from pages where pages.PageID = sections.PageID) as page_name FROM sections
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
                if i["SectionImage"]:
                    i["SectionImagePath"] = i['SectionImage']
                    i["SectionImage"] =  host + "/" + i['SectionImage']

                search_media = """select * from media where MediaID = '{MediaID}'""".format(MediaID=i["MediaID"])
                get_media = search_all(search_media)
                if len(get_media)!=0:
                    for k in get_media:
                        k['MediaID'] = base64_operation(k['MediaID'],'encode')
                        if k["FilePath"]:
                            k["FilePath"] =  host + "/" + k['FilePath']
                        
                        data_format(data=k,page_number=page_number,index=index)

                i['SectionID'] = base64_operation(i['SectionID'],'encode')
                i['PageID'] = base64_operation(i['PageID'],'encode')
                i['MediaID'] = base64_operation(i['MediaID'],'encode')
                if i['Description'] :
                    i['Description'] = base64_operation(i['Description'],'decode')

                i["media_details"] = get_media

                #To get encoded page_id,serial number,formatted,readable created and modified_date 
                data_format(data=i,page_number=page_number,index=index)
                                    
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
 
    # except Exception as Err:
    #     response_exception(Err)
    #     return JsonResponse(str(Err), safe=False)
    

@csrf_exempt
def sections_status(request):
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
                'section_ids': {'req_msg': 'Section is required','val_msg': '', 'type': ''}, 
                'active_status': {'req_msg': 'Active status is required','val_msg': '', 'type': ''}, 
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,"message_type":"specific"}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            section_id_list = data['section_ids']
            for section_id in section_id_list:
                section_id_en = base64_operation(section_id,'decode')  
                
                active_status = data["active_status"]                                                             
                query = """
                UPDATE sections 
                SET ActiveStatus = {active_status} WHERE SectionID = '{SectionID}';
                """.format(SectionID=section_id_en,active_status=active_status)
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
def sections_delete(request):
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
                'section_ids': {'req_msg': 'Section is required','val_msg': '', 'type': ''}, 
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,"message_type":"specific"}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            section_id_list = data['section_ids']
            for section_id in section_id_list:
                section_id_en = base64_operation(section_id,'decode')  
                                                           
                query = """delete from sections where SectionID = '{SectionID}';""".format(SectionID=section_id_en)                
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
    