import requests
from bs4 import BeautifulSoup

target_url = "https://www.churchofjesuschrist.org/?lang=eng"

response = requests.get(target_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    text = ""

    # Extract and format the text
    for paragraph in soup.find_all('p'):
        text += paragraph.get_text(strip=True) + "\n\n"

    # Save the extracted text to a file
    with open('website_text.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(text)

    print("Text extracted and saved successfully!")

else:
    print(f"Error: Failed to retrieve website content. Status code: {response.status_code}")
