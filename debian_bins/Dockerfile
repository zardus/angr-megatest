from debian:buster

run dpkg --add-architecture amd64
run dpkg --add-architecture arm64
run dpkg --add-architecture armel
run dpkg --add-architecture armhf
run dpkg --add-architecture i386
run dpkg --add-architecture mips
run dpkg --add-architecture mips64el
run dpkg --add-architecture mipsel
run dpkg --add-architecture ppc64el
#run dpkg --add-architecture 390x
run echo "deb http://deb.debian.org/debian-debug/ stretch-debug main" >> /etc/apt/sources.list.d/ddebs.list
run echo "deb http://deb.debian.org/debian-debug/ stretch-proposed-updates-debug main" >> /etc/apt/sources.list.d/ddebs.list
run apt-get update
run DEBIAN_FRONTEND=noninteractive apt-get install -yqq debian-goodies liblz4-tool
