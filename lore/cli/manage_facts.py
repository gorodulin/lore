"""
Create, read, edit, and delete facts in .lore.json files.

Usage:
    lore create <root> --fact "text" --incl "g:pattern" [--incl ...] [--skip "g:pattern"]
    lore read   <root> <fact_id> [fact_id ...]
    lore edit   <root> <fact_id> [--fact "text"] [--incl "g:pattern"] [--skip "g:pattern"]
    lore delete <root> <fact_id>
    lore match  <root> <path>
    lore validate <root>

Output:
    JSON to stdout describing the operation result.
"""

import argparse
import json
import os
import sys

from lore.facts.create_fact import create_fact
from lore.facts.edit_fact import edit_fact
from lore.facts.delete_fact import delete_fact
from lore.facts.match_facts_for_path import match_facts_for_path
from lore.facts.read_fact import read_fact
from lore.validation.run_all_validation_checks import run_all_validation_checks
from lore.client.try_send_fact_request import try_send_fact_request


def manage_facts():
    parser = argparse.ArgumentParser(
        prog="lore",
        description="Create, edit, and delete facts in .lore.json files",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create subcommand
    create_parser = subparsers.add_parser("create", help="Create a new fact")
    create_parser.add_argument("root", help="Project root directory")
    create_parser.add_argument("--fact", required=True, help="Fact text")
    create_parser.add_argument(
        "--incl", action="append", required=True, help="Inclusion pattern (repeatable)"
    )
    create_parser.add_argument(
        "--skip", action="append", default=None, help="Exclusion pattern (repeatable)"
    )
    create_parser.add_argument("--id", default=None, help="Explicit fact ID")
    create_parser.add_argument(
        "--tag", action="append", default=None, help="Tag (repeatable, e.g. hook:read)"
    )

    # read subcommand
    read_parser = subparsers.add_parser("read", help="Read and display a fact")
    read_parser.add_argument("root", help="Project root directory")
    read_parser.add_argument("fact_ids", nargs="+", help="ID(s) of the fact(s) to read")

    # edit subcommand
    edit_parser = subparsers.add_parser("edit", help="Edit an existing fact")
    edit_parser.add_argument("root", help="Project root directory")
    edit_parser.add_argument("fact_id", help="ID of the fact to edit")
    edit_parser.add_argument("--fact", default=None, help="New fact text")
    edit_parser.add_argument(
        "--incl", action="append", default=None, help="New inclusion pattern (repeatable)"
    )
    edit_parser.add_argument(
        "--skip", action="append", default=None, help="New exclusion pattern (repeatable)"
    )
    edit_parser.add_argument(
        "--tag", action="append", default=None, help="Tag (repeatable, e.g. hook:read)"
    )

    # delete subcommand
    delete_parser = subparsers.add_parser("delete", help="Delete a fact")
    delete_parser.add_argument("root", help="Project root directory")
    delete_parser.add_argument("fact_id", help="ID of the fact to delete")

    # match subcommand
    match_parser = subparsers.add_parser("match", help="Find facts matching a file path")
    match_parser.add_argument("root", help="Project root directory")
    match_parser.add_argument("path", help="File path to match against facts")

    # validate subcommand
    validate_parser = subparsers.add_parser("validate", help="Run validation checks on all facts")
    validate_parser.add_argument("root", help="Project root directory")

    args = parser.parse_args()

    root = os.path.realpath(args.root)
    if not os.path.isdir(root):
        print(f"Error: {args.root} is not a directory", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == "create":
            params = {"fact": args.fact, "incl": args.incl}
            if args.skip:
                params["skip"] = args.skip
            if args.id:
                params["fact_id"] = args.id
            if args.tag:
                params["tags"] = args.tag
            result = try_send_fact_request(root, "create_fact", params)
            if result is None:
                result = create_fact(root, args.fact, args.incl, args.skip, fact_id=args.id, tags=args.tag)
        elif args.command == "read":
            if len(args.fact_ids) == 1:
                fid = args.fact_ids[0]
                result = try_send_fact_request(root, "read_fact", {"fact_id": fid})
                if result is None:
                    result = read_fact(root, fid)
            else:
                result = []
                for fid in args.fact_ids:
                    server_result = try_send_fact_request(root, "read_fact", {"fact_id": fid})
                    if server_result is not None:
                        result.append(server_result)
                    else:
                        result.append(read_fact(root, fid))
        elif args.command == "edit":
            params = {"fact_id": args.fact_id}
            if args.fact is not None:
                params["fact"] = args.fact
            if args.incl is not None:
                params["incl"] = args.incl
            if args.skip is not None:
                params["skip"] = args.skip
            if args.tag is not None:
                params["tags"] = args.tag
            result = try_send_fact_request(root, "edit_fact", params)
            if result is None:
                result = edit_fact(root, args.fact_id, fact_text=args.fact, incl=args.incl, skip=args.skip, tags=args.tag)
        elif args.command == "delete":
            result = try_send_fact_request(root, "delete_fact", {"fact_id": args.fact_id})
            if result is None:
                result = delete_fact(root, args.fact_id)
        elif args.command == "match":
            file_path = args.path
            content = None
            full_path = os.path.join(root, file_path)
            if os.path.isfile(full_path):
                try:
                    with open(full_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except OSError:
                    pass
            params = {"file_path": file_path}
            if content is not None:
                params["content"] = content
            result = try_send_fact_request(root, "find_facts", params)
            if result is None:
                result = match_facts_for_path(root, file_path, content=content)
        elif args.command == "validate":
            result = try_send_fact_request(root, "validate", {})
            if result is None:
                result = run_all_validation_checks(root)
        else:
            parser.print_help()
            sys.exit(1)
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    manage_facts()
