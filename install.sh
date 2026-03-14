#!/usr/bin/bash

mkdir -p $HOME/.local/share/picontroller
cd $HOME/.local/share/
git clone https://github.com/franciszekadamski/picontroller.git
cd $HOME/.local/share/picontroller
git checkout 18-prepare-installation-script

export PICONTROLLER_PROJECT_PATH=$HOME/.local/share/picontroller
export PATH=$PATH:$PICONTROLLER_PROJECT_PATH

echo "export PICONTROLLER_PROJECT_PATH=$PICONTROLLER_PROJECT_PATH" >> $HOME/.bashrc
echo 'export PATH=$PATH:$PICONTROLLER_PROJECT_PATH' >> $HOME/.bashrc

source $HOME/.bashrc

cp -r $PICONTROLLER_PROJECT_PATH/user_configuration $HOME/
echo "PICONTROLLER_HUB_IP=127.0.0.1" >> $HOME/user_configuration/configuration.env
echo "PICONTROLLER_HUB_USER=$USER" >> $HOME/user_configuration/configuration.env
echo "PICONTROLLER_PROJECT_PATH=$PICONTROLLER_PROJECT_PATH" >> $HOME/user_configuration/configuration.env

export PICONTROLLER_CONFIGURATION_PATH=$HOME/user_configuration

picontroller_setup $PICONTROLLER_CONFIGURATION_PATH

systemctl status picontroller.service
systemctl status picontrollerserver.service


