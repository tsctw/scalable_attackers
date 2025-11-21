# html = parse('index.html')
# analyze(html)
# select class=progress
# inject the correct answer
# select one of the falling word
# enable verify button

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException


def getFallingWordCaptcha(driver):
    driver.refresh()
    # time.sleep(1) is used here as a pause to wait for the component to update.
    time.sleep(1)

    #  Locate start button and click
    startButton = driver.find_element(By.ID, "start-btn")
    actions = ActionChains(driver)
    actions.move_to_element(startButton)
    actions.click().perform()
    
    time.sleep(1)

    # On the Captcha page (don't know which one)
    elements = driver.find_elements(By.ID, "target-word")
    return elements

# --- CAPTCHA Solving Logic Function ---
def solve_falling_words_captcha(driver):
    print("Inside solve falling words")

    try:
        # 1. Wait for CAPTCHA container to load
        elements = getFallingWordCaptcha(driver)
        # if it is not falling words captcha, fresh the page until it is
        while len(elements) == 0:
            elements = getFallingWordCaptcha(driver)
        
        target = elements[0].text
        print(f"Target captcha is: {target}")

        while len(target) > 0:
            time.sleep(0.1)
            print("I'm here, first loop")
            letter_elems = driver.find_elements(By.CLASS_NAME, "falling-letter")

            letters = []
            for elem in letter_elems:
                try:
                    letter = elem.text
                    top = float(elem.value_of_css_property("top").replace("px", ""))
                    letters.append((top, letter, elem))
                except:
                    continue

            if not letters:
                time.sleep(0.1)
                continue

            letters.sort(key=lambda x: x[0], reverse=True)

            for top, letter, elem in letters:
                if letter == target[0]:
                    print(f"Found {letter} at top={top}, clicking...")

                    target = target[1:]

                    try:
                        elem.click()
                        progress = driver.find_element(By.ID, "progress")
                        print(f"Progress text: {progress.text}")
                        break
                    except StaleElementReferenceException:
                        print("Element gone before click. Retrying...")
                        break
                    except ElementClickInterceptedException:
                        print("Click blocked by overlay, retrying...")
                        break 

        # if progress is not done, fill random characters and verify and go to next round
        progress = driver.find_element(By.ID, "progress").text
        print(progress)
        progress_clean = progress.replace(" ", "").replace("_", "")
        print(progress_clean)
        target = elements[0].text
        while len(progress_clean) != len(target):
            time.sleep(1)
            print("I'm here, second loop")
            print(len(progress_clean))
            progress = driver.find_element(By.ID, "progress").text
            progress_clean = progress.replace(" ", "").replace("_", "")
            letter_elems = driver.find_elements(By.CLASS_NAME, "falling-letter")
            try:
                letter_elems[0].click()
            except StaleElementReferenceException:
                print("Element gone before click. Retrying...")
            except ElementClickInterceptedException:
                print("Click blocked by overlay, retrying...")
        
        time.sleep(1)
        verify_btn = driver.find_element(By.ID, "final-verify-btn")

        if verify_btn.is_enabled() and verify_btn.get_attribute("disabled") is None:
            print("Verify button enabled → clicking")
            try:
                verify_btn.click()
            except:
                return
        else:
            print("Verify button disabled")

        
    except Exception as e:
        print(f"A severe error occurred during the solution attempt: {e}")

def start_captcha(driver, url):
    print("Navigating and attempting to solve CAPTCHA...")
    driver.get(url)

    result_elems = driver.find_elements(By.ID, "resolve-btn")

    print(result_elems)
    # Get result page
    while len(result_elems) == 0:
        try:
            solve_falling_words_captcha(driver)
            time.sleep(1)
            result_elems = driver.find_elements(By.ID, "captcha-container")
            print("Get result")
            break
        except Exception as e:
            print(f"A severe error occurred during the solution attempt: {e}")

# --- Main Program Execution Block ---
if __name__ == "__main__":
    
    # *** CHANGE THIS: Replace with your local development server URL ***
    TARGET_URL = "http://127.0.0.1:5000/"
    
    # Initialize WebDriver
    driver = webdriver.Chrome()
    
    # Set a variable to control how long the browser stays open
    KEEP_BROWSER_OPEN_SECONDS = 600 # Set the number of seconds you want the browser to remain open
    
    try:
        # Run the solution function
        start_captcha(driver, TARGET_URL)

        # ----------------------------------------------------
        # 🌟 Key Modification 🌟
        # ----------------------------------------------------
        if KEEP_BROWSER_OPEN_SECONDS > 0:
            print(f"\nOperations complete. Keeping browser open for {KEEP_BROWSER_OPEN_SECONDS} seconds for observation...")
            time.sleep(KEEP_BROWSER_OPEN_SECONDS) 
        
    except Exception as overall_error:
        print(f"\nA main thread error occurred: {overall_error}")
        
    finally:
        # Ensure the browser is closed regardless of error
        driver.quit()
        print("\nSelenium browser closed.")
