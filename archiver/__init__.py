from secret import MAIL_ARCHIVE_DIR
import os
import time


def archive(is_inbound, scam_email, bait_email, subject, body):
    archive_name = scam_email + ".txt"

    archive_content = \
        f'\n# {"Inbound" if is_inbound else "Outbound"}\n' \
        f'FROM: {scam_email if is_inbound else bait_email}\n' \
        f'To: {bait_email if is_inbound else scam_email}\n' \
        f'SUBJECT: {subject}\n' \
        f'TIME: {int(time.time())}\n' \
        f'\n{body}\n'

    if not os.path.exists(MAIL_ARCHIVE_DIR):
        os.makedirs(MAIL_ARCHIVE_DIR)

    with open(f"{MAIL_ARCHIVE_DIR}/{archive_name}", "a", encoding="utf8") as f:
        f.write(archive_content)

    # Save conversation history

    history_filename = scam_email + ".his"

    if is_inbound:
        his_content = "[scam_start]\n" + body + "\n[scam_end]\n"
    else:
        his_content = "[bait_start]\n" + body + "\n[bait_end]\n"

    with open(os.path.join(MAIL_ARCHIVE_DIR, history_filename), "a", encoding="utf8") as f:
        f.write(his_content)

    print(f"Archive for {scam_email} completed")
