import base64
import os

def decode_data_url(data_url):
    """Decode a data URL and return the content"""
    if data_url.startswith('data:'):
        # Extract base64 data
        base64_data = data_url.split('base64,')[1]
        return base64.b64decode(base64_data)
    return data_url

def save_attachment(attachment, save_path):
    """Save an attachment to the specified path"""
    try:
        content = decode_data_url(attachment['url'])
        with open(save_path, 'wb') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving attachment: {e}")
        return False

def create_license_file():
    """Create MIT License file content"""
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
