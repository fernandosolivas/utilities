import boto3
from datetime import datetime, timezone
from typing import List, Optional
import argparse

def change_storage_to_glacier(
    bucket_name: str,
    prefix: Optional[str] = None,
    older_than_days: Optional[int] = None
) -> None:
    """
    Changes objects in an S3 bucket to Glacier storage class.
    
    Args:
        bucket_name: Name of the S3 bucket
        prefix: Optional prefix to filter objects (folder path)
        older_than_days: Optional, only change objects older than specified days
    """
    try:
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Prepare listing parameters
        list_params = {
            'Bucket': bucket_name
        }
        if prefix:
            list_params['Prefix'] = prefix
            
        # Get current time for age comparison
        current_time = datetime.now(timezone.utc)
        
        # Counter for modified objects
        modified_count = 0
        skipped_count = 0
        error_count = 0
        
        # List all objects in the bucket (handles pagination automatically)
        paginator = s3_client.get_paginator('list_objects_v2')
        
        print(f"Scanning bucket: {bucket_name}")
        print(f"Prefix filter: {prefix if prefix else 'None'}")
        print(f"Age filter: {older_than_days if older_than_days else 'None'} days")
        
        for page in paginator.paginate(**list_params):
            if 'Contents' not in page:
                continue
                
            for obj in page['Contents']:
                try:
                    key = obj['Key']
                    current_storage_class = obj.get('StorageClass', 'STANDARD')
                    
                    # Skip if already in Glacier
                    if current_storage_class == 'GLACIER':
                        print(f"⏭️  Skipping {key} - Already in Glacier")
                        skipped_count += 1
                        continue
                    
                    # Check age if specified
                    if older_than_days:
                        age_days = (current_time - obj['LastModified']).days
                        if age_days < older_than_days:
                            print(f"⏭️  Skipping {key} - Too recent ({age_days} days old)")
                            skipped_count += 1
                            continue
                    
                    # Change storage class to Glacier
                    s3_client.copy_object(
                        Bucket=bucket_name,
                        CopySource={'Bucket': bucket_name, 'Key': key},
                        Key=key,
                        StorageClass='GLACIER',
                        MetadataDirective='COPY'
                    )
                    
                    print(f"✅ Changed to Glacier: {key}")
                    modified_count += 1
                    
                except Exception as e:
                    print(f"❌ Error processing {key}: {str(e)}")
                    error_count += 1
        
        # Print summary
        print("\nSummary:")
        print(f"Modified: {modified_count} objects")
        print(f"Skipped: {skipped_count} objects")
        print(f"Errors: {error_count} objects")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Change S3 objects to Glacier storage class')
    parser.add_argument('bucket', help='Name of the S3 bucket')
    parser.add_argument('--prefix', help='Optional prefix filter (folder path)')
    parser.add_argument('--older-than', type=int, help='Only change objects older than specified days')
    
    args = parser.parse_args()
    
    print("Starting S3 to Glacier migration...")
    change_storage_to_glacier(
        bucket_name=args.bucket,
        prefix=args.prefix,
        older_than_days=args.older_than
    )
    print("\nFinished!")

if __name__ == "__main__":
    main() 