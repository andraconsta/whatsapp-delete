# whatsapp-delete
This script automates the process of scrolling through WhatsApp group chats, extracting chat history, and identifying inactive users who have not participated in the group for over two months, with the goal of assisting in their removal from the group

---

# WhatsApp Group Chat Cleanup

This Python script automates the process of managing WhatsApp group chats by identifying and exporting chat history. The primary goal is to assist in identifying inactive users who have not participated in group chats for over two months, allowing for their removal from the group.

## Features

- **Automated Scrolling:** The script automatically scrolls through WhatsApp group chat history for 5 minutes to load as much content as possible.
- **Message Extraction:** After scrolling, the script extracts the messages from the chat history.
- **Export to CSV:** All extracted messages are saved to a CSV file for easy review and analysis.

## Prerequisites

- Python 3.x
- Selenium
- WebDriver Manager for Python (`webdriver_manager`)
- Pandas

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/andraconsta/whatsapp-delete.git
   cd whatsapp-delete
