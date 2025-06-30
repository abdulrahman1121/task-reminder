import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import schedule
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    filename="task_reminder.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_credentials():
    try:
        with open("email_credentials.txt", "r") as f:
            email, password = f.read().strip().split("\n")
        return email, password
    except Exception as e:
        logging.error(f"Failed to load credentials: {e}")
        raise

def send_email(to_email, subject, body):
    email, password = load_credentials()
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email, password)
            server.send_message(msg)
        logging.info(f"Email sent to {to_email}: {subject}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        raise

def check_tasks():
    try:
        # Read tasks
        tasks = pd.read_csv("tasks.csv")
        tasks["due_date"] = pd.to_datetime(tasks["due_date"])
        today = datetime.now().date()

        # Filter tasks due today or overdue
        due_tasks = tasks[tasks["due_date"].dt.date <= today]
        if due_tasks.empty:
            logging.info("No tasks due today.")
            return

        # Send email for each due task
        email, _ = load_credentials()
        for _, task in due_tasks.iterrows():
            subject = f"Task Reminder: {task['task_name']} (Priority: {task['priority']})"
            body = f"Reminder: The task '{task['task_name']}' is due on {task['due_date'].strftime('%Y-%m-%d')}.\nPriority: {task['priority']}"
            send_email(email, subject, body)
    except Exception as e:
        logging.error(f"Error checking tasks: {e}")

def main():
    logging.info("Starting task reminder automation")
    # Schedule task check daily at 8:00 AM
    schedule.every().day.at("08:00").do(check_tasks)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()