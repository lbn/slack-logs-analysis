#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import argparse

from pymongo import MongoClient

def main():
    parser = argparse.ArgumentParser(description="Download Slack logs from MongoDB and save them to JSON")
    parser.add_argument("--mongo", required=True, type=str, metavar="MONGOCON", help="MongoDB connection string")
    args = parser.parse_args()

    db = MongoClient(args.mongo).get_default_database()
    messages = db.messages.find({
        "text": {"$exists": 1},
        "type": "message",
        "user_name": "danielle",
        "$or": [
            {"subtype": {"$exists": 0}},
            {"subtype": "me_message"}
        ]
    }, {"text": 1, "ts": 1, "user_name": 1, "channel_name": 1, "_id": 0})

    messages = list(messages)

    with open("danielle_messages.json", "w") as f:
        json.dump(list(messages), f)



if __name__ == "__main__":
    main()
