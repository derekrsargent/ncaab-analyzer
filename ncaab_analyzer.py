import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# ------------------------------ COVERS SCRAPE ------------------------------ #

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/39.0.2171.95 Safari/537.36'}

page = requests.get("https://contests.covers.com/consensus/topconsensus/ncaab/", headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')

# Grab the tables, which contains the data we want for this webpage
tables = soup.find_all('table')
block_name = soup.find_all('span', class_="covers-CoversConsensus-table--teamBlock")
block2_name = soup.find_all('span', class_="covers-CoversConsensus-table--teamBlock2")

# This webpage has two tables we need to scrape from
block_names = []
block2_names = []

for name in block_name:
    block_names.append(name.contents[5]['title'])

for name in block2_name:
    block2_names.append(name.contents[5]['title'])

covers_data = []
counter = 0

# The tables have spaces and newline characters we need to remove
for table in tables:
    for row in table.find_all('tr'):
        columns = row.find_all('td')
        l = []
        for column in columns:
            i = column.get_text().strip().replace(" ", "")
            i = i.replace("\r\n", " ")
            i = i.replace("\n", " ")
            j = i.split(" ")
            j = list(filter(None, j))
            l.append(j)

        # Since the first one is coming in blank, make sure it contains elements
        if l:
            # split_element and split_spread are used to separate the '-3.5+3.5' during the web scraping
            split_element = l[3][0]
            split_element = split_element.replace("+", " +").replace("-", " -")
            split_spread = split_element.split(" ")
            split_spread = list(filter(None, split_spread))
            covers_list = [l[0][1].upper(), block_names[counter-1].upper(), float(split_spread[0]), l[0][2].upper(),
                           block2_names[counter-1].upper(), float(split_spread[1]), l[2][0], l[2][1]]
            covers_data.append(covers_list)
        counter += 1


# ------------------------------ OLG SCRAPE ------------------------------ #

# This uses Selenium because we need a browser environment for the scripts in the webpage
driver = webdriver.Chrome("C:/Users/derek/Downloads/chromedriver_win32/chromedriver.exe")
driver.get('https://www.proline.ca/#pointspread?sport=cbk')

element_match_home = driver.find_elements_by_class_name('match-home')
element_match_home_spread = driver.find_elements_by_class_name('match-home-spread')
element_match_visitor = driver.find_elements_by_class_name('match-visitor')
element_match_visitor_spread = driver.find_elements_by_class_name('match-visitor-spread')
element_match_number = driver.find_elements_by_class_name('match-number')

olg_data = []
olg_list = []

# Get the relevant data for each match (ie each 'game')
for match in range(len(element_match_number)):
    match_home = element_match_home[match].get_attribute('data-short')
    match_home_full = element_match_home[match].text
    match_home_spread = element_match_home_spread[match].text.replace("(", "").replace(")", "").replace(" ", "")
    match_visitor = element_match_visitor[match].get_attribute('data-short')
    match_visitor_full = element_match_visitor[match].text
    match_visitor_spread = element_match_visitor_spread[match].text.replace("(", "").replace(")", "").replace(" ", "")
    match_number = element_match_number[match].text

    if match_home_spread == '':
        match_home_spread = match_visitor_spread.replace("-", "+")

    if match_visitor_spread == '':
        match_visitor_spread = match_home_spread.replace("-", "+")

    # This webpage can have a blank match which would cause an error when trying to parse to a float
    if match_home_spread != '':
        olg_list = [match_home.upper(), match_home_full, float(match_home_spread),
                    match_visitor.upper(), match_visitor_full, float(match_visitor_spread), match_number]
        olg_data.append(olg_list)

driver.quit()


# ------------------------------ PICKWISE SCRAPE ------------------------------ #

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/39.0.2171.95 Safari/537.36'}

page = requests.get("https://www.pickswise.com/sports/college-basketball/", headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')

# Pickwise needs us to grab data separately, so this is more involved
teams = soup.find_all("div", class_="Pick__team-name")
outcomes = soup.find_all("div", class_="PickPrediction__pick-text PickPrediction__pick-text--short-coutcome")
confidences = soup.find_all("i", class_="ConfidenceRating__star")

# Convert outcomes to a list and filter out any starting with 'Under' or 'Over',
# and strip() is because there's multiple whitespaces when scraping it (removes '\n' too)
outcomes_list = []
outcomes_edited = []
outcomes_split = []

for j in range(len(outcomes)):
    outcomes_edited.append(outcomes[j].text.replace('-', '^-').replace('+', '^+'))

    # Fix cases where '-' is in the team name so it doesn't split at it and cause a parse error
    if outcomes_edited[j].count('+') == 1:
        outcomes_edited[j] = outcomes_edited[j].replace('^-', '-')
    elif outcomes_edited[j].count('-') == 2:
        outcomes_edited[j] = outcomes_edited[j].replace('^-', '-', 1)

    outcomes_split = outcomes_edited[j].strip().split('^')
    for i in range(len(outcomes_split)):
        if i == 0:
            outcomes_split[i] = outcomes_split[i].rstrip()
            # This '123' is a placeholder for the match data which we later filter out
            outcomes_split.append('123')
        if i == 1:
            outcomes_split[i] = outcomes_split[i].split()[0]
    outcomes_list.append(outcomes_split)

# Convert confidences to a list and then add up every three star/no-star to get the confidence value
# Can't remove every other value since on 12/08/20 there was a hidden Miami -1 game with no Over/Under
confidences_list = []
iter_counter = 0
star_counter = 0
for j in range(len(confidences)):
    if len(confidences[j]['class']) == 4:
        star_counter += 1
    iter_counter += 1
    if iter_counter == 3:
        confidences_list.append(star_counter)
        star_counter = 0
        iter_counter = 0

# Merge outcomes and confidences into a dictionary and remove the paired (ie key:value) 'Under/Over' outcomes
pickwise_data = {}
for j in range(len(outcomes_list)):
    pickwise_data[outcomes_list[j][0].upper()] = [float(outcomes_list[j][1]), int(confidences_list[j])]

pickwise_data = {k: v for (k, v) in pickwise_data.items() if 'OVER' not in k}
pickwise_data = {k: v for (k, v) in pickwise_data.items() if 'UNDER' not in k}


# ------------------------------ COMPARE OLG TO COVERS ------------------------------ #

print('olg_data: ', olg_data)
print('covers_data: ', covers_data)
print('pickwise_data: ', pickwise_data)

# covers_data is already sorted by the consensus
print('SURVEY SAYS!:')
for covers_match in covers_data:
    for olg_match in olg_data:
        pickwise_match = '[NO PICKWISE MATCH]'
        if olg_match[1] == covers_match[1] or olg_match[1] == covers_match[4]:
            if covers_match[6] > covers_match[7]:
                team_selection = [covers_match[1], covers_match[2], covers_match[6]]
            else:
                team_selection = [covers_match[4], covers_match[5], covers_match[7]]
            if covers_match[1] in pickwise_data:
                pickwise_match = pickwise_data[covers_match[1]]
            elif covers_match[4] in pickwise_data:
                pickwise_match = pickwise_data[covers_match[4]]
            print('>>> OLG: ', olg_match, '>>> Covers: ', team_selection, '>>> Pickwise: ', pickwise_match)
