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

def loadFile(file,tp='r'):
	try:
		f=open(file,tp)
		fs=f.read()
		f.close()
		return fs
	except:
		return None

def writeFile(file,data,tp='w'):
	try:
		f=open(file,tp)
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

def printTitle():
	version=f'v{VERSION["versionUpdate"][0]["mainVersion"]} Build {VERSION["versionUpdate"][0]["dateVersion"]}'
	os.system('cls')
	os.system(f'title {VERSION["appNameCN"]} {version}')
	out.outlnC(f'-=<欢迎使用{VERSION["appNameCN"]}！>=-','purple','black',1)
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

def initBackup():
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
	
	curTime=time.strftime('%Y%m%d_%H%M%S')
	while True:
		backupRoot=makeOutputDir(f'{configData["backupPath"]}\\{curTime}')
		if exist(backupRoot):
			out.outlnC(f'\n备份路径：{backupRoot}','purple','black',1)
			break
		else:
			out.outlnC(f'\n备份路径：{backupRoot}创建失败！按任意键重试！','red','black',1)
			pause()
	
	out.outlnC('正在备份数据，请稍候……','cyan','black',1)
	isBackupSuccess=True
	for bk in bkList:
		if not bk['enabled']:
			continue
		out.outlnC(f' > 正在备份：{bk["name"]}','yellow','black',1)
		backupPath=makeOutputDir(f'{backupRoot}\\{bk["name"]}')
		for p in bk['path']:
			out.outC(f'   > {p}','white','black',1)
			pName=p.split('\\')[-1]
			try:
				if os.path.isdir(p):
					shutil.copytree(p,backupPath+"\\"+pName)
				else:
					shutil.copy2(p,backupPath+"\\"+pName)
				out.outlnC(' [成功]','green','black',1)
			except Exception as e:
				out.outlnC(' [失败]','red','black',1)
				logger.exception('Exception')
				isBackupSuccess=False
	
	if isBackupSuccess:
		out.outlnC(f'所有数据备份成功！按任意键退出。','green','black',1)
	else:
		out.outlnC(f'部分数据备份失败！按任意键退出。','red','black',1)
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