FROM postgres:latest


#RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | \
#  tee /etc/apt/sources.list.d/webupd8team-java.list
#RUN echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | \
#   tee -a /etc/apt/sources.list.d/webupd8team-java.list

RUN apt-get update --fix-missing


RUN apt-get install -q -y --force-yes \
	unzip \
	wget \
	git \
	mercurial \
	python-dev \
	cmake \
	subversion \
	python-pip \
	build-essential \
	git-core \
	pkg-config \
    curl \
    vim \
    man
 #   oracle-java8-installer

RUN \
    echo "===> add webupd8 repository..."  && \
    echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee /etc/apt/sources.list.d/webupd8team-java.list  && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list  && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886  && \
    apt-get update

RUN echo "===> install Java"  && \
    echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections  && \
    echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections  && \
    DEBIAN_FRONTEND=noninteractive  apt-get install -y --force-yes oracle-java8-installer oracle-java8-set-default
    
RUN echo "===> clean up..."  && \
    rm -rf /var/cache/oracle-jdk8-installer  && \
    apt-get clean  && \
    rm -rf /var/lib/apt/lists/*

RUN echo "Reset."

#Get the project
RUN git clone https://github.com/caseycas/gitcproc /home/gitcproc
WORKDIR /home/gitcproc
RUN git pull

#Set up a database in postgresql? Or do this in the docker.

#Install needed python libraries
RUN pip2 install --upgrade pip
RUN pip2 install nltk GitPython PyYAML
RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader wordnet
RUN pip2 install psycopg2


#ENTRYPOINT ["/bin/bash"]
