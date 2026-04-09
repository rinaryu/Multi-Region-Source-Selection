import json
import os
import collections

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(BASE_DIR)

def main():
    if not os.path.exists("results.json"):
        print("ERROR: results.json not found. Please run scripts/run_experiments.py first.")
        return

    with open("results.json", "r") as f:
        data = json.load(f)

    # Accumulate data
    analyzer = collections.defaultdict(lambda: collections.defaultdict(list))
    for row in data:
        region = row["region"]
        policy = row["policy"]
        analyzer[region][policy].append({
            "quality": row["quality_id"],
            "stalls": row["buffer_stalls"],
            "startup_delay": row.get("startup_delay", 0)
        })

    print("=" * 70)
    print(f"{'MULTI-REGION DASH LATENCY REPORT':^70}")
    print("=" * 70)
    
    policies = ["distance", "round_robin", "random"]
    
    for region, policies_data in analyzer.items():
        print(f"\n[CLIENT REGION: {region.upper()}]")
        print("-" * 65)
        print(f"{'POLICY':<15} | {'TTFB/DELAY':<10} | {'AVG BITRATE (ID)':<16} | {'AVG STALLS':<10}")
        print("-" * 65)
        
        for policy in policies:
            runs = policies_data.get(policy, [])
            if not runs:
                print(f"{policy:<15} | {'No Data':<16} | {'No Data':<10}")
                continue
                
            avg_quality = sum(r["quality"] for r in runs) / len(runs)
            avg_stalls = sum(r["stalls"] for r in runs) / len(runs)
            avg_ttfb = sum(r.get("startup_delay", 0) for r in runs) / len(runs)
            
            # Formulate human string
            if avg_quality > 1.8:
                qual_str = "High (720p)"
            elif avg_quality > 0.8:
                qual_str = "Med (480p)"
            else:
                qual_str = "Low (360p)"
                
            print(f"{policy:<15} | {avg_ttfb:>5.0f}ms | {avg_quality:.1f} - {qual_str:<8} | {avg_stalls:.1f}")

if __name__ == "__main__":
    main()
