import requests

def solve_captcha():
    
    sess = requests.post("http://127.0.0.1:5000/start_session").json()
    session_id = sess["session_id"]

    captcha1 = requests.get(f"http://localhost:5055/get_challenge?sessionId={session_id}").json()

    attempt_info = requests.get(
        f"http://127.0.0.1:5000/get_challenge/1?session_id={session_id}"
    ).json()

    print(attempt_info)
    

    main_verify_payload = {
        "correct_word": captcha1["word"],
        "session_id": session_id,
        "status": "passed",
        "user_answer": captcha1["word"]
    }
    
    main_verify_res = requests.post("http://127.0.0.1:5000//verify/1", json=main_verify_payload).json()
    print(main_verify_res)


    # captcha1_verify_payload = {
    #     "challengeId": captcha1["challengeId"],
    #     "answer": captcha1["word"]
    # }
    # res = requests.post("http://localhost:5055/verify", json=captcha1_verify_payload)
    # print(res)


if __name__ == "__main__":
    solve_captcha()