import os
import json
import base64
import uuid
import time
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from github import Github, GithubException
import hashlib

# Load environment variables
load_dotenv()

# Import generators
try:
    from generators.sum_of_sales import SumOfSalesGenerator
    from generators.markdown_to_html import MarkdownToHtmlGenerator
    from generators.github_user_created import GithubUserCreatedGenerator
except ImportError as e:
    print(f"Import error: {e}")
    from generators.base_generator import BaseGenerator
    # Fallback generators...

app = Flask(__name__)

class DeploymentManager:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.secret = os.getenv('SECRET')
        self.g = Github(self.github_token) if self.github_token else None
        self.user = self.g.get_user() if self.g else None
        
    def verify_secret(self, request_secret):
        return request_secret == self.secret
    
    def get_repo(self, repo_url):
        """Get repository from URL"""
        try:
            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1]
            return self.user.get_repo(repo_name)
        except:
            return None
    
    def create_repo(self, task_id, brief):
        repo_name = f"task-{task_id}-{str(uuid.uuid4())[:8]}"
        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=f"Auto-generated project: {brief[:100]}",
                private=False,
                auto_init=False
            )
            return repo, repo_name
        except GithubException as e:
            print(f"Error creating repo: {e}")
            return None, None
    
    def commit_files(self, repo, files, commit_message="Initial commit"):
        try:
            # Start with LICENSE
            license_content = self.get_license_content()
            repo.create_file("LICENSE", f"{commit_message} - Add LICENSE", license_content)
            
            # Add other files
            for file_path, content in files.items():
                repo.create_file(file_path, commit_message, content)
            
            return repo.get_branch("main").commit.sha
        except GithubException as e:
            print(f"Error committing files: {e}")
            return None
    
    def update_repo(self, repo, files, commit_message="Update for round 2"):
        """Update existing repository with new files"""
        try:
            for file_path, content in files.items():
                try:
                    # Try to get file to see if it exists
                    file_contents = repo.get_contents(file_path)
                    # Update existing file
                    repo.update_file(file_path, commit_message, content, file_contents.sha)
                except:
                    # Create new file
                    repo.create_file(file_path, commit_message, content)
            
            return repo.get_branch("main").commit.sha
        except GithubException as e:
            print(f"Error updating repo: {e}")
            return None
    
    def get_license_content(self):
        return """MIT License

Copyright (c) 2024 Student

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

deployment_manager = DeploymentManager()

def get_generator(brief):
    brief_lower = brief.lower()
    if 'sales' in brief_lower and 'sum' in brief_lower:
        return SumOfSalesGenerator()
    elif 'markdown' in brief_lower and 'html' in brief_lower:
        return MarkdownToHtmlGenerator()
    elif 'github' in brief_lower and 'user' in brief_lower:
        return GithubUserCreatedGenerator()
    else:
        return SumOfSalesGenerator()

def process_attachments(attachments):
    processed = {}
    for attachment in attachments:
        name = attachment['name']
        data_url = attachment['url']
        if data_url.startswith('data:'):
            base64_data = data_url.split('base64,')[1]
            decoded_data = base64.b64decode(base64_data)
            processed[name] = decoded_data
        else:
            processed[name] = data_url
    return processed

def notify_evaluation_with_retry(evaluation_url, data, max_retries=5):
    """Notify evaluation URL with exponential backoff as required"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                evaluation_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            if response.status_code == 200:
                print(f"✅ Successfully notified evaluation URL (attempt {attempt + 1})")
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1, 2, 4, 8 seconds - exponential backoff
            print(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    print("Failed to notify evaluation URL after all retries")
    return False

def process_round1_deployment(request_data):
    """Process Round 1 deployment - Create new repository"""
    try:
        # Verify secret
        if not deployment_manager.verify_secret(request_data.get('secret')):
            return None, "Invalid secret"
        
        # Get generator
        generator = get_generator(request_data['brief'])
        
        # Process attachments
        attachments = process_attachments(request_data.get('attachments', []))
        
        # Generate files for round 1
        files = generator.generate_round1(
            request_data['brief'], 
            request_data.get('checks', []),
            attachments
        )
        
        # Create repo
        repo, repo_name = deployment_manager.create_repo(
            request_data['task'], 
            request_data['brief']
        )
        
        if not repo:
            return None, "Failed to create repository"
        
        # Commit files
        commit_sha = deployment_manager.commit_files(repo, files, "Initial commit - Round 1")
        
        if not commit_sha:
            return None, "Failed to commit files"
        
        # Build evaluation data EXACTLY as required
        evaluation_data = {
            # Copy from request as required
            "email": request_data['email'],
            "task": request_data['task'],
            "round": request_data['round'],
            "nonce": request_data['nonce'],
            # Repository details
            "repo_url": f"https://github.com/{deployment_manager.user.login}/{repo_name}",
            "commit_sha": commit_sha,
            "pages_url": f"https://{deployment_manager.user.login}.github.io/{repo_name}/"
        }
        
        return evaluation_data, "Round 1 deployment completed successfully"
        
    except Exception as e:
        return None, f"Deployment failed: {str(e)}"

def process_round2_deployment(request_data):
    """Process Round 2 deployment - Update existing repository"""
    try:
        # Verify secret
        if not deployment_manager.verify_secret(request_data.get('secret')):
            return None, "Invalid secret"
        
        # Get the original repo (from previous round)
        # In a real scenario, you'd track this, but for now we'll extract from brief
        # or use a different approach based on task ID
        
        # For simplicity, we'll create a new repo for round 2 as well
        # In production, you'd look up the existing repo from your database
        
        generator = get_generator(request_data['brief'])
        attachments = process_attachments(request_data.get('attachments', []))
        
        # Generate files for round 2
        files = generator.generate_round2(
            request_data['brief'], 
            request_data.get('checks', []),
            attachments,
            {}  # Existing files would be passed here
        )
        
        # Create new repo for round 2 (in real scenario, update existing)
        repo, repo_name = deployment_manager.create_repo(
            f"{request_data['task']}-round2", 
            request_data['brief']
        )
        
        if not repo:
            return None, "Failed to create repository for round 2"
        
        # Commit files
        commit_sha = deployment_manager.commit_files(repo, files, "Round 2 updates")
        
        if not commit_sha:
            return None, "Failed to commit files for round 2"
        
        # Build evaluation data for round 2
        evaluation_data = {
            "email": request_data['email'],
            "task": request_data['task'],
            "round": request_data['round'],  # This will be 2
            "nonce": request_data['nonce'],
            "repo_url": f"https://github.com/{deployment_manager.user.login}/{repo_name}",
            "commit_sha": commit_sha,
            "pages_url": f"https://{deployment_manager.user.login}.github.io/{repo_name}/"
        }
        
        return evaluation_data, "Round 2 deployment completed successfully"
        
    except Exception as e:
        return None, f"Round 2 deployment failed: {str(e)}"

def process_deployment_async(request_data):
    """Process deployment in background thread"""
    try:
        round_num = request_data.get('round', 1)
        
        if round_num == 1:
            evaluation_data, message = process_round1_deployment(request_data)
        elif round_num == 2:
            evaluation_data, message = process_round2_deployment(request_data)
        else:
            print(f"Unsupported round: {round_num}")
            return
        
        if evaluation_data:
            # Notify evaluation URL with retry mechanism
            success = notify_evaluation_with_retry(
                request_data['evaluation_url'], 
                evaluation_data
            )
            
            if success:
                print(f"✅ Round {round_num} completed: {message}")
                print(f"📊 Repo: {evaluation_data['repo_url']}")
            else:
                print(f"⚠️ Round {round_num} completed but notification failed: {message}")
        else:
            print(f"❌ Deployment failed: {message}")
            
    except Exception as e:
        print(f"💥 Error in deployment process: {e}")

@app.route('/api/deploy', methods=['POST'])
def deploy():
    """Main deployment endpoint - Handles both Round 1 and Round 2"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        # Validate required fields
        required_fields = ['email', 'secret', 'task', 'round', 'nonce', 'brief', 'evaluation_url']
        missing_fields = [field for field in required_fields if field not in request_data]
        
        if missing_fields:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {missing_fields}"
            }), 400
        
        # Verify secret immediately
        if not deployment_manager.verify_secret(request_data.get('secret')):
            return jsonify({
                "status": "error",
                "message": "Invalid secret"
            }), 401
        
        # Start async processing
        thread = threading.Thread(target=process_deployment_async, args=(request_data,))
        thread.daemon = True
        thread.start()
        
        # Return immediate response as required
        round_num = request_data.get('round', 1)
        return jsonify({
            "status": "accepted",
            "message": f"Round {round_num} deployment process started",
            "round": round_num,
            "task": request_data['task']
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy", 
        "service": "LLM Deployment API",
        "version": "4.0",
        "features": ["round1", "round2", "github_pages", "evaluation_notification"]
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))
    print(f"🚀 LLM Deployment API v4.0 - Round 1 & 2 Support")
    print(f"🔗 Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
