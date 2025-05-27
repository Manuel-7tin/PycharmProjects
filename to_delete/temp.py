# with open("temp.txt", mode="a") as fp:
#     fp.write("\navah, dddasd, sfscs")
for i in range(7):
    print(f"F{i}")
    if i == 3:
        continue
    print(f"L{i}")

episodes = [201, 202, 203, 204, 205]
retry_limit = 3  # Max retries per episode
retry_counts = {}

i = 0
while i < len(episodes):
    episode = episodes[i]
    print(f"Trying episode {episode}")

    try:
        # Try your download logic here
        # simulate_download(episode)
        if episode == 203:  # Simulate failure
            raise Exception("Download failed")

        print(f"✅ Downloaded episode {episode}")
        i += 1  # Move to next only if successful

    except Exception as e:
        print(f"❌ Error downloading episode {episode}: {e}")
        retry_counts[episode] = retry_counts.get(episode, 0) + 1

        if retry_counts[episode] >= retry_limit:
            print(f"⚠️ Skipping episode {episode} after {retry_limit} failed attempts.")
            i += 1  # Give up on it
        else:
            print(f"🔁 Will retry episode {episode}")
            # i stays the same — this episode will be retried
