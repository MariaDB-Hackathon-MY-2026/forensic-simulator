import urllib.request
import urllib.parse
from http.cookiejar import CookieJar
import json
import base64
import zlib
import re

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), NoRedirectHandler())

# 1. Trigger Deletion on student STU001
req = urllib.request.Request('http://127.0.0.1:5000/scenario/delete_student', data=urllib.parse.urlencode({'student_id': 'STU001'}).encode())
try:
    res = opener.open(req)
except urllib.error.HTTPError as e:
    res = e

# 2. Get backups
res = urllib.request.urlopen('http://127.0.0.1:5000/recovery')
html = res.read().decode()
matches = re.findall(r'<input type=\"hidden\" name=\"backup_id\" value=\"(\d+)\">', html)
print('Backups generated:', matches[:3] if matches else None)

# 3. If we restore the first backup (which might be a record, not the student)
if len(matches) > 0:
    # let's just see what the backups are
    tables = re.findall(r'<span class="backup-table-badge">(.*?)</span>', html)
    print('Backup tables in order:', tables[:3])

