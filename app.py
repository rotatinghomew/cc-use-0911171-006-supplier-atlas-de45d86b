import argparse
import json
from pathlib import Path
from records import load, save


def inspect(data, as_of):
    from profiles import build, mixed_exposure
    from segments import effective_members
    from strategies import dispatch, summarize
    return {"mixed_exposure": mixed_exposure(data, as_of), "profiles": build(data, as_of), "members": effective_members(data, as_of),
            "dispatch": dispatch(data, as_of), "summary": summarize(data, as_of)}



def main():
    parser = argparse.ArgumentParser(description="供应商观察窗画像、混合车次质量记录和经营跟进策略。")
    parser.add_argument("action", choices=["demo", "inspect"])
    parser.add_argument("--data", type=Path, default=Path(__file__).parent / "fixtures/data.json")
    parser.add_argument("--as-of", default="2026-10-31")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect(load(args.data), args.as_of)
    if args.output:
        save(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
