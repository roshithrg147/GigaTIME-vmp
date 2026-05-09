from integrations.gemini_integrator import GeminiIntegrator

def manual_test():
    integrator = GeminiIntegrator()
    prompt = "Summarize the clinical implications of spatial architecture in cancer."
    
    print(f"Sending prompt to Gemini...")
    try:
        response = integrator.generate_completion(prompt)
        print("\n--- Response ---")
        print(response)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    manual_test()
