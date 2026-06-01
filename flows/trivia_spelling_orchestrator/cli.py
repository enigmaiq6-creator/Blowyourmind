#!/usr/bin/env python3
"""CLI entry point for the Spelling Trivia Video Generator."""

import argparse
from pathlib import Path
from dotenv import load_dotenv

from tools.common.messenger import Messenger
from flows.trivia_spelling_orchestrator.generator import SpellingTriviaGenerator
from flows.trivia_spelling_orchestrator.pipeline import SpellingTriviaPipeline


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(
        description="Generate English Spelling & Vocabulary Trivia Videos"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("output/trivia_spelling"),
        help="Output directory (default: output/trivia_spelling)",
    )
    parser.add_argument(
        "--plan", "-p",
        type=Path,
        default=None,
        help="Path to an existing trivia plan JSON (skip generation)",
    )
    parser.add_argument(
        "--generate-only", "-g",
        action="store_true",
        help="Only generate the trivia plan JSON, don't render video",
    )
    args = parser.parse_args()

    pipeline = SpellingTriviaPipeline(output_base=args.output)

    plan = None
    if args.plan:
        import json
        from flows.trivia_spelling_orchestrator.schemas import TriviaVideoPlan
        data = json.loads(args.plan.read_text(encoding="utf-8"))
        plan = TriviaVideoPlan.model_validate(data)
        Messenger.info(f"Loaded plan from: {args.plan}")

    if args.generate_only:
        if plan is None:
            gen = SpellingTriviaGenerator()
            plan = gen.generate()
        plan_path = args.output / "scripts" / "trivia_plan.json"
        gen = SpellingTriviaGenerator()
        gen.save_plan(plan, plan_path)
        Messenger.step_success(f"Plan saved to {plan_path}. Run without --generate-only to render.")
        return

    pipeline.run(plan=plan)


if __name__ == "__main__":
    main()
