# Import modules
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from random import randint
from googlesearch import search
import sys

# Instantiate chrome driver
def Chrome_Driver(choice):
    # Instantiate chrome options object to set preferences
    chrome_options = Options()
    # Specifies the path to the chromedriver.exe (put your path here)
    path = 'path/to/chromedriver.exe'
    if 'headless' in choice:
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options,executable_path=path)
    else:
        driver = webdriver.Chrome(executable_path=path)
    return driver
  
# Authenticate user by logging into Linkedin
def Authenticate_LinkedIn(user_name,pass_word): 
    start = time.time()  
    # driver.get method() will navigate to a page given by the URL address
    driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    # locate email form by_class_name
    elementID = driver.find_element_by_name('session_key')
    # send_keys() to simulate key strokes
    elementID.send_keys(user_name)
    # sleep for random no.of seconds to avoid account cancellation
    time.sleep(randint(1,5))
    # locate password form by_class_name
    elementID = driver.find_element_by_name('session_password')
    # send_keys() to simulate key strokes
    elementID.send_keys(pass_word)
    time.sleep(randint(1,5))
    end = time.time()
    # Total time needed to run this function is measured
    runtime = end-start
    return runtime  
  
# Google search for all possible LinkedIn profiles of person
def Get_LinkedIn_Links(person,company):
    start = time.time()
    # "linkedin" in query ensures all links are from linkedin 
    query = '"linkedin" '+person+" "+company
    linkedin_list = []
    for link in search(query,lang='en',num=10,stop=10):
        # Only append links that have https://in.linkedin.com/in/
        if '/in/' in link:
            linkedin_list.append(link)
    # Display links got so far
    print(linkedin_list)
    end = time.time()
    # Display execution time for Google search
    print("Runtime for Google search: ",(end-start))
    return linkedin_list
  
def Get_LinkedIn_Data(url):
    start = time.time()
    f.write('-------------------------------------------------------------------\n')
    f.write('\nURL results for: '+url)
    f.write('\n')
    f.write('\nPersonal details\n')
    print("Start: LinkedIn search for",url,"\n")
    driver.get(url)
    end = time.time()
    # Display time needed to run google search
    print("Runtime for Linked search: ",(end-start))
    print("\nEnd: LinkedIn search for",url,"\n")
    
    # Full page is not loaded at start, so scroll till bottom
    start_scroll = time.time()
    SCROLL_PAUSE_TIME = 5
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    print("Start: LinkedIn page scroll\n")
    # Scroll page in sets of 3 
    for i in range(3):
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    end_scroll = time.time()
    print("\nRuntime for LinkedIn page scroll: ",(end_scroll-start_scroll))
    print("\nEnd: LinkedIn page scroll\n")
    # Create BeautifulSoup object for data extraction
    src = driver.page_source
    soup = BeautifulSoup(src,"lxml")

    start_data = time.time()
    print("Start: Getting LinkedIn data\n")
    # Get name, location and no.of connections
    name_div = soup.find('div', {'class': 'flex-1 mr5'})
    #print(name_div)
    name_loc = name_div.find_all('ul')
    name = name_loc[0].find('li').get_text().strip()
    location = name_loc[1].find('li').get_text().strip()
    # sleep for random no.of seconds to avoid account cancellation
    time.sleep(randint(1,5))
        #print("Name:",name)
        #print("Location:",location)
    f.write("Name: "+name)
    f.write('\n')
    f.write("Location: "+location)
    f.write('\n')

    # Get position and no.of connections
    profile_title = name_div.find('h2').get_text().strip()
    connection = name_loc[1].find_all('li')
    connection = connection[1].get_text().strip()
    # sleep for random no.of seconds to avoid account cancellation
    time.sleep(randint(1,5))
        #print("Working as:",profile_title)
        #print("No.of connections:",connection)
    f.write("Current position: "+profile_title)
    f.write('\n')
    f.write("No.of LinkedIn connections: "+connection)
    f.write('\n')

    # Get experience for a user (if it exists)
    f.write('\nWork experience\n')
    try:
        exp_section = soup.find('section', {'id': 'experience-section'}).find('ul')
        exp_list = exp_section.find_all('li')
        for lineitem in exp_list:
            div_tag = lineitem.find('div')
            a_tag = div_tag.find('a')
            # Extract job title 
            job_title = a_tag.find('h3').get_text().strip()
            f.write('Job title: '+job_title)
            f.write('\n')
            # Extract organisation name
            company_name = a_tag.find_all('p')[1].get_text().strip()
            f.write('Organisation name: '+company_name)
            f.write('\n')
            # Extract no.of days working for company
            joining_date = a_tag.find_all('h4')[0].find_all('span')[1].get_text().strip()
            f.write('Working duration: '+joining_date)
            exp = a_tag.find_all('h4')[1].find_all('span')[1].get_text().strip()
            # Duration of work done
            f.write(' ('+exp+') ')
            f.write('\n')
            f.write('\n')
    except:
        f.write('No experience data found\n')
    
    # Get education details (if it exists)
    f.write('\nEducation\n')
    try:
        edu_section = soup.find('section', {'id': 'education-section'}).find('ul')
        edu_list = edu_section.find_all('li')
        for lineitem in edu_list:
            # Name of institutes studied at
            f.write('Studied at: '+lineitem.find('h3').get_text().strip())
            f.write('\n')
            # Degree name
            degree_name = lineitem.find('p', {'class': 'pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal'}).find_all('span')[1].get_text().strip()
            f.write('Degree in: '+degree_name)
            # Area of specialization
            stream = lineitem.find('p', {'class': 'pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal'}).find_all('span')[1].get_text().strip()
            f.write(' '+stream)
            f.write('\n')
            # Year of graduation
            degree_year = lineitem.find('p', {'class': 'pv-entity__dates t-14 t-black--light t-normal'}).find_all('span')[1].get_text().strip()
            f.write('Year of graduation: '+degree_year)
            f.write('\n')
            f.write('\n')
            
    except:
        f.write('No more details found\n')
    # End of data for 1 person
    f.write('-------------------------------------------------------------------\n')
    end_data = time.time()
    # Time needed to get LinkedIn data for 1 person
    print("Runtime for getting LinkedIn data: ",(end_data-start_data))
    print("\nEnd: Getting LinkedIn data\n")
    
# Driver code
# Extract choice (head/headless) from command line
file_name = sys.argv[0]
# If no argument provided, take headless as default
try:
    choice = str(sys.argv[1])
except:
    choice = '--headless'

# Check else for help
if choice == '--head':
    # Keep browser open
    print("Running script with browser open\n")
elif choice == '--headless':
    # Browser runs in the background
    print("Running script\n")
else:
    # Keep browser closed as default
    print("Enter --head to see selenium browser running\nEnter --headless to run browser in background\n")
    print("Enter space for person/company to skip those fields\n")
    print("Default is script running(--headless)\n")
    
# Ask user for query to search for
person = input("Enter person name: ")
company = input("Enter company name: ")

# Write scraped information into file
f = open('data.txt','w')

# Read username and password from config.txt
# Create your config.txt before running this code
file = open('config.txt')
lines = file.readlines()
# Email id and password of user logging into LinkedIn to get required info on person and company
user_name = lines[0] # user_name = 'your email id'
pass_word = lines[1] # pass_word = 'your password'

# Get first link from linkedin_list and get data 
print("Start: Google search\n")
results = Get_LinkedIn_Links(person,company)
print("\nEnd: Google search\n")

# Log into LinkedIn using email id and password
print("Start: LinkedIn login\n")
# Create driver for all web searches
driver = Chrome_Driver(choice)
authenticate_time = Authenticate_LinkedIn(user_name,pass_word)
print("Runtime for LinkedIn login: ",authenticate_time)
print("\nEnd: LinkedIn login\n")

if company == ' ' or person == ' ':
    # Get LinkedIn data for all url results
    for url in results:
        Get_LinkedIn_Data(url)
else:
    # Get LinkedIn data for first url alone (person+company)
    url = results[0]
    Get_LinkedIn_Data(url)

# End of script
f.close()
driver.quit()
