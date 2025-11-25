import requests

from ocr.base64_to_png import base64_to_png
from ocr.classify import classify_image

def solve_captcha():
    client = requests.Session()
    
    session = client.post("http://127.0.0.1:5000/start_session").json()
    session_id = session["session_id"]
    print(session_id)

    captcha1 = client.get(f"http://localhost:5055/get_challenge?sessionId={session_id}").json()
    print(captcha1)

    # generate png file
    base64_to_png(captcha1["svgImg"], 'output.png')

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
        "user_answer": target,
        "correct_word": captcha1["randomLetters"],
        "status": "passed",
        "metrics": {
            "reaction_time_mean_ms": 1922,
            "solve_time_std_ms": 199776.04999995232,
            "interkey_interval_std_ms": 1,
            "path_entropy": 0.5751942410279781,
            "velocity_std_px_per_s": 303.39539360134313,
            "click_offset_avg_px": 161.23409208103513,
            "hover_dwell_avg_ms": 319.68499999841055,
            "backspace_count": 1,
            "solve_entropy": 199776.04999995232,
            "entry_points_unique": 66,
            "focus_change_events": 2,
            "swipe_accel_var": 1,
            "pause_variance_ms": 1,
            "pressure_std": 1,
            "fingerprint_entropy": 1,
            "overall_variance_score": 199776.04999995232
        }
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