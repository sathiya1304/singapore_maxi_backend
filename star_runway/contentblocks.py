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
def contentblocks(request):
    """
    Inserts data into the master.

    Args:
        request (HttpRequest): The HTTP request object containing the data to be inserted.

    Returns:
        JsonResponse: A JSON response indicating the result of the data insertion.

    The `contentblocks` API is responsible for adding new records to the master database.
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
            table_name = 'contentblocks'
            
            # #To verify the authorization
            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if not state:
                return JsonResponse(msg, safe=False)
            
            user_id = user[0]["ref_user_id"]
            #To create the data
            if request.method == "POST":
                # To throw an required error message
                errors = {
                    'section_id': {'req_msg': 'Section is required','val_msg': '', 'type': ''},
                    'contenttype_id': {'req_msg': 'Content type is required','val_msg': '', 'type': ''},
                    'description': {'req_msg': 'Description is required','val_msg': '', 'type': ''},
                    'title': {'req_msg': 'Title is required','val_msg': '', 'type': ''}, 
                    'slug': {'req_msg': 'Slug is required','val_msg': '', 'type': ''},
                    'unique_contentblock_name': {'req_msg': 'Unique block name is required','val_msg': '', 'type': ''},   
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,'message_type':"specific"}, safe=False)
            
                contentblock_id = str(uuid.uuid4())
                section_id = base64_operation(data["section_id"],'decode')
                contenttype_id = base64_operation(data["contenttype_id"],'decode')  
                description = base64_operation(data["description"],'encode')
                title = data["title"]
                subtitle = data.get("subtitle","")
                description_two = base64_operation(data.get("description_two",""),'encode')
                slug = data["slug"]
                media_id = base64_operation(data.get("media_id",""),'decode')  
                position = data.get("position", 0)
                settings = data.get("settings","")
                unique_contentblock_name = data["unique_contentblock_name"]

                is_exist, message = check_existing_value(unique_contentblock_name, "unique_contentblock_name", "UniqueContentBlockName",table_name)
                
                if is_exist:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False) 
   
                query = """insert into contentblocks (ContentBlockID,SectionID,ContentTypeID,Title,SubTitle,Description,DescriptionTwo,Slug,MediaID,Position,Settings,UniqueContentBlockName,CreatedAt,UpdatedAt) values ('{ContentBlockID}','{SectionID}','{ContentTypeID}','{Title}','{SubTitle}',{Description},{DescriptionTwo},'{Slug}','{MediaID}',{Position},'{Settings}','{UniqueContentBlockName}','{CreatedAt}','{UpdatedAt}');""".format(ContentBlockID=contentblock_id,SectionID=section_id,ContentTypeID=contenttype_id,Title=title,SubTitle=subtitle,Description=json.dumps(description),DescriptionTwo=json.dumps(description_two),Slug=slug,MediaID=media_id,Position=position,Settings=settings,UniqueContentBlockName=unique_contentblock_name,CreatedAt=utc_time,UpdatedAt=utc_time)
                
                success_message = "Data created successfully"
                error_message = "Failed to create data"
            
            #To modify the data
            elif request.method == "PUT":
                #To throw an required error message
                errors = {
                    'section_id': {'req_msg': 'Section is required','val_msg': '', 'type': ''},
                    'contentblock_id': {'req_msg': 'Content block is required','val_msg': '', 'type': ''},
                    'contenttype_id': {'req_msg': 'Content type is required','val_msg': '', 'type': ''},
                    'description': {'req_msg': 'Description is required','val_msg': '', 'type': ''},
                    'title': {'req_msg': 'Title is required','val_msg': '', 'type': ''}, 
                    'slug': {'req_msg': 'Slug is required','val_msg': '', 'type': ''},   
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,'message_type':"specific"}, safe=False)
                
                contentblock_id = base64_operation(data["contentblock_id"],'decode')  
                section_id = base64_operation(data["section_id"],'decode')
                contenttype_id = base64_operation(data["contenttype_id"],'decode')  
                description = base64_operation(data["description"],'encode')
                title = data["title"]
                subtitle = data.get("subtitle","")
                description_two = base64_operation(data.get("description_two",""),'encode')
                slug = data["slug"]
                media_id = base64_operation(data.get("media_id",""),'decode')  
                position = data.get("position", 0)
                settings = data.get("settings","")
                unique_contentblock_name = data["unique_contentblock_name"]

                is_exist, message = check_existing_value(unique_contentblock_name, "unique_contentblock_name", "UniqueContentBlockName", table_name, "ContentBlockID", contentblock_id)
                
                if is_exist:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False) 
                
                query = """UPDATE contentblocks SET SectionID = '{SectionID}', ContentTypeID = '{ContentTypeID}', Title = '{Title}', SubTitle = '{SubTitle}', Description = {Description}, DescriptionTwo = {DescriptionTwo}, Slug = '{Slug}', MediaID = '{MediaID}', Position = {Position}, Settings = '{Settings}', UniqueContentBlockName = '{UniqueContentBlockName}',UpdatedAt = '{UpdatedAt}' WHERE ContentBlockID = '{ContentBlockID}';""".format(ContentBlockID=contentblock_id,SectionID=section_id,ContentTypeID=contenttype_id,Title=title,SubTitle=subtitle,Description=json.dumps(description),DescriptionTwo=json.dumps(description_two),Slug=slug,MediaID=media_id,Position=position,Settings=settings,UniqueContentBlockName=unique_contentblock_name,UpdatedAt=utc_time)

                success_message = "Data updated successfully"
                error_message = "Failed to update data"            
           
            #To delete the data
            elif request.method == "DELETE":
                contentblock_id = base64_operation(data["contentblock_id"],'decode')    
                query = """DELETE FROM contentblocks where ContentBlockID = '{ContentBlockID}';""".format(ContentBlockID=contentblock_id)
                success_message = "Data deleted successfully"
                error_message = "Failed to delete data"
           
            execute = django_execute_query(query)

            if execute!=0:
                message = {
                        'action':'success',
                        'message':success_message,
                        'ContentBlockID':contentblock_id
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
def contentblocks_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `contentblocks_get` API is responsible for fetching data from the master database
    based on the parameters provided in the HTTP request. The request may include filters, sorting
    criteria, or other parameters to customize the query.
    """
    try:
        
        if request.method == "GET": 
            utc_time = datetime.utcnow()

            request_header = request.headers
            auth_token = request_header["Authorization"]
            access_token = request.GET["access_token"]
            table_name = 'contentblocks'

            protocol = request.META['SERVER_PROTOCOL']
            host = protocol[:protocol.index('/')].lower() + '://' + request.META['HTTP_HOST']

            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if state == False:
                return JsonResponse(msg, safe=False)
            
            else:            
                search_input = request.GET.get('search_input',None)
                section_id = request.GET.get('section_id',None)
                media_id = request.GET.get('media_id',None)
                position = request.GET.get('position',None)
                data_uniq_id = request.GET.get('data_uniq_id', None)

                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_join += " AND ({table_name}.UniqueContentBlockName REGEXP '{inp}' OR {table_name}.Title REGEXP '{inp}' OR {table_name}.SubTitle REGEXP '{inp}' OR {table_name}.Description REGEXP '{inp}' OR {table_name}.DescriptionTwo REGEXP '{inp}' OR {table_name}.Settings REGEXP '{inp}' )".format(inp=search_input,table_name=table_name)

                if data_uniq_id:                            
                    data_uniq_id = base64_operation(data_uniq_id,'decode')  
                    search_join += "AND {table_name}.ContentBlockID = '{data_uniq_id}' ".format(data_uniq_id=data_uniq_id,table_name=table_name)

                if section_id:
                    section_id = base64_operation(section_id, 'decode').strip()
                    search_join += " AND {table_name}.SectionID = '{SectionID}' ".format(SectionID=section_id,table_name=table_name)

                if media_id:
                    media_id = base64_operation(media_id, 'decode').strip()
                    search_join += " AND {table_name}.MediaID = '{MediaID}' ".format(MediaID=media_id,table_name=table_name)

                if position:
                    position = position
                    search_join += " AND {table_name}.Position = {Position} ".format(Position=position,table_name=table_name)


                #Query to make the count of data
                count_query = """ SELECT count(*) as count
                FROM {table_name}
                WHERE 1=1 {search_join};""".format(search_join=search_join,table_name=table_name)
                get_count = search_all(count_query)

                #Query to fetch all the data 
                fetch_data_query = """ SELECT *, DATE_FORMAT(contentblocks.CreatedAt, '%b %d, %Y | %l:%i %p') as created_f_date FROM contentblocks WHERE 1=1  {search_join} {order_by} {limit};""".format(search_join=search_join,order_by=order_by,limit=limit_offset) 
                                    
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
                    #To get encoded page_id,serial number,formatted,readable created and modified_date 
                    data_format(data=i,page_number=page_number,index=index,user_time_zone=user[0]['user_time_zone'])

                    search_sections = """select * from sections where SectionID = '{SectionID}'""".format(SectionID=i["SectionID"])
                    get_sections = search_all(search_sections)
                    
                    search_media = """select * from media where MediaID = '{MediaID}'""".format(MediaID=i["MediaID"])
                    get_media = search_all(search_media)

                    search_contenttype = """select * from contenttypes where ContentTypeID = '{ContentTypeID}'""".format(ContentTypeID=i["ContentTypeID"])
                    get_contenttype = search_all(search_contenttype)

                    if len(get_sections)!=0:
                        for j in get_sections:
                            search_pages = """select * from pages where PageID = '{PageID}'""".format(PageID=j['PageID'])
                            get_pages = search_all(search_pages)
                            if len(get_pages)!=0:
                                j['page_details'] = get_pages 
                                for m in get_pages:
                                    m['PageID'] = base64_operation(m['PageID'],'encode')

                            j['PageID'] = base64_operation(j['PageID'],'encode')
                            j['SectionID'] = base64_operation(j['SectionID'],'encode')
    
                            data_format(data=j,page_number=page_number,index=index,user_time_zone=user[0]['user_time_zone'])

                    if len(get_media)!=0:
                        for k in get_media:
                            k['MediaID'] = base64_operation(k['MediaID'],'encode')
                            if k["FilePath"]:
                                k["FilePath"] =  host + "/" + k['FilePath']
                            
                            data_format(data=k,page_number=page_number,index=index,user_time_zone=user[0]['user_time_zone'])

                    if len(get_contenttype)!=0:
                        for l in get_contenttype:
                            l['ContentTypeID'] = base64_operation(l['ContentTypeID'],'encode')
                            
                            data_format(data=l,page_number=page_number,index=index,user_time_zone=user[0]['user_time_zone'])
                            
                    i['ContentBlockID'] = base64_operation(i['ContentBlockID'],'encode')
                    i['SectionID'] = base64_operation(i['SectionID'],'encode')
                    i['ContentTypeID'] = base64_operation(i['ContentTypeID'],'encode')
                    i['MediaID'] = base64_operation(i['MediaID'],'encode')
                    i['Description'] = base64_operation(i['Description'],'decode')
                    i['DescriptionTwo'] = base64_operation(i['DescriptionTwo'],'decode')
                    i["section_details"] = get_sections
                    i["media_details"] = get_media
                    i["content_type_details"] = get_contenttype
                                       
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
def contentblocks_status(request):
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
                'contentblock_ids': {'req_msg': 'Content Block is required','val_msg': '', 'type': ''}, 
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,"message_type":"specific"}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            contentblock_id_list = data['contentblock_ids']
            for contentblock_id in contentblock_id_list:
                contentblock_id_en = base64_operation(contentblock_id,'decode')  
                
                active_status = data["active_status"]                                                             
                query = """
                UPDATE contentblocks 
                SET ActiveStatus = {active_status} WHERE ContentBlockID = '{ContentBlockID}';
                """.format(ContentBlockID=contentblock_id_en,active_status=active_status)
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
def contentblocks_delete(request):
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
                'contentblock_ids': {'req_msg': 'Content Block is required','val_msg': '', 'type': ''}, 
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,"message_type":"specific"}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            contentblock_id_list = data['contentblock_ids']
            for contentblock_id in contentblock_id_list:
                contentblock_id_en = base64_operation(contentblock_id,'decode')  
                                                       
                query = """delete from contentblocks where ContentBlockID = '{ContentBlockID}';""".format(ContentBlockID=contentblock_id_en)                
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
 