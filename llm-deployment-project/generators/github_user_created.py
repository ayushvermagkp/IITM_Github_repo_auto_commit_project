from .base_generator import BaseGenerator

class GithubUserCreatedGenerator(BaseGenerator):
    def generate_round1(self, brief, checks, attachments):
        # Simple seed extraction that never fails
        seed = "default123"
        
        # Try to extract any ID from the brief
        import re
        seed_match = re.search(r'github-user-([\w]+)', brief)
        if seed_match:
            seed = seed_match.group(1)
        else:
            # Use a hash of the brief as seed
            import hashlib
            seed = hashlib.md5(brief.encode()).hexdigest()[:8]
        
        print(f"🔧 Using seed for GitHub form: {seed}")
        
        # Rest of the HTML and JS content remains the same as above
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub User Lookup</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>GitHub Account Creation Date</h1>
        <form id="github-user-{seed}" class="mt-4">
            <div class="mb-3">
                <label for="username" class="form-label">GitHub Username</label>
                <input type="text" class="form-control" id="username" required>
            </div>
            <div class="mb-3">
                <label for="token" class="form-label">GitHub Token (Optional)</label>
                <input type="password" class="form-control" id="token">
            </div>
            <button type="submit" class="btn btn-primary">Lookup</button>
        </form>
        
        <div id="result" class="mt-4" style="display: none;">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Account Information</h5>
                    <p class="card-text">Creation Date: <span id="github-created-at"></span></p>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>"""
        
        js_content = f"""document.getElementById('github-user-{seed}').addEventListener('submit', async function(e) {{
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const token = document.getElementById('token').value;
    
    if (!username) {{
        alert('Please enter a GitHub username');
        return;
    }}
    
    try {{
        const headers = {{}};
        if (token) {{
            headers['Authorization'] = `Bearer ${{token}}`;
        }}
        
        const response = await fetch(`https://api.github.com/users/${{username}}`, {{ headers }});
        
        if (!response.ok) {{
            throw new Error('User not found or API limit exceeded');
        }}
        
        const userData = await response.json();
        const createdAt = new Date(userData.created_at);
        const formattedDate = createdAt.toISOString().split('T')[0];
        
        document.getElementById('github-created-at').textContent = formattedDate;
        document.getElementById('result').style.display = 'block';
        
    }} catch (error) {{
        alert('Error: ' + error.message);
    }}
}});"""
        
        setup_instructions = """1. Clone this repository
2. Open index.html in a web browser
3. No additional setup required"""
        
        usage_instructions = f"""Enter a GitHub username to see their account creation date."""
        
        files = {
            'index.html': html_content,
            'script.js': js_content,
            'README.md': self.create_readme(brief, setup_instructions, usage_instructions)
        }
        
        return files
    
    def generate_round2(self, brief, checks, attachments, existing_files):
        return self.generate_round1(brief, checks, attachments)