"""Publish the static review blueprint and evidence; never run experiments."""
from pathlib import Path
import shutil


def build_blueprint(destination):
    source = Path(__file__).resolve().parent
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / 'index.template.html', destination / 'index.html')
    for name in ('bedrock-evidence.json', 'models.json'):
        shutil.copyfile(source / name, destination / name)
    shutil.copytree(source / 'archive', destination / 'archive', dirs_exist_ok=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='part2/preview/blueprint')
    build_blueprint(parser.parse_args().out)
