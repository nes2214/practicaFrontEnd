#/bin/bash

if ! command -v poetry &> /dev/null; then
    curl -sSL https://install.python-poetry.org | python3 -
fi

if ! command -v bun &> /dev/null; then
    sudo apt install -y unzip
    curl -fsSL https://bun.sh/install | bash
fi

if ! command -v docker &> /dev/null; then
    curl -L sh.xtec.dev/docker.sh | sh
fi

echo
echo "source ~/.bashrc"