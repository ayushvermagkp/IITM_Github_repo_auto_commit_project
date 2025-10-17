from .base_generator import BaseGenerator

class MarkdownToHtmlGenerator(BaseGenerator):
    def generate_round1(self, brief, checks, attachments):
        # Get markdown content from attachments
        markdown_content = ""
        if 'input.md' in attachments:
            markdown_content = attachments['input.md'].decode('utf-8')
        else:
            markdown_content = "# Sample Markdown\n\nThis is **bold** and this is *italic*."
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown to HTML Converter</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
</head>
<body>
    <div class="container" style="max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1>Markdown Converter</h1>
        <div id="markdown-output" style="border: 1px solid #ccc; padding: 20px; border-radius: 5px;"></div>
    </div>
    <script>
        // Configure marked
        marked.setOptions({{
            highlight: function(code, lang) {{
                const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                return hljs.highlight(code, {{ language }}).value;
            }},
            langPrefix: 'hljs language-'
        }});
        
        // Convert and display markdown
        const markdownContent = `{markdown_content.replace('`', '\\`')}`;
        document.getElementById('markdown-output').innerHTML = marked.parse(markdownContent);
        
        // Apply highlighting
        document.querySelectorAll('pre code').forEach((block) => {{
            hljs.highlightElement(block);
        }});
    </script>
</body>
</html>"""
        
        setup_instructions = """1. Clone this repository
2. Open index.html in a web browser
3. No additional setup required - uses CDN for marked and highlight.js"""
        
        usage_instructions = """The page automatically converts the provided markdown content to HTML with syntax highlighting."""
        
        files = {
            'index.html': html_content,
            'input.md': markdown_content,
            'README.md': self.create_readme(brief, setup_instructions, usage_instructions)
        }
        
        return files
    
    def generate_round2(self, brief, checks, attachments, existing_files):
        return self.generate_round1(brief, checks, attachments)
