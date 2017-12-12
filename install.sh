sudo apt-get update

sudo add-apt-repository ppa:openjdk-r/ppa  
sudo apt-get install python-dev python-pip

cat req/jdk_part* > req/jdk-7u80-linux-x64.tar.gz
sudo mv req/jdk-7u80-linux-x64.tar.gz /var/cache/oracle-jdk7-installer/
sudo apt-get install oracle-java7-installer
export JAVA_HOME="/usr/lib/jvm/java-7-oracle/"

sudo pip install numpy matplotlib jpype1 flask
sudo Xvfb :1 -screen 0 1024x768x24 </dev/null &
export DISPLAY=":1"
