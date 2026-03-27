"""
URL configuration for star_runway project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from star_runway.login import *
from star_runway.create_user import *
from star_runway.logout import *
from star_runway.change_password import *
from star_runway.forgot_password import *
from star_runway.model_master import *
from star_runway.enquiry import *
from star_runway.pages import *
from star_runway.sections import *
from star_runway.contentblocks import *
from star_runway.blocks import *
from star_runway.contentitems import *
from star_runway.webpages import *


urlpatterns = [
    path('admin/', admin.site.urls),

# VALIDATION START \\\\\\\\\\
    path('decode_encode',decode_encode,name='decode_encode'),
    path('valid_token',valid_token,name ='valid_token'),
# VALIDATION START \\\\\\\\\\

# USER MANAGEMENT START \\\\\\\\\\
    path('send_otp',send_otp,name='send_otp'),
    path('verify_otp',verify_otp,name='verify_otp'),
    path('update_password',update_password,name='update_password'),
    path('password_change',password_change,name='password_change'),
    path('user_login',user_login,name='user_login'),
    path('user_delete',user_delete,name='user_delete'),
    path('user_logout',user_logout,name='user_logout'),   
    path('user_get',user_get,name='user_get'), 
    path('create_user',create_user,name='create_user'),
    path('user_status',user_status,name='user_status'),
    path('user_delete',user_delete,name='user_delete'),
# USER MANAGEMENT END \\\\\\\\\\

# MODEL MASTER START \\\\\\\\\\    
    path('model_master',model_master,name='model_master'),
    path('model_master_get',model_master_get,name='model_master_get'),
    path('model_master_status',model_master_status,name='model_master_status'),
    path('model_master_delete',model_master_delete,name='model_master_delete'),
    path('model_master_web_get',model_master_web_get,name='model_master_web_get'),
# MODEL MASTER END \\\\\\\\\\

    path('enquiry',enquiry,name='enquiry'),
    path('enquiry_get',enquiry_get,name='enquiry_get'),
    path('change_enquiry_status',change_enquiry_status,name='change_enquiry_status'),

# PAGES START \\\\\\\\\\    
    path('pages',pages,name='pages'),
    path('pages_get',pages_get,name='pages_get'),
    path('pages_status',pages_status,name='pages_status'),
    path('pages_delete',pages_delete,name='pages_delete'),
# PAGES END \\\\\\\\\\

# SECTIONS START \\\\\\\\\\    
    path('sections',sections,name='sections'),
    path('sections_get',sections_get,name='sections_get'),
    path('sections_status',sections_status,name='sections_status'),
    path('sections_delete',sections_delete,name='sections_delete'),
# SECTIONS END \\\\\\\\\\ 


# CONTENTBLOCKS START \\\\\\\\\\    
    path('contentblocks',contentblocks,name='contentblocks'),
    path('contentblocks_get',contentblocks_get,name='contentblocks_get'),
    path('contentblocks_status',contentblocks_status,name='contentblocks_status'),
    path('contentblocks_delete',contentblocks_delete,name='contentblocks_delete'),
# CONTENTBLOCKS END \\\\\\\\\\ 


# BLOCK START \\\\\\\\\\    
    path('blocks',blocks,name='blocks'),
    path('blocks_get',blocks_get,name='blocks_get'),
    path('blocks_status',blocks_status,name='blocks_status'),
    path('blocks_delete',blocks_delete,name='blocks_delete'),
    path('edit_block_item',edit_block_item,name='edit_block_item'),
    path('block_items_get',block_items_get,name='block_items_get'),
    path('web_blocks_get',web_blocks_get,name='web_blocks_get'),
# BLOCK END \\\\\\\\\\  

# CONTENT ITEM START \\\\\\\\\\    
    path('contentitems',contentitems,name='contentitems'),
    path('contentitems_get',contentitems_get,name='contentitems_get'),
    path('contentitems_status',contentitems_status,name='contentitems_status'),
    path('contentitems_delete',contentitems_delete,name='contentitems_delete'),
# CONTENT ITEM END \\\\\\\\\\ 

# Web Page Start \\\\\\\\\\
    path('web_pages_get',web_pages_get,name='web_pages_get'),
# Web Page End \\\\\\\\\\   

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
