"""fal のキュー方式の小さな呼び出し口（標準ライブラリだけ）。
キーはこの環境のプロキシが付けるので、ここでは Authorization を付けない。
投げる → 返ってきた status_url を待つ → response_url から結果を受け取る（URL は手で組まない）。"""
import base64, json, mimetypes, os, ssl, sys, time, urllib.request, urllib.error

CA = os.environ.get('SSL_CERT_FILE') or ('/root/.ccr/ca-bundle.crt' if os.path.exists('/root/.ccr/ca-bundle.crt') else None)
CTX = ssl.create_default_context(cafile=CA) if CA else ssl.create_default_context()


def _req(url, data=None, method=None, timeout=120):
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, method=method or ('POST' if body else 'GET'),
                               headers={'Content-Type': 'application/json'} if body else {})
    for i in range(5):
        try:
            with urllib.request.urlopen(r, context=CTX, timeout=timeout) as res:
                return json.loads(res.read() or b'{}')
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='ignore')[:600]
            if e.code in (429, 500, 502, 503, 504) and i < 4:
                time.sleep(2 ** (i + 1)); continue
            raise RuntimeError(f'HTTP {e.code} {url}: {msg}')
        except (urllib.error.URLError, TimeoutError) as e:
            if i < 4:
                time.sleep(2 ** (i + 1)); continue
            raise


def data_uri(path):
    mt = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    if path.endswith('.m4a'):
        mt = 'audio/mp4'
    return f'data:{mt};base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def run(endpoint, args, poll=1.5, limit=900):
    sub = _req(f'https://queue.fal.run/{endpoint}', args)
    t0 = time.time()
    while True:
        st = _req(sub['status_url'])
        if st.get('status') == 'COMPLETED':
            return _req(sub['response_url'])
        if time.time() - t0 > limit:
            raise RuntimeError(f'timeout {endpoint} {sub.get("request_id")}')
        time.sleep(poll)


def download(url, path):
    with urllib.request.urlopen(urllib.request.Request(url), context=CTX, timeout=120) as res, open(path, 'wb') as f:
        f.write(res.read())
    return path


if __name__ == '__main__':
    print(json.dumps(run(sys.argv[1], json.loads(sys.argv[2])), ensure_ascii=False, indent=1))
