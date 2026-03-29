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

@csrf_exempt
def web_pages_get(request):

    """
    Retrieves data from the master database.

    Args:
        request (HttpRequest): The HTTP request object containing parameters for data retrieval.

    Returns:
        JsonResponse: A JSON response indicating the result of the data retrieval.

    The `web_pages_get` API is responsible for fetching data from the master database
    based on the parameters provided in the HTTP request. The request may include filters, sorting
    criteria, or other parameters to customize the query.
    """
    # try:
        
    if request.method == "GET": 
        utc_time = datetime.utcnow()

        request_header = request.headers
        auth_token = request_header["Authorization"]
        # access_token = request.GET["access_token"]
        table_name = 'pages'

        protocol = request.META['SERVER_PROTOCOL']
        host = protocol[:protocol.index('/')].lower() + '://' + request.META['HTTP_HOST']

        #To verify the authorization
        state,msg,response = check_authorization_key(auth_token=auth_token)
        if not state:
            return JsonResponse(msg, safe=False)
        
        else:            
            search_input = request.GET.get('search_input',None)
            data_uniq_id = request.GET.get('data_uniq_id', None)
            unique_keyname = request.GET.get('unique_keyname', None)

            #To filter using limit,from_date,to_date,active_status,order_type,order_field
            limit_offset,search_join,items_per_page,page_number,order_by = data_filter(request,table_name)

            if search_input:
                search_join += " AND  ({table_name}.PageName REGEXP '{inp}' OR {table_name}.UniquePageName REGEXP '{inp}' OR {table_name}.Slug REGEXP '{inp}' )".format(inp=search_input,table_name=table_name)

            if data_uniq_id:                            
                data_uniq_id = base64_operation(data_uniq_id,'decode')  
                search_join += "AND {table_name}.PageID = '{data_uniq_id}' ".format(data_uniq_id=data_uniq_id,table_name=table_name)

            if unique_keyname:
                unique_keyname = unique_keyname
                search_join += " AND {table_name}.UniquePageName = '{UniqueKeyName}' ".format(UniqueKeyName=unique_keyname,table_name=table_name)
            
            #Query to make the count of data
            count_query = """ SELECT count(*) as count
            FROM {table_name}
            WHERE 1=1 {search_join};""".format(search_join=search_join,table_name=table_name)
            get_count = search_all(count_query)

            #Query to fetch all the data 
            fetch_data_query = """ SELECT *, DATE_FORMAT(pages.CreatedAt, '%b %d, %Y | %l:%i %p') as created_f_date FROM pages
            WHERE 1=1  {search_join} {order_by} {limit};""".format(search_join=search_join,order_by=order_by,limit=limit_offset) 
                                
            get_all_data = search_all(fetch_data_query)

            # return JsonResponse(get_all_data,safe=False)
            
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
                search_sections = """select * from sections where PageID = '{SectionID}' order by Position asc;""".format(SectionID=i["PageID"],order_by=order_by)
                get_sections = search_all(search_sections)
                if len(get_sections)!=0:
                    # return JsonResponse(i["SectionID"],safe=False)
                    
                    for j in get_sections:
                        search_blocks = """select * from contentblocks where SectionID = '{SectionID}' order by Position asc;""".format(SectionID=j["SectionID"],order_by=order_by)
                        get_blocks = search_all(search_blocks)
                        web_data_format(data=j,page_number=page_number,index=index)
                        print("section:",get_blocks)
                        if len(get_blocks)!=0:
                            
                            j['block_details'] = get_blocks 
                            for m in get_blocks:

                                if m['Description']:
                                    m['Description']  = base64_operation(m['Description'],'decode')

                                web_data_format(data=m,page_number=page_number,index=index)
                                search_items = """select * from contentitems where ContentBlockID = '{ContentBlockID}' order by Position asc;""".format(ContentBlockID=m["ContentBlockID"])
                                get_items = search_all(search_items)
                                if len(get_items)!=0:
                                    if m['BlockName']:
                                        m['BlockName']  = base64_operation(m['BlockName'],'decode')
                                    
                                # select_model_data = f"""SELECT model FROM model_master WHERE data_uniq_id='{m['BlockName']}';"""
                                # get_model_data = search_one(select_model_data)
                                # if len(get_model_data)!=0:

                                #     model_value = get_model_data['model']
                                # # print(model_value,"jhgygyg")
                                # # i['BlockName'] = select_model_data['model']
                                #     m['BlockNames'] = model_value

                                        select_model_data = f"""SELECT model FROM model_master WHERE data_uniq_id='{m['BlockName']}';"""
                                        get_model_data = search_all(select_model_data)
                                        
                                        # i['BlockName'] = select_model_data['model']         

                                        if len(get_model_data)!=0:
                                            model_value = get_model_data[0]['model']
                                            m['BlockNames'] = model_value
                                        else:
                                            m['BlockNames'] = ""
                                                
                                if len(get_items)!=0:
                                    m['items_details'] = get_items 
                                    for r in get_items:
                                        if r["ContentItemID"]:
                                            r["ContentItemID"] = base64_operation(r['ContentItemID'],'encode')
                                        if r["Content"]:
                                            r["Content"] = base64_operation(r['Content'],'decode')
                                        if r["ExtraData"]:
                                            r["ExtraData"] = base64_operation(r['ExtraData'],'decode')
                                        if r["MediaID"] :
                                            r["MediaID"] =  host + "/" + r['MediaID']
                                        # if r["Description"]:   
                                        
                                    if r["ContentBlockID"]:
                                        r["ContentBlockID"] = base64_operation(r['ContentBlockID'],'encode')

                                        #To get encoded page_id,serial number,formatted,readable created and modified_date 
                                        web_data_format(data=r,page_number=page_number,index=index)
                            
                            if m['ContentBlockID']:
                                m['ContentBlockID'] = base64_operation(m['ContentBlockID'],'encode')
                                if m["BlockImage"]:
                                    m["BlockImagePath"] = m['BlockImage']
                                    if m['BlockImage'].startswith('http'):
                                        m["BlockImage"] = m['BlockImage']
                                    else:
                                        m["BlockImage"] = host + "/" + m['BlockImage']
                                # if m['Description']:
                                #     m['Description'] = base64_operation(m['Description'],'decode') 
                                if m['DescriptionTwo']: 
                                    m['DescriptionTwo'] = base64_operation(m['DescriptionTwo'],'decode')
                    
                    if  j['PageID']:       
                        j['PageID'] = base64_operation(j['PageID'],'encode')

                    if  j['SectionID']:       
                        j['SectionID'] = base64_operation(j['SectionID'],'encode')
                    if j['Description']:
                        j['Description'] = base64_operation(j['Description'],'decode') 
                    # if j['DescriptionTwo']:
                    #     # if j['DescriptionTwo']: 
                    #     j['DescriptionTwo'] = base64_operation(j['DescriptionTwo'],'decode')
                    if j["SectionImage"]:
                        j["SectionImagePath"] = j['SectionImage']
                        j["SectionImage"] =  host + "/" + j['SectionImage']


            if  i['PageID']:
                i['PageID'] = base64_operation(i['PageID'],'encode')
                i["section_details"] = get_sections
                #To get encoded page_id,serial number,formatted,readable created and modified_date 
                web_data_format(data=i,page_number=page_number,index=index)
                                    
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
 
    # except Exception as Err:
    #     response_exception(Err)
    #     return JsonResponse(str(Err), safe=False)
 