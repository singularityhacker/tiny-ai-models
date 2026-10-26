import argparse
import json
from pathlib import Path
from .core import historical_inventory, plan, write_new


def main():
    parser = argparse.ArgumentParser(description='Tiny Models Part II — isolated pilot tools')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('plan', 'prepare', 'run'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--config', default='configs/pilot.json')
        if name != 'plan':
            cmd.add_argument('--out', required=True)
        if name == 'run':
            cmd.add_argument('--panel', required=True)
            cmd.add_argument('--model', required=True)
            cmd.add_argument('--arm', choices=['none', 'single', 'multi_rerank'], required=True)
            cmd.add_argument('--device', choices=['cpu', 'mps', 'cuda'], default='cpu')
            cmd.add_argument('--evidence')
    audit = sub.add_parser('audit-history')
    audit.add_argument('--results', default='../results')
    audit.add_argument('--out', required=True)
    report = sub.add_parser('report')
    report.add_argument('--runs', default='artifacts/runs')
    report.add_argument('--out', default='preview/index.html')
    args = parser.parse_args()
    if args.command in ('plan', 'prepare', 'run'):
        config = json.loads(Path(args.config).read_text())
        proposal = plan(config)
        if args.command == 'plan':
            print(json.dumps(proposal, indent=2))
        elif args.command == 'prepare':
            if not config.get('execution_approved', False):
                parser.error('Blueprint awaits approval; data preparation and experiments are disabled.')
            from .harness import prepare
            prepare(config, args.out)
        else:
            if not config.get('execution_approved', False):
                parser.error('Blueprint awaits approval; experiment execution is disabled.')
            from .harness import run
            panel = json.loads(Path(args.panel).read_text())
            evidence = json.loads(Path(args.evidence).read_text()) if args.evidence else None
            run(config, panel, args.model, args.arm, args.out, args.device, evidence)
    elif args.command == 'audit-history':
        write_new(args.out, historical_inventory(Path(args.results)))
    else:
        from .report import render
        render(args.runs, args.out)


if __name__ == '__main__':
    main()
