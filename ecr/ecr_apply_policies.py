import boto3
import json

def apply_lifecycle_policies():
    try:
        # Create ECR client
        # Assumes you have AWS credentials configured locally via AWS CLI
        ecr_client = boto3.client('ecr')
        
        # Get list of all repositories
        print("Fetching ECR repositories...")
        repositories = ecr_client.describe_repositories()['repositories']
        
        if not repositories:
            print("No ECR repositories found.")
            return
        
        # Lifecycle policy to keep only 3 most recent images
        lifecycle_policy = {
            "rules": [
                {
                    "rulePriority": 1,
                    "description": "Keep only 3 most recent images",
                    "selection": {
                        "tagStatus": "any",
                        "countType": "imageCountMoreThan",
                        "countNumber": 3
                    },
                    "action": {
                        "type": "expire"
                    }
                }
            ]
        }
        
        # Apply lifecycle policy to each repository
        for repo in repositories:
            repo_name = repo['repositoryName']
            try:
                ecr_client.put_lifecycle_policy(
                    registryId=repo['registryId'],
                    repositoryName=repo_name,
                    lifecyclePolicyText=json.dumps(lifecycle_policy)
                )
                print(f"✅ Successfully applied lifecycle policy to: {repo_name}")
            except Exception as e:
                print(f"❌ Error applying lifecycle policy to {repo_name}: {str(e)}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Starting ECR lifecycle policy application...")
    apply_lifecycle_policies()
    print("Finished!")