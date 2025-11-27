# html = parse('index.html')
# analyze(html)
# select class=progress
# inject the correct answer
# select one of the falling word
# enable verify button

import time
import re
from ocr.base64_to_png import base64_to_png
from ocr.classify import classify_image
import uuid
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

    img = driver.find_element(By.ID, "captcha-canvas")
    img_64 = img.get_attribute("src")


    # generate png file
    base64_to_png(img_64, 'output.png', 260, 80)

    target = classify_image("test", "symbols.txt", "output.png")
    return target

# --- CAPTCHA Solving Logic Function ---
def solve_falling_words_captcha(driver):
    print("Inside solve falling words")

    try:
        # 1. Wait for CAPTCHA container to load
        question_text = getFallingWordCaptcha(driver)
        # if it is not falling words captcha, fresh the page until it is
        while len(question_text) == 0:
            question_text = getFallingWordCaptcha(driver)

        target = question_text        
        print(f"Target captcha is: {target}")

        while len(target) > 0:
            time.sleep(0.5)
            letter_elems = driver.find_elements(By.CLASS_NAME, "falling-letter")

            for elem in letter_elems:
                try:
                    img_64 = elem.get_attribute("src")
                except StaleElementReferenceException:
                    continue  # reselect element, non-stop

                base64_to_png(img_64, "char.png", 60, 60)
                letter = classify_image("test_char", "symbols.txt", "char.png")
                print(letter)

                # get the latest elem then click
                if letter == target[0]:
                    try:
                        fresh_elements = driver.find_elements(By.CLASS_NAME, "falling-letter")
                        for fresh in fresh_elements:
                            if fresh.get_attribute("src") == img_64:
                                fresh.click()
                                target = target[1:]
                                break
                    except:
                        continue
                    break


        # if progress is not done, fill random characters and verify and go to next round
        progress = driver.find_element(By.ID, "progress").text
        progress_clean = progress.replace(" ", "").replace("_", "")
        print(progress_clean)
        target = question_text
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

    solve_falling_words_captcha(driver)

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
