import re
import requests
from bs4 import BeautifulSoup
from email import policy
from email.parser import BytesParser

def extract_links_from_text(text):
    # Basic regex for URLs
    return re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)

def extract_links_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return links

def check_link(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code >= 400:
            # try GET if HEAD fails
            response = requests.get(url, allow_redirects=True, timeout=5)
        return response.status_code
    except requests.RequestException as e:
        return str(e)

def verify_email_links(email_path):
    with open(email_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    all_links = set()

    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type == 'text/plain':
            all_links.update(extract_links_from_text(part.get_content()))
        elif content_type == 'text/html':
            all_links.update(extract_links_from_html(part.get_content()))

    results = {}
    for link in all_links:
        status = check_link(link)
        results[link] = status

    return results

# Example usage
if __name__ == "__main__":
    email_file = "test_message.eml"  # path to saved email
    results = verify_email_links(email_file)

    print("Link Validation Results:")
    for link, status in results.items():
        print(f"{link} -> {status}")
