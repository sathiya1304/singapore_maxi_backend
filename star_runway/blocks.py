"""
====================================================================================
File                :   enquiry.py
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


#This api is created to create content block
@csrf_exempt
def blocks(request):
    """
    Inserts data into the master.

    Args:
        request (HttpRequest): The HTTP request object containing the data to be inserted.

    Returns:
        JsonResponse: A JSON response indicating the result of the data insertion.

    The `blocks` API is responsible for adding new records to the master database.
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
            table_name2 = "contentitems"
            
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
                    'block_name': {'req_msg': 'Model is required','val_msg': '', 'type': ''},
                    # 'unique_contentblock_name': {'req_msg': 'Unique page name is required','val_msg': 'A unique name should not have any spaces between the words', 'type': 'key_format'},
                    'title': {'req_msg': 'Model Type is required','val_msg': '', 'type': ''}, 
                    'description_two': {'req_msg': 'Passenger is required','val_msg': '', 'type': ''},
                    'description': {'req_msg': 'Status is required','val_msg': '', 'type': ''}, 
                    'position': {'req_msg': 'Position is required','val_msg': '', 'type': ''},      
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,'message_type':"specific"}, safe=False)
                
                #block details
                contentblock_id = str(uuid.uuid4())
                section_id = base64_operation(data["section_id"],'decode') 
                block_name = data["block_name"]
                # if block_name != "" and block_name != None:
                #     block_name = base64_operation(block_name,'decode')

                unique_contentblock_name = data["unique_contentblock_name"]
                position = data.get("position", 0)
                title = data["title"]
                subtitle = data.get("subtitle","")
                slug = data.get("slug","")
                image_name = data.get("image_name","")
                block_image = data.get("block_image","")
                media_folder = 'media/contentblock_images/' 
                if image_name:
                    image_path = save_file(block_image, image_name, media_folder)
                else:
                    image_path = ""
                description = base64_operation(data.get("description",""),'encode') 
                description_two = base64_operation(data.get("description_two",""),'encode')

                if unique_contentblock_name!= "":

                    is_exist, message = check_existing_value_2(unique_contentblock_name, "unique_contentblock_name", "UniqueContentBlockName",table_name)
                    
                    if is_exist:
                        return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False)

                search_position = """select * from contentblocks where Position = {position} and SectionID = '{section_id}'""".format(position=position,section_id=section_id)
                get_position = search_all(search_position)
                if len(get_position) !=0:
                    message = {
                        "position":"Position already exists"
                    }
                    return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False) 

                # errors_index = {
                # 'contenttype': {'req_msg': 'Content type is required','val_msg': '', 'type': ''},
                # 'content': {'req_msg': 'Content is required','val_msg': '', 'type': ''}, 
                # 'key_name': {'req_msg': 'Key name is required','val_msg': '', 'type': ''},
                # 'unique_keyname': {'req_msg': 'Unique key name is required','val_msg': '', 'type': ''}, 
                # 'position': {'req_msg': 'Position is required','val_msg': '', 'type': ''},                                        
                # }
                
                #item details
                items_list = data.get('items_list',"")
                error_data = []
                for index,i in enumerate(items_list):
                    unique_keyname = i.get("unique_keyname","")
                    if unique_keyname!="":
                        is_exist, message = check_existing_value_2(unique_keyname, "unique_keyname", "UniqueKeyName",table_name2)
                    
                        if is_exist:
                            error_data.append({'index': index,index: message}) 
                    
                if len(error_data) !=0:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': error_data, "message_type": "specific"}, safe=False)
                   
                for i in items_list:
                    contentitems_id = str(uuid.uuid4())
                    contenttype = i.get("contenttype","")
                    content = i.get("content","")
                    key_name = i.get("key_name","")
                    unique_keyname = i.get("unique_keyname","")
                    item_position = i.get("position",0)
                    price = i.get("price","")

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

                    # is_exist, message = check_existing_value(position, "position", "Position", table_name)
                
                    # if is_exist:
                    #     return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False) 

                    insert_query = """insert into contentitems (ContentItemID,ContentBlockID,RefSectionId,Content,KeyName,UniqueKeyName,MediaID,ExtraData,Position,CreatedAt,UpdatedAt,HtmlContent,ContentType,price) values ('{ContentItemID}','{ContentBlockID}','{RefSectionId}','{Content}','{KeyName}','{UniqueKeyName}','{MediaID}','{ExtraData}','{Position}','{CreatedAt}','{UpdatedAt}','{HtmlContent}','{ContentType}','{price}');""".format(ContentItemID=contentitems_id,ContentBlockID=contentblock_id,RefSectionId=section_id,Content=text,KeyName=key_name,UniqueKeyName=unique_keyname,MediaID=media_path,ExtraData=json_data,Position=item_position,CreatedAt=utc_time,UpdatedAt=utc_time,HtmlContent=html,ContentType=contenttype,price=price)
                    execution = django_execute_query(insert_query)

                query = """insert into contentblocks (ContentBlockID,BlockName,SectionID,Title,SubTitle,Description,DescriptionTwo,Slug,Position,UniqueContentBlockName,CreatedAt,UpdatedAt,BlockImage) values ('{ContentBlockID}','{BlockName}','{SectionID}','{Title}','{SubTitle}',{Description},{DescriptionTwo},'{Slug}',{Position},'{UniqueContentBlockName}','{CreatedAt}','{UpdatedAt}','{BlockImage}');""".format(ContentBlockID=contentblock_id,BlockName=block_name,SectionID=section_id,Title=title,SubTitle=subtitle,Description=json.dumps(description),DescriptionTwo=json.dumps(description_two),Slug=slug,Position=position,UniqueContentBlockName=unique_contentblock_name,CreatedAt=utc_time,UpdatedAt=utc_time,BlockImage=image_path)
                execute = django_execute_query(query)
                
                success_message = "Data created successfully"
                error_message = "Failed to create data"
            
            
            #To modify the data
            elif request.method == "PUT":
                #To throw an required error message
                errors = {
                    'contentblock_id': {'req_msg': 'Block ID is required','val_msg': '', 'type': ''},
                    'block_name': {'req_msg': 'Block name is required','val_msg': '', 'type': ''},
                    # 'unique_contentblock_name': {'req_msg': 'Unique block name is required','val_msg': '', 'type': ''},
                    'title': {'req_msg': 'Title is required','val_msg': '', 'type': ''}, 
                    # 'subtitle': {'req_msg': 'Sub title is required','val_msg': '', 'type': ''},
                    # 'slug': {'req_msg': 'Slug is required','val_msg': '', 'type': ''}, 
                    'position': {'req_msg': 'Position is required','val_msg': '', 'type': ''},      
                }
                validation_errors = validate_data(data,errors)
                if validation_errors:
                    return JsonResponse({'status': 400, 'action': 'error', 'message': validation_errors,'message_type':"specific"}, safe=False)
                
                contentblock_id = base64_operation(data["contentblock_id"],'decode')  
                # section_id = base64_operation(data["section_id"],'decode') 
                block_name = data["block_name"]
                
                # if block_name != "" and block_name != None:
                #     block_name = base64_operation(block_name,'decode')

                # unique_contentblock_name = data["unique_contentblock_name"]
                position = data.get("position", 0)
                title = data["title"]
                subtitle = data.get("subtitle","")
                slug = data.get("slug","")
                image_name = data.get("image_name","")
                block_image = data.get("block_image","")
                block_image_path = data.get("block_image_path","")
                media_folder = 'media/contentblock_images/' 
                
                image_path = ""
                if block_image_path != "":
                    image_path = block_image_path
                elif block_image !="" and block_image != None :
                    image_path = save_file(block_image, image_name, media_folder)                    
            
                description = base64_operation(data.get("description",""),'encode')
                description_two = base64_operation(data.get("description_two",""),'encode')

                # is_exist, message = check_existing_value(unique_contentblock_name, "unique_contentblock_name", "UniqueContentBlockName", table_name, "ContentBlockID", contentblock_id)
                
                # if is_exist:
                #     return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False)
                # 
                # is_exist, message = check_existing_value(position, "position", "Position", table_name, "ContentBlockID", contentblock_id)
                
                # if is_exist:
                #     return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False) 
                search_section = """select * from contentblocks where ContentBlockID = '{contentblock_id}'""".format(contentblock_id=contentblock_id)
                get_section = search_all(search_section)
                if len(get_section)!=0:
                    section_id = get_section[0]["SectionID"]

                search_position = """select * from contentblocks where Position = {position} and SectionID = '{section_id}' and ContentBlockID != '{content_block_id}'""".format(position=position,section_id=section_id,content_block_id=contentblock_id)
                get_position = search_all(search_position)
                # return JsonResponse(search_position,safe=False)
                if len(get_position) !=0:
                    message = {
                        "position":"Position already exists"
                    }
                    return JsonResponse({'status': 400, 'action': 'error', 'message': message,"message_type":"specific"}, safe=False)
                
                query = """UPDATE contentblocks SET Title = '{Title}', SubTitle = '{SubTitle}', Description = {Description}, DescriptionTwo = {DescriptionTwo}, Slug = '{Slug}', Position = {Position},UpdatedAt = '{UpdatedAt}',BlockName = '{block_name}', BlockImage = '{BlockImage}' WHERE ContentBlockID = '{ContentBlockID}';""".format(ContentBlockID=contentblock_id,Title=title,SubTitle=subtitle,Description=json.dumps(description),DescriptionTwo=json.dumps(description_two),Slug=slug,Position=position,UpdatedAt=utc_time,block_name=block_name,BlockImage=image_path)
                execute = django_execute_query(query)

                success_message = "Data updated successfully"
                error_message = "Failed to update data"            
           
            #To delete the data
            elif request.method == "DELETE":
                contentblock_id = base64_operation(data["contentblock_id"],'decode')    
                query = """DELETE FROM contentblocks where ContentBlockID = '{ContentBlockID}';""".format(ContentBlockID=contentblock_id)
                execute = django_execute_query(query)
                success_message = "Data deleted successfully"
                error_message = "Failed to delete data"
           
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
    
#This API can be used to edit item orelse contentitems api PUT
@csrf_exempt
def edit_block_item(request):
    """
    Inserts data into the master.

    Args:
        request (HttpRequest): The HTTP request object containing the data to be inserted.

    Returns:
        JsonResponse: A JSON response indicating the result of the data insertion.

    The `blocks` API is responsible for adding new records to the master database.
    It expects an HTTP request object containing the data to be inserted. The data should be in a
    specific format, such as JSON, and must include the necessary fields required by the master database.
    """
    try:
        
        if request.method == "PUT":
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
            
            media_path = ""
            json_data = ""
            text = ""
            html = ""

            search_query = """select * from contentitems where ContentItemID = '{contentitems_id}'""".format(contentitems_id=contentitems_id)
            get_query = search_all(search_query)

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

            query = """UPDATE contentitems SET Content = '{Content}',MediaID = '{MediaID}',ExtraData = '{ExtraData}',Position = '{Position}',CreatedAt = '{CreatedAt}',UpdatedAt = '{UpdatedAt}',HtmlContent = '{HtmlContent}' WHERE ContentItemID = '{ContentItemID}';""".format(ContentItemID=contentitems_id,Content=text,MediaID=media_path,ExtraData=json_data,Position=position,CreatedAt=utc_time,UpdatedAt=utc_time,HtmlContent=html)
            execute = django_execute_query(query)
            success_message = "Data updated successfully"
            error_message = "Failed to update data"
           
            if execute!=0:
                message = {
                        'action':'success',
                        'message':success_message,
                        'ContentBlockID':contentitems_id
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
def blocks_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `blocks_get` API is responsible for fetching data from the master database
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
                unique_keyname = request.GET.get('unique_keyname', None)

                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_join += " AND ({table_name}.UniqueContentBlockName REGEXP '{inp}' OR {table_name}.Title REGEXP '{inp}' OR {table_name}.SubTitle REGEXP '{inp}' OR {table_name}.Description REGEXP '{inp}' OR {table_name}.DescriptionTwo REGEXP '{inp}' OR {table_name}.Settings REGEXP '{inp}' )".format(inp=search_input,table_name=table_name)

                if data_uniq_id:                            
                    data_uniq_id = base64_operation(data_uniq_id,'decode')  
                    search_join += "AND {table_name}.ContentBlockID = '{data_uniq_id}' ".format(data_uniq_id=data_uniq_id,table_name=table_name)

                if section_id:
                    section_id = base64_operation(section_id, 'decode')
                    search_join += " AND {table_name}.SectionID = '{SectionID}' ".format(SectionID=section_id,table_name=table_name)

                if media_id:
                    media_id = base64_operation(media_id, 'decode')
                    search_join += " AND {table_name}.MediaID = '{MediaID}' ".format(MediaID=media_id,table_name=table_name)

                if position:
                    position = position
                    search_join += " AND {table_name}.Position = {Position} ".format(Position=position,table_name=table_name)
                
                if unique_keyname:
                    unique_keyname = unique_keyname
                    search_join += " AND {table_name}.UniqueContentBlockName = '{UniqueKeyName}' ".format(UniqueKeyName=unique_keyname,table_name=table_name)
                    # return JsonResponse(search_join,safe=False)

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
                    if i["BlockImage"]:
                        i["BlockImagePath"] = i['BlockImage']
                        i["BlockImage"] =  host + "/" + i['BlockImage']

                    search_items = """select * from contentitems where ContentBlockID = '{ContentBlockID}'""".format(ContentBlockID=i["ContentBlockID"])
                    get_items = search_all(search_items)

                    if len(get_items)!=0:
                        # return JsonResponse(get_items,safe=False)
                        for r in get_items:
                            if r["ContentItemID"]:
                                r["ContentItemID"] = base64_operation(r['ContentItemID'],'encode')
                            if r["Content"]:
                                r["Content"] = base64_operation(r['Content'],'decode')
                            if r["ExtraData"]:
                                r["ExtraData"] = base64_operation(r['ExtraData'],'decode')
                            if r["MediaID"] :
                                r["MediaID"] =  host + "/" + r['MediaID']
                        if r["ContentBlockID"]:
                            r["ContentBlockID"] = base64_operation(r['ContentBlockID'],'encode')
                            #To get encoded page_id,serial number,formatted,readable created and modified_date 
                            data_format(data=r,page_number=page_number,index=index)


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
                            data_format(data=j,page_number=page_number,index=index)

                            if len(get_pages)!=0:
                                j['page_details'] = get_pages 
                                for m in get_pages:
                                    m['PageID'] = base64_operation(m['PageID'],'encode')

                            if j['PageID']:
                                j['PageID'] = base64_operation(j['PageID'],'encode')
                            if j['SectionID']:
                                j['SectionID'] = base64_operation(j['SectionID'],'encode')
                            data_format(data=m,page_number=page_number,index=index)
                            
                    if len(get_media)!=0:
                        for k in get_media:
                            if k['MediaID']:
                                k['MediaID'] = base64_operation(k['MediaID'],'encode')
                            if k["FilePath"]:
                                k["FilePath"] =  host + "/" + k['FilePath']
                            
                            data_format(data=k,page_number=page_number,index=index)

                    if len(get_contenttype)!=0:
                        for l in get_contenttype:
                            if l['ContentTypeID']:
                                l['ContentTypeID'] = base64_operation(l['ContentTypeID'],'encode')
                            data_format(data=l,page_number=page_number,index=index)

                    data_format(data=i,page_number=page_number,index=index)      

                    # i['ContentBlockID'] = base64_operation(i['ContentBlockID'],'encode')
                    i['BlockName']  = base64_operation(i['BlockName'],'decode')
                    select_model_data = f"""SELECT model FROM model_master WHERE data_uniq_id='{i['BlockName']}';"""
                    get_model_data = search_all(select_model_data)
                    print(get_model_data,"get_model_data")
                    # i['BlockName'] = select_model_data['model']         

                    if len(get_model_data)!=0:
                        model_value = get_model_data[0]['model']
                        i['BlockNames'] = model_value
                    else:
                        i['BlockNames'] = ""

                    if i['SectionID']:
                        i['SectionID'] = base64_operation(i['SectionID'],'encode')
                    if i['ContentTypeID']:
                        i['ContentTypeID'] = base64_operation(i['ContentTypeID'],'encode')
                    if i['MediaID']:
                        i['MediaID'] = base64_operation(i['MediaID'],'encode')
                    if i['Description']:
                        i['Description'] = base64_operation(i['Description'],'decode')
                    if i['DescriptionTwo']:
                        i['DescriptionTwo'] = base64_operation(i['DescriptionTwo'],'decode')
                    if i['ContentBlockID']:
                        i['ContentBlockID'] = base64_operation(i['ContentBlockID'],'encode')
                    if i['BlockName']:
                        i['BlockName'] = base64_operation(i['BlockName'],'encode')
                    i["section_details"] = get_sections
                    i["media_details"] = get_media
                    i["content_type_details"] = get_contenttype
                    i['block_items'] = get_items
                                       
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
def blocks_status(request):
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
def blocks_delete(request):
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
    
#This is the latest api created to list the items
@csrf_exempt
def block_items_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `block_items_get` API is responsible for fetching data from the master database
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
                section_id = request.GET.get('section_id',None)
                media_id = request.GET.get('media_id',None)
                position = request.GET.get('position',None)
                data_uniq_id = request.GET.get('data_uniq_id', None)
                block_id = request.GET.get('block_id', None)


                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_join += " AND ({table_name}.UniqueContentBlockName REGEXP '{inp}' OR {table_name}.Title REGEXP '{inp}' OR {table_name}.SubTitle REGEXP '{inp}' OR {table_name}.Description REGEXP '{inp}' OR {table_name}.DescriptionTwo REGEXP '{inp}' OR {table_name}.Settings REGEXP '{inp}' )".format(inp=search_input,table_name=table_name)

                if data_uniq_id:                            
                    data_uniq_id = base64_operation(data_uniq_id,'decode')  
                    search_join += "AND {table_name}.ContentItemID = '{data_uniq_id}' ".format(data_uniq_id=data_uniq_id,table_name=table_name)

                if section_id:
                    section_id = base64_operation(section_id, 'decode').strip()
                    search_join += " AND {table_name}.RefSectionId = '{SectionID}' ".format(SectionID=section_id,table_name=table_name)

                if block_id:
                    block_id = base64_operation(block_id, 'decode').strip()
                    search_join += " AND {table_name}.ContentBlockID = '{ContentBlockID}' ".format(ContentBlockID=block_id,table_name=table_name)

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
                fetch_data_query = """ SELECT *, DATE_FORMAT(contentitems.CreatedAt, '%b %d, %Y | %l:%i %p') as created_f_date FROM contentitems WHERE 1=1  {search_join} {order_by} {limit};""".format(search_join=search_join,order_by=order_by,limit=limit_offset) 
                                    
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
                    data_format(data=i,page_number=page_number,index=index)
                    if i["MediaID"]:
                        i["MediaID"] =  host + "/" + i['MediaID']

                    i['ContentItemID'] = base64_operation(i['ContentItemID'],'encode')
                    i['ContentBlockID'] = base64_operation(i['ContentBlockID'],'encode')
                    i['RefSectionId'] = base64_operation(i['RefSectionId'],'encode')
                    i['Content'] = base64_operation(i['Content'],'decode')
                    i['ExtraData'] = base64_operation(i['ExtraData'],'decode')

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
def web_blocks_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `web_blocks_get` API is responsible for fetching data from the master database
    based on the parameters provided in the HTTP request. The request may include filters, sorting
    criteria, or other parameters to customize the query.
    """
    try:
        
        if request.method == "GET": 
            utc_time = datetime.utcnow()

            request_header = request.headers
            auth_token = request_header["Authorization"]
            # access_token = request.GET["access_token"]
            table_name = 'contentblocks'

            protocol = request.META['SERVER_PROTOCOL']
            host = protocol[:protocol.index('/')].lower() + '://' + request.META['HTTP_HOST']

            #To verify the authorization
            state,msg = check_authorization_key(auth_token=auth_token)
            if not state:
                return JsonResponse(msg, safe=False)
            
            else:   
                search_input = request.GET.get('search_input',None)
                section_id = request.GET.get('section_id',None)
                media_id = request.GET.get('media_id',None)
                position = request.GET.get('position',None)
                data_uniq_id = request.GET.get('data_uniq_id', None)
                unique_keyname = request.GET.get('unique_keyname', None)

                #To filter using limit,from_date,to_date,active_status,order_type,order_field
                limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

                if search_input:
                    search_join += " AND ({table_name}.UniqueContentBlockName REGEXP '{inp}' OR {table_name}.Title REGEXP '{inp}' OR {table_name}.SubTitle REGEXP '{inp}' OR {table_name}.Description REGEXP '{inp}' OR {table_name}.DescriptionTwo REGEXP '{inp}' OR {table_name}.Settings REGEXP '{inp}' )".format(inp=search_input,table_name=table_name)

                if data_uniq_id:                            
                    data_uniq_id = base64_operation(data_uniq_id,'decode')  
                    search_join += "AND {table_name}.ContentBlockID = '{data_uniq_id}' ".format(data_uniq_id=data_uniq_id,table_name=table_name)

                if section_id:
                    section_id = base64_operation(section_id, 'decode')
                    search_join += " AND {table_name}.SectionID = '{SectionID}' ".format(SectionID=section_id,table_name=table_name)

                if media_id:
                    media_id = base64_operation(media_id, 'decode')
                    search_join += " AND {table_name}.MediaID = '{MediaID}' ".format(MediaID=media_id,table_name=table_name)

                if position:
                    position = position
                    search_join += " AND {table_name}.Position = {Position} ".format(Position=position,table_name=table_name)
                
                if unique_keyname:
                    unique_keyname = unique_keyname
                    search_join += " AND {table_name}.UniqueContentBlockName = '{UniqueKeyName}' ".format(UniqueKeyName=unique_keyname,table_name=table_name)
                    # return JsonResponse(search_join,safe=False)

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
                    if i["BlockImage"]:
                        i["BlockImagePath"] = i['BlockImage']
                        i["BlockImage"] =  host + "/" + i['BlockImage']

                    search_items = """select * from contentitems where ContentBlockID = '{ContentBlockID}' order by Position asc """.format(ContentBlockID=i["ContentBlockID"])
                    get_items = search_all(search_items)

                    if len(get_items)!=0:
                        # return JsonResponse(get_items,safe=False)
                        for r in get_items:
                            r["ContentItemID"] = base64_operation(r['ContentItemID'],'encode')
                            if r["Content"]:
                                r["Content"] = base64_operation(r['Content'],'decode')
                            if r["ExtraData"]:
                                r["ExtraData"] = base64_operation(r['ExtraData'],'decode')
                            if r["MediaID"] :
                                r["MediaID"] =  host + "/" + r['MediaID']
                            r["ContentBlockID"] = base64_operation(r['ContentBlockID'],'encode')
                            #To get encoded page_id,serial number,formatted,readable created and modified_date 
                            web_data_format(data=r,page_number=page_number,index=index)

                    search_sections = """select * from sections where SectionID = '{SectionID}' order by Position asc""".format(SectionID=i["SectionID"])
                    get_sections = search_all(search_sections)

                    
                    
                    # search_media = """select * from media where MediaID = '{MediaID}'""".format(MediaID=i["MediaID"])
                    # get_media = search_all(search_media)

                    # search_contenttype = """select * from contenttypes where ContentTypeID = '{ContentTypeID}'""".format(ContentTypeID=i["ContentTypeID"])
                    # get_contenttype = search_all(search_contenttype)
                    

                    if len(get_sections)!=0:
                        
                        for j in get_sections:
                            search_pages = """select * from pages where PageID = '{PageID}'""".format(PageID=j['PageID'])
                            get_pages = search_all(search_pages)
                            web_data_format(data=j,page_number=page_number,index=index)

                            if len(get_pages)!=0:
                                j['page_details'] = get_pages 
                                for m in get_pages:
                                    m['PageID'] = base64_operation(m['PageID'],'encode')
                            j['PageID'] = base64_operation(j['PageID'],'encode')
                            j['SectionID'] = base64_operation(j['SectionID'],'encode')
                            web_data_format(data=m,page_number=page_number,index=index)

                            
                    # if len(get_media)!=0:

                    #     for k in get_media:
                    #         k['MediaID'] = base64_operation(k['MediaID'],'encode')
                    #         if k["FilePath"]:
                    #             k["FilePath"] =  host + "/" + k['FilePath']
                            
                    #         data_format(data=k,page_number=page_number,index=index,user_time_zone=user[0]['user_time_zone'])

                            


                    # if len(get_contenttype)!=0:
                    #     for l in get_contenttype:
                    #         l['ContentTypeID'] = base64_operation(l['ContentTypeID'],'encode')
                    #         data_format(data=l,page_number=page_number,index=index,user_time_zone=user[0]['user_time_zone'])
                    # return JsonResponse("yessss",safe=False)


                    web_data_format(data=i,page_number=page_number,index=index)  

                    i['ContentBlockID'] = base64_operation(i['ContentBlockID'],'encode')
                    i['SectionID'] = base64_operation(i['SectionID'],'encode')
                    i['ContentTypeID'] = base64_operation(i['ContentTypeID'],'encode')
                    i['MediaID'] = base64_operation(i['MediaID'],'encode')
                    i['Description'] = base64_operation(i['Description'],'decode')
                    i['DescriptionTwo'] = base64_operation(i['DescriptionTwo'],'decode')
                    i["section_details"] = get_sections
                    # i["media_details"] = get_media
                    # i["content_type_details"] = get_contenttype
                    i['block_items'] = get_items
                                       
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
    
