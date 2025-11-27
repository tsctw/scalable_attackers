import requests

from metrics import METRICS
from ocr.base64_to_png import base64_to_png
from ocr.classify import classify_image

def solve_captcha():
    client = requests.Session()
    
    session = client.post("http://127.0.0.1:5000/start_session", headers={"X-Forwarded-For": "8.8.8.8"}).json()
    # print(session)
    session_id = session["session_id"]
    # print(session_id)

    captcha1 = client.get(f"http://localhost:5055/get_challenge?sessionId={session_id}").json()
    print(captcha1)

    target_list = []

    for elem in captcha1['randomLetters']:
        target_list.append(elem['letter'])


    target = ''.join(target_list)

    # generate png file
    base64_to_png(captcha1["captcha"], 'output.png')

    target = classify_image("test", "symbols.txt", "output.png")

    print(target)
    

    # ---------------------------
    verify_payload = {
        "answer": target,
        "challengeId": captcha1["challengeId"],
    }
    verify = client.post(
        f"http://localhost:5055/verify", json=verify_payload).json()
    print(verify)
    
    # ---------------------------
    main_verify_payload = {
        "session_id": session_id,
        "status": "passed",
        "metrics": METRICS
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "sec-ch-ua": '"Chromium";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
    }

    
    main_verify_res = client.post("http://127.0.0.1:5000//verify/1", json=main_verify_payload, headers=headers).json()
    print(main_verify_res)

if __name__ == "__main__":
    solve_captcha()