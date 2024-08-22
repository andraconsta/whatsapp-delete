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

# Wait for the first group to appear and click on it
try:
    print("Waiting for the first group to appear...")
    first_group = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "(//div[@aria-label='Chat list']//div[@tabindex='-1'])[1]")))
    group_name = first_group.text.split("\n")[0]  # Extract the group name for verification
    
    print(f"First group detected: {group_name}")
    first_group.click()
    print(f"Clicked on group: {group_name}")

    print("Waiting for 'Syncing older messages' to complete...")
    WebDriverWait(driver, 300).until_not(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Syncing older messages')]")))
    print("Syncing completed.")

    print("Waiting for the chat container to load...")
    chat_container = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'copyable-area')]"))
    )
    print("Chat container located.")

    print("Starting to scroll through chat history with high frequency...")
    start_time = time.time()
    end_time = start_time + 3 * 60  # 3 minutes
    last_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
    
    while time.time() < end_time:
        driver.execute_script("arguments[0].scrollTop = 0;", chat_container)
        time.sleep(0.5)  # Frequent scrolling
        new_height = driver.execute_script("return arguments[0].scrollHeight", chat_container)
        
        if new_height == last_height:
            print("Reached the top of the chat history.")
            break
        
        last_height = new_height
        
    print("Finished loading chat history for group:", group_name)

    print("Extracting messages...")
    group_data = []
    messages = chat_container.find_elements(By.XPATH, ".//div[contains(@class, 'focusable-list-item')]")

    for message in messages:
        try:
            timestamp = message.find_element(By.XPATH, ".//div[contains(@class, 'copyable-text')]").get_attribute("data-pre-plain-text")
            text = message.find_element(By.XPATH, ".//span[contains(@class, 'selectable-text')]").text
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

except Exception as e:
    print(f"Failed to process group: {e}")

# Keep the browser open for you to inspect
input("Press Enter to close the browser...")

# Close the browser
driver.quit()
