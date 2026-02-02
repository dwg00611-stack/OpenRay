#!/usr/bin/env python3
"""
Generate operator-specific ranking files based on check_counts.json data.
Creates separate ranking files for each operator:
- mci_top100.txt
- irancell_top100.txt
- tci_top100.txt
- others_top100.txt
- iran_top100.txt (overall Iran ranking)
"""

import json
import os
from typing import Dict, Any, List, Tuple


def load_check_counts(check_counts_file: str) -> Dict[str, Any]:
    """Load check counts from JSON file."""
    if not os.path.exists(check_counts_file):
        print(f"Check counts file not found: {check_counts_file}")
        return {}
    
    with open(check_counts_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_operator_ranking(
    counts: Dict[str, Any], 
    operator: str, 
    output_file: str,
    active_proxies: List[str] = None
) -> None:
    """Generate ranking for a specific operator."""
    # Filter to active proxies if provided
    if active_proxies:
        proxy_set = set(active_proxies)
        filtered_counts = {k: v for k, v in counts.items() if k in proxy_set}
    else:
        filtered_counts = counts
    
    # Score each proxy by operator count, then total iran count, then global count
    scored = []
    for proxy, data in filtered_counts.items():
        if isinstance(data, dict) and "iran" in data and isinstance(data["iran"], dict):
            operator_count = data["iran"]["operators"].get(operator, 0)
            total_iran = data["iran"]["total"]
            global_count = data.get("global", 0)
        else:
            # Handle old format
            operator_count = 0
            total_iran = data.get("iran", 0) if isinstance(data, dict) else 0
            global_count = data.get("global", 0) if isinstance(data, dict) else data if isinstance(data, (int, float)) else 0
        
        scored.append((operator_count, total_iran, global_count, proxy))
    
    # Sort by operator count desc, then total iran desc, then global desc
    scored.sort(key=lambda x: (-x[0], -x[1], -x[2]))
    
    # Get top 100
    top_100 = [proxy for _, _, _, proxy in scored[:100]]
    
    # Write to file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for proxy in top_100:
            f.write(proxy + '\n')
    
    print(f"Generated {output_file} with {len(top_100)} proxies")


def generate_overall_iran_ranking(
    counts: Dict[str, Any], 
    output_file: str,
    active_proxies: List[str] = None
) -> None:
    """Generate overall Iran ranking based on total Iran count."""
    # Filter to active proxies if provided
    if active_proxies:
        proxy_set = set(active_proxies)
        filtered_counts = {k: v for k, v in counts.items() if k in proxy_set}
    else:
        filtered_counts = counts
    
    # Score each proxy by total iran count, then global count
    scored = []
    for proxy, data in filtered_counts.items():
        if isinstance(data, dict) and "iran" in data and isinstance(data["iran"], dict):
            total_iran = data["iran"]["total"]
            global_count = data.get("global", 0)
        else:
            # Handle old format
            total_iran = data.get("iran", 0) if isinstance(data, dict) else data if isinstance(data, (int, float)) else 0
            global_count = data.get("global", 0) if isinstance(data, dict) else data if isinstance(data, (int, float)) else 0
        
        scored.append((total_iran, global_count, proxy))
    
    # Sort by total iran count desc, then global desc
    scored.sort(key=lambda x: (-x[0], -x[1]))
    
    # Get top 100
    top_100 = [proxy for _, _, proxy in scored[:100]]
    
    # Write to file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        for proxy in top_100:
            f.write(proxy + '\n')
    
    print(f"Generated {output_file} with {len(top_100)} proxies")


def load_active_proxies(proxy_file: str) -> List[str]:
    """Load active proxies from file."""
    if not os.path.exists(proxy_file):
        print(f"Active proxies file not found: {proxy_file}")
        return []
    
    with open(proxy_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def main():
    # Define file paths
    check_counts_file = os.path.join('.state', 'check_counts.json')
    output_dir = os.path.join('output_iran')
    
    # Load check counts
    counts = load_check_counts(check_counts_file)
    if not counts:
        print("No check counts data found. Exiting.")
        return
    
    print(f"Loaded check counts for {len(counts)} proxies")
    
    # Load active proxies for Iran (optional filtering)
    active_proxies_file = os.path.join('output', 'all_valid_proxies.txt')
    active_proxies = load_active_proxies(active_proxies_file)
    
    if active_proxies:
        print(f"Loaded {len(active_proxies)} active proxies for filtering")
    else:
        print("Could not load active proxies - will rank all proxies in check_counts.json")
    
    # Generate operator-specific rankings
    operators = ['mci', 'irancell', 'tci', 'others']
    
    for operator in operators:
        output_file = os.path.join(output_dir, f'{operator}_top100.txt')
        generate_operator_ranking(counts, operator, output_file, active_proxies)
    
    # Generate overall Iran ranking
    iran_output_file = os.path.join(output_dir, 'iran_top100.txt')
    generate_overall_iran_ranking(counts, iran_output_file, active_proxies)
    
    print("All operator rankings generated successfully!")


if __name__ == "__main__":
    main()