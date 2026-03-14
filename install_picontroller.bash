#!/usr/bin/bash

mkdir -p $HOME/.local/share/picontroller
rm -rf $HOME/.local/share/picontroller
cd $HOME/.local/share/

git clone https://github.com/franciszekadamski/picontroller.git
cd $HOME/.local/share/picontroller
git checkout 18-prepare-installation-script

export PICONTROLLER_PROJECT_PATH=$HOME/.local/share/picontroller
export PATH=$PATH:$PICONTROLLER_PROJECT_PATH


if ! grep -q "PICONTROLLER_PROJECT_PATH=" "$HOME/.bashrc"; then
	  echo "export PICONTROLLER_PROJECT_PATH=$PICONTROLLER_PROJECT_PATH" >> "$HOME/.bashrc"
fi

if ! grep -q 'PATH=\$PATH:\$PICONTROLLER_PROJECT_PATH' "$HOME/.bashrc"; then
	  echo 'export PATH=$PATH:$PICONTROLLER_PROJECT_PATH' >> "$HOME/.bashrc"
fi

if ! grep -q 'PATH=\$PATH:\$PICONTROLLER_CONFIGURATION_PATH' "$HOME/.bashrc"; then
	  echo 'export PATH=$PATH:$PICONTROLLER_CONFIGURATION_PATH' >> "$HOME/.bashrc"
fi

source $HOME/.bashrc

if [ ! -d "$HOME/user_configuration" ]; then
    cp -r $PICONTROLLER_PROJECT_PATH/user_configuration $HOME/
fi

CONF_FILE="$HOME/user_configuration/configuration.env"

grep -q "PICONTROLLER_HUB_IP=" "$CONF_FILE" || echo "PICONTROLLER_HUB_IP=127.0.0.1" >> "$CONF_FILE"

grep -q "PICONTROLLER_HUB_USER=" "$CONF_FILE" || echo "PICONTROLLER_HUB_USER=$USER" >> "$CONF_FILE"

grep -q "PICONTROLLER_PROJECT_PATH=" "$CONF_FILE" || echo "PICONTROLLER_PROJECT_PATH=$PICONTROLLER_PROJECT_PATH" >> "$CONF_FILE"


export PICONTROLLER_CONFIGURATION_PATH=$HOME/user_configuration

grep -q "PICONTROLLER_CONFIGURATION_PATH=" "$CONF_FILE" || echo "PICONTROLLER_CONFIGURATION_PATH=$PICONTROLLER_CONFIGURATION_PATH" >> "$CONF_FILE"

sudo systemctl stop picontroller.service
sudo systemctl stop picontrollerserver.service
sudo systemctl disable picontroller.service
sudo systemctl disable picontrollerserver.service

sudo rm /etc/systemd/system/picontroller.service
sudo rm /etc/systemd/system/picontrollerserver.service

$PICONTROLLER_PROJECT_PATH/scripts/picontroller_setup $PICONTROLLER_CONFIGURATION_PATH

echo $(systemctl status picontroller.service)
echo $(systemctl status picontrollerserver.service)


