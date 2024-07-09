from google.cloud import storage
import os
 
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'jingye-zhang-2ca0d3f5ff72.json'
# Instantiates a client
storage_client = storage.Client()
bucket_name = "jingye_zhang"
bucket = storage_client.get_bucket(bucket_name)
picBlob = bucket.blob(os.sys.argv[1])
print('/home/shanepriyanka/' + os.sys.argv[1])
picBlob.upload_from_filename('/home/shanepriyanka/' + os.sys.argv[1])
print("Bucket {bucket.name} created.")
