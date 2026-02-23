import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

# Constants for the test (these should be parameterized/configured as needed)
DASHBOARD_URL = "https://your-app-url.com/dashboard"
USERNAME = "auditee_user"
PASSWORD = "secure_password"
APPROACHING_THRESHOLD_DAYS = 7  # Example threshold, adjust as needed

@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def login_as_auditee(driver):
    driver.get("https://your-app-url.com/login")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "login-button").click()
    # Wait for dashboard to load
    WebDriverWait(driver, 10).until(
        EC.url_contains("/dashboard")
    )

# Utility to find issues and extract their closure dates
def get_issues_with_closure_dates(driver):
    # Locate the issue elements on the dashboard
    # This CSS selector is just an example; update as per your app
    issues = driver.find_elements(By.CSS_SELECTOR, ".issue-row")
    issue_data = []
    for issue in issues:
        # Extract closure date (update selector as per real app)
        closure_date_str = issue.find_element(By.CSS_SELECTOR, ".closure-date").text
        # Parse closure date (update format as needed)
        try:
            closure_date = datetime.strptime(closure_date_str, "%Y-%m-%d")
        except ValueError:
            # If format is different, handle accordingly
            continue
        # Check if the issue is visually highlighted (e.g., has a warning class or icon)
        is_highlighted = 'highlight' in issue.get_attribute('class') or \
                         len(issue.find_elements(By.CSS_SELECTOR, '.overdue, .approaching')) > 0
        issue_data.append({
            'element': issue,
            'closure_date': closure_date,
            'is_highlighted': is_highlighted
        })
    return issue_data

@pytest.mark.usefixtures("login_as_auditee")
def test_issues_with_non_approaching_closure_dates_not_highlighted(driver):
    """
    Ensure that issues with closure dates not approaching or overdue are not highlighted.
    Preconditions:
      - User is logged in as an Auditee.
      - Dashboard contains issues with closure dates more than the 'approaching' threshold in the future.
    Steps:
      1. Navigate to the dashboard.
      2. Identify issues with closure dates greater than the 'approaching' threshold (e.g., today + 15 days).
    Expected:
      - None of these issues should be visually highlighted as 'approaching' or 'overdue'.
    """
    driver.get(DASHBOARD_URL)
    # Wait for dashboard issue list to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".issue-row"))
    )
    issue_data = get_issues_with_closure_dates(driver)
    today = datetime.today().date()
    for issue in issue_data:
        closure_date = issue['closure_date'].date()
        delta = (closure_date - today).days
        # Only check issues with closure dates greater than the 'approaching' threshold
        if delta > APPROACHING_THRESHOLD_DAYS:
            assert not issue['is_highlighted'], (
                f"Issue with closure date {closure_date} is incorrectly highlighted "
                f"(should not be highlighted when >{APPROACHING_THRESHOLD_DAYS} days in future)"
            )