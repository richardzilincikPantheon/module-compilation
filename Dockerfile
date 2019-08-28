FROM ubuntu:latest
ARG YANG_ID_GID

ENV YANG_ID_GID "$YANG_ID_GID"
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/sdo_analysis

RUN groupadd -r yang \
  && useradd --no-log-init -r -g yang -u ${YANG_ID_GID} -d $VIRTUAL_ENV yang

#Install Cron
RUN apt-get update
RUN apt-get -y install cron \
  && apt-get autoremove -y

COPY ./sdo_analysis $VIRTUAL_ENV
COPY ./resources/* $VIRTUAL_ENV/

WORKDIR $VIRTUAL_ENV

ENV confd_version 6.7

RUN apt-get update
RUN apt-get install -y \
    wget \
    gnupg2

RUN apt-get update \
  && apt-get -y install clang cmake libpcre3-dev git libxml2-dev \
  && cd /home; mkdir w3cgrep \
  && cd /home; git clone https://github.com/CESNET/libyang.git \
  && cd /home/libyang; mkdir build \
  && cd /home/libyang/build && cmake .. && make && make install

# Install Java.
RUN \
  apt-get update && \
#  apt-get install -y libffi libssl1.0 libcrypto.so.6 openjdk-7-jdk openssh-client build-essential ant && \
   apt-get -y install rsync python3.6 python3-pip && \
   apt-get install -y openssh-client build-essential libssl-dev libssl1.0.0

RUN cd /home; git clone https://github.com/decalage2/pyhtgen.git \
  && mv setup.py /home/pyhtgen/pyhtgen; cd /home/pyhtgen/pyhtgen;  python setup.py install

RUN apt-get install -y \
    openssh-client \
    && rm  -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install requests
RUN pip3 install xym
RUN pip3 install -r requirements.txt

RUN mkdir /opt/confd
RUN /sdo_analysis/confd-${confd_version}.linux.x86_64.installer.bin /opt/confd

RUN dpkg -i yumapro-client-18.10-9.u1804.amd64.deb

RUN chmod 0777 bin/configure.sh

COPY ./conf/yangdump-pro.conf /etc/yumapro/yangdump-pro.conf
COPY ./conf/yangdump-pro-allinclusive.conf /etc/yumapro/yangdump-pro-allinclusive.conf

# Add crontab file in the cron directory
COPY ./sdo_analysis/crontab /etc/cron.d/ietf-cron

RUN chown yang:yang /etc/cron.d/ietf-cron
USER ${YANG_ID_GID}:0

# Apply cron job
RUN crontab /etc/cron.d/ietf-cron

USER root:root

ENV PYTHONPATH=$VIRTUAL_ENV/bin/python
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git

ENV YANG=/.
ENV YANGVAR="get_config.py --section Directory-Section --key var"
ENV BIN=$YANG/sdo_analysis/bin
ENV CONF=$YANG/sdo_analysis/conf
ENV BACKUPDIR="get_config.py --section Directory-Section --key backup"
ENV CONFD_DIR="get_config.py --section Tool-Section --key confd_dir"
ENV PYANG="get_config.py --section Tool-Section --key pyang_exec"

#
# Repositories
#
ENV NONIETFDIR="get_config.py --section Directory-Section --key non_ietf_directory"
ENV IETFDIR="get_config.py --section Directory-Section --key ietf_directory"
ENV MODULES="get_config.py --section Directory-Section --key modules_directory"

#
# Working directories
ENV LOGS="get_config.py --section Directory-Section --key logs"
ENV TMP="get_config.py --section Directory-Section --key temp"

#
# Where the HTML pages lie
#
ENV WEB_PRIVATE="get_config.py --section Web-Section --key private_directory"
ENV WEB_DOWNLOADABLES="get_config.py --section Web-Section --key downloadables_directory"
ENV WEB="get_config.py --section Web-Section --key public_directory"

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/ietf-cron

# Run the command on container startup
CMD cron -f && tail -f /var/yang/logs/cronjob-daily.log
