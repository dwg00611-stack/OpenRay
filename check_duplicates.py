from src.common import normalize_proxy_uri, get_openray_dedup_key
proxies = [
"vless://TELEGRAM-NUFiLTER-3@nufilter.fastlynew.hosting-ip.com:80?encryption=none&type=ws&host=barayekhoda.global.ssl.fastly.net&path=%2Ftelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%3Fed%3D1024&security=none#%5BOpenRay%5D%20Dynamic-4",
"vless://TELEGRAM-NUFiLTER-3@NUFiLTER.fastlynew.hosting-ip.com:80?path=%2Ftelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%2Ctelegram-NUFiLTER%3Fed%3D1024&security=none&encryption=none&host=barayekhoda.global.ssl.fastly.net&type=ws#%5BOpenRay%5D%20Dynamic-10798"





]
for i,p in enumerate(proxies,1):
    norm = normalize_proxy_uri(p)
    key = get_openray_dedup_key(p)
    print(f"{i} norm: {norm}")
    print(f"{i} key : {key}")
print('unique keys:', len({get_openray_dedup_key(p) for p in proxies}))