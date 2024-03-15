from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from upload.utils import serializers, services
from django.conf import settings
import os


class FileUpload(APIView):
    serializer = serializers.FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser) # to be able to collect file from the frontend when being sent as formdata

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            return Response("No file found", status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.data['file']
        file_content = uploaded_file.read()

        # create the new key
        key = services.security.create_new_key()

        # encrypt the file uploaded
        encrypted_file = services.security.encrypt_file(file_content, key)


        # store in a file system
        save_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'encrypted_files')

        # Create directory if it does not exist
        if not os.path.exists(save_directory):
            os.mkdir(save_directory)

            encrypted_file_path = os.path.join(save_directory, uploaded_file.name + '.encrypted')
            
            with open(encrypted_file_path, 'wb') as encrypted_data:
                encrypted_data.write(encrypted_file)


        # store the encrypted file in S3 bucket
        # services.Security.upload_to_s3( 'name.txt', encrypted_file,)

        return Response("File encrypted and uploaded to S3", status=status.HTTP_201_CREATED)