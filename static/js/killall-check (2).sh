#!/bin/bash
VER="Trojan Scanner v1.8, 11/07/2014. Author: Jin Bai(PT)"

CHATTR="/usr/bin/chattr"

RPM="
openssh-server
coreutils
findutils
lsof
net-tools
procps
psmisc
"

PROCESS="
[222]
java.1
squid1
chinacache
tomcat-manager
vncserver
vnc
Xvnc
java-jdk
java-jdks
.ctrl
.rst
rst
ttyload
getty
ttymon
scanssh
linuxx
.IptabLes
.IptabLex
dbus-sshd
dbus-fx
lsi_mrdsnmp
xnode
CHN-24
CHN-64
coppy
dashuai
diols
dos
dosh
dx
shl
sshpa
megaeyes_cms_db
CapsLK
L26
cache
Javar
Javar64
dbus-java
linux
linuxx
linuxxx
bsd-port
node26
nodeJR
pscan2
.sshd
.sshf
bassh
basshh
Blueit
mafix
mafixlibs
"

FILE="
/lib/jwswtr.rd
/root/rm
/root/gosh.jpg
/tmp/mafix
/tmp/mafixlibs
/bin/java-jdk
/etc/chinacache
/etc/tomcat-manager
/root/chinacache
/etc/squid
/etc/squid1
/etc/java-jdks
/etc/linuxx
/etc/init.d/.IptabLes
/etc/init.d/.IptabLex
/etc/init.d/IptabLes
/etc/init.d/IptabLex
/etc/dbus-sshd
/etc/dx
/etc/ssh/sshpa
/etc/dbus-java
/etc/java
/etc/linuxx
/etc/init.d/DbSecuritySpt
/etc/init.d/DbSecurityMdt
/etc/bassh
/etc/basshh
/root/s
/root/Internet
/root/Server
/root/SYSTEM
/root/Xiang
/root/Xiao
/root/.ctrl
/root/bash
/tmp/scanssh
/tmp/scanner
/tmp/bios.txt
/tmp/mass
/tmp/x
/boot/.IptabLes
/boot/.IptabLex
/root/dbus-fx
/root/lsi_mrdsnmp
/tmp/zero.pl
/usr/xnode
/root/CHN-24
/root/CHN-64
/usr/coppy
/usr/bin/dashuai
/usr/diols
/usr/bin/dos
/usr/bin/dosh
/usr/bin/shl
/root/megaeyes_cms_db
/root/CapsLK
/root/L26
/tmp/cache
/usr/Javar
/usr/Javar64
/lib/udev/udev
/root/fake.cfg
/tmp/gates.lock
/tmp/gates.lod
/tmp/moni.lod
/root/.rst
/root/rst
/root/.bash_historys
/root/.aassh
/root/.pro
/root/64
/root/bin/linux
/root/s1hh
/root/ssh32
/root/ssh64
/root/svchost
/root/svchosts
/root/x64
/root/xnode
/root/zv32
/root/zv64
/tmp/qs8glscl
/root/squid
/usr/linux
/root/linuxx
/usr/linuxxx
/usr/bin/bsd-port
/usr/ip
/sbin/ttyload
/sbin/ttymon
/root/node26
/root/nodeJR
/usr/node
/tmp/pscan2
/root/syslogd
/usr/bin/acpid
/usr/bin/.sshd
/usr/bin/.sshf
/tmp/bill.lock
/root/Blueit
"

DIR="
/boot/es
/root/es
/tmp/es
/root/gosh
/root/muma
/usr/lib/libsh
/usr/bin/dpkgd
/var/.blueshield
/usr/bin/bsd-port
"

PROTECT="
/etc/bashrc
/etc/profile
/etc/resolv.conf
/etc/shadow
/etc/passwd
/etc/group
/root/.bashrc
/root/.bash_profile
/root/.bash_logout
"

function checking_per_pid() {
	for i in /proc/[1-9]*
#	for i in /proc/7040
	do
		DELETE=""
#		if [ "`cat $i/cmdline 2>/dev/null`" != "" ]
#		then
			PID=`echo $i | awk -F'/' '{print $NF}'`
			PROCESS_LNAME=`cat $i/cmdline 2>/dev/null| sed 's/\x0/ /g' | awk '{print $1}'`
			PROCESS_SNAME=`basename $PROCESS_LNAME 2>/dev/null`
			LS=`ls -al $i/exe 2>/dev/null`
			EXE=`echo $LS | awk '{print $NF}'`
			if [ "$EXE" = "(deleted)" ]
			then
				EXE=`echo $LS | awk '{print $(NF-1)}'`
				DELETE=`echo $LS | awk '{print $NF}'`
			fi
#			echo "PID: $PID"
#			echo "PROCESS_LNAME: $PROCESS_LNAME ($PROCESS_SNAME)"
#			echo "EXE: $EXE"
#			echo "DELETE: $DELETE"
#			echo "LS: $LS"
#			if [ "$DELETE" = "(deleted)" ] && [ "`echo $EXE | egrep '^/boot|^/root|^/tmp|^/etc|^/var|^/misc|^/bin|^/sbin|^/usr/bin|^/usr/sbin' | grep -v '/tmp/par'`" != "" ]
			if [ "$DELETE" = "(deleted)" ] && [ "`echo $EXE | egrep '^/boot|^/root|^/tmp|^/etc|^/var|^/misc' | grep -v '/tmp/par'`" != "" ]
#			if [ "$DELETE" = "(deleted)" ]
			then
				echo "*** Found Trojan Process: $PROCESS_LNAME($PID) -> File: $EXE(MD5 Error)"
				VULN="1"
			fi
#		fi
	done
}

function killing_progs() {
	for i in $PROCESS; do
		if [ "$i" = "getty" ] && [ "`head -1 /etc/issue | grep -i 'ubuntu'`" != "" ]
		then
			continue
		fi
		KILL_RESULT=`sudo -u bin killall -9 $i 2>&1 | grep 'Operation not permitted'`
		if [ "$KILL_RESULT" != "" ]; then
			echo "*** Found Trojan Process: `echo $KILL_RESULT | awk '{print $1}' | sed 's/://'`"
                        if [ "$i" == "Xvnc" ]; then
                                killall -9 $i
                        fi
			VULN="1"
		fi
	done
}

function killing_progs_special() {
	killall -9 syslogd &>/dev/null
	service syslog restart &>/dev/null
	service syslog-ng restart &>/dev/null
}

function cleaning_files() {
	for i in $FILE; do
		if [ -f $i ]; then
			echo "*** Found Trojan File: $i" && VULN="1"
		fi
		if [ -f $i.1 ]; then
			echo "*** Found Trojan File: $i.1" && VULN="1"
		fi
		if [ -f $i.2 ]; then
			echo "*** Found Trojan File: $i.2" && VULN="1"
		fi
	done
}

KNOWN_FILES="
lotServerInstaller.sh
"

function cleaning_keyword_files() {
	for F in `find /boot /root /etc /tmp /usr /var /opt /misc -type f -size -10240k -size +100c -maxdepth 1 2>/dev/null`
	do
		KNOWN_FILE="0"
		for FF in $KNOWN_FILES; do
			if [ "`echo $F | grep $FF`" != "" ]; then
				KNOWN_FILE="1"
				break;
			fi
		done
		if [ "$KNOWN_FILE" != "1" ] && [ "`egrep -rn 'Keld Simonsen|Enjoy the shell' $F 2>/dev/null`" != "" ]
		then
			TROJAN_PROCESS=`ps aux | grep $F | grep -v grep`
			PID=`echo $TROJAN_PROCESS | awk '{print $2}'`
			if [ "$PID" != "" ]
			then
				KILL_RESULT=`sudo -u bin kill -9 $PID 2>&1 | grep 'Operation not permitted'`
				if [ "$KILL_RESULT" != "" ]; then
					echo "*** Found Trojan Process:"
					echo "$TROJAN_PROCESS"
					VULN="1"
				fi
			fi
			echo "*** Found Trojan Fingerprint File: $F"
			VULN="1"
		fi
	done
}

function cleaning_files_special() {
	if [ "`head -1 /etc/issue | grep -i 'ubuntu'`" != "" ]
	then
		return
	fi
	if [ "`grep ttyload /etc/inittab`" != "" ]
	then
		echo "*** Found: ttyload in /etc/inittab"
		VULN="1"
	fi
}

function cleaning_dirs() {
	for i in $DIR; do
		if [ -d $i ]; then
			echo "*** Found Trojan Directory: $i" && VULN="1"
		fi
	done
}

function correcting_env() {
	PATH="/bin:/sbin:/usr/bin:/usr/sbin:$PATH"
	if [ -d /usr/lib/libsh/.backup ]; then
		PATH="/usr/lib/libsh/.backup:$PATH"
		echo "*** Found Rootkit backup files, add /usr/lib/libsh/.backup to PATH temperature."
	elif [ -d /usr/bin/dpkgd ]; then
		PATH="/usr/bin/dpkgd:$PATH"
		echo "*** Found Rootkit backup files, add /usr/bin/dpkgd to PATH temperature."
	elif [ -d /var/.blueshield/libsh/.backup ]; then
		PATH="/var/.blueshield/libsh/.backup:$PATH"
		echo "*** Found Rootkit backup files by BlueShield, add /var/.blueshield/libsh/.backup to PATH temperature."
	fi

	if [ ! -f /root/.bash_profile ]; then
		echo "### NO ROOT Directory."
		VULN="1"
	fi

	chmod 755 $CHATTR &>/dev/null

#	SSHCHECK=`find /root/.ssh -type f 2>/dev/null`
#	if [ "$SSHCHECK" != "" ]; then
#		echo "### Found SSH Certification:"
#		ls -al /root/.ssh
#		VULN="1"
#	fi

	sed -i 's/^\(Defaults.*requiretty\)/#\1/' /etc/sudoers &>/dev/null

	CHMOD=`ls -al /usr/bin/wget | awk '{print $1}' | egrep 'x'`
	if [ "$CHMOD" = "" ]
	then
		echo "*** WTF: `ls -al /usr/bin/wget`"
		VULN="1"
		ATTR=`lsattr /usr/bin/wget | awk '{print $1}' | egrep 'a|i'`
		if [ "$ATTR" != "" ]
		then
			echo "*** WTF: `lsattr /usr/bin/wget`"
			VULN="1"
			$CHATTR -ai /usr/bin/wget &>/dev/null
		fi
		chmod 755 /usr/bin/wget &>/dev/null
	fi

	IPTABLES=`iptables-save 2>&1 | egrep '(19009|3333).*ACCEPT'`
	if [ "$IPTABLES" != "" ]
	then
		echo "*** WTF: $IPTABLES"
		VULN="1"
	fi

	PASSWD=`grep ':0:0:' /etc/passwd | grep -v '^root:x:0:0:'`
	if [ "$PASSWD" != "" ]
	then
		echo "*** Found ANOTHER ROOT ACCOUNT in /etc/passwd"
		VULN="1"
		ACCOUNT=`echo "$PASSWD" | awk -F ':' '{print $1}'`
		SHADOW=`grep "^$ACCOUNT:" /etc/shadow`
		echo -e "*** /etc/passwd:\n$PASSWD"
		echo -e "*** /etc/shadow:\n$SHADOW"
	fi

	for i in $RPM
	do
		RPMSTAT=`rpm -V $i 2>&1 | egrep '^..5.*/bin/|^..5.*/sbin/'`
		if [ "$RPMSTAT" != "" ]
		then
			echo "RPM Package \"$i\": MD5 checksum error"
			echo "$RPMSTAT"
			VULN="1"
		fi
	done
}

function bashcheck() {
	r=`x="() { :; }; echo x" bash -c ""`
	if [ -n "$r" ]; then
		echo "+++ Vulnerable to CVE-2014-6271 (original shellshock)"
		VULN="1"
	fi

	cd /tmp;rm echo 2>/dev/null
	X='() { function a a>\' bash -c echo 2>/dev/null > /dev/null
	if [ -e echo ]; then
		echo "+++ Vulnerable to CVE-2014-7169 (taviso bug)"
		VULN="1"
	fi

	bash -c "`for i in {1..200}; do echo -n "for x$i in; do :;"; done; for i in {1..200}; do echo -n "done;";done`" 2>/dev/null
	if [ $? != 0 ]; then
		echo "+++ Vulnerable to CVE-2014-7187 (nested loops off by one)"
		VULN="1"
	fi

	r=`a="() { echo x;}" bash -c a 2>/dev/null`
	if [ -n "$r" ]; then
		echo "+++ Variable function parser still active, likely vulnerable to yet unknown parser bugs like CVE-2014-6277 (lcamtuf bug)"
		VULN="1"
	fi
}

function ohacl() {
	if [ -d /Application/oh/etc ]
	then
		if [ ! -f /Application/oh/etc/config.yaml ]
		then
			cp -f /Application/oh/etc/config.yaml.default /Application/oh/etc/config.yaml
			sed -i 's/Acl: disable/Acl: enable/g' /Application/oh/etc/config.yaml &>/dev/null
		fi
		amr restart oh &>/dev/null
		if [ "$?" != 0 ] && [ "`tail -2 /etc/hosts.allow | grep 'sshd.*deny'`" = "" ]; then
			echo "### WARNING: OH ACL cannot work well."
		fi
	fi
}

# start from here

export LANG=C
export LC_ALL=C

# Self Checking
correcting_env
ohacl

# Trojans Check
cleaning_files_special
cleaning_files
cleaning_dirs
killing_progs
#killing_progs_special
cleaning_keyword_files
checking_per_pid
# Bash Check
bashcheck

if [ "$REINSTALL" = "1" ]; then
	echo "REINSTALL"
elif [ "$VULN" != "1" ]; then
	echo "PASSED"
fi
