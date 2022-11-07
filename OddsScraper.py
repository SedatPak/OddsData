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
    ## Match info
    match_url = "https://www.oddsportal.com/soccer/spain/laliga/rayo-vallecano-real-madrid-KAOyH3RR/"

    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver = webdriver.Chrome()
    driver.maximize_window()

    ## Login
    driver.get(login_url)
    driver.implicitly_wait(5)
    login1 = driver.find_element(By.ID, "login-username1")
    login2 = driver.find_element(By.ID, "login-password1")
    login1.send_keys(un)
    login2.send_keys(pw)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()


    ## Open the match and press the 'show more bookmakers' button if necessary
    driver.get(match_url)
    try:
        driver.find_element(By.CSS_SELECTOR, 'a[onclick^="page.showHiddenProviderTable"]').click()
    except:
        print("no need to press more bookmakers button")

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

    ## Combine into one data frame and save the df
    odds_table = pd.DataFrame(np.column_stack([Bookmakers, Home, Away, Draw, Payout]),
                              columns=['Bookmakers', 'Home', 'Away', 'Draw', 'Payout'])
    odds_table.to_csv("oddstable.csv")


if __name__ == '__main__':
    main()