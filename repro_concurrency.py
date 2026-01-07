import sys
import os
import concurrent.futures
import time

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from net import validate_with_v2ray_core
from constants import V2RAY_CORE_PATH

def test_single_proxy(uri):
    start = time.time()
    res = validate_with_v2ray_core(uri, timeout_s=15)
    end = time.time()
    return res, end - start

if __name__ == "__main__":
    if not V2RAY_CORE_PATH or not os.path.exists(V2RAY_CORE_PATH):
        print(f"Xray core not found at {V2RAY_CORE_PATH}")
        sys.exit(1)
        
    # A sample public proxy URI (might be dead, but we want to see if it even tries)
    # Using a dummy one just to test the process spawning logic
    test_uri = "vless://00000000-0000-0000-0000-000000000000@1.2.3.4:443?encryption=none&security=tls&type=tcp#Test"
    
    print(f"Starting concurrency test with {V2RAY_CORE_PATH}")
    concurrency = 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(test_single_proxy, test_uri) for _ in range(concurrency)]
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res, duration = future.result()
            print(f"Test {i}: result={res}, duration={duration:.2f}s")
