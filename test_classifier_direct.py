from ai.classifier import classify_complaint
try:
    result = classify_complaint("live wire hanging near school gate, sparking in the rain")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
