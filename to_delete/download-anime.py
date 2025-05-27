from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime

base_url = "https://animepahe.ru/anime/d58fc9f8-582e-fdf0-3618-112cd54ed5ab"
start_page = 30
# start_episode = 212
start_episodes = [i for i in range(241, 259)]
exceptions = [242]
go_back_one = False

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(chrome_options)

retry_limit = 3  # Max retries per episode
retry_counts = {}

j = 0
while j < len(start_episodes):
    if start_episodes[j] in exceptions:
        continue
    start_episode = start_episodes[j]
    driver.get(f"{base_url}?page={start_page}")
    time.sleep(10)
    print(f"Trying episode {start_episode}")
    try:
        episodes = driver.find_elements(By.CLASS_NAME, value="episode-wrap")
    # print(episodes)
    # print(driver.find_element(By.TAG_NAME, "a"))
        link_text = [i.find_element(By.TAG_NAME, value="a").text for i in episodes]
        links = [i.find_element(By.TAG_NAME, value="a").get_attribute("href") for i in episodes]
    # try:
        max_page_ep = int(link_text[0].split()[2])
    # except Exception as e:
    #     go_back_one = True
        # driver.refresh()
        # continue
        ep_position = (max_page_ep - start_episode)

        driver.get(links[ep_position])
        for i in range(3):
            time.sleep(1)
            download_btn = driver.find_element(By.ID, value="downloadMenu")
            try:
                download_btn.click()
            except Exception as e:
                print(f"INterc3eption: {e}")
                driver.refresh()
            else:
               break
        download_link = driver.find_element(By.PARTIAL_LINK_TEXT, value="HorribleSubs · 720p")

        driver.get(download_link.get_attribute("href"))
        time.sleep(4)
        "pl-5e665a97aec27d3d9d2ec573a80ea0bf__close"
        for i in range(3):
            try:
                continue_btn = driver.find_element(By.LINK_TEXT, value="Continue")
                # continue_btn.click()
                final_link = continue_btn.get_attribute("href")
                driver.get(final_link)
            except Exception as e:
                time.sleep(2)
                print(driver.find_element(By.TAG_NAME, value="h1"))
                print(f"Error: {e}")
            else:
                time.sleep(3)
                break
        for i in range(3):
            try:
                final_btn = driver.find_element(By.XPATH, value='//*[@title="Sorry for the ads, we really need them to pay server bills and to keep the site up!"]')
                final_btn.click()
            except Exception as e:
                time.sleep(1)
            else:
                break
    except Exception as e:
        print(f"❌ Error downloading episode {start_episode}: {e}")
        retry_counts[start_episode] = retry_counts.get(start_episode, 0) + 1

        if retry_counts[start_episode] >= retry_limit:
            print(f"⚠️ Skipping episode {start_episode} after {retry_limit} failed attempts.")
            j += 1  # Give up on it
        else:
            print(f"🔁 Will retry episode {start_episode}")
            # i stays the same — this episode will be retried
    else:
        print(f"✅ Downloaded episode {start_episode}")
        j += 1
        time.sleep(1000)

# for i in link_text:
print(retry_counts)
# for j in links:
#     print(j)
# print([max_page_ep, ep_position])
