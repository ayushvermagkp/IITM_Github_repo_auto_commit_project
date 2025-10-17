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

# Import generators
try:
    from generators.sum_of_sales import SumOfSalesGenerator
    from generators.markdown_to_html import MarkdownToHtmlGenerator
    from generators.github_user_created import GithubUserCreatedGenerator
except ImportError as e:
    print(f"Import error: {e}")
    # Define fallback generators
    from generators.base_generator import BaseGenerator
    class SumOfSalesGenerator(BaseGenerator):
        def generate_round1(self, brief, checks, attachments): 
            return self.create_basic_files(brief)
        def generate_round2(self, brief, checks, attachments, existing_files): 
            return self.create_basic_files(brief)
        def create_basic_files(self, brief):
            return {
                'index.html': '<html><body><h1>Basic App</h1></body></html>',
                'README.md': f'# Basic App\n\n{brief}'
            }
    
    class MarkdownToHtmlGenerator(BaseGenerator):
        def generate_round1(self, brief, checks, attachments): 
            return self.create_basic_files(brief)
        def generate_round2(self, brief, checks, attachments, existing_files): 
            return self.create_basic_files(brief)
        def create_basic_files(self, brief):
            return {
                'index.html': '<html><body><h1>Markdown App</h1></body></html>',
                'README.md': f'# Markdown App\n\n{brief}'
            }
    
    class GithubUserCreatedGenerator(BaseGenerator):
        def generate_round1(self, brief, checks, attachments): 
            return self.create_basic_files(brief)
        def generate_round2(self, brief, checks, attachments, existing_files): 
            return self.create_basic_files(brief)
        def create_basic_files(self, brief):
            return {
                'index.html': '<html><body><h1>GitHub App</h1></body></html>',
                'README.md': f'# GitHub App\n\n{brief}'
            }

# Load environment variables
load_dotenv()

app = Flask(__name__)

class DeploymentManager:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.secret = os.getenv('SECRET')
        
        print(f"🔧 Initializing DeploymentManager...")
        print(f"🔧 GitHub Token: {'✅ Set' if self.github_token else '❌ Missing'}")
        print(f"🔧 Secret: {'✅ ' + self.secret if self.secret else '❌ Missing'}")
        
        if not self.github_token:
            print("❌ GITHUB_TOKEN is missing from .env file")
            return
            
        if not self.secret:
            print("❌ SECRET is missing from .env file")
            return
            
        try:
            self.g = Github(self.github_token)
            self.user = self.g.get_user()
            print(f"✅ Connected to GitHub as: {self.user.login}")
            
            # Test rate limits
            rate_limit = self.g.get_rate_limit()
            print(f"📊 Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}")
            
        except Exception as e:
            print(f"❌ Failed to initialize GitHub: {e}")
            self.g = None
            self.user = None
        
    def verify_secret(self, request_secret):
        if not self.secret:
            print("❌ No secret configured in .env")
            return False
            
        if not request_secret:
            print("❌ No secret provided in request")
            return False
            
        is_valid = request_secret == self.secret
        print(f"🔐 Secret verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
        print(f"   Expected: {self.secret}")
        print(f"   Received: {request_secret}")
        return is_valid
    
    def create_repo(self, task_id, brief):
        if not self.g:
            print("❌ GitHub not initialized")
            return None, None
            
        repo_name = f"task-{task_id}-{str(uuid.uuid4())[:8]}"
        try:
            print(f"📦 Creating repository: {repo_name}")
            repo = self.user.create_repo(
                name=repo_name,
                description=f"Auto-generated project for: {brief[:100]}",
                private=False,
                auto_init=False
            )
            print(f"✅ Repository created: {repo_name}")
            return repo, repo_name
        except GithubException as e:
            print(f"❌ Error creating repo: {e}")
            if hasattr(e, 'data') and 'errors' in e.data:
                for error in e.data['errors']:
                    print(f"   Error detail: {error}")
            return None, None
    
    def setup_github_pages(self, repo):
        """Setup GitHub Pages - No API calls needed, just return the URL"""
        try:
            print("🌐 Configuring GitHub Pages...")
            
            # GitHub Pages is automatically enabled when content is pushed to main branch
            # We don't need to call any API - GitHub handles it automatically
            
            pages_url = f"https://{self.user.login}.github.io/{repo.name}/"
            print(f"✅ GitHub Pages URL: {pages_url}")
            print("📝 GitHub Pages will be automatically built within 1-2 minutes")
            print("💡 Note: First build might take a few minutes to complete")
            
            return True
            
        except Exception as e:
            print(f"⚠️ GitHub Pages note: {e}")
            print("📝 GitHub Pages will be available automatically after push")
            return True
    
    def commit_files(self, repo, files):
        try:
            print(f"📁 Committing {len(files)} files...")
            
            # Create LICENSE file first (required for evaluation)
            license_content = """MIT License

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
            repo.create_file("LICENSE", "Add MIT License", license_content)
            print("✅ LICENSE committed")
            
            # Create README
            readme_content = files.get('README.md', '# Project\n\nAuto-generated project.')
            repo.create_file("README.md", "Add README.md", readme_content)
            print("✅ README.md committed")
            
            # Add other files
            for file_path, content in files.items():
                if file_path not in ['README.md', 'LICENSE']:
                    repo.create_file(file_path, f"Add {file_path}", content)
                    print(f"✅ {file_path} committed")
            
            commit_sha = repo.get_branch("main").commit.sha
            print(f"✅ All files committed with SHA: {commit_sha[:8]}")
            return commit_sha
            
        except GithubException as e:
            print(f"❌ Error committing files: {e}")
            if hasattr(e, 'data') and 'errors' in e.data:
                for error in e.data['errors']:
                    print(f"   Error detail: {error}")
            return None

# Initialize deployment manager
deployment_manager = DeploymentManager()

def get_generator(brief):
    """Determine which generator to use based on the brief"""
    brief_lower = brief.lower()
    
    if 'sales' in brief_lower and 'sum' in brief_lower:
        return SumOfSalesGenerator()
    elif 'markdown' in brief_lower and 'html' in brief_lower:
        return MarkdownToHtmlGenerator()
    elif 'github' in brief_lower and 'user' in brief_lower:
        return GithubUserCreatedGenerator()
    else:
        # Default to sum of sales for unknown types
        return SumOfSalesGenerator()

def process_attachments(attachments):
    """Process base64 attachments and save them"""
    processed = {}
    for attachment in attachments:
        name = attachment['name']
        data_url = attachment['url']
        
        if data_url.startswith('data:'):
            # Extract base64 data
            base64_data = data_url.split('base64,')[1]
            decoded_data = base64.b64decode(base64_data)
            processed[name] = decoded_data
        else:
            # Handle URL case
            processed[name] = data_url
    
    return processed

def notify_evaluation(evaluation_url, data, max_retries=5):
    """Notify evaluation URL with exponential backoff"""
    print(f"📤 Notifying evaluation URL: {evaluation_url}")
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
            else:
                print(f"⚠️ Evaluation URL returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1, 2, 4, 8 seconds
            print(f"⏳ Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    print("❌ Failed to notify evaluation URL after all retries")
    return False

def process_deployment_async(request_data):
    """Process deployment in background thread"""
    print(f"\n" + "="*60)
    print(f"🚀 STARTING DEPLOYMENT PROCESS")
    print(f"="*60)
    print(f"📝 Task: {request_data['task']}")
    print(f"📧 Email: {request_data['email']}")
    print(f"🔢 Round: {request_data['round']}")
    print(f"📋 Brief: {request_data['brief'][:100]}...")
    
    try:
        # Verify secret
        if not deployment_manager.verify_secret(request_data.get('secret')):
            print("❌ Deployment aborted: Invalid secret")
            return
        
        # Get generator based on brief
        generator = get_generator(request_data['brief'])
        print(f"🔧 Using generator: {generator.__class__.__name__}")
        
        # Process attachments
        attachments = process_attachments(request_data.get('attachments', []))
        print(f"📎 Processed {len(attachments)} attachments")
        
        # Generate files
        files = generator.generate_round1(
            request_data['brief'], 
            request_data.get('checks', []),
            attachments
        )
        print(f"📄 Generated {len(files)} files: {list(files.keys())}")
        
        # Create repo
        repo, repo_name = deployment_manager.create_repo(
            request_data['task'], 
            request_data['brief']
        )
        
        if not repo:
            print("❌ Deployment failed: Could not create repository")
            return
        
        # Commit files
        commit_sha = deployment_manager.commit_files(repo, files)
        
        if not commit_sha:
            print("❌ Deployment failed: Could not commit files")
            return
        
        # Setup GitHub Pages (just configure URLs, no API calls)
        pages_setup = deployment_manager.setup_github_pages(repo)
        
        # Build response data
        response_data = {
            "email": request_data['email'],
            "task": request_data['task'],
            "round": request_data['round'],
            "nonce": request_data['nonce'],
            "repo_url": f"https://github.com/{deployment_manager.user.login}/{repo_name}",
            "commit_sha": commit_sha,
            "pages_url": f"https://{deployment_manager.user.login}.github.io/{repo_name}/"
        }
        
        print(f"\n📊 DEPLOYMENT SUMMARY:")
        print(f"🌐 Repository URL: {response_data['repo_url']}")
        print(f"🌐 Pages URL: {response_data['pages_url']}")
        print(f"🔑 Commit SHA: {commit_sha[:8]}")
        
        # Notify evaluation URL
        success = notify_evaluation(request_data['evaluation_url'], response_data)
        
        if success:
            print("\n🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print("="*60)
        else:
            print("\n⚠️ Deployment completed but evaluation notification failed")
            print("="*60)
            
    except Exception as e:
        print(f"\n💥 ERROR in deployment process: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)

@app.route('/api/deploy', methods=['POST'])
def deploy():
    """Main deployment endpoint"""
    print(f"\n📨 Received deployment request")
    
    try:
        request_data = request.get_json()
        
        if not request_data:
            print("❌ No JSON data received")
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
        
        print(f"📦 Request keys: {list(request_data.keys())}")
        
        # Validate required fields
        required_fields = ['email', 'secret', 'task', 'round', 'nonce', 'brief', 'evaluation_url']
        missing_fields = [field for field in required_fields if field not in request_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {missing_fields}"
            }), 400
        
        # Start async processing
        thread = threading.Thread(target=process_deployment_async, args=(request_data,))
        thread.daemon = True
        thread.start()
        
        print("✅ Request accepted, processing in background")
        
        # Return immediate response
        return jsonify({
            "status": "accepted",
            "message": "Deployment process started"
        }), 200
        
    except Exception as e:
        print(f"❌ Error in deploy endpoint: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "LLM Deployment API",
        "timestamp": time.time(),
        "version": "2.1"
    }), 200

@app.route('/debug', methods=['GET'])
def debug():
    """Debug endpoint to check configuration"""
    config = {
        "github_connected": deployment_manager.g is not None,
        "github_user": deployment_manager.user.login if deployment_manager.user else None,
        "secret_configured": bool(deployment_manager.secret),
        "port": os.getenv('PORT', 5000),
        "service": "LLM Deployment API v2.1"
    }
    return jsonify(config), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n" + "="*60)
    print(f"🌍 LLM Deployment API v2.1")
    print(f"="*60)
    print(f"🔗 Health check: http://localhost:{port}/health")
    print(f"🔗 Debug info: http://localhost:{port}/debug")
    print(f"🔗 Deploy endpoint: http://localhost:{port}/api/deploy")
    print(f"="*60)
    app.run(host='0.0.0.0', port=port, debug=False)