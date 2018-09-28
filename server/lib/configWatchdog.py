#!/usr/bin/python2

# written by sqall
# twitter: https://twitter.com/sqall01
# blog: http://blog.h4des.org
# github: https://github.com/sqall01
#
# Licensed under the GNU Affero General Public License, version 3.

import threading
import time
import logging
import os
import hashlib
from userBackend import CSVBackend


# This class handles all changes to configurations that can be handled
# at runtime.
class ConfigWatchdog(threading.Thread):

	def __init__(self, globalData, configCheckInterval):
		threading.Thread.__init__(self)

		# Get global configured data
		self.globalData = globalData
		self.logger = self.globalData.logger
		self.userBackend = self.globalData.userBackend

		# File name of this file (used for logging)
		self.fileName = os.path.basename(__file__)

		# Get value for the configured check interval.
		self.configCheckInterval = configCheckInterval

		# Set exit flag as false
		self.exitFlag = False

		# Set which configuration files should be checked.
		self.CSVUsersCheck = False
		self.CSVUsersHash  = ""
		self.CSVUsersFile = self.globalData.userBackendCsvFile
		self.CSVUsersLastCheck = 0.0
		if isinstance(self.userBackend, CSVBackend):
			self.CSVUsersCheck = True


	def _createHash(self, fileLocation):
		md5 = hashlib.md5()
		with open(fileLocation, 'rb') as fp:
			while True:
				data = fp.read(4096)
				if not data:
					break
				md5.update(data)

		return md5.hexdigest()


	def run(self):

		if self.CSVUsersCheck and os.path.isfile(self.CSVUsersFile):
			self.CSVUsersHash = self._createHash(self.CSVUsersFile)
			self.CSVUsersLastCheck = int(time.time())

		while True:
			# Wait 5 seconds before checking time of last received data.
			for i in range(5):
				if self.exitFlag:
					self.logger.info("[%s]: Exiting ConfigWatchdog."
						% self.fileName)
					return
				time.sleep(1)

			# Check CSV users file if we are using it.
			if self.CSVUsersCheck:
				diffTime = int(time.time()) - self.CSVUsersLastCheck
				if diffTime > self.configCheckInterval:

					self.logger.debug("[%s]: Checking changes of "
						% self.fileName
						+ "CSV users file.")

					newHash = self._createHash(self.CSVUsersFile)
					self.CSVUsersLastCheck = int(time.time())

					# Reload CSV users file if it has changed.
					if self.CSVUsersHash != newHash:

						self.logger.info("[%s]: CSV users file changed."
							% self.fileName)

						self.CSVUsersHash = newHash
						self.userBackend.readUserdata()