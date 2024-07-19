import os
import sys
import json
import time
import psutil
import shutil
import subprocess
import send2trash
from loguru import logger
import colorout as out

VERSION={
"appName":"BackupData",
"appNameCN":"数据备份工具",
"versionUpdate":[
{
	"mainVersion":"1.0.3",
	"dateVersion":"20240719",
	"versionDesc":[
		"优化\\*通配符文件遇到错误时的处理方式。",
	""]
},
{
	"mainVersion":"1.0.2",
	"dateVersion":"20240718",
	"versionDesc":[
		"加入日志功能。",
		"加入统计执行时间功能。",
		"加入计算文件大小功能。",
	""]
},
{
	"mainVersion":"1.0.1",
	"dateVersion":"20240712",
	"versionDesc":[
		"加入\\*通配符匹配多文件功能。",
		"修复无法识别配置中的中文路径的bug。",
	""]
},
{
	"mainVersion":"1.0",
	"dateVersion":"20240710",
	"versionDesc":[
		"实现需求功能。",
	""]
},
{
	"mainVersion":"1.0",
	"dateVersion":"20240709",
	"versionDesc":[
		"完成读取配置文件功能。",
	""]
},
{
	"mainVersion":"1.0",
	"dateVersion":"20240708",
	"versionDesc":[
		"初始版本。",
	""]
}
]
}

'''
Configs
'''
defaultConfig='config.json'
backupLog='backup.log'
'''
Utils
'''
def cmd(c):
	os.system(c)

def wait(n):
	time.sleep(n)

def runBat(batStr,output=''):
	batFile=f'{output}temp.bat'
	writeFile(batFile,batStr)
	if not exist(batFile):
		logger.error(f'{batFile} not exist!')
		return
	os.system([rf'"{batFile}"'])
	os.remove(batFile)

def run(exe='', params=[]):
	exeList=[exe]+params
	return subprocess.call(exeList)

def pause(c=None):
	if c:
		print(c)
	cmd('pause>nul')

def cwd():
	return os.getcwd()

def exist(dirs):
	return os.path.exists(dirs)

def loadFile(file,tp='r',encoding='utf-8'):
	try:
		f=open(file,tp,encoding=encoding)
		fs=f.read()
		f.close()
		return fs
	except:
		return None

def writeFile(file,data,tp='w',encoding='utf-8'):
	try:
		f=open(file,tp,encoding=encoding)
		f.write(data)
		f.close()
		return True
	except:
		return False
	
def getCWDPath():
	argv=sys.argv
	cwd=os.getcwd()
	executable=sys.executable
	return {
		'execFileName':argv[0].split('\\')[-1],
		'executable':executable,
		'argv0':argv[0],
		'argv':argv,
		'cwd':cwd,
		'realPath':os.path.realpath(sys.executable),
		'dirname':os.path.dirname(os.path.realpath(argv[0])),
		'realDirname':os.path.dirname(os.path.realpath(sys.executable)),
	}

def getFileList(addr):
	fileList=[]
	if not exist(addr):
		pass
	elif not os.path.isdir(addr):
		fileList.append(addr) 
	else:
		fileNames=os.listdir(addr)
		for file in fileNames:
			curPath=os.path.join(addr,file)
			if not os.path.isdir(curPath):
				fileList.append(curPath)
	return fileList


def getAllFileList(addr,includeFolders=False):
	allFileList={'files':[],'folders':[]}
	if not exist(addr): #路径不存在的情况
		pass
	elif not os.path.isdir(addr): #路径为文件的情况
		allFileList['files'].append(addr)
	else: #路径为文件夹的情况
		for root, dirs, files in os.walk(addr):
			for name in files:
				allFileList['files'].append(os.path.join(root, name))
			for name in dirs:
				allFileList['folders'].append(os.path.join(root, name))
	if includeFolders==True:
		return allFileList
	else:
		return allFileList['files']

def getAllFileSize(fileList):
	fileSize=0
	for file in fileList:
		fileSize+=os.path.getsize(file)
	return fileSize

def formatFileSize(b):
	units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
	size = b
	unitIndex = 0
	while size >= 1024 and unitIndex < len(units) - 1:
		size /= 1024
		unitIndex+=1
	
	# 保留两位小数，四舍五入
	size = round(size * 100) / 100
	return f'{size} {units[unitIndex]}'

def formatSeconds(s):
	timeObj=time.gmtime(s)
	timeStr=''
	if s<60:
		timeStr=f'{round(s,2)}秒'
	else:
		if timeObj.tm_yday-1>0:
			timeStr+=f'{timeObj.tm_yday-1}天'
		if timeObj.tm_hour>0:
			timeStr+=f'{timeObj.tm_hour}小时'
		if timeObj.tm_min>0:
			timeStr+=f'{timeObj.tm_min}分'
		if timeObj.tm_sec>=0:
			timeStr+=f'{timeObj.tm_sec}秒'
	return timeStr

def getProcess():
	processList=[]
	for process in psutil.process_iter(['name']):
		processList.append(process.info['name'].lower())
	return processList

def makeOutputDir(addr):
	dirs=f'{addr}'
	if not exist(dirs):
		os.makedirs(dirs)
	return dirs

configData={}
def loadConfig(file):
	global configData
	fileData=loadFile(file)
	try:
		configData=json.loads(fileData)
		return True
	except Exception as e:
		return False

def outLog(log='',tp='log'):
	logPath=f'{backupRoot}\\{backupLog}'
	if log=='':
		logStr='\n'
	else:
		curTime=time.strftime('%Y-%m-%d %H:%M:%S')
		logStr=f'[{curTime}] {tp.upper()}: {log}\n'
	f=open(logPath,'a',encoding='utf-8')
	f.write(logStr)
	f.close()

def printTitle():
	version=f'v{VERSION["versionUpdate"][0]["mainVersion"]} Build {VERSION["versionUpdate"][0]["dateVersion"]}'
	os.system('cls')
	os.system(f'title {VERSION["appNameCN"]} {version}')
	out.outlnC(f'-=<欢迎使用{VERSION["appNameCN"]}！>=-','purple','black',1)
	out.outlnC(f'{version}','purple','black',1)
	out.outln('')
	return version

def checkProcessList(bkList):
	processList=getProcess()
	checkedList=[]
	for bk in bkList:
		if not bk['enabled']:
			continue
		for ps in bk['process']:
			if ps.lower() in processList:
				checkedList.append(ps)
	return checkedList

backupRoot=''
def initBackup():
	global backupRoot
	out.outlnC('即将进行备份的内容：','cyan','black',1)
	bkList=configData['backupList']
	for bk in bkList:
		if not bk['enabled']:
			continue
		out.outlnC(f' > {bk["name"]}','yellow','black',1)
	out.outC('按任意键开始备份数据！','cyan','black',1)
	pause()
	
	while True:
		psList=checkProcessList(bkList)
		if len(psList)>0:
			psListStr='\n * '.join(psList)
			out.outlnC(f'\n检测到以下程序正在运行，请退出后再试：','cyan','black',1)
			out.outlnC(f' * {psListStr}','yellow','black',1)
			out.outC('按任意键重试！','cyan','black',1)
			pause()
		else:
			break
	
	while True:
		backupTime=time.strftime('%Y%m%d_%H%M%S')
		backupRoot=makeOutputDir(f'{configData["backupPath"]}\\{backupTime}')
		if exist(backupRoot):
			out.outlnC(f'\n备份路径：{backupRoot}','purple','black',1)
			outLog(f'Create backup root: {backupRoot} Success','CREATE_BACKUP')
			break
		else:
			out.outlnC(f'\n备份路径：{backupRoot}创建失败！按任意键重试！','red','black',1)
			pause()
	
	out.outlnC('正在备份数据，请稍候……','cyan','black',1)
	isBackupSuccess=True
	allBeginTime=time.time()
	for bk in bkList:
		if not bk['enabled']:
			continue
		bkBeginTime=time.time()
		out.outlnC(f' > 正在备份：{bk["name"]}','yellow','black',1)
		outLog(f'Begin backup: {bk["name"]}','BEGIN_BACKUP')
		backupPath=makeOutputDir(f'{backupRoot}\\{bk["name"]}')
		for p in bk['path']:
			pName=p.split('\\')[-1]
			try:
				if os.path.isdir(p):
					# 备份路径为文件夹
					beginTime=time.time()
					sizef=formatFileSize(getAllFileSize(getAllFileList(p)))
					out.outC(f'   > {p} {sizef}','white','black',1)
					shutil.copytree(p,backupPath+"\\"+pName)
					endTime=time.time()
					usedTime=formatSeconds(endTime - beginTime)
					out.outlnC(f' [成功，用时{usedTime}]','green','black',1)
					outLog(f'{p} {sizef} UsedTime: {usedTime}','COPY_FOLDER')
				else:
					# 备份路径为文件
					if '*' in p:
						# 处理*通配符的情况
						psp=p.split('\\')
						pnamesp=psp[-1].split('.')
						psp.pop()
						fileList=[fl for fl in getFileList('\\'.join(psp)) if len(pnamesp)==1 or f'.{pnamesp[1]}' in fl]
						for f in fileList:
							try:
								beginTime=time.time()
								sizef=formatFileSize(os.path.getsize(f))
								out.outC(f'   > {f} {sizef}','white','black',1)
								shutil.copy2(f,backupPath)
								endTime=time.time()
								usedTime=formatSeconds(endTime - beginTime)
								out.outlnC(f' [成功，用时{usedTime}]','green','black',1)
								outLog(f'{f} {sizef} UsedTime: {usedTime}','COPY_FILE')
							except Exception as e:
								out.outlnC(' [失败]','red','black',1)
								outLog(f'{f} Error: {e}','COPY_FILE')
								logger.exception('Exception')
								isBackupSuccess=False
					else:
						beginTime=time.time()
						sizef=formatFileSize(os.path.getsize(p))
						out.outC(f'   > {p} {sizef}','white','black',1)
						shutil.copy2(p,backupPath+"\\"+pName)
						endTime=time.time()
						usedTime=formatSeconds(endTime - beginTime)
						out.outlnC(f' [成功，用时{usedTime}]','green','black',1)
						outLog(f'{p} {sizef} UsedTime: {usedTime}','COPY_FILE')
			except Exception as e:
				out.outlnC(' [失败]','red','black',1)
				outLog(f'{p} Error: {e}','COPY_FILE')
				logger.exception('Exception')
				isBackupSuccess=False
		bkEndTime=time.time()
		bkUsedTime=formatSeconds(bkEndTime - bkBeginTime)
		out.outlnC(f' > 备份完成：{bk["name"]}，用时{bkUsedTime}','green','black',1)
		out.outln()
		outLog(f'Finish backup: {bk["name"]} UsedTime: {bkUsedTime}','FINISH_BACKUP')
		outLog()
	
	allEndTime=time.time()
	allUsedTime=formatSeconds(allEndTime - allBeginTime)
	if isBackupSuccess:
		out.outlnC(f'所有数据备份成功！用时{allUsedTime}，按任意键退出。','green','black',1)
		outLog(f'All data backup success. UsedTime: {allUsedTime}','BACKUP_RESULT')
	else:
		out.outlnC(f'部分数据备份失败！用时{allUsedTime}，按任意键退出。','red','black',1)
		outLog(f'Some data backup failed. UsedTime: {allUsedTime}','BACKUP_RESULT')
	pause()


def main(args):
	os.system('cls')
	out.outlnC('正在读取配置数据，请稍候……','cyan','black',1)
	cfgLoadSuccess=False
	try:
		if len(args)<2: # 默认配置文件，config.json
			cfgLoadSuccess=loadConfig(defaultConfig)
		elif len(args)==2: # 传参配置文件
			cfgLoadSuccess=loadConfig(args[1])
		else:
			out.outlnC('未找到配置文件！按任意键重试！','red','black',1)
			pause()
			main([args[0]]) # 传参配置文件读取失败时，尝试读取默认配置文件
		if cfgLoadSuccess:
			printTitle()
			initBackup()
		else:
			out.outlnC('配置文件读取失败！按任意键重试！','red','black',1)
			pause()
			main([args[0]]) # 传参配置文件读取失败时，尝试读取默认配置文件
	except Exception as e:
		out.outlnC(f'配置文件读取错误！','red','black',1)
		logger.exception('Exception')
		out.outln('按任意键退出。')

if __name__=='__main__':
	main(sys.argv)