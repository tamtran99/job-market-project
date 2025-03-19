from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time




# Khởi tạo trình duyệt
driver = webdriver.Chrome()

# Thông tin đăng nhập
email = "congtamtran1410@gmail.com"
password = "@Tam123456"
search_query = "Data Analyst"

# Mở LinkedIn Login
driver.get("https://www.linkedin.com/login")
time.sleep(2)

# Đăng nhập
driver.find_element(By.ID, 'username').send_keys(email)
time.sleep(1)
driver.find_element(By.ID, 'password').send_keys(password)
time.sleep(1)
driver.find_element(By.XPATH, '//*[@id="organic-div"]/form/div[4]/button').click()
time.sleep(5)

# Tìm ô tìm kiếm
search_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search"]'))
)

# Nhập từ khóa tìm kiếm và tìm kiếm
search_field.send_keys(search_query)
time.sleep(2)
search_field.send_keys(Keys.RETURN)
time.sleep(5)

# Chuyển sang tab "Jobs" (Công việc)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//button[text()='Jobs']"))
).click()
time.sleep(5)


job_title = driver.find_element(By.XPATH, '//a[contains(@class, "ember-view")]').text
print(job_title) 



print(job_title)
