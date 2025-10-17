import base64
from .base_generator import BaseGenerator

class SumOfSalesGenerator(BaseGenerator):
    def generate_round1(self, brief, checks, attachments):
        # Extract seed from brief or use default
        seed = "default"
        if "seed" in brief:
            try:
                seed_part = brief.split("seed")[1].split()[0].strip('"\'')
                seed = seed_part
            except Exception as e:
                print(f"Error extracting seed: {e}")
                seed = "default"
        
        # Get CSV data from attachments
        csv_data = ""
        if 'data.csv' in attachments:
            csv_data = attachments['data.csv'].decode('utf-8')
        else:
            # Generate sample data
            csv_data = "product,sales\nProduct A,100\nProduct B,150\nProduct C,75"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Summary {seed}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Sales Summary {seed}</h1>
        <div class="card mt-4">
            <div class="card-body">
                <h5 class="card-title">Total Sales</h5>
                <p class="card-text fs-3 text-primary" id="total-sales">Calculating...</p>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>"""
        
        js_content = f"""// Sales calculation script
async function loadSalesData() {{
    try {{
        const response = await fetch('data.csv');
        const csvText = await response.text();
        const lines = csvText.trim().split('\\n').slice(1);
        
        let total = 0;
        lines.forEach(line => {{
            if (line.trim()) {{
                const cells = line.split(',');
                const sales = parseFloat(cells[1]);
                if (!isNaN(sales)) {{
                    total += sales;
                }}
            }}
        }});
        
        document.getElementById('total-sales').textContent = total.toFixed(2);
    }} catch (error) {{
        console.error('Error loading sales data:', error);
        document.getElementById('total-sales').textContent = 'Error';
    }}
}}

// Load data when page loads
document.addEventListener('DOMContentLoaded', loadSalesData);"""
        
        setup_instructions = """1. Clone this repository
2. Open index.html in a web browser
3. No additional setup required - uses CDN for Bootstrap"""
        
        usage_instructions = """The page will automatically load the sales data from data.csv and display the total sum."""
        
        files = {
            'index.html': html_content,
            'script.js': js_content,
            'data.csv': csv_data,
            'README.md': self.create_readme(brief, setup_instructions, usage_instructions)
        }
        
        return files
    
    def generate_round2(self, brief, checks, attachments, existing_files):
        # This would handle round 2 modifications
        # For now, return round1 files
        return self.generate_round1(brief, checks, attachments)