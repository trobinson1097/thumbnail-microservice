import json
import boto3
import os
from PIL import Image
from io import BytesIO

s3_client = boto3.client('s3')

# Thumbnail sizes to generate
THUMBNAIL_SIZES = {
    'small': (150, 150),
    'medium': (300, 300),
    'large': (600, 600)
}

def lambda_handler(event, context):
    """
    Triggered when an image is uploaded to S3.
    Creates thumbnails in multiple sizes.
    """
    
    # Get bucket and key from S3 event
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        print(f"Processing image: {key} from bucket: {bucket}")
        
        # Only process files in the 'original' folder
        if '/original/' not in key:
            print(f"Skipping {key} - not in original folder")
            return {
                'statusCode': 200,
                'body': json.dumps('Not an original image, skipping')
            }
        
        # Download the image from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        
        # Open image with Pillow
        image = Image.open(BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Generate thumbnails for each size
        thumbnails_created = []
        
        for size_name, dimensions in THUMBNAIL_SIZES.items():
            # Create thumbnail
            thumbnail = image.copy()
            thumbnail.thumbnail(dimensions, Image.Resampling.LANCZOS)
            
            # Save to buffer
            buffer = BytesIO()
            thumbnail.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            
            # Generate new key for thumbnail
            # Example: rocks/5/original/abc.jpg -> rocks/5/thumbnails/medium/abc.jpg
            thumbnail_key = key.replace('/original/', f'/thumbnails/{size_name}/')
            
            # Upload to S3
            s3_client.put_object(
                Bucket=bucket,
                Key=thumbnail_key,
                Body=buffer,
                ContentType='image/jpeg'
            )
            
            thumbnails_created.append(thumbnail_key)
            print(f"Created thumbnail: {thumbnail_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Thumbnails created successfully',
                'original': key,
                'thumbnails': thumbnails_created
            })
        }
        
    except Exception as e:
        print(f'Error processing image: {str(e)}')
        raise e



