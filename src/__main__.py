"""CLI for bodha."""
import sys, json, argparse
from .core import Bodha

def main():
    parser = argparse.ArgumentParser(description="Bodha — AI Document Simplifier. Simplify complex documents for different reading levels.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Bodha()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.process(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"bodha v0.1.0 — Bodha — AI Document Simplifier. Simplify complex documents for different reading levels.")

if __name__ == "__main__":
    main()
