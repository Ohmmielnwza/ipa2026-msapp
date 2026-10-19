from app import app,routers,interface_status
from datetime import datetime,timezone,timedelta
import re
test=app.test_client()
print('LIVE WEB AND DATABASE CHECK')
print('Checked:', datetime.now(timezone.utc).isoformat())
print('Router source: DEMO; Web/RabbitMQ/Worker/MongoDB run in real containers')
print('Homepage:',test.get('/').status_code)
assert test.get('/').status_code==200
assert test.get('/router/not-an-objectid').status_code==400
print('Invalid ID: HTTP 400 — PASS')
recent=interface_status.count_documents({'source':'demo','timestamp':{'$gte':datetime.now(timezone.utc)-timedelta(minutes=5)}})
assert recent>0
print('New demo snapshots during last 5 minutes:',recent)
for r in routers.find({}, {'password':0}):
    response=test.get('/router/'+str(r['_id']))
    html=response.get_data(as_text=True)
    times=set(re.findall(r'\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+',html))
    rows=html.count('<tr>')-1
    assert response.status_code==200
    assert len(times)==3, (r.get('ip'),times)
    assert rows==12,(r.get('ip'),rows)
    assert 'Demo data' in html
    snapshots=list(interface_status.find({'router_id':r['_id'],'source':'demo'}).sort([('timestamp',-1),('_id',-1)]).limit(3))
    expected={s['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f') for s in snapshots}
    assert times==expected
    print(r.get('ip'),': HTTP 200 / latest 3 snapshots / 12 interface rows / DEMO label — PASS')
print('All live checks passed.')
