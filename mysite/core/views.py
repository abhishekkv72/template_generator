import datetime
from http.client import HTTPResponse
import zipfile
from django.http import JsonResponse
import pandas as pd
import json
import urllib.request
from django.conf import settings
import shutil
import os
from django.shortcuts import redirect
from azure.storage.blob import BlobServiceClient
from django.shortcuts import render
from django.views.generic import TemplateView
from requests import request
import webbrowser
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

@csrf_exempt
def upload(request):

    if request.method == 'POST':
        uploaded_files = request.FILES['document']
        df = pd.read_csv(uploaded_files, index_col=False)
        df = df.reset_index()
        ls_list = []
        for index, row in df.iterrows():
            html_content = f""" <h1> Hello {row['Name']}</h1>
                                <p>This is your Voucher: {row['Voucher']}</p>
                           """
            file_name = "./mysite/Data/" + \
                f"{row['Name']}{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.html"
            file = open(file_name, 'w')
            file.write(html_content)
            file.close()
            ls_list.append(file_name)
        zip_file = zipfiles(ls_list)

        storage_container_name = settings.STORAGE_CONTAINER_NAME
        connection_string = settings.CONNECTION_STRING
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string)
        blob_client = blob_service_client.get_blob_client(
            container=storage_container_name, blob=zip_file[1])
        with open(zip_file[0], 'rb')as data:
            blob_client.upload_blob(data)
        link = (blob_client.url)
        shutil.rmtree('./mysite/Data/')
        os.mkdir('./mysite/Data/')

        return render(request, 'core/upload.html', {'link': link})

    return render(request, "core/upload.html")


def zipfiles(ls_files):
    f_name = f"myzip{datetime.datetime.now().strftime('%Y%m%d%H%M%f')}.zip"
    zf = zipfile.ZipFile("./mysite/Data/"+f_name, "x")
    for file in ls_files:
        zf.write(file)
    zf.close()
    return ("./mysite/Data/"+f_name, f_name)
