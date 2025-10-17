from .base_generator import BaseGenerator
import json

class SumOfSalesGenerator(BaseGenerator):
    def generate_round1(self, brief, checks, attachments):
        seed = self.extract_seed(brief)
        csv_data = self.get_csv_data(attachments)
        
        html_content = self.create_round1_html(seed)
        js_content = self.create_round1_js()
        
        files = {
            'index.html': html_content,
            'script.js': js_content,
            'data.csv': csv_data,
            'README.md': self.create_readme(brief, 
                "1. Open index.html in browser\n2. Uses Bootstrap CDN", 
                "Page automatically loads and displays total sales",
                round_num=1)
        }
        
        return files
    
    def generate_round2(self, brief, checks, attachments, existing_files):
        seed = self.extract_seed(brief)
        
        if "Bootstrap table" in brief or "product-sales" in brief:
            return self.add_product_table(brief, seed, attachments)
        elif "currency" in brief:
            return self.add_currency_converter(brief, seed, attachments)
        elif "region" in brief or "filter" in brief:
            return self.add_region_filter(brief, seed, attachments)
        else:
            # Default round 2 enhancement
            return self.add_product_table(brief, seed, attachments)
    
    def add_product_table(self, brief, seed, attachments):
        """Add product sales table for round 2"""
        csv_data = self.get_csv_data(attachments)
        
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
        
        <div class="card mt-4">
            <div class="card-body">
                <h5 class="card-title">Product Sales</h5>
                <table class="table table-striped" id="product-sales">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Sales</th>
                        </tr>
                    </thead>
                    <tbody id="product-sales-body">
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>"""
        
        js_content = """// Enhanced sales calculation with product table
async function loadSalesData() {
    try {
        const response = await fetch('data.csv');
        const csvText = await response.text();
        const lines = csvText.trim().split('\\n').slice(1);
        
        let total = 0;
        const productSales = [];
        const tableBody = document.getElementById('product-sales-body');
        tableBody.innerHTML = '';
        
        lines.forEach(line => {
            if (line.trim()) {
                const cells = line.split(',');
                const product = cells[0];
                const sales = parseFloat(cells[1]);
                if (!isNaN(sales)) {
                    total += sales;
                    productSales.push({ product, sales });
                    
                    // Add to table
                    const row = document.createElement('tr');
                    row.innerHTML = `<td>${product}</td><td>${sales.toFixed(2)}</td>`;
                    tableBody.appendChild(row);
                }
            }
        });
        
        document.getElementById('total-sales').textContent = total.toFixed(2);
    } catch (error) {
        console.error('Error loading sales data:', error);
        document.getElementById('total-sales').textContent = 'Error';
    }
}

document.addEventListener('DOMContentLoaded', loadSalesData);"""
        
        files = {
            'index.html': html_content,
            'script.js': js_content,
            'data.csv': csv_data,
            'README.md': self.create_readme(brief,
                "1. Open index.html in browser",
                "Shows total sales and product-wise breakdown in a table",
                round_num=2)
        }
        
        return files
    
    def add_currency_converter(self, brief, seed, attachments):
        # Implementation for currency converter
        pass
    
    def add_region_filter(self, brief, seed, attachments):
        # Implementation for region filter
        pass
    
    def extract_seed(self, brief):
        # Seed extraction logic
        return "default"
    
    def get_csv_data(self, attachments):
        if 'data.csv' in attachments:
            return attachments['data.csv'].decode('utf-8')
        return "product,sales\\nProduct A,100\\nProduct B,150\\nProduct C,75"
    
    def create_round1_html(self, seed):
        # Round 1 HTML template
        return f"""<!DOCTYPE html>
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
    
    def create_round1_js(self):
        # Round 1 JavaScript
        return """// Sales calculation script
async function loadSalesData() {
    try {
        const response = await fetch('data.csv');
        const csvText = await response.text();
        const lines = csvText.trim().split('\\n').slice(1);
        
        let total = 0;
        lines.forEach(line => {
            if (line.trim()) {
                const cells = line.split(',');
                const sales = parseFloat(cells[1]);
                if (!isNaN(sales)) {
                    total += sales;
                }
            }
        });
        
        document.getElementById('total-sales').textContent = total.toFixed(2);
    } catch (error) {
        console.error('Error loading sales data:', error);
        document.getElementById('total-sales').textContent = 'Error';
    }
}

document.addEventListener('DOMContentLoaded', loadSalesData);"""
