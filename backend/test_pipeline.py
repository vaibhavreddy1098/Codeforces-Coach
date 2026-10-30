import os
import json
from ml_engine import analyze_user_profile
from chat_engine import fetch_practice_problem
from config import CF_PROFILE_HANDLE

def run_pipeline_test():
    print("\n" + "="*60)
    print("AI COACH END-TO-END PIPELINE TESTER")
    print("="*60)

    if not os.getenv("GEMINI_API_KEY"):
        print("[-] WARNING: GEMINI_API_KEY is not set in your environment variables!")
        print("[-] Gemini-only features will use the configured local fallback.")

    handle = CF_PROFILE_HANDLE

    # --- STEP 1: ML ENGINE ---
    print(f"\n[1/3] Fetching Codeforces profile and extracting features for '{handle}'...")
    user_profile = analyze_user_profile(handle)

    if "error" in user_profile:
        print(f"\nPipeline failed at profile analysis: {user_profile['error']}")
        return

    print("[+] ML Profile Successfully Built!")
    print(f"    -> Persona: {user_profile['persona_name']} (Cluster {user_profile['cluster']})")
    confidence = user_profile.get("cluster_probability")
    if confidence is not None:
        print(f"    -> Match Confidence: {confidence * 100:.1f}%")
    else:
        print("    -> Profile Mode: rating-based fallback (trained model files unavailable)")
    print(f"    -> User Rating: {user_profile['current_rating']}")
    print(f"    -> Historical Accuracy: {user_profile['metrics']['accuracy']*100:.1f}%")
    print(f"    -> Attempted Problems Filter Loaded: {len(user_profile.get('attempted_problems', []))} problems")

    # --- STEP 2: CHAT ENGINE (RETRIEVAL & RANKING) ---
    print("\n[2/3] Running the problem recommender (ChromaDB + XGBoost)...")
    try:
        recommendation = fetch_practice_problem(user_profile)
    except Exception as e:
        print(f"\nRecommendation engine failed: {e}")
        return

    if not recommendation.get("problem_details"):
        print("\nThe engine could not find a valid problem.")
        print(f"Engine output: {recommendation.get('message') or recommendation.get('error')}")
        return

    print("[+] Problem Successfully Ranked and Selected!")
    print(f"    -> Selected Problem: {recommendation['problem_details'].get('name')}")
    print(f"    -> Target Rating: {recommendation['problem_details'].get('rating')}")

    # --- STEP 3: FINAL PRESENTATION ---
    print("\n[3/3] Problem presentation is ready.\n")
    print("="*60)
    print("FINAL LLM OUTPUT TO FRONTEND:")
    print("-" * 60)
    print(recommendation["message"])
    print("="*60)
    
    print("\nPipeline execution complete.")

if __name__ == "__main__":
    run_pipeline_test()