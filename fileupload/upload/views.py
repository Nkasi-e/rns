from datetime import datetime
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import FileUploadSerializer
from .services import security
import os


class FileUpload(APIView):
    serializer_class = FileUploadSerializer
    parser_classes = (MultiPartParser, FormParser) # to be able to collect file from the frontend when being sent as formdata

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        file_content = uploaded_file.read()

        # create the new key
        key = security.create_new_key()

        # encrypt the file uploaded
        encrypted_file = security.encrypt_file(file_content, key)


        # store in a file system
        save_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'encrypted_files')

        # Create directory if it does not exist
        if not os.path.exists(save_directory):
            os.mkdir(save_directory)

            # Generate a unique fielname based on the time it was uploaded
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            encrypted_file_name = f'{uploaded_file.name}_{timestamp}.encrypted'

            encrypted_file_path = os.path.join(save_directory, encrypted_file_name)
            
            with open(encrypted_file_path, 'ab') as encrypted_data:
                encrypted_data.write(encrypted_file)


        # store the encrypted file in S3 bucket
        try:

            security.upload_to_s3( uploaded_file.name, encrypted_file)

            return Response("File encrypted and uploaded to S3", status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=500)