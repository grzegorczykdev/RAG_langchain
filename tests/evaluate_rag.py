"""
Offline RAG evaluation pipeline for NutriMind AI using Ragas and Google Gemini.

Run from the project root:
    python tests/evaluate_rag.py

Requires:
    - GEMINI_API_KEY in .env (or environment)
    - Indexed Chroma database (python creating_database.py)
    - tests/eval_dataset.json populated with question / ground_truth pairs
"""

from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv

# Legacy Ragas metrics work with LangChain Gemini wrappers used in this project.
# collections.* imports are modules; evaluate() requires instantiated Metric objects.
warnings.filterwarnings("ignore", category=DeprecationWarning, module="ragas")

# Allow imports from the project root when executed as a script.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd  # noqa: E402
from datasets import Dataset  # noqa: E402
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings  # noqa: E402
from ragas import evaluate  # noqa: E402
from ragas.embeddings import LangchainEmbeddingsWrapper  # noqa: E402
from ragas.llms import LangchainLLMWrapper  # noqa: E402
from ragas.metrics import answer_relevancy, faithfulness  # noqa: E402
from ragas.run_config import RunConfig  # noqa: E402

from constants import GEMINI_CHAT_MODEL, GEMINI_EMBEDDING_MODEL  # noqa: E402
from query_data import query_documents_with_contexts  # noqa: E402

TESTS_DIR = Path(__file__).resolve().parent
DATASET_PATH = TESTS_DIR / "eval_dataset.json"
REPORT_PATH = TESTS_DIR / "evaluation_report.csv"

METRICS = [faithfulness, answer_relevancy]
METRIC_NAMES = ["faithfulness", "answer_relevancy"]

# Faithfulness runs 2 LLM passes per row (statement split + NLI). Gemini can exceed
# short defaults under load; Ragas maps any job failure to NaN in the CSV.
RAGAS_RUN_CONFIG = RunConfig(
    timeout=600,
    max_retries=5,
    max_workers=2,
)
GEMINI_REQUEST_TIMEOUT_S = 180


def load_eval_dataset(path: Path) -> list[dict[str, str]]:
    """Load and validate the evaluation JSON dataset."""
    if not path.is_file():
        raise FileNotFoundError(f"Evaluation dataset not found: {path}")

    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, list) or len(raw) < 1:
        raise ValueError("eval_dataset.json must be a non-empty JSON array.")

    validated: list[dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Row {index}: each entry must be a JSON object.")
        question = str(item.get("question", "")).strip()
        ground_truth = str(item.get("ground_truth", "")).strip()
        if not question or not ground_truth:
            raise ValueError(
                f"Row {index}: both 'question' and 'ground_truth' are required."
            )
        validated.append({"question": question, "ground_truth": ground_truth})

    return validated


def require_api_key() -> str:
    load_dotenv(PROJECT_ROOT / ".env")
    key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if not key:
        raise EnvironmentError(
            "GEMINI_API_KEY is missing. Add it to .env before running evaluation."
        )
    return key


def collect_rag_outputs(
    dataset: list[dict[str, str]],
    api_key: str,
) -> dict[str, list]:
    """Run each evaluation question through the production RAG pipeline."""
    questions: list[str] = []
    answers: list[str] = []
    contexts: list[list[str]] = []
    ground_truths: list[str] = []

    total = len(dataset)
    for index, row in enumerate(dataset, start=1):
        question = row["question"]
        print(f"[{index}/{total}] Running RAG query: {question[:80]}...")

        result = query_documents_with_contexts(question, gemini_api_key=api_key)

        questions.append(question)
        answers.append(result["answer"])
        contexts.append(result.get("contexts", []))
        ground_truths.append(row["ground_truth"])

    return {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    }


def build_ragas_llm_and_embeddings(api_key: str) -> tuple[LangchainLLMWrapper, LangchainEmbeddingsWrapper]:
    """Configure Gemini models used as the Ragas critic / judge."""
    llm = LangchainLLMWrapper(
        ChatGoogleGenerativeAI(
            model=GEMINI_CHAT_MODEL,
            google_api_key=api_key,
            temperature=0,
            timeout=GEMINI_REQUEST_TIMEOUT_S,
        )
    )
    embeddings = LangchainEmbeddingsWrapper(
        GoogleGenerativeAIEmbeddings(
            model=GEMINI_EMBEDDING_MODEL,
            google_api_key=api_key,
        )
    )
    return llm, embeddings


def build_full_report(rag_records: dict[str, list], scores_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge Ragas metric scores with the original evaluation inputs.

    Ragas to_pandas() returns only metric columns, not question/answer/context fields.
    """
    input_df = pd.DataFrame(
        {
            "question": rag_records["question"],
            "ground_truth": rag_records["ground_truth"],
        }
    )
    return pd.concat(
        [input_df.reset_index(drop=True), scores_df.reset_index(drop=True)],
        axis=1,
    )


def print_summary_table(report_df: pd.DataFrame) -> None:
    """Print mean metric scores and per-row results to the console."""
    print("\n" + "=" * 60)
    print("  NutriMind AI — Ragas Evaluation Summary")
    print("=" * 60)

    print("\nMean scores:")
    print("-" * 40)
    for name in METRIC_NAMES:
        if name in report_df.columns:
            mean_score = report_df[name].mean(skipna=True)
            nan_count = int(report_df[name].isna().sum())
            score_text = f"{mean_score:.4f}" if not pd.isna(mean_score) else "NaN (failed jobs)"
            suffix = f"  [{nan_count} failed]" if nan_count else ""
            print(f"  {name:20s} {score_text}{suffix}")
        else:
            print(f"  {name:20s} (not returned)")

    if "faithfulness" in report_df.columns and report_df["faithfulness"].isna().any():
        print(
            "\nNote: faithfulness NaN means Ragas caught an error (often TimeoutError) "
            "while judging that row. Re-run after increasing timeouts or check API limits."
        )

    print("\nPer-sample results:")
    print("-" * 60)
    preferred = ["question"] + [c for c in METRIC_NAMES if c in report_df.columns]
    display_cols = [c for c in preferred if c in report_df.columns]
    if not display_cols:
        display_cols = list(report_df.columns)
    print(report_df[display_cols].to_string(index=False, max_colwidth=50))
    print("=" * 60 + "\n")


def main() -> None:
    print("Loading evaluation dataset...")
    eval_rows = load_eval_dataset(DATASET_PATH)

    api_key = require_api_key()

    if not (PROJECT_ROOT / "chroma").is_dir():
        print(
            "Warning: chroma/ directory not found. "
            "Run 'python creating_database.py' first for meaningful scores."
        )

    print(f"Collecting RAG outputs for {len(eval_rows)} samples...")
    rag_records = collect_rag_outputs(eval_rows, api_key)

    hf_dataset = Dataset.from_dict(rag_records)
    llm, embeddings = build_ragas_llm_and_embeddings(api_key)

    print(
        "Running Ragas evaluation (faithfulness, answer_relevancy)... "
        f"timeout={RAGAS_RUN_CONFIG.timeout}s per job, workers={RAGAS_RUN_CONFIG.max_workers}"
    )
    evaluation_result = evaluate(
        dataset=hf_dataset,
        metrics=METRICS,
        llm=llm,
        embeddings=embeddings,
        run_config=RAGAS_RUN_CONFIG,
        raise_exceptions=False,
    )

    scores_df = evaluation_result.to_pandas()
    full_report_df = build_full_report(rag_records, scores_df)
    full_report_df.to_csv(REPORT_PATH, index=False, encoding="utf-8")

    print_summary_table(full_report_df)
    print(f"Detailed report saved to: {REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, EnvironmentError) as exc:
        print(f"Evaluation aborted: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nEvaluation interrupted by user.", file=sys.stderr)
        sys.exit(130)
