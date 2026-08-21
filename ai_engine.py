import pickle
import os

# This file will handle the actual Machine Learning predictions

def load_model():
    """Loads the pre-trained machine learning model from disk."""
    model_path = os.path.join("models", "model.pkl")
    vectorizer_path = os.path.join("models", "vectorizer.pkl")
    
    # TODO: We will connect this to your actual OCR model files tomorrow!
    print("AI Model loaded successfully.")
    return True

def run_prediction(text_input):
    """Takes user input from the website and runs it through the AI model."""
    # Placeholder logic until we connect the real model
    print(f"Running prediction on: {text_input}")
    
    # Dummy prediction result for testing the frontend
    result = {
        "category": "Food/Expense",
        "confidence": 94.5
    }
    
    return result

if __name__ == "__main__":
    # Test the engine locally
    load_model()
    print(run_prediction("Paid 500 for lunch"))