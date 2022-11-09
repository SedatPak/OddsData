from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

def main():

    ## Login info
    login_url = "https://www.oddsportal.com/login/"

    ## TODO: take into account wrong un/pw combination
    un = input("username: ")
    pw = input("password: ")

    ## TODO: ability to input your own match
    ## TODO: ability to iterate over matches in a league
    league_url = "https://www.oddsportal.com/soccer/england/premier-league/"
    href_url = "/soccer/england/premier-league/"

    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver = webdriver.Chrome()
    driver.maximize_window()

    ## Login
    driver.get(login_url)
    driver.implicitly_wait(0.5)
    login1 = driver.find_element(By.ID, "login-username1")
    login2 = driver.find_element(By.ID, "login-password1")
    login1.send_keys(un)
    login2.send_keys(pw)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()

    ## Find all the match urls using the league url
    driver.get(league_url)
    results = driver.find_elements(By.CSS_SELECTOR, f'a[href^="{href_url}"]')

    match_urls = []

    for result in results:
        href = result.get_attribute('href')
        if (href != "https://www.oddsportal.com/soccer/england/premier-league/" and
        href != "https://www.oddsportal.com/soccer/england/premier-league/outrights/" and
        href != "https://www.oddsportal.com/soccer/england/premier-league/results/" and
        href != "https://www.oddsportal.com/soccer/england/premier-league/standings/"):
            match_urls.append(href)

    ## Have an oddstable filled by iterating over all the matches in the league
    odds_table = pd.DataFrame(columns=['Match_id', 'Bookmakers', 'Home', 'Away', 'Draw', 'Payout'])
    match_table = pd.DataFrame(columns = ['Match_id', 'Result', 'Firsthalf', 'Secondhalf', 'Hometeam', 'Awayteam', 'Matchdate', 'Matchtime'])

    for i, match_url in enumerate(match_urls):
        driver.get(match_url)
        odds_table = odds_from_match(driver, odds_table, i)
        match_table = matchdata_from_match(driver, match_table, i)

    odds_table.to_csv("oddstable.csv", index = False)
    match_table.to_csv("matchtable.csv", index = False)

## Function that takes as input a match and file and adds the match data to the file
def odds_from_match(driver, oddsdataframe, match_id):

    try:
        driver.find_element(By.CSS_SELECTOR, 'a[onclick^="page.showHiddenProviderTable"]').click()
    except:
        pass

    ## Extract the odds into a data frame
    odds_table = driver.find_element(By.CSS_SELECTOR, 'table[class="table-main detail-odds sortable"]')
    soup = BeautifulSoup(odds_table.text, "html.parser")

    df = pd.DataFrame(soup)

    ## Split the data-frame to get just  the bookmakers and the odds

    ## Need to remove spaces from Bookmakers
    df[0] = df[0].str.replace('N1 Bet', 'N1_Bet')
    df[0] = df[0].str.replace('Vulkan Bet', 'Vulkan_Bet')
    df[0] = df[0].str.replace('William Hill', 'William_Hill')

    ## Only need the data between 'payout' and 'average', remove all spaces and newlines
    df[0] = df[0].str.replace('Average', 'Payout')
    df[0] = df[0].str.replace('\n', ' ')
    df = df[0].str.split('Payout', expand=True)
    df = df.iloc[0, :]
    df = pd.DataFrame(df)
    df = df.iloc[1, :].str.split(' ', expand=True)

    df = df[df != '']
    df = pd.DataFrame(df)
    df = df.dropna(axis=1)

    ## Retrieve the 5 different columns out of the data
    Bookmakers = np.transpose(df.iloc[:, ::5])
    Home = np.transpose(df.iloc[:, 1::5])
    Away = np.transpose(df.iloc[:, 2::5])
    Draw = np.transpose(df.iloc[:, 3::5])
    Payout = np.transpose(df.iloc[:, 4::5])
    Match_ids = np.full((len(Payout), 1), match_id)

    ## Combine into one data frame and save the df
    newdata = pd.DataFrame(np.column_stack([Match_ids, Bookmakers, Home, Away, Draw, Payout]),
               columns=['Match_id', 'Bookmakers', 'Home', 'Away', 'Draw', 'Payout'])
    oddsdataframe = pd.concat([oddsdataframe, newdata])

    return oddsdataframe

def matchdata_from_match(driver, matchdataframe, match_id):
    ## Get the match result if the match has been played
    try:
        result = driver.find_element(By.CLASS_NAME, 'result').text
        firsthalf = result.split('t ')[1].split(' (')
        finalresult = firsthalf[0]
        secondhalf = firsthalf[1].split(', ')
        firsthalf = secondhalf[0]
        secondhalf = secondhalf[1].split(')')[0]
    except:
        finalresult = None
        firsthalf = None
        secondhalf = None


    ## Get the match teams
    teams = driver.find_element(By.ID, "breadcrumb").text.split("»")
    teams = teams[len(teams) - 1]
    hometeam = teams.split("-")[0].strip()
    awayteam = teams.split("-")[1].strip()

    ## Get the match date
    dates = driver.find_element(By.CSS_SELECTOR, '[class^="date datet"]').text
    matchdate = dates.split(", ")
    matchtime = matchdate[2]
    matchdate = matchdate[1]


    newdata = pd.DataFrame({
        'Match_id': [match_id],
        'Result' : [finalresult],
        'Firsthalf': [firsthalf],
        'Secondhalf': [secondhalf],
        'Hometeam': [hometeam],
        'Awayteam': [awayteam],
        'Matchdate': [matchdate],
        'Matchtime': [matchtime]
    })

    matchdataframe = pd.concat([matchdataframe, newdata])
    return matchdataframe

if __name__ == '__main__':
    main()