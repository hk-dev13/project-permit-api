from api.api_server import app

states = ["VA", "TX", "CA", "NY", "HI", "PR"]
limit = 3

client = app.test_client()

print("State, Status, Count, SampleState, SampleName")
for st in states:
    resp = client.get(f"/global/emissions?state={st}&limit={limit}")
    ok = resp.status_code
    try:
        data = resp.get_json()
    except Exception:
        data = None
    n = len(data.get("data", [])) if isinstance(data, dict) else 0
    sample_state = None
    sample_name = None
    if n:
        sample = data["data"][0]
        sample_state = (sample.get("extras") or {}).get("state")
        sample_name = sample.get("nama_perusahaan")
    print(f"{st}, {ok}, {n}, {sample_state}, {sample_name}")
