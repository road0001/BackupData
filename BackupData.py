import os
import sys
import json
import time
import psutil
import shutil
import threading
import subprocess
import send2trash
from loguru import logger
import colorout as out

'''
TODO
~将文件夹刷屏改为显示全体进度和单文件百分比~
'''

VERSION={
"appName":"BackupData",
"appNameCN":"数据备份工具",
"versionUpdate":[
{
	"mainVersion":"1.0.8",
	"dateVersion":"20240805",
	"versionDesc":[
		"优化日志输出逻辑，减轻写入量。",
		"修复复制文件报错的bug。",
		"修复复制文件计数错误的bug。",
	""]
},
{
	"mainVersion":"1.0.7",
	"dateVersion":"20240804",
	"versionDesc":[
		"加入文件复制进度显示。",
		"优化复制文件夹的算法。",
	""]
},
{
	"mainVersion":"1.0.6",
	"dateVersion":"20240725",
	"versionDesc":[
		"调整部分文字显示效果。",
	""]
},
{
	"mainVersion":"1.0.5",
	"dateVersion":"20240725",
	"versionDesc":[
		"加入单条目选择备份功能。",
		"加入验证备份后文件大小功能。",
	""]
},
{
	"mainVersion":"1.0.4",
	"dateVersion":"20240720",
	"versionDesc":[
		"加入多文件进度显示功能。",
		"优化条目显示方式。",
	""]
},
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

logArr=[]
def outLog(log='',tp='log'):
	global logArr
	if log=='':
		logStr='\n'
	else:
		curTime=time.strftime('%Y-%m-%d %H:%M:%S')
		logStr=f'[{curTime}] {tp.upper()}: {log}\n'
	logArr.append(logStr)

def writeLog():
	global logArr
	logPath=f'{backupRoot}\\{backupLog}'
	f=open(logPath,'a',encoding='utf-8')
	f.write(''.join(logArr))
	f.close()
	logArr=[]

def progress(cur, total, type='progress'):
	curStr=f'{cur}'
	totalStr=f'{total}'
	if type=='progress':
		return f'{curStr.rjust(len(totalStr))}/{total}'
	elif type=='percent':
		curStr+='%'
		totalStr+='%'
		bb='\b'*len(totalStr)
		return f'{curStr.rjust(len(totalStr))}{bb}'
	elif type=='number':
		return f'{curStr.rjust(len(totalStr))}'
	else:
		return curStr

def copyProcess(src, dst):
	srcSize=0
	dstSize=0
	count=0
	maxCount=300
	lastDstSize=0
	sizeLimit=104857600
	if os.path.isdir(dst):
		dst = os.path.join(dst, os.path.basename(src))
	while True:
		try:
			if os.path.exists(src):
				srcSize=os.path.getsize(src)
				if srcSize<=sizeLimit:
					return
			if os.path.exists(dst):
				dstSize=os.path.getsize(dst)
			if dstSize >= srcSize or srcSize<=0:
				dstSize = srcSize
				# c.outlnC(f'[完成]','green','black',1)
				return
			else:
				percent=int(dstSize / srcSize  * 100)
				out.outC(progress(percent, 99, 'percent'),'yellow','black',1)
			if dstSize != lastDstSize:
				lastDstSize=dstSize
				count=0
			else:
				count+=1
			if count >= maxCount:
				return
			time.sleep(0.1)
		except Exception as e:
			return

def copyWithInfo(f, backupPath, i, fileList, isFolder=False):
	try:
		beginTime=time.time()
		if isFolder:
			spaces='     '
			#end='     > [    236/1126185] 111205.3 MB [成功，用时{usedTime}]{end}'
			# end =f'{" "*70}\r'
			end ='\r'
			backupp=backupPath
			print(' '*70, end='\r', flush=True)
			# fileName=f.split('\\')[-1]
			out.outC(f'{spaces}> [{progress(i+1, len(fileList))}] ','white','black',1)
		else:
			spaces='   '
			end='\n'
			backupp=backupPath+"\\"+f.split('\\')[-1]
			out.outC(f'{spaces}> [{progress(i+1, len(fileList))}] {f} ','white','black',1)
		fileSize=os.path.getsize(f)
		sizef=formatFileSize(fileSize)
		out.outC(f'{sizef} ','yellow','black',1)
		
		t = threading.Thread(target=copyProcess, args=(f, backupp))
		t.start()
		shutil.copy2(f,backupp)
		
		backupFileSize=os.path.getsize(backupp)
		sizefb=formatFileSize(backupFileSize)
		endTime=time.time()
		usedTime=formatSeconds(endTime - beginTime)
		
		if fileSize==backupFileSize:
			out.outC(f'[成功，用时{usedTime}]{end}','green','black',1)
			outLog(f'[{progress(i+1, len(fileList))}] {f} {sizef} SUCCESS UsedTime: {usedTime}','COPY_FILE')
			return True
		else:
			out.outC(f'[大小不一致，用时{usedTime}]{end}','yellow','black',1)
			outLog(f'[{progress(i+1, len(fileList))}] {f} {sizef} {sizefb} SIZE_WRONG UsedTime: {usedTime}','COPY_FILE')
			return formatFileSize
	except Exception as e:
		out.outC(f' [失败]{end}','red','black',1)
		outLog(f'[{progress(i+1, len(fileList))}] {f} Error: {e}','COPY_FILE')
		logger.exception('Exception')
		return False

copyCount=0
def copyFolder(source_folder, destination_folder, fileList):
	global copyCount
	# 创建目标文件夹
	os.makedirs(destination_folder, exist_ok=True)
	# 遍历源文件夹中的所有文件和文件夹
	for item in os.listdir(source_folder):
		source_item = os.path.join(source_folder, item)
		destination_item = os.path.join(destination_folder, item)
		# 判断是否为文件夹
		if os.path.isdir(source_item):
			# 递归复制子文件夹
			copyFolder(source_item, destination_item, fileList)
		else:
			# 复制文件
			copyWithInfo(source_item, destination_item, copyCount, fileList, True)
			copyCount+=1

def copyTreeWithInfo(p, backupPath, i, fileList):
	try:
		beginTime=time.time()
		global copyCount
		isCopyTreeSuccess=True
		pName=p.split('\\')[-1]
		out.outC(f'   > [{progress(i+1, len(fileList))}] {p} ','white','black',1)
		allFileList=getAllFileList(p)
		out.outC(f'{len(allFileList)}个文件 ','white','black',1)
		fileSize=getAllFileSize(allFileList)
		sizef=formatFileSize(fileSize)
		out.outlnC(f'{sizef} ','yellow','black',1)
		backupp=backupPath+"\\"+pName
		copyCount=0
		copyFolder(p,backupp,allFileList)
		backupFileSize=getAllFileSize(getAllFileList(backupp))
		sizefb=formatFileSize(backupFileSize)
		endTime=time.time()
		usedTime=formatSeconds(endTime - beginTime)
		# print('\r', end='', flush=True)
		out.outln()
		if fileSize==backupFileSize:
			out.outlnC(f'   [成功，用时{usedTime}]','green','black',1)
			outLog(f'[{progress(i+1, len(fileList))}] {p} {sizef} SUCCESS UsedTime: {usedTime}','COPY_FOLDER')
			return isCopyTreeSuccess
		else:
			out.outlnC(f'   [大小不一致，用时{usedTime}]','yellow','black',1)
			outLog(f'[{progress(i+1, len(fileList))}] {p} {sizef} {sizefb} SIZE_WRONG UsedTime: {usedTime}','COPY_FOLDER')
			return False
	except Exception as e:
		out.outlnC(' [失败]','red','black',1)
		outLog(f'[{progress(i+1, len(fileList))}] {p} Error: {e}','COPY_FILE')
		logger.exception('Exception')
		isBackupSuccess=False

def printTitle():
	version=f'v{VERSION["versionUpdate"][0]["mainVersion"]} Build {VERSION["versionUpdate"][0]["dateVersion"]}'
	os.system('cls')
	os.system(f'title {VERSION["appNameCN"]} {version}')
	out.outlnC(f'-=<欢迎使用{VERSION["appNameCN"]}！>=-','purple','black',1)
	out.outlnC(f'{version}','purple','black',1)
	out.outln('')
	return version

def checkProcessList(bkList, index=-1):
	processList=getProcess()
	checkedList=[]
	for i,bk in enumerate(bkList):
		if index>=0 and index!=i:
			continue
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
	for i,bk in enumerate(bkList):
		if not bk['enabled']:
			continue
		out.outlnC(f' {progress(i+1, len(bkList), "number")}. {bk["name"]}','yellow','black',1)
	out.outC('按数字键选择要备份的数据，按回车键开始备份所有数据：','cyan','black',1)
	selectBackup=input()
	if selectBackup.isdigit():
		selectBackup=int(selectBackup)-1
	else:
		selectBackup=-1
	
	while True:
		psList=checkProcessList(bkList, selectBackup)
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
			outLog(f'Create backup root: {backupRoot} SUCCESS','CREATE_BACKUP')
			outLog()
			break
		else:
			out.outlnC(f'\n备份路径：{backupRoot}创建失败！按任意键重试！','red','black',1)
			pause()
	out.outln()
	out.outlnC('正在备份数据，请稍候……','cyan','black',1)

	isBackupSuccess=True
	allBeginTime=time.time()
	for bi,bk in enumerate(bkList):
		if selectBackup>=0 and bi!=selectBackup:
			continue
		if not bk['enabled']:
			continue
		bkBeginTime=time.time()
		out.outlnC(f' > [{progress(bi+1, len(bkList))}] 正在备份：{bk["name"]}','yellow','black',1)
		outLog(f'Begin backup: [{progress(bi+1, len(bkList))}] {bk["name"]}','BEGIN_BACKUP')
		backupPath=makeOutputDir(f'{backupRoot}\\{bk["name"]}')
		for index, p in enumerate(bk['path']):
			pName=p.split('\\')[-1]
			try:
				if os.path.isdir(p):
					# 备份路径为文件夹
					copyRs=copyTreeWithInfo(p,backupPath,index,bk['path'])
					if not copyRs:
						isBackupSuccess=False
				else:
					# 备份路径为文件
					if '*' in p:
						# 处理*通配符的情况
						psp=p.split('\\')
						pnamesp=psp[-1].split('.')
						psp.pop()
						fileList=[fl for fl in getFileList('\\'.join(psp)) if len(pnamesp)==1 or f'.{pnamesp[1]}' in fl]
						for i,f in enumerate(fileList):
							copyRs=copyWithInfo(f, backupPath, i, fileList)
							if not copyRs:
								isBackupSuccess=False
					else:
						copyRs=copyWithInfo(p, backupPath, index, bk["path"])
						if not copyRs:
							isBackupSuccess=False
			except Exception as e:
				out.outlnC(' [失败]','red','black',1)
				outLog(f'[{progress(index+1, len(bk["path"]))}] {p} Error: {e}','COPY_FILE')
				logger.exception('Exception')
				isBackupSuccess=False
		bkEndTime=time.time()
		bkUsedTime=formatSeconds(bkEndTime - bkBeginTime)
		out.outlnC(f' > 备份完成：[{progress(bi+1, len(bkList))}] {bk["name"]}，用时{bkUsedTime}','green','black',1)
		out.outln()
		outLog(f'Finish backup: [{progress(bi+1, len(bkList))}] {bk["name"]} UsedTime: {bkUsedTime}','FINISH_BACKUP')
		outLog()
	
	allEndTime=time.time()
	allUsedTime=formatSeconds(allEndTime - allBeginTime)
	if isBackupSuccess:
		out.outlnC(f'所有数据备份成功！用时{allUsedTime}，按任意键退出。','green','black',1)
		outLog(f'All data backup success. UsedTime: {allUsedTime}','BACKUP_RESULT')
	else:
		out.outlnC(f'部分数据备份失败！用时{allUsedTime}，按任意键退出。','red','black',1)
		outLog(f'Some data backup failed. UsedTime: {allUsedTime}','BACKUP_RESULT')
	writeLog()
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