import urllib.request
from http.cookiejar import CookieJar

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

routes = ['/', '/timeline', '/reports']
for r in routes:
    try:
        res = opener.open(f'http://127.0.0.1:5000{r}')
        print(f'{r}: {res.code}')
    except Exception as e:
        print(f'{r}: ERROR {e}')
