from responder import get_replier_randomly, get_replier_by_name

for _ in range(100):
    print(get_replier_by_name("Template").get_reply("test"))
