from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Set up the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open WhatsApp Web
driver.get('https://web.whatsapp.com')

# Locate the "Groups" tab and click it
try:
    print("Waiting for the 'Groups' tab...")
    groups_tab = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Groups']")))
    time.sleep(1)
    groups_tab.click()
    print("Clicked on the 'Groups' tab.")
except Exception as e:
    print(f"Failed to click on 'Groups' tab: {e}")
    driver.quit()
    exit()

# Process the first 10 groups
for i in range(1, 11):
    try:
        print(f"Waiting for group {i} to appear...")
        group_xpath = f"(//div[@aria-label='Chat list']//div[@tabindex='-1'])[{i}]"
        group_element = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, group_xpath)))
        group_name = group_element.text.split("\n")[0]  # Extract the group name for verification
        
        print(f"Group {i} detected: {group_name}")
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable(group_element)).click()
        print(f"Clicked on group: {group_name}")

        print("Waiting 5 minutes to allow all messages to load...")
        time.sleep(5 * 60)  # 5 minutes wait for each chat

        print("Starting to scroll through chat history with high frequency for 5 minutes...")
        scroll_duration = 5 * 60  # 5 minutes of scrolling

        start_time = time.time()
        end_time = start_time + scroll_duration
        chat_container = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'copyable-area')]"))
        )
        last_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
        
        while time.time() < end_time:
            driver.execute_script("arguments[0].scrollTop = 0;", chat_container)
            time.sleep(0.5)  # Frequent scrolling
            new_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
            
            if new_height == last_height:
                print("Reached the top of the chat history.")
                break
            
            last_height = new_height
            
        print(f"Finished loading chat history for group {i}: {group_name}")

        print("Extracting messages...")
        group_data = []
        messages = chat_container.find_elements(By.XPATH, ".//div[contains(@class, 'focusable-list-item')]")

        for message in messages:
            try:
                timestamp_element = message.find_element(By.XPATH, ".//div[contains(@class, 'copyable-text')]")
                text_element = message.find_element(By.XPATH, ".//span[contains(@class, 'selectable-text')]")
                
                timestamp = timestamp_element.get_attribute("data-pre-plain-text") if timestamp_element else "N/A"
                text = text_element.text if text_element else "N/A"
                
                group_data.append([timestamp, text])
            except Exception as e:
                print(f"Failed to extract a message: {e}")

        # Save the data to a CSV file
        if group_data:
            df = pd.DataFrame(group_data, columns=["Timestamp", "Message"])
            sanitized_group_name = group_name.replace(" ", "_").replace("/", "_")
            df.to_csv(f"{sanitized_group_name}_chat.csv", index=False)
            print(f"Exported messages for group: {group_name} to CSV")
        else:
            print("No messages found to export.")
        
        # Go back to the "Groups" list before moving to the next group
        driver.back()
        time.sleep(2)  # Give the browser a moment to load the previous screen

    except Exception as e:
        print(f"Failed to process group {i}: {e}")
        break

# Keep the browser open for you to inspect
input("Press Enter to close the browser...")

# Close the browser
driver.quit()
