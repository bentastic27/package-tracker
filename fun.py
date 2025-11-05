import valkey
r = valkey.Valkey(host='127.0.0.1', port=6379, db=0)

some_dict = {
  "this": "that",
  "what": "ever"
}

r.hset(name="somekey", mapping=some_dict)
r.keys()