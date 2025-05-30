from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from datetime import datetime


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(chrome_options)
nums = []
papers = ["IFB", "BT", "MA", "FA", "LW", "PM", "TX", "FR", "AA", "FM", "SBL", "SBR", "AFM", "APM", "ATX", "AAA"]

username = "21861061"
pword = "Monday12"
driver.get("https://portal.accaglobal.com/")
time.sleep(6)
user_field = driver.find_element(By.ID, value="signInName")
password_field = driver.find_element(By.ID, value="password")
submit_button = driver.find_element(By.ID, value="next")
user_field.send_keys(username)
password_field.send_keys(pword)
submit_button.click()
time.sleep(2)

driver.get("https://portal.accaglobal.com/tpweb/faces/page/secure/tuitionprovider/tp_common/EnterStudentDetails/XXTPStudentDetailsVO1Table.jspx;jsessionid=e89e47ace6b0910e86cf36671bda9ba2a0f28531d8db1104a0d851e76e7c82e2.e34Nah4LbNaLci0Lc3qKc38MbhyOe6fznA5Pp7ftnR9Jrl0")
time.sleep(4)
open_papers = driver.find_element(By.ID, value="XXTPStudentDetailsVO1ToMasterStudentEntryVO1Button")
open_papers.click()
time.sleep(1)

r = pd.read_csv("../../Downloads/Add ALP name - J25 AC.csv")
for i in r[40:82].iterrows():
    reg = i[1]["Reg Number *"]
    name = i[1]["Student Surname *"] + " " + i[1]["Student First Name"]
    date = datetime.strptime(i[1]["Date of Birth"], "%m/%d/%Y").strftime("%d-%b-%Y")
    print(reg, name, date)
    to_remove = []

    reg_no = driver.find_element(By.ID, value="MasterStudentEntryVO1Partynumber")
    reg_no.clear()
    reg_no.send_keys(reg)
    names = driver.find_element(By.ID, value="MasterStudentEntryVO1Partyname")
    names.clear()
    names.send_keys(name)
    bd = driver.find_element(By.ID, value="MasterStudentEntryVO1DateOfBirth")
    bd.clear()
    bd.send_keys(date)

    for m in nums:
        driver.find_element(By.ID, value=f"ACCAQUALVO1Table:{m}:ACCAQUALVO1DlExists").click()
    for j in range(3):
        course = i[1][f"Exam {j+1}"]
        if not isinstance(course, str):
            continue
        digit = papers.index(course)
        an_id = f"ACCAQUALVO1Table:{digit}:ACCAQUALVO1DlExists"
        pick_it = driver.find_element(By.ID, value=an_id)
        pick_it.click()
        to_remove.append(i[1][f"Exam {j+1}"])

    save = driver.find_element(By.XPATH, value='//*[@id="pageButtons"]/tbody/tr/td[1]/button')
    save.click()
    time.sleep(2)
    output = driver.find_element(By.CLASS_NAME, value="x53")

    if output.text == "- Data Saved Successfully":
        with open("passed.txt", mode="a") as fp:
            fp.write(f"\n{reg}, {name}, {date}, {to_remove} {output.text}")
    else:
        with open("failed.txt", mode="a") as fp:
            fp.write(f"\n{reg}, {name}, {date}, {to_remove} {output.text}")
    nums = [papers.index(n) for n in to_remove]
    print(output.text)
    time.sleep(5)