# Catalog App

Udacity - Full Stack Web Developer Nanodegree - Servers, Authorization, and CRUD Project.

The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system.

## Getting Started
This project used **Python 2.7.12**, **PostgreSQL**, **Flask**, **Sqlalchemy**  and  if you not install it yet you can follow step below to get that.

### Install VirtualBox
VirtualBox is the software that actually runs the virtual machine. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.

Currently (October 2017), the supported version of VirtualBox to install is version 5.1. Newer versions do not work with the current release of Vagrant.

### Install Vagrant
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. [Download it from vagrantup.com.](https://www.vagrantup.com/downloads.html) Install the version for your operating system.

If Vagrant is successfully installed, you will be able to run `vagrant --version`
in your terminal to see the version number.

### Download the VM configuration
There are a couple of different ways you can download the VM configuration.

You can download and unzip this file: [FSND-Virtual-Machine.zip](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) This will give you a directory called FSND-Virtual-Machine. It may be located inside your Downloads folder.

Either way, you will end up with a new directory containing the VM files. Change to this directory in your terminal with `cd`. Inside, you will find another directory called **vagrant**. Change directory to the **vagrant** directory.

### Start the virtual machine
From your terminal, inside the **vagrant** subdirectory, run the command `vagrant up`. This will cause Vagrant to download the Linux operating system and install it. This may take quite a while (many minutes) depending on how fast your Internet connection is.

When `vagrant up` is finished running, you will get your shell prompt back. At this point, you can run `vagrant ssh` to log in to your newly installed Linux VM!

### Started Data
To load the data, `cd` into the `vagrant/catalog` directory and use the command
```bash
python initcatalog.py
```

## How to run program
`cd` into the `vagrant/catalog` directory and use the command
```bash
python project.py
```
open internet browser (ex. Google Chrome) and access to
http://localhost:8000
(Log in by Google Plus Account)

## Author
* Dejnarong Lamleangpon - _Programmer_ - [Profiles](https://github.com/Dejnarong)


## Program's Functions
* Add Category Item
* Edit Category Item
* Delete Category Item
* Catalog.json (Get json)

## Acknowledgments
    * Some code (in section of OAuth) are taken from lesson in Servers, Authorization, and CRUD.
    * Some installation guide (links / information) are taken from what I learned in the udacity course.