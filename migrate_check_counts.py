#!/usr/bin/env python3
"""
Migration script to convert existing check_counts.json to new structure.
Converts:
- "main" field to "global"
- "iran" integer to object structure with operators
"""

import json
import os
from typing import Dict, Any


def migrate_check_counts(input_file: str, output_file: str) -> None:
    """
    Migrate check_counts.json from old structure to new structure.
    
    Old structure:
    {
      "vless://uuid@server:port": {
        "main": 17,
        "iran": 2,
        "consecutive_failures": 0
      }
    }
    
    New structure:
    {
      "vless://uuid@server:port": {
        "global": 17,
        "iran": {
          "total": 5,
          "operators": {
            "mci": 0,
            "irancell": 0,
            "tci": 0,
            "others": <existing_iran_value>
          }
        },
        "consecutive_failures": 0
      }
    }
    """
    print(f"Loading existing check_counts.json from: {input_file}")
    
    # Load existing data
    with open(input_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    print(f"Loaded {len(old_data)} proxy entries")
    
    # Transform data to new structure
    new_data: Dict[str, Any] = {}
    migrated_count = 0
    
    for proxy_url, old_counts in old_data.items():
        # Handle both old and new formats (in case of partial migration)
        if isinstance(old_counts, dict):
            # New format - preserve as is
            if "iran" in old_counts and isinstance(old_counts["iran"], dict):
                new_data[proxy_url] = old_counts
            else:
                # Old format - transform
                main_count = old_counts.get("main", 0)
                iran_count = old_counts.get("iran", 0)
                consecutive_failures = old_counts.get("consecutive_failures", 0)
                
                new_entry = {
                    "global": main_count,
                    "iran": {
                        "total": iran_count,
                        "operators": {
                            "mci": 0,
                            "irancell": 0,
                            "tci": 0,
                            "others": iran_count  # Preserve existing iran count as 'others'
                        }
                    },
                    "consecutive_failures": consecutive_failures
                }
                
                new_data[proxy_url] = new_entry
                migrated_count += 1
        else:
            # Very old format where value was just an integer
            main_count = int(old_counts) if isinstance(old_counts, (int, str)) else 0
            
            new_entry = {
                "global": main_count,
                "iran": {
                    "total": 0,
                    "operators": {
                        "mci": 0,
                        "irancell": 0,
                        "tci": 0,
                        "others": 0
                    }
                },
                "consecutive_failures": 0
            }
            
            new_data[proxy_url] = new_entry
            migrated_count += 1
    
    print(f"Migrated {migrated_count} entries to new structure")
    
    # Calculate total operator counts to verify integrity
    total_mci = sum(entry["iran"]["operators"]["mci"] for entry in new_data.values())
    total_irancell = sum(entry["iran"]["operators"]["irancell"] for entry in new_data.values())
    total_tci = sum(entry["iran"]["operators"]["tci"] for entry in new_data.values())
    total_others = sum(entry["iran"]["operators"]["others"] for entry in new_data.values())
    total_iran_field = sum(entry["iran"]["total"] for entry in new_data.values())
    
    print(f"Verification - Total operator counts:")
    print(f"  MCI: {total_mci}")
    print(f"  Irancell: {total_irancell}")
    print(f"  TCI: {total_tci}")
    print(f"  Others: {total_others}")
    print(f"  Sum of operators: {total_mci + total_irancell + total_tci + total_others}")
    print(f"  Total Iran field: {total_iran_field}")
    
    # Write new structure to output file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    
    print(f"Migration completed. New structure saved to: {output_file}")
    print(f"Total entries in new structure: {len(new_data)}")


def verify_migration(input_file: str) -> bool:
    """Verify that the migration produced valid data."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check structure for first few entries
        sample_entries = list(data.items())[:3]
        
        for proxy_url, counts in sample_entries:
            # Verify global field exists
            if "global" not in counts:
                print(f"ERROR: Missing 'global' field in {proxy_url}")
                return False
            
            # Verify iran structure exists
            if "iran" not in counts or not isinstance(counts["iran"], dict):
                print(f"ERROR: Invalid 'iran' structure in {proxy_url}")
                return False
            
            # Verify iran sub-fields
            iran_data = counts["iran"]
            if "total" not in iran_data or "operators" not in iran_data:
                print(f"ERROR: Missing 'total' or 'operators' in iran field for {proxy_url}")
                return False
            
            operators = iran_data["operators"]
            required_operators = ["mci", "irancell", "tci", "others"]
            for op in required_operators:
                if op not in operators:
                    print(f"ERROR: Missing operator '{op}' in {proxy_url}")
                    return False
        
        print("✓ Migration verification passed")
        return True
    except Exception as e:
        print(f"ERROR: Verification failed - {e}")
        return False


if __name__ == "__main__":
    input_path = os.path.join(os.path.dirname(__file__), ".state", "check_counts.json")
    backup_path = input_path + ".backup"
    output_path = input_path  # We'll overwrite after backup
    
    print("Starting check_counts.json migration...")
    
    # Backup original file
    print(f"Creating backup: {backup_path}")
    with open(input_path, 'rb') as src, open(backup_path, 'wb') as dst:
        dst.write(src.read())
    
    print("Backup created. Starting migration...")
    
    # Perform migration
    migrate_check_counts(input_path, output_path)
    
    # Verify migration
    if verify_migration(output_path):
        print("\n✅ Migration completed successfully!")
        print(f"Original file backed up to: {backup_path}")
        print(f"New structure saved to: {output_path}")
    else:
        print("\n❌ Migration verification failed!")
        print("Please restore from backup and investigate the issue.")