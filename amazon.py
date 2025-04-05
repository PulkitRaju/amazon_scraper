from selectorlib import Extractor
import requests 
import json 
from time import sleep
import re
import random
import os
from datetime import datetime


# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Create an Extractor by reading from the YAML file
extractor = Extractor.from_yaml_file(os.path.join(script_dir, 'selectors.yml'))

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    return random.choice(user_agents)

def get_headers(is_amazon_in=False):
    # Get a random user agent
    user_agent = get_random_user_agent()
    
    # Generate a random session ID
    session_id = ''.join(random.choices('0123456789ABCDEF', k=32))
    
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
        'DNT': '1',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="92"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Cookie': f'session-id={session_id}; session-token={session_id}',
    }
    
    if is_amazon_in:
        headers['Referer'] = 'https://www.amazon.in/'
        headers['Origin'] = 'https://www.amazon.in'
        headers['Host'] = 'www.amazon.in'
    else:
        headers['Referer'] = 'https://www.amazon.com/'
        headers['Origin'] = 'https://www.amazon.com'
        headers['Host'] = 'www.amazon.com'
    
    return headers

def scrape(url, max_retries=3):  
    # Check if the URL is for Amazon India
    is_amazon_in = 'amazon.in' in url
    
    for attempt in range(max_retries):
        try:
            # Add a random delay between requests
            sleep_time = random.uniform(1, 3)
            sleep(sleep_time)
            
            # Get headers for this request
            headers = get_headers(is_amazon_in)
            
            # Download the page using requests
            print(f"Downloading {url} (Attempt {attempt + 1}/{max_retries})")
            r = requests.get(url, headers=headers, timeout=10)
            
            # Check if we got blocked
            if r.status_code > 500:
                if "To discuss automated access to Amazon data please contact" in r.text:
                    print(f"Page {url} was blocked by Amazon. Please try using better proxies\n")
                else:
                    print(f"Page {url} must have been blocked by Amazon as the status code was {r.status_code}")
                continue
            
            # Check if we got a valid HTML response
            if not r.text or len(r.text) < 100:
                print(f"Received empty or very short response from {url}")
                continue
                
            # Save the HTML for debugging if needed
            debug_file = os.path.join(script_dir, 'debug.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(r.text)
                
            # Extract data using the selector
            data = extractor.extract(r.text)
            
            # Process the data to ensure all fields are properly formatted
            if data:
                # Extract ASIN from URL if not found in the page
                if not data.get('asin'):
                    if 'asin=' in url:
                        asin_match = re.search(r'asin=([A-Z0-9]{10})', url)
                        if asin_match:
                            data['asin'] = asin_match.group(1)
                    elif '/dp/' in url:
                        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
                        if asin_match:
                            data['asin'] = asin_match.group(1)
                
                # Clean up the top critical review if it exists
                if data.get('top_critical_review'):
                    data['top_critical_review'] = data['top_critical_review'].strip()
                
                # Ensure all fields exist in the output
                for field in ['title', 'price', 'style_code', 'asin', 'rating', 'number_of_reviews', 
                             'stock_status', 'about_this_item', 'top_critical_review', 'short_description', 
                             'product_description', 'sales_rank']:
                    if field not in data:
                        data[field] = None
                
                # Clean up price field
                if data.get('price'):
                    price_match = re.search(r'([\$₹£]?\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)', str(data['price']))
                    if price_match:
                        data['price'] = price_match.group(1)
                    else:
                         # Try extracting digits if no currency symbol found
                         digits = re.findall(r'\d+', str(data['price']))
                         if digits:
                            data['price'] = "".join(digits)
                         else:
                            data['price'] = data['price'].strip() # Keep original if no match
                
                # Clean up rating field
                if data.get('rating'):
                    rating_match = re.search(r'(\d+(\.\d+)?)', data['rating'])
                    if rating_match:
                        data['rating'] = rating_match.group(1) + " out of 5"
                
                # Clean up style code (Item model number)
                if data.get('style_code'):
                    # Remove potential leading/trailing whitespace and extra characters
                    data['style_code'] = re.sub(r'^\s*([^\s\w]*)\s*', '', data['style_code']).strip()
                    # Specific trim for the observed issue if needed, but let's try a general clean first
                    # data['style_code'] = data['style_code'].strip().rstrip('1') # Example specific trim
                
                # Clean up stock status
                if data.get('stock_status'):
                    if 'in stock' in data['stock_status'].lower():
                        data['stock_status'] = 'In Stock'
                    elif 'out of stock' in data['stock_status'].lower():
                        data['stock_status'] = 'Out of Stock'
                    elif 'temporarily out of stock' in data['stock_status'].lower():
                        data['stock_status'] = 'Temporarily Out of Stock'
                
                return data
            else:
                print(f"No data extracted from {url}")
                continue
                
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            if attempt < max_retries - 1:
                continue
            else:
                return None
    
    return None

if __name__ == '__main__':
    with open("urls.txt",'r') as urllist, open('output.jsonl','w') as outfile:
        for url in urllist.read().splitlines():
            data = scrape(url) 
            if data:
                json.dump(data,outfile)
                outfile.write("\n")
                # Add a random delay between requests
                sleep(random.uniform(2, 5))
    