import datetime, os
import urllib, urllib2, base64
import xml.etree.ElementTree as ET

class CampusNetDrop():
	def __init__(self):
		# self.dirname, self.filename = os.path.split(os.path.abspath(__file__))
		self.dirname="."
		self.log = None
		self.dl = None

	def setLogTable(self,logTable):
		self.log = logTable
		self.log.writeLog(199)

	def setDlTab(self,dlTab):
		self.dl = dlTab

	def initDlTab(self):
		try:
			courses = self.readConfigFile()
			for course in courses:
				if int(course['studentfolder'])==1:
					studentfolder=True
				else:
					studentfolder=False
				self.dl.writeCourse(course['name'],course['elementID'],dlCourse=True,studentfolder=studentfolder,path=course['directory'])
		except IOError:
			pass

	def login(self,username,password):
		self.log.writeLog(100, username)

		username = username.strip()
		password = password.strip()
		if len(password)>0:
			# Login request
			url = 'https://auth.dtu.dk/dtu/mobilapp.jsp'
			values = { 'username' : username, 'password' : password}
			data = urllib.urlencode(values)
			req = urllib2.Request(url,data)
			try:
				response = urllib2.urlopen(req)
				root = ET.fromstring(response.read())
				try:
					# Get Permanent Access Password
					PApassword = root.findall('LimitedAccess')[0].get('Password')
					# Save it into directory of the running script
					f = open(self.dirname+'/lmtdAccss.txt','w')
					f.write(PApassword+"\n")
					f.write(username)
					f.close()
					# log
					self.log.writeLog(101)
					self.log.writeLog(102)
				except IndexError:
					self.log.writeLog(201)
			except urllib2.URLError:
				self.log.writeLog(200)
		else:
			self.log.writeLog(201)

	def getCourses(self):
		self.log.writeLog(103)
		# Create request and load XML into 'root'
		url = 'https://www.campusnet.dtu.dk/data/CurrentUser/Elements'
		try:
			req = self.createRequest(url)
			try:
				response = urllib2.urlopen(req)
				root = ET.fromstring(response.read())
				self.dl.clear()
				for node in root:
					for child in node:
						self.dl.writeCourse(child.get('Name'),child.get('Id'))
				self.log.writeLog(104)
				self.log.writeLog(105)
				self.log.writeLog(106)
				self.log.writeLog(107)
			except urllib2.URLError:
				self.log.writeLog(200)
		except:
			self.log.writeLog(202)

	def downloadCourseContents(self):
		root = self.dl.tree.invisibleRootItem()
		child_count = root.childCount()
		rdy_to_download = False
		# Check if anything is in the table - 205
		if not child_count == 0:
			ticked_child_count = 0
			allSet = True
			for i in range(child_count):
				item = root.child(i)
				if item.checkState(0):
					ticked_child_count=ticked_child_count+1
					if item.text(2)=="DOUBLE CLICK HERE TO SET PATH" or len(item.text(2))==0:
						allSet = False
			# check if anything is ticked - 203
			if not ticked_child_count==0:
				# check if all paths are set - 204
				if allSet:
					# write each course into config file
					f = open(self.dirname+'/config.txt','w')
					for i in range(child_count):
						item = root.child(i)
						if item.checkState(0):
							if item.checkState(1):
								studentfolder=1
							else:
								studentfolder=0
							directory=item.text(2).replace("\\","/")
							f.write(item.text(0)+";"+item.text(3)+";"+directory+";"+str(studentfolder)+"\n")
					f.close()
					rdy_to_download = True
				else:
					self.log.writeLog(204)
			else:
				self.log.writeLog(203)
		else:
			self.log.writeLog(205)

		if rdy_to_download:
			courses = self.readConfigFile()

			for course in courses:
				url='https://www.campusnet.dtu.dk/data/CurrentUser/Elements/%s/Files' % (course['elementID'])
				try:
					req = self.createRequest(url)
					try:
						self.log.writeLog(112, course['name'])
						response = urllib2.urlopen(req)
						root = ET.fromstring(response.read())
						self.createFolders(root,str(course['directory']))
						to_download = []
						self.getFiles(root,"",to_download)
						for download in to_download:
							file_path = course['directory']+download['Path']+"/"+download['Name']
							if not ("Student folder" in file_path and int(course['studentfolder'])==0):
								if os.path.isfile(file_path):
									file_created = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
									if not file_created > download['Created']:
										self.download_file(course['elementID'],download['Id'],file_path)
									else:
										self.log.writeLog(109,file_path)
								else:
									self.download_file(course['elementID'],download['Id'],file_path)

					except urllib2.URLError:
						self.log.writeLog(200)
				except:
					self.log.writeLog(202)
				self.log.writeLog(111, course['name'])

	def createFolders(self,root,path):
		"""Run through XML nodes and copy folder structure into 'path' """
		for node in root:
			if node.tag == "Folder":
				self.createFolder(node.get('Name'),path)
				if len(node):
					self.createFolders(node,path+"/"+node.get('Name'))

	def createFolder(self,name,path):
		"""Create folder if not already there"""
		directory = path+"/"+name
		if not os.path.isdir(directory):
			self.log.writeLog(108, directory)
			os.makedirs(directory)

	def getFiles(self,root,path,to_download):
		"""Fill list of all files you could possible download"""
		for node in root:		
			if node.tag == "File":
				created = self.getLatestVersion(node)
				to_download.append({'Id':node.get('Id'), 'Name':node.get('Name'),'Path':path,'Created':created})
			if len(node):
				self.getFiles(node,path+"/"+node.get('Name'),to_download)

	def getLatestVersion(self,root):
		"""Check all versions for latest date"""
		first_run = True
		for node in root.iter('FileVersion'):
			if first_run:
				latest_date = datetime.datetime.strptime(node.get('Created').split(".")[0], "%Y-%m-%dT%H:%M:%S") 
			else:
				new_date = datetime.datetime.strptime(node.get('Created').split(".")[0], "%Y-%m-%dT%H:%M:%S") 
				if new_date > latest_date:
					latest_date = new_date
			first_run = False
		return latest_date

	def download_file(self,elementID,downloadID,file_path):
		"""Simply download a file"""
		self.log.writeLog(110,file_path)
		url='https://www.campusnet.dtu.dk/data/CurrentUser/Elements/%s/Files/%s/Bytes' % (str(elementID),str(downloadID))
		req = self.createRequest(url)
		try:
			response = urllib2.urlopen(req)
			data = response.read()
			with open(file_path, 'wb') as f:
				f.write(data)
		except urllib2.URLError:
			self.log.writeLog(200)

	def readConfigFile(self):
		configFile = open(self.dirname+'/config.txt')
		lines = configFile.readlines()
		configFile.close()
		courses = []
		for line in lines:
			line = line.strip()
			line = line.split(";")
			elementID = line[1]
			directory = line[2]
			courses.append({'name':line[0],'studentfolder':line[3],'directory':line[2],'elementID':line[1]})
		return courses

	def createRequest(self,url):
		with open(self.dirname+"/token.txt") as f:
			data=f.readlines()
		appName=data[0].strip()
		appToken=data[1].strip()
		lmtdAccssFile = open(self.dirname+'/lmtdAccss.txt')
		lines = lmtdAccssFile.readlines()
		lmtdAccssFile.close()
		PApassword = lines[0].strip()
		username = lines[1].strip()

		req = urllib2.Request(url)
		base64string = base64.standard_b64encode('%s:%s' % (username, PApassword))
		req.add_header("Authorization", "Basic %s" % base64string)
		req.add_header("X-appname", appName)
		req.add_header("X-token", appToken)

		return req
			