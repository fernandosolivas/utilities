import boto3
from datetime import datetime
from typing import List, Dict

def cleanup_ecr_images():
    try:
        # Create ECR client
        ecr_client = boto3.client('ecr')
        
        # Get list of all repositories
        print("Fetching ECR repositories...")
        repositories = ecr_client.describe_repositories()['repositories']
        
        if not repositories:
            print("No ECR repositories found.")
            return
        
        # Process each repository
        for repo in repositories:
            repo_name = repo['repositoryName']
            try:
                print(f"\nProcessing repository: {repo_name}")
                
                # Get all images for the repository
                images = ecr_client.describe_images(repositoryName=repo_name)['imageDetails']
                
                if len(images) <= 3:
                    print(f"Repository has {len(images)} images. No cleanup needed.")
                    continue
                
                # Sort images by push date (newest first)
                sorted_images = sorted(
                    images,
                    key=lambda x: x['imagePushedAt'],
                    reverse=True
                )
                
                # Keep the 3 most recent images
                images_to_delete = sorted_images[3:]
                
                if not images_to_delete:
                    continue
                
                # Prepare image identifiers for deletion
                image_ids = []
                for image in images_to_delete:
                    identifier = {'imageDigest': image['imageDigest']}
                    if 'imageTag' in image:
                        print(f"  Will delete: {image['imageTag']} "
                              f"(pushed on {image['imagePushedAt'].strftime('%Y-%m-%d %H:%M:%S')})")
                    else:
                        print(f"  Will delete: {image['imageDigest'][:12]} "
                              f"(pushed on {image['imagePushedAt'].strftime('%Y-%m-%d %H:%M:%S')})")
                    image_ids.append(identifier)
                
                # Delete the images
                if image_ids:
                    response = ecr_client.batch_delete_image(
                        repositoryName=repo_name,
                        imageIds=image_ids
                    )
                    
                    # Process response
                    if 'imageIds' in response:
                        print(f"✅ Successfully deleted {len(response['imageIds'])} images")
                    if 'failures' in response and response['failures']:
                        print("❌ Failed to delete some images:")
                        for failure in response['failures']:
                            print(f"  - {failure['imageId']}: {failure['failureReason']}")
                
            except Exception as e:
                print(f"❌ Error processing repository {repo_name}: {str(e)}")
                continue

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Starting ECR image cleanup...")
    cleanup_ecr_images()
    print("\nFinished!") 