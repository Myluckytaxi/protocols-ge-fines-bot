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
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://protocols.ge/")

    time.sleep(4)

    # Вкладка Vehicle
    try:
        vehicle_tab = driver.find_element(By.XPATH, "//button[contains(text(), 'Vehicle')]")
        vehicle_tab.click()
    except:
        pass

    time.sleep(1)

    # Поля ввода
    inputs = driver.find_elements(By.CSS_SELECTOR, "input")
    if len(inputs) < 2:
        driver.quit()
        return ["❌ Не найдены поля ввода на сайте"]

    inputs[0].send_keys(car_number)
    inputs[1].send_keys(tech_passport)

    # Поиск
    search_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
    search_button.click()

    time.sleep(5)

    results = []
    fine_blocks = driver.find_elements(By.CLASS_NAME, "fineItem")

    for block in fine_blocks:
        try:
            text = block.text
            if include_media:
                photo_btn = block.find_elements(By.CLASS_NAME, "finePhotoCount")
                video_btn = block.find_elements(By.CLASS_NAME, "fineVideoBtn")
                text += f"\n📷 Фото: {photo_btn[0].text if photo_btn else '—'}"
                text += f"\n🎥 Видео: {'Есть' if video_btn else 'Нет'}"
            results.append(f"📋 {text.strip()}")
        except Exception as e:
            results.append(f"⚠️ Ошибка при обработке штрафа: {e}")

    driver.quit()
    return results