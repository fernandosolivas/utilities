import boto3
from datetime import datetime, timezone
from tabulate import tabulate

def list_repositories_by_last_push():
    try:
        # Create ECR client
        ecr_client = boto3.client('ecr')
        
        # Get list of all repositories
        print("Fetching ECR repositories...")
        repositories = ecr_client.describe_repositories()['repositories']
        
        if not repositories:
            print("No ECR repositories found.")
            return

        # List to store repository details
        repo_details = []

        for repo in repositories:
            repo_name = repo['repositoryName']
            try:
                # Get all images for the repository
                images = ecr_client.describe_images(
                    repositoryName=repo_name
                )['imageDetails']
                
                # If repository has images
                if images:
                    # Sort images by pushDate
                    sorted_images = sorted(images, key=lambda x: x['imagePushedAt'])
                    last_push_date = sorted_images[-1]['imagePushedAt']
                    days_since_push = (datetime.now(timezone.utc) - last_push_date).days
                    image_count = len(images)
                else:
                    last_push_date = None
                    days_since_push = float('inf')  # To sort empty repos at the end
                    image_count = 0

                repo_details.append({
                    'Repository Name': repo_name,
                    'Image Count': image_count,
                    'Last Push Date': last_push_date.strftime('%Y-%m-%d %H:%M:%S') if last_push_date else 'Never',
                    'Days Since Last Push': days_since_push if days_since_push != float('inf') else 'N/A',
                    'Created Date': repo['createdAt'].strftime('%Y-%m-%d %H:%M:%S')
                })

            except Exception as e:
                print(f"Error processing repository {repo_name}: {str(e)}")

        # Sort repositories by days since last push (oldest first)
        repo_details.sort(key=lambda x: (
            x['Days Since Last Push'] if x['Days Since Last Push'] != 'N/A' else float('inf')
        ))

        # Print results in a table format
        headers = ['Repository Name', 'Image Count', 'Last Push Date', 'Days Since Last Push', 'Created Date']
        table_data = [[repo[h] for h in headers] for repo in repo_details]
        
        print("\nECR Repositories (ordered by oldest push date first):")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))

        # Print summary
        print(f"\nTotal repositories: {len(repo_details)}")
        empty_repos = sum(1 for repo in repo_details if repo['Image Count'] == 0)
        print(f"Empty repositories: {empty_repos}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Starting ECR repository analysis...")
    list_repositories_by_last_push()
    print("\nFinished!")