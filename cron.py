import json
import os
import shutil
import sys
import traceback

import crawler
import mailgun
import responder
import solution_manager
from secret import MAIL_SAVE_DIR, MAIL_HANDLED_DIR
from archiver import archive


def main(crawl=True):
    if crawl:
        crawler.fetch_all()

    # Handle incoming emails

    email_filenames = os.listdir(MAIL_SAVE_DIR)

    for email_filename in email_filenames:
        try:
            print(f"Handling {email_filename}")
            email_path = os.path.join(MAIL_SAVE_DIR, email_filename)
            with open(email_path, "r", encoding="utf8") as f:
                email_obj = json.load(f)

            text = email_obj["content"]
            subject = str(email_obj["title"])
            if not subject.startswith("Re:"):
                subject = "Re: " + subject
            scam_email = email_obj["from"]

            if "bait_email" not in email_obj:
                # Email just crawled

                if solution_manager.scam_exists(scam_email):
                    print("This crawled email has been replied, ignoring")
                    os.remove(email_path)
                    continue
                    # pass

                archive(True, scam_email, "CRAWLER", email_obj["title"], text)

                print("This email is just crawled, using random replier")
                replier = responder.get_replier_randomly()
                bait_email = solution_manager.gen_new_addr(scam_email, replier.name)
                stored_info = solution_manager.get_stored_info(bait_email, scam_email)
            else:
                bait_email = email_obj["bait_email"]
                stored_info = solution_manager.get_stored_info(bait_email, scam_email)

                if stored_info is None:
                    print(f"Cannot found replier for {bait_email}")
                    os.remove(email_path)
                    continue

                print(f"Found selected replier {stored_info.sol}")
                replier = responder.get_replier_by_name(stored_info.sol)
                if replier is None:
                    print("Replier Sol_name not found")
                    os.remove(email_path)
                    continue

            try:
                res_text = replier.get_reply_by_his(scam_email)
            except Exception as e:
                print("GENERATING ERROR")
                print(e)
                print(traceback.format_exc())
                print("Due to CUDA Error, stopping whole sequence")
                return

                # Add Signature
            res_text += f"\nBest,\n{stored_info.username}"

            send_result = mailgun.send_email(stored_info.username, stored_info.addr, scam_email, subject, res_text)
            if send_result:
                print(f"Successfully sent response to {scam_email}")

                # Move to queued
                if not os.path.exists(MAIL_HANDLED_DIR):
                    os.makedirs(MAIL_HANDLED_DIR)
                shutil.move(email_path, os.path.join(MAIL_HANDLED_DIR, email_filename))

                archive(False, scam_email, bait_email, subject, res_text)
        except Exception as e:
            print(e)
            print(traceback.format_exc())


if __name__ == '__main__':

    if os.path.exists("./lock"):
        quit(-1)

    with open("./lock", "w") as f:
        f.write("Running")

    arg_crawl = not ("--no-crawl" in sys.argv)
    main(crawl=arg_crawl)

    os.remove("./lock")
