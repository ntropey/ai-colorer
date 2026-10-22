"""
Dolce Colore - Key Generator Utility
Run: python keygen.py [--count 5] [--tier PRO1]
Generates algorithmic serial numbers for Revisited Labs customers.
"""

import sys
import argparse
import license_manager

def main():
    parser = argparse.ArgumentParser(description="Dolce Colore Serial Key Generator for Revisited Labs")
    parser.add_argument("--count", type=int, default=5, help="Number of keys to generate")
    parser.add_argument("--tier", type=str, default="PRO1", choices=["PRO1", "STUD", "LABS"], help="License tier code")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  Revisited Labs (https://revisitedlabs.com)")
    print(f"  Dolce Colore Serial Key Generator - Tier: {args.tier}")
    print("=" * 60)
    for i in range(1, args.count + 1):
        key = license_manager.generate_key(args.tier)
        valid, tier_name = license_manager.verify_key(key)
        print(f"  {i}. {key}  [{tier_name}]")
    print("=" * 60)

if __name__ == "__main__":
    main()
