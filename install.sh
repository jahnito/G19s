#!/bin/bash

inst_path='/opt/G19s'

function copy_files {
    cp start.sh $inst_path
    cp *.py $inst_path
    cp *.jpg $inst_path
    cp requirements.txt $inst_path
    cp -r tokens $inst_path
}

if [ -d $inst_path ]; then
    copy_files
else
    mkdir -p /opt/G19s
    copy_files
fi

if [ "$?" -ne 0 ]; then
    echo "Error"
    exit 1
fi

cd $inst_path
chmod +x start.sh

python3 -m venv .env
if [ "$?" -ne 0 ]; then
    echo "Error"
    exit 2
fi

source .env/bin/activate
pip install -r requirements.txt
if [ "$?" -ne 0 ]; then
    echo "Error"
    exit 3
fi

cat > /etc/systemd/system/g19s.service <<EOF
[Unit]
  Description=Logitech G19s

[Service]
  Type=simple
  ExecStart=/opt/G19s/start.sh
  Restart=always

[Install]
  WantedBy=multi-user.target
EOF

if [ "$?" -ne 0 ]; then
    echo "Error"
    exit 4
fi

sudo systemctl enable g19s.service
if [ "$?" -ne 0 ]; then
    echo "Error"
    exit 5
fi

sudo systemctl start g19s.service
