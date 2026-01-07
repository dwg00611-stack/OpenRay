from src.common import normalize_proxy_uri, get_openray_dedup_key
proxies = [
    "trojan://.+QAJot50sDi6mvb@5.188.108.13:11790/?type=tcp&security=tls&sni=runningshoes.purpletornado.click#%5BOpenRay%5D%20%F0%9F%87%B5%F0%9F%87%B1%20PL-104",
    "trojan://.+QAJot50sDi6mvb@5.188.108.13:11790?security=tls&sni=runningshoes.purpletornado.click&type=tcp&path=/#%5BOpenRay%5D%20%F0%9F%87%B5%F0%9F%87%B1%20PL-106"
]
for i,p in enumerate(proxies,1):
    norm = normalize_proxy_uri(p)
    key = get_openray_dedup_key(p)
    print(f"{i} norm: {norm}")
    print(f"{i} key : {key}")
print('unique keys:', len({get_openray_dedup_key(p) for p in proxies}))