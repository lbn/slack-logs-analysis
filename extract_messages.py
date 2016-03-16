import json
import re
from collections import Counter
from numpy.random import choice

users = {}
with open("users.json") as f:
    for user_s in f.readlines():
        user = json.loads(user_s)
        if "real_name" in user:
            users[user["id"]] = user["real_name"]

re_user = re.compile(r"<@(U[A-Z0-9]+)>")

def resolve_user(uid):
    if uid in users:
        return users[uid]
    return "butt"

def clean(msg):
    text = msg["text"]
    # Resolve users
    text = re.sub(re_user, lambda m: resolve_user(m.group(1)), text)
    if "```" in text:
        return ""
    if "<http" in text:
        return ""
    if "`" in text:
        return ""

    text = text.replace("’", "'")

    return text.lower()

START = "<^>"
END = ">^<"

from collections import namedtuple

NextGram = namedtuple("NextGram", "grams probs")


def main():
    probs = {}
    words = {}
    with open("danielle_messages.json") as f:
        js = json.load(f)
        messages = [clean(msg) for msg in js]
        messages = [msg for msg in messages if len(msg.split()) > 4]
        for msg in messages:
            local_words = msg.split()
            local_words.insert(0, START)
            local_words.append(END)
            for i in range(len(local_words)-2):
                index = local_words[i]
                if index not in words:
                    words[index] = []
                words[index].append(local_words[i+1])

                index = local_words[i]+"===="+local_words[i+1]
                if index not in words:
                    words[index] = []
                words[index].append(local_words[i+2])

            index = local_words[-2]
            if index not in words:
                words[index] = []
            words[index].append(local_words[-1])


        def calc_next(this_gram):
            nexts = words[this_gram]
            c = Counter(nexts)
            next_grams = list(c.keys())
            next_probs = [c[g] for g in next_grams]
            next_probs = [float(v)/len(next_probs) for v in next_probs]
            return NextGram(grams=next_grams, probs=next_probs)

        probs = {this_gram: calc_next(this_gram) for this_gram in words}

        def next_gram(this_gram, allow_end=False):
            return choice(probs[this_gram].grams, 1, probs[this_gram].probs)[0]


        for j in range(10000):
            sentence = []
            gram = next_gram(START)
            for i in range(20):
                sentence.append(gram)
                gram_ = next_gram("====".join(sentence[-2:]),allow_end=i<10-1)
                if gram_ == END:
                    break
                gram = gram_

            print(" ".join(sentence))

if __name__ == "__main__":
    main()
