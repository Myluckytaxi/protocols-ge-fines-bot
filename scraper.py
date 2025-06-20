
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def check_fines(car_number, tech_passport, include_media=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://protocols.ge/")
    time.sleep(4)
    try:
        driver.find_element(By.XPATH, "//button[contains(text(), 'Vehicle')]").click()
    except:
        pass
    inputs = driver.find_elements(By.CSS_SELECTOR, "input")
    if len(inputs) < 2:
        driver.quit()
        return ["❌ Не найдены поля ввода"]
    inputs[0].send_keys(car_number)
    inputs[1].send_keys(tech_passport)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Search')]").click()
    time.sleep(6)
    results = []
    fine_blocks = driver.find_elements(By.CLASS_NAME, "fineItem")
    for block in fine_blocks:
        text = block.text
        if include_media:
            photo_btn = block.find_elements(By.CLASS_NAME, "finePhotoCount")
            video_btn = block.find_elements(By.CLASS_NAME, "fineVideoBtn")
            text += f"\n📷 Фото: {photo_btn[0].text if photo_btn else '—'}"
            text += f"\n🎥 Видео: {'Есть' if video_btn else 'Нет'}"
        results.append("📋 " + text.strip())
    driver.quit()
    return results
