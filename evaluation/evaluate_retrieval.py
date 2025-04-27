import pandas as pd
from app.server import ask

def evaluate(csv_path):
    df = pd.read_csv(csv_path)
    results = []

    for _, row in df.iterrows():
        question = row['question']
        expected_keywords = row['expected_answer_keywords'].split(',')
        response = ask(question)["response"]

        # Simple keyword matching
        match_score = sum(1 for kw in expected_keywords if kw.lower() in response.lower())
        match_percent = match_score / len(expected_keywords) * 100

        results.append((question, response, match_percent))

    results_df = pd.DataFrame(results, columns=["Question", "Response", "Match %"])
    results_df.to_csv("evaluation_results.csv", index=False)
    print("Evaluation completed! Results saved to evaluation_results.csv")

if __name__ == "__main__":
    evaluate("evaluation/eval_questions.csv")
