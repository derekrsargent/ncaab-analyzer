# ncaab-analyzer
Look for value using Covers.com consensus data and Pickwise.com selections compared to available OLG games

In Python 3 install the required libraries using:  
pip3 freeze > requirements.txt
pip3 install -r requirements.txt

Download ChromeDriver and move to the required folder. 

Output will be in this form:
OLG:  ['ORST', 'OREGON ST.', 7.0, 'ARZ', 'ARIZONA', -7.0, 'NO.78'] >>> Covers:  ['ARIZONA', -8.0, '55%'] >>> Pickwise:  [-8.0, 3]

Where the relevant OLG data is shown; along with the corresponding Covers consensus pick % for that team, and the spread that Pickwise has selected with the number of stars they rate it. 
