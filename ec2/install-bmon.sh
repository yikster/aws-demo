git clone https://github.com/tgraf/bmon.git
cd bmon
sudo yum install make libconfuse-devel libnl3-devel libnl-route3-devel ncurses-devel autoconf gcc automake -y
sudo ./autogen.sh
sudo ./configure
sudo make
sudo make install
