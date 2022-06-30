from flask import Flask, render_template,request,redirect
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import sqlite3
import urllib.request
from pprint import pprint
from html_table_parser.parser import HTMLTableParser
import pandas as pd
def url_get_contents(url):
    req = urllib.request.Request(url=url)
    f = urllib.request.urlopen(req)
    return f.read()
scraper=HTMLTableParser()
app=Flask(__name__)
#configure database here
conn=sqlite3.connect('interiit.db',check_same_thread=False)
c=conn.cursor()

#____________
#UNCOMMENT THIS FOR THE FIRST TIME USE
c.execute(''' CREATE TABLE gradez(id TEXT, no TEXT, name TEXT,credits TEXT, grades TEXT)''')
#____________
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/',methods=['POST'])
def getValue():
    username=request.form['rollnumber']
    password =request.form['ldap']

    
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://www.iitm.ac.in/viewgrades/')
    driver.implicitly_wait(20)
    Roll_No=driver.find_element_by_name('rollno')
    Roll_No.send_keys(username)
    Password=driver.find_element_by_name('pwd')
    Password.send_keys(password)
    Submit_suc=driver.find_element_by_name('submit')
    Submit_suc.send_keys('Submit')
    Submit_suc.click()
    
    driver.get("https://www.iitm.ac.in/viewgrades/studentauth/btechdual.php")
    r = driver.page_source
    soup =BeautifulSoup(r,'html.parser')
    table1=soup.find('table')
    table2=soup.find_all('table')[2]
    courseid=[]
    courseno=[]
    coursename=[]
    coursecredits=[]
    coursegrades=[]

    
    for i in table2.find_all('tr'):
        vals=i.find_all('td')
        if(len(vals)==7):
            if(vals[5].text!=""):
                courseid.append(vals[0].text)
                courseno.append(vals[1].text)
                coursename.append(vals[2].text)
                coursecredits.append(vals[4].text)
                coursegrades.append(vals[5].text)
    for j in range(0,22):
        c.execute('''INSERT INTO gradez VALUES (?,?,?,?,?)''',(courseid[j],courseno[j],coursename[j],coursecredits[j],coursegrades[j]))
        conn.commit()
    c.execute('''SELECT * FROM gradez''')
    res=c.fetchall()
    print(res)
    return redirect('user_info')

@app.route('/user_info')
def users():
    userdetails=c.execute('''SELECT * FROM gradez''')
    return render_template('pass.html',u=userdetails)
if __name__== '__main__':
    app.run()