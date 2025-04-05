from amazon import scrape
import json

# Test URL from Amazon India
test_url = "https://www.amazon.in/dp/B076CJMHBC"

# Scrape the product
print(f"Testing scraper with URL: {test_url}")
data = scrape(test_url)

# Print the results
if data:
    print("\nScraping successful! Here are the results:")
    print(f"Title: {data.get('title')}")
    print(f"Price: {data.get('price')}")
    print(f"ASIN: {data.get('asin')}")
    print(f"Rating: {data.get('rating')}")
    print(f"Number of Reviews: {data.get('number_of_reviews')}")
    print(f"Stock Status: {data.get('stock_status')}")
    print(f"Style Code: {data.get('style_code')}")
    
    # Save to a test output file
    with open('test_output.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("\nFull data saved to test_output.json")
else:
    print("\nScraping failed. Check the error messages above.") 