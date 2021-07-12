def test_req_1(api):
    api.get("https://httpbin.org/get")
    api.post("https://httpbin.org/get")
    api.put("https://httpbin.org/get")


def test_req_2(api):
    api.get("https://httpbin.org/post")
    api.post("https://httpbin.org/post")
    api.put("https://httpbin.org/post")


def test_req_3(api):
    api.get("https://httpbin.org/put")
    api.post("https://httpbin.org/put")
    api.put("https://httpbin.org/put")
