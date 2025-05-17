from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# Pattern Settings
USER_MACHINE = "gamep"
PATH_TO_WEBDRIVER = "C:/WebDrivers/yandexdriver.exe"
SEARCHING_KEY = "портал НИЯУ МИФИ"
EXPECTED_RESOURCES = "https://home.mephi.ru/"
NUMBER_OF_RESOURCES_CHECKED = 7


def handle_captcha(driver):
    def is_captcha_visible():
        try:
            return any([
                "Подтвердите, что запросы отправляли вы, а не робот" in driver.page_source,
                "Нажмите в таком порядке" in driver.page_source,
                len(driver.find_elements(By.CSS_SELECTOR, "iframe[src*='captcha']")) > 0,
                "SmartCaptcha by Yandex Cloud" in driver.page_source
            ])
        except:
            return False

    if not is_captcha_visible():
        return True

    print("\n=== ОБНАРУЖЕНА КАПЧА ===")
    print("Пожалуйста, решите капчу вручную в браузере...")

    initial_captcha_state = is_captcha_visible()

    start_time = time.time()
    while time.time() - start_time < 300:
        current_captcha_state = is_captcha_visible()

        if current_captcha_state != initial_captcha_state:
            print("Обнаружено взаимодействие с капчей...")
            initial_captcha_state = current_captcha_state

        if not current_captcha_state:
            print("Капча успешно решена!")
            return True

        print(f"Ожидание решения капчи... Прошло {int(time.time() - start_time)} сек")
        time.sleep(5)

    if is_captcha_visible():
        print("Превышено время ожидания решения капчи (5 минут)")
        return False

    return True


def check_links(driver, expected_url, max_links=5):
    def get_clean_urls(results):
        urls = []
        for result in results:
            try:
                link = result.find_element(By.CSS_SELECTOR, "a[href]:not([role='button'])")
                url = link.get_attribute("href")
                if url:
                    clean_url = url.split('?')[0].split('#')[0]
                    urls.append(clean_url)
            except:
                continue
            if len(urls) >= max_links:
                break
        return urls

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.serp-item"))
        )

        search_results = driver.find_elements(By.CSS_SELECTOR, "li.serp-item")[:max_links * 2]
        clean_urls = get_clean_urls(search_results)

        print(f"\nПроверяем первые {len(clean_urls)} результатов:")
        match_position = None

        for i, url in enumerate(clean_urls, 1):
            print(f"{i}. {url}")
            if expected_url in url:
                print(f"  ✓ Найдено совпадение с {expected_url}")
                match_position = i
                break

        if match_position:
            print(f"\nИтог: совпадение найдено в позиции {match_position}")
            return clean_urls[match_position - 1]
        else:
            print("\nИтог: совпадений не найдено")
            return None

    except Exception as e:
        print(f"\nОшибка при проверке результатов: {str(e)}")
        return None

options = Options()
options.binary_location = f"C:/Users/{USER_MACHINE}/AppData/Local/Yandex/YandexBrowser/Application/browser.exe"

service = Service(executable_path=PATH_TO_WEBDRIVER)
driver = webdriver.Chrome(service=service, options=options)

try:
    print("Открываем Яндекс...")
    driver.get("https://ya.ru")
    if not handle_captcha(driver):
        print("Не удалось решить капчу. Продолжение невозможно.")
        input("Нажмите Enter для закрытия браузера...")
        exit()

    print("\nВыполняем поиск...")
    search_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "text"))
    )
    search_box.clear()
    search_box.send_keys(SEARCHING_KEY)
    search_box.send_keys(Keys.RETURN)
    if not handle_captcha(driver):
        print("Не удалось решить капчу. Продолжение невозможно.")
        input("Нажмите Enter для закрытия браузера...")
        exit()

    expected_url = EXPECTED_RESOURCES
    time.sleep(3)
    found_url = check_links(driver, EXPECTED_RESOURCES, NUMBER_OF_RESOURCES_CHECKED)

    if found_url:
        print(f"\nОткрываем найденную ссылку: {found_url}")
        driver.get(found_url)
    else:
        print(f"\nОткрываем ожидаемый URL напрямую: {expected_url}")
        driver.get(expected_url)

except Exception as e:
    print(f"\nПроизошла ошибка: {str(e)}")

finally:
    input("Нажмите Enter для закрытия браузера...")
    driver.quit()