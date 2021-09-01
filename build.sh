#! /bin/bash


function build() {
    folder=$1
    module=$2
    if [ ! $folder && ! $module ]; then
      echo "folder and module is null"
      return
    fi
    echo "change dir $folder"
    cd $folder
    echo "remove module $module"
    pip3  uninstall  -y $module
    python3 setup.py sdist bdist_wheel
    pip3 install dist/*.whl
}

build $1 $2