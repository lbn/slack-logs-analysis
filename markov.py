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
    text = text.replace(",", "")
    text = text.replace(".", " "+END)
    text = text.replace("?", " "+END)
    text = text.replace("!", " "+END)

    return text.lower()

START = "<^>"
END = ">^<"

from collections import namedtuple

NextGram = namedtuple("NextGram", "grams probs")

KEY_CONN = "===="
def get_tuples(words, k=2):
    cache = [START]*k
    for word in words:
        yield(tuple(cache), word)
        cache = cache[1:] + [word]

class MarkovGenerator(object):
    def __init__(self):
        self.n = 2

    def train(self, messages):
        words = {}
        for msg in messages:
            # words in this sentence
            local_words = msg.split()
            # prepend START and append END symbols
            local_words.append(END)
            for previous, this in get_tuples(local_words, k=self.n):
                if previous not in words:
                    words[previous] = []
                words[previous].append(this)

        def calc_next(this_gram):
            nexts = words[this_gram]
            c = Counter(nexts)
            next_grams = list(c.keys())
            next_probs = [c[g] for g in next_grams]
            next_probs = [float(v)/len(next_probs) for v in next_probs]
            return NextGram(grams=next_grams, probs=next_probs)

        self.probs = {gram: calc_next(gram) for gram in words}

    def generate(self, n=5):
        def next_gram(this_gram, allow_end=False):
            return choice(self.probs[this_gram].grams, 1, self.probs[this_gram].probs)[0]
        for j in range(n):
            sentence = [START]*self.n
            gram = next_gram((START,)*self.n)
            for i in range(100):
                sentence.append(gram)
                gram_ = next_gram(tuple(sentence[-self.n:]),allow_end=i<10-1)
                if gram_ == END:
                    break
                gram = gram_

            yield " ".join(sentence[self.n:])


def main():
    probs = {}
    words = {}
    with open("danielle_messages.json") as f:
        js = json.load(f)
        messages = [clean(msg) for msg in js]
        messages = [msg for msg in messages if len(msg.split()) > 4]
        mg = MarkovGenerator()
        mg.train(messages)

        for msg in mg.generate(1000):
            print(msg)

if __name__ == "__main__":
    main()
