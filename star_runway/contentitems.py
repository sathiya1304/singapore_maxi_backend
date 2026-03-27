"""
====================================================================================
File                :   contentitems.py
Description         :   This file contains code related to the contentitems API.
Author              :   Haritha sree S
Date Created        :   June 3rd 2024
Last Modified BY    :   Haritha sree S
Date Modified       :   June 3rd 2024
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

#This api is created to create and edit content items9separate edit api is also available)
@csrf_exempt
def contentitems(request):
    """
    Inserts data into the master.

    Args:
        request (HttpRequest): The HTTP request object containing the data to be inserted.

    Returns:
        JsonResponse: A JSON response indicating the result of the data insertion.

    The `contentitems` API is responsible for adding new records to the master database.
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
            table_name = 'contentitems'
            
            # #To verify the authorization
            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if not state:
                return JsonResponse(msg, safe=False)
            
            user_id = user[0]["ref_user_id"]
            #To create the data
            if request.method == "POST":
                # To throw an required error message
                errors = {
                    'content_block_id': {'req_msg': 'Content block is required','val_msg': '', 'type': ''},
                    # 'unique_keyname': {'req_msg': 'Unique key name is required','val_msg': 'A unique name should not have any spaces between the words', 'type': 'key_format'},
                    'contenttype': {'req_msg': 'Content type is required','val_msg': '', 'type': ''},  
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,'message_type':"specific"}, safe=False)
            
                contentitems_id = str(uuid.uuid4())
                content_block_id = base64_operation(data["content_block_id"],'decode') 
                contenttype = data["contenttype"]
                content = data["content"]
                key_name = data["key_name"]
                unique_keyname = data["unique_keyname"]
                position = data["position"]
                price = data.get("price","")
                
                media_path = ""
                json_data = ""
                text = ""
                html = ""

                if contenttype == "media":
                    item_image_name = data.get("item_image_name","")
                    item_image = data.get("item_image","")
                    media_folder = 'media/item_images/' 
                    if item_image_name:
                        media_path = save_file(item_image, item_image_name, media_folder)
                elif contenttype == "json":                        
                    json_data = base64_operation(content,'encode')
                elif contenttype == "text":
                    text = base64_operation(content,'encode')
                elif contenttype == "html":
                    html = content

                # is_exist, message = check_existing_value(unique_keyname, "unique_keyname", "UniqueKeyName", table_name)
                
                # if is_exist:
                #     return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False) 

                select_query = """select * from contentblocks where ContentBlockID = '{ContentBlockID}'""".format(ContentBlockID=content_block_id)
                get_query = search_all(select_query)
                if len(get_query)!=0:
                    section_id = get_query[0]["SectionID"]

                search_position = """select * from contentitems where Position = {position} and ContentBlockID = '{content_block_id}'""".format(position=position,content_block_id=content_block_id)
                get_position = search_all(search_position)
                if len(get_position) !=0:
                    message = {
                        "position":"Position already exists"
                    }
                    return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False)
   
                query = """insert into contentitems (ContentItemID,ContentBlockID,RefSectionId,Content,ContentType,KeyName,UniqueKeyName,MediaID,ExtraData,Position,HtmlContent,CreatedAt,UpdatedAt,price) values ('{ContentItemID}','{ContentBlockID}','{RefSectionId}','{Content}','{ContentType}','{KeyName}','{UniqueKeyName}','{MediaID}','{ExtraData}','{Position}','{HtmlContent}','{CreatedAt}','{UpdatedAt}','{price}');""".format(ContentItemID=contentitems_id,ContentBlockID=content_block_id,RefSectionId=section_id,Content=text,ContentType=contenttype,KeyName=key_name,UniqueKeyName=unique_keyname,MediaID=media_path,ExtraData=json_data,Position=position,HtmlContent=html,CreatedAt=utc_time,UpdatedAt=utc_time,price=price)

                success_message = "Data created successfully"
                error_message = "Failed to create data"
            
            #To modify the data
            elif request.method == "PUT":
                #To throw an required error message
                errors = {
                    'contentitems_id': {'req_msg': 'Content item is required','val_msg': '', 'type': ''},
                    'contenttype': {'req_msg': 'Content type is required','val_msg': '', 'type': ''},  
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,'message_type':"specific"}, safe=False)
                
                user_id = user[0]["ref_user_id"]
                contentitems_id = base64_operation(data["contentitems_id"],'decode') 
                contenttype = data["contenttype"]
                content = data["content"]
                position = data["position"]
                price = data["price"]
                
                media_path = ""
                json_data = ""
                text = ""
                html = ""

                search_query = """select * from contentitems where ContentItemID = '{contentitems_id}'""".format(contentitems_id=contentitems_id)
                get_query = search_all(search_query)
                
                content_block_id = get_query[0]["ContentBlockID"]

                search_position = """select * from contentitems where Position = {position} and ContentBlockID = '{content_block_id}' and ContentItemID != '{contentitems_id}'""".format(position=position,content_block_id=content_block_id,contentitems_id=contentitems_id)
                get_position = search_all(search_position)
                # return JsonResponse(search_position,safe=False)
                if len(get_position) !=0:
                    message = {
                        "position":"Position already exists"
                    }
                    return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False)

                if contenttype == "media":
                    item_image_name = data.get("item_image_name","")
                    item_image = data.get("item_image","")
                    media_folder = 'media/item_images/' 
                    if item_image_name:
                        media_path = save_file(item_image, item_image_name, media_folder)
                    else:
                        media_path = get_query[0]["MediaID"]

                elif contenttype == "json": 
                    if content:                        
                        json_data = base64_operation(content,'encode')
                    else:
                        json_data = get_query[0]["ExtraData"]
                elif contenttype == "text":
                    if content:
                        text = base64_operation(content,'encode')
                    else:
                        text = get_query[0]["Content"]
                elif contenttype == "html":
                    if content:
                        html = content
                    else:
                        html = get_query[0]["HtmlContent"]

                query = """UPDATE contentitems SET Content = '{Content}',MediaID = '{MediaID}',ExtraData = '{ExtraData}',Position = '{Position}',CreatedAt = '{CreatedAt}',UpdatedAt = '{UpdatedAt}',HtmlContent = '{HtmlContent}',price = '{price}' WHERE ContentItemID = '{ContentItemID}';""".format(ContentItemID=contentitems_id,Content=text,MediaID=media_path,ExtraData=json_data,Position=position,CreatedAt=utc_time,UpdatedAt=utc_time,HtmlContent=html,price=price)
                execute = django_execute_query(query)
                success_message = "Data updated successfully"
                error_message = "Failed to update data"           
            
            #To delete the data
            elif request.method == "DELETE":
                contentitems_id = base64_operation(data["contentitems_id"],'decode') 
                query = """DELETE FROM contentitems where ContentItemID = '{ContentItemID}';""".format(ContentItemID=contentitems_id)
                success_message = "Data deleted successfully"
                error_message = "Failed to delete data"
           
            execute = django_execute_query(query)

            if execute!=0:
                message = {
                        'action':'success',
                        'message':success_message,
                        'contentitemsID':contentitems_id
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
def create_multiple_items(request):
    """
    Inserts datas into the master.

    Args:
        request (HttpRequest): The HTTP request object containing the data to be inserted.

    Returns:
        JsonResponse: A JSON response indicating the result of the data insertion.

    The `create_multiple_items` API is responsible for adding new records to the master database.
    It expects an HTTP request object containing the data to be inserted. The data should be in a
    specific format, such as JSON, and must include the necessary fields required by the master database.
    """
    try:
        
        if request.method == "POST":
            data = json.loads(request.body)
            utc_time = datetime.utcnow()
            request_header = request.headers
            auth_token = request_header["Authorization"]
            access_token = data["access_token"]
            table_name = 'contentitems'
            
            #To verify the authorization
            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if not state:
                return JsonResponse(msg, safe=False)
            
            user_id = user[0]["ref_user_id"]            
            
            errors = {
                    'content_block_id': {'req_msg': 'Content block is required','val_msg': '', 'type': ''},
                    'unique_page_name': {'req_msg': 'Unique page name is required','val_msg': 'A unique name should not have any spaces between the words', 'type': 'key_format'},  
                    'contenttype': {'req_msg': 'Content type is required','val_msg': '', 'type': ''},  
                }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,'message_type':"specific"}, safe=False)
            
            content_block_id = base64_operation(data["content_block_id"],'decode') 
            select_query = """select * from contentblocks where ContentBlockID = '{ContentBlockID}'""".format(ContentBlockID=content_block_id)
            get_query = search_all(select_query)
            if len(get_query)!=0:
                section_id = get_query[0]["SectionID"]

            items_list = data.get('items_list',"")
            error_data = []
            for index,i in enumerate(items_list):
                unique_keyname = i["unique_keyname"]
                is_exist, message = check_existing_value(unique_keyname, "unique_keyname", "UniqueKeyName",table_name)
            
                if is_exist:
                    error_data.append({'index': index,index: message}) 
                
            if len(error_data) !=0:
                return JsonResponse({'status': 400, 'action': 'error', 'message': error_data, "message_type": "specific"}, safe=False)
                
            for i in items_list:
                contentitems_id = str(uuid.uuid4())
                contenttype = i.get("contenttype","")
                content = i.get("content","")
                key_name = i.get("key_name","")
                unique_keyname = i["unique_keyname"]
                position = i.get("position",0)
                
                media_path = ""
                json_data = ""
                text = ""
                html = ""

                if contenttype == "media":
                    item_image_name = i.get("item_image_name","")
                    item_image = i.get("item_image","")
                    media_folder = 'media/item_images/' 
                    if item_image_name:
                        media_path = save_file(item_image, item_image_name, media_folder)
                elif contenttype == "json":                        
                    json_data = base64_operation(content,'encode')
                elif contenttype == "text":
                    text = base64_operation(content,'encode')
                elif contenttype == "html":
                    html = content

                insert_query = """insert into contentitems (ContentItemID,ContentBlockID,RefSectionId,Content,KeyName,UniqueKeyName,MediaID,ExtraData,Position,CreatedAt,UpdatedAt,HtmlContent,ContentType) values ('{ContentItemID}','{ContentBlockID}','{RefSectionId}','{Content}','{KeyName}','{UniqueKeyName}','{MediaID}','{ExtraData}','{Position}','{CreatedAt}','{UpdatedAt}','{HtmlContent}','{ContentType}');""".format(ContentItemID=contentitems_id,ContentBlockID=content_block_id,RefSectionId=section_id,Content=text,KeyName=key_name,UniqueKeyName=unique_keyname,MediaID=media_path,ExtraData=json_data,Position=position,CreatedAt=utc_time,UpdatedAt=utc_time,HtmlContent=html,ContentType=contenttype)
                execute = django_execute_query(insert_query)
                success_message = "Data created successfully"
                error_message = "Failed to create data"
            
            if execute!=0:
                message = {
                        'action':'success',
                        'message':success_message,
                        'data_uniq_id':contentitems_id
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
      

        
#This api is created earlier
@csrf_exempt
def contentitems_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `contentitems_get` API is responsible for fetching data from the master database
    based on the parameters provided in the HTTP request. The request may include filters, sorting
    criteria, or other parameters to customize the query.
    """
    try:
        
        if request.method == "GET": 
            utc_time = datetime.utcnow()

            request_header = request.headers
            auth_token = request_header["Authorization"]
            access_token = request.GET["access_token"]
            table_name = 'contentitems'

            protocol = request.META['SERVER_PROTOCOL']
            host = protocol[:protocol.index('/')].lower() + '://' + request.META['HTTP_HOST']

            state,msg,user = authorization(auth_token=auth_token,access_token=access_token)
            if state == False:
                return JsonResponse(msg, safe=False)
            
            else:            
                search_input = request.GET.get('search_input',None)
                content_block_id = request.GET.get('content_block_id',None)
                media_id = request.GET.get('media_id',None)
                position = request.GET.get('position',None)
                data_uniq_id = request.GET.get('data_uniq_id', None)
                unique_keyname = request.GET.get('unique_keyname', None)

                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_join += " AND ({table_name}.Content REGEXP '{inp}' OR {table_name}.KeyName REGEXP '{inp}' OR {table_name}.UniqueKeyName REGEXP '{inp}' )".format(inp=search_input,table_name=table_name)

                if data_uniq_id:                            
                    data_uniq_id = base64_operation(data_uniq_id,'decode')  
                    search_join += "AND {table_name}.ContentItemID = '{data_uniq_id}' ".format(data_uniq_id=data_uniq_id,table_name=table_name)

                if content_block_id:
                    content_block_id = base64_operation(content_block_id, 'decode').strip()
                    search_join += " AND {table_name}.ContentBlockID = '{ContentBlockID}' ".format(ContentBlockID=content_block_id,table_name=table_name)

                if media_id:
                    media_id = base64_operation(media_id, 'decode').strip()
                    search_join += " AND {table_name}.MediaID = '{MediaID}' ".format(MediaID=media_id,table_name=table_name)

                if position:
                    position = position
                    search_join += " AND {table_name}.Position = {Position} ".format(Position=position,table_name=table_name)

                if unique_keyname:
                    unique_keyname = unique_keyname
                    search_join += " AND {table_name}.UniqueKeyName = '{UniqueKeyName}' ".format(UniqueKeyName=unique_keyname,table_name=table_name)

                #Query to make the count of data
                count_query = """ SELECT count(*) as count
                FROM {table_name}
                WHERE 1=1 {search_join};""".format(search_join=search_join,table_name=table_name)
                get_count = search_all(count_query)

                #Query to fetch all the data 
                fetch_data_query = """ SELECT *, DATE_FORMAT(contentitems.CreatedAt, '%b %d, %Y | %l:%i %p') as created_f_date FROM contentitems
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
                    #To get encoded contentitems_id,serial number,formatted,readable created and modified_date 
                    data_format(data=i,page_number=page_number,index=index)

                    search_media = """select * from media where MediaID = '{MediaID}'""".format(MediaID=i["MediaID"])
                    get_media = search_all(search_media)

                    search_block = """select * from contentblocks where ContentBlockID = '{ContentBlockID}'""".format(ContentBlockID=i["ContentBlockID"])
                    get_block = search_all(search_block)

                    if len(get_media)!=0:
                        for k in get_media:
                            k['MediaID'] = base64_operation(k['MediaID'],'encode')
                            if k["FilePath"]:
                                k["FilePath"] =  host + "/" + k['FilePath']

                            data_format(data=k,page_number=page_number,index=index)

                    if len(get_block)!=0:
                        for j in get_block:
                            data_format(data=j,page_number=page_number,index=index)

                            search_sections = """select * from sections where SectionID = '{SectionID}'""".format(SectionID=j["SectionID"])
                            get_sections = search_all(search_sections)

                            j["section_details"] = get_sections
                            
                            search_block_media = """select * from media where MediaID = '{MediaID}'""".format(MediaID=j["MediaID"])
                            get_block_media = search_all(search_block_media)

                            j["media_details"] = get_block_media

                            search_contenttype = """select * from contenttypes where ContentTypeID = '{ContentTypeID}'""".format(ContentTypeID=j["ContentTypeID"])
                            get_contenttype = search_all(search_contenttype) 

                            j["content_type_details"] = get_contenttype

                            if len(get_sections)!=0:
                                for n in get_sections:
                                    search_pages = """select * from pages where PageID = '{PageID}'""".format(PageID=n['PageID'])
                                    get_pages = search_all(search_pages)
                                    if len(get_pages)!=0:
                                        n['page_details'] = get_pages 
                                        for m in get_pages:
                                            m['PageID'] = base64_operation(m['PageID'],'encode')

                                    n['PageID'] = base64_operation(n['PageID'],'encode')
                                    n['SectionID'] = base64_operation(n['SectionID'],'encode')
            
                                    data_format(data=n,page_number=page_number,index=index)

                            if len(get_block_media)!=0:
                                for p in get_block_media:
                                    p['MediaID'] = base64_operation(p['MediaID'],'encode')
                                    if p["FilePath"]:
                                        p["FilePath"] =  host + "/" + p['FilePath']
                                    
                                    data_format(data=p,page_number=page_number,index=index)

                            if len(get_contenttype)!=0:
                                for l in get_contenttype:
                                    l['ContentTypeID'] = base64_operation(l['ContentTypeID'],'encode')
                                    
                                    data_format(data=l,page_number=page_number,index=index)

                            j['ContentBlockID'] = base64_operation(j['ContentBlockID'],'encode')
                            j['SectionID'] = base64_operation(j['SectionID'],'encode')
                            j['ContentTypeID'] = base64_operation(j['ContentTypeID'],'encode')
                            j['MediaID'] = base64_operation(j['MediaID'],'encode')

                    i['ContentItemID'] = base64_operation(i['ContentItemID'],'encode')
                    i['ContentBlockID'] = base64_operation(i['ContentBlockID'],'encode')
                    i['MediaID'] = base64_operation(i['MediaID'],'encode')
                    i['ExtraData'] = base64_operation(i['ExtraData'],'decode')
                    i["media_details"] = get_media
                    i["content_block_details"] = get_block
                                        
                message = {
                        'action':'success',
                        'data':get_all_data,  
                        'page_number': page_number,
                        'items_per_page': items_per_page,
                        'total_pages': total_pages,
                        'total_items': count ,
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
def contentitems_status(request):
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
                'contentitems_ids': {'req_msg': 'Content item is required','val_msg': '', 'type': ''}, 
                'active_status': {'req_msg': 'Active status is required','val_msg': '', 'type': ''}, 
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,"message_type":"specific"}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            contentitems_id_list = data['contentitems_ids']
            for contentitems_id in contentitems_id_list:
                contentitems_id_en = base64_operation(contentitems_id,'decode')  
                
                active_status = data["active_status"]                                                             
                query = """
                UPDATE contentitems 
                SET ActiveStatus = {active_status} WHERE ContentItemID = '{ContentItemID}';
                """.format(ContentItemID=contentitems_id_en, active_status=active_status)
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
def contentitems_delete(request):
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
                'contentitems_ids': {'req_msg': 'Content item is required','val_msg': '', 'type': ''},  
            }
            validation_errors = validate_data(data,errors)
            if validation_errors:
                return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,"message_type":"specific"}, safe=False)
            
            user_id = user[0]["ref_user_id"]

            contentitems_id_list = data['contentitems_ids']
            for contentitems_id in contentitems_id_list:
                contentitems_id_en = base64_operation(contentitems_id,'decode')  
                                                                           
                query = """delete from contentitems WHERE ContentItemID = '{ContentItemID}';""".format(ContentItemID=contentitems_id_en)                
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
    


@csrf_exempt
def web_contentitems_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `web_contentitems_get` API is responsible for fetching data from the master database
    based on the parameters provided in the HTTP request. The request may include filters, sorting
    criteria, or other parameters to customize the query.
    """
    try:
        
        if request.method == "GET": 
            utc_time = datetime.utcnow()

            request_header = request.headers
            auth_token = request_header["Authorization"]
            # access_token = request.GET["access_token"]
            table_name = 'contentitems'

            protocol = request.META['SERVER_PROTOCOL']
            host = protocol[:protocol.index('/')].lower() + '://' + request.META['HTTP_HOST']

            state,msg = check_authorization_key(auth_token=auth_token)
            if not state:
                return JsonResponse(msg, safe=False)
            
            else:            
                search_input = request.GET.get('search_input',None)
                content_block_id = request.GET.get('content_block_id',None)
                media_id = request.GET.get('media_id',None)
                position = request.GET.get('position',None)
                data_uniq_id = request.GET.get('data_uniq_id', None)
                unique_keyname = request.GET.get('unique_keyname', None)

                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_join += " AND ({table_name}.Content REGEXP '{inp}' OR {table_name}.KeyName REGEXP '{inp}' OR {table_name}.UniqueKeyName REGEXP '{inp}' )".format(inp=search_input,table_name=table_name)

                if data_uniq_id:                            
                    data_uniq_id = base64_operation(data_uniq_id,'decode')  
                    search_join += "AND {table_name}.ContentItemID = '{data_uniq_id}' ".format(data_uniq_id=data_uniq_id,table_name=table_name)

                if content_block_id:
                    content_block_id = base64_operation(content_block_id, 'decode').strip()
                    search_join += " AND {table_name}.ContentBlockID = '{ContentBlockID}' ".format(ContentBlockID=content_block_id,table_name=table_name)

                if media_id:
                    media_id = base64_operation(media_id, 'decode').strip()
                    search_join += " AND {table_name}.MediaID = '{MediaID}' ".format(MediaID=media_id,table_name=table_name)

                if position:
                    position = position
                    search_join += " AND {table_name}.Position = {Position} ".format(Position=position,table_name=table_name)

                if unique_keyname:
                    unique_keyname = unique_keyname
                    search_join += " AND {table_name}.UniqueKeyName = '{UniqueKeyName}' ".format(UniqueKeyName=unique_keyname,table_name=table_name)

                #Query to make the count of data
                count_query = """ SELECT count(*) as count
                FROM {table_name}
                WHERE 1=1 {search_join};""".format(search_join=search_join,table_name=table_name)
                get_count = search_all(count_query)

                #Query to fetch all the data 
                fetch_data_query = """ SELECT *, DATE_FORMAT(contentitems.CreatedAt, '%b %d, %Y | %l:%i %p') as created_f_date FROM contentitems
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
                    #To get encoded contentitems_id,serial number,formatted,readable created and modified_date 
                    web_data_format(data=i,page_number=page_number,index=index)

                    search_media = """select * from media where MediaID = '{MediaID}'""".format(MediaID=i["MediaID"])
                    get_media = search_all(search_media)

                    search_block = """select * from contentblocks where ContentBlockID = '{ContentBlockID}' order by Position asc""".format(ContentBlockID=i["ContentBlockID"])
                    get_block = search_all(search_block)

                    if len(get_media)!=0:
                        for k in get_media:
                            k['MediaID'] = base64_operation(k['MediaID'],'encode')
                            if k["FilePath"]:
                                k["FilePath"] =  host + "/" + k['FilePath']

                            web_data_format(data=k,page_number=page_number,index=index)

                    if len(get_block)!=0:
                        for j in get_block:
                            web_data_format(data=j,page_number=page_number,index=index)

                            search_sections = """select * from sections where SectionID = '{SectionID}' order by Position asc""".format(SectionID=j["SectionID"])
                            get_sections = search_all(search_sections)

                            j["section_details"] = get_sections
                            
                            search_block_media = """select * from media where MediaID = '{MediaID}'""".format(MediaID=j["MediaID"])
                            get_block_media = search_all(search_block_media)

                            j["media_details"] = get_block_media

                            search_contenttype = """select * from contenttypes where ContentTypeID = '{ContentTypeID}'""".format(ContentTypeID=j["ContentTypeID"])
                            get_contenttype = search_all(search_contenttype) 

                            j["content_type_details"] = get_contenttype

                            if len(get_sections)!=0:
                                for n in get_sections:
                                    search_pages = """select * from pages where PageID = '{PageID}'""".format(PageID=n['PageID'])
                                    get_pages = search_all(search_pages)
                                    if len(get_pages)!=0:
                                        n['page_details'] = get_pages 
                                        for m in get_pages:
                                            m['PageID'] = base64_operation(m['PageID'],'encode')

                                    n['PageID'] = base64_operation(n['PageID'],'encode')
                                    n['SectionID'] = base64_operation(n['SectionID'],'encode')
            
                                    web_data_format(data=n,page_number=page_number,index=index)

                            if len(get_block_media)!=0:
                                for p in get_block_media:
                                    p['MediaID'] = base64_operation(p['MediaID'],'encode')
                                    if p["FilePath"]:
                                        p["FilePath"] =  host + "/" + p['FilePath']
                                    
                                    web_data_format(data=p,page_number=page_number,index=index)

                            if len(get_contenttype)!=0:
                                for l in get_contenttype:
                                    l['ContentTypeID'] = base64_operation(l['ContentTypeID'],'encode')
                                    
                                    web_data_format(data=l,page_number=page_number,index=index)

                            j['ContentBlockID'] = base64_operation(j['ContentBlockID'],'encode')
                            j['SectionID'] = base64_operation(j['SectionID'],'encode')
                            j['ContentTypeID'] = base64_operation(j['ContentTypeID'],'encode')
                            j['MediaID'] = base64_operation(j['MediaID'],'encode')

                    i['ContentItemID'] = base64_operation(i['ContentItemID'],'encode')
                    i['ContentBlockID'] = base64_operation(i['ContentBlockID'],'encode')
                    i['MediaID'] = base64_operation(i['MediaID'],'encode')
                    i['ExtraData'] = base64_operation(i['ExtraData'],'decode')
                    i["media_details"] = get_media
                    i["content_block_details"] = get_block
                                        
                message = {
                        'action':'success',
                        'data':get_all_data,  
                        'page_number': page_number,
                        'items_per_page': items_per_page,
                        'total_pages': total_pages,
                        'total_items': count ,
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
    


    