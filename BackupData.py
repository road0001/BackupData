import os
import sys
import json
import time
import subprocess
import send2trash
from loguru import logger
from shutil import copyfile
import colorout as out

VERSION={
"appName":"BackupData",
"appNameCN":"数据备份工具",
"versionUpdate":[
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
defaultBackupPath='backup'

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
	return version

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
			print(configData)
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