#!/usr/bin/env python3
"""Quick test script to verify the analysis pipeline works end-to-end"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis import analyze_session

# Find a test EEG file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_files = [
    os.path.join(base_dir, "cap_data", "n13.edf"),
    os.path.join(base_dir, "cap_data", "n12.edf"),
]

test_file = None
for f in test_files:
    if os.path.exists(f):
        test_file = f
        break

# Allow command line override
if len(sys.argv) > 1:
    test_file = os.path.abspath(sys.argv[1])

if not test_file:
    print("❌ No test EEG file found. Please provide a .edf file path as argument.")
    print("\nUsage: python3 test_pipeline.py /path/to/file.edf")
    sys.exit(1)

print(f"🧪 Testing analysis pipeline with: {os.path.basename(test_file)}")
print("-" * 60)

try:
    results = analyze_session(test_file)
    print("✅ Analysis completed successfully!\n")
    print("📊 Results Summary:")
    print(f"   Subtype: {results['phenotype']['type']}")
    print(f"   Confidence: {results['phenotype']['confidence']:.2%}")
    print(f"   Cluster: {results['clusterAssignment']['cluster']}")
    print(f"   Total Sleep Time: {results['summary']['totalSleepTime']} min")
    print(f"   Sleep Efficiency: {results['summary']['sleepEfficiency']}%")
    print("\n📈 Spectral Analysis:")
    for band in results['spectralAnalysis']:
        print(f"   {band['frequency']} Hz: {band['power']:.4f}")
    
    print("\n💡 Characteristics:")
    for char in results['phenotype']['characteristics']:
        print(f"   • {char}")
    
    print("\n✅ All systems operational!")
    
except Exception as e:
    print(f"❌ Analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
