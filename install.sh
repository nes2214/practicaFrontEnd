#/bin/bash

curl -L sh.xtec.dev/docker.sh | sh

curl -sSL https://install.python-poetry.org | python3 -

sudo apt install -y unzip
curl -fsSL https://bun.sh/install | bash

echo "source /home/box/.bashrc"