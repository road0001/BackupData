import os
import sys
import time
import BackupData as b
import colorout as c
import shutil
import threading

# for i in range(0,100):
# 	p=b.progress(i,99,'percent')
# 	sys.stdout.write(f'{p}')
# 	sys.stdout.flush()
# 	time.sleep(0.1)
# time.sleep(1)
# c.outC(f'[完成]','green','black',1)

# def copyWithProgress(origin, target, keepMeta=True):
# 	originName=origin.split('\\')[-1]
# 	originSize=os.path.getsize(origin)
# 	print(target)
# 	if os.path.isdir(target):
# 		targetFolder=target
# 		target+=f'\\{originName}'
# 	else:
# 		targetSplit=target.split('\\')
# 		targetSplit.pop()
# 		targetFolder='\\'.join(targetSplit)
# 	print(target)
# 	return
# 	makeOutputDir(targetFolder)
# 	with open(origin,'rb') as originFile, open(target,'wb') as targetFile:
# 		bf=1024
# 		copied=0
# 		while True:
# 			buffer = originFile.read(bf)
# 			if not buffer:
# 				break
# 			targetFile.write(buffer)
# 			copied += len(buffer)
# 			percent=int(copied / originSize * 100)
# 			out.outC(progress(percent,100,'percent'),'white','black',1)
# 			time.sleep(0.000000001)
# 	if keepMeta:
# 		shutil.copystat(origin, target)

# copyWithProgress('D:\\User\\JMRY\\Documents\\Tencent Files\\376509849\\CustomFace.db','D:\\git\\BackupData\\dist\\Test111')
# c.outC(f'[完成]','green','black',1)


def copyTest(src, dst, *, follow_symlinks=True):
	if os.path.isdir(dst):
		dst = os.path.join(dst, os.path.basename(src))
	return dst

def copyProcess(src, dst):
	srcSize=1
	dstSize=1
	if os.path.isdir(dst):
		dst = os.path.join(dst, os.path.basename(src))
	while True:
		if os.path.exists(src):
			srcSize=os.path.getsize(src)
		if os.path.exists(dst):
			dstSize=os.path.getsize(dst)
		if dstSize >= srcSize:
			dstSize = srcSize
			# c.outlnC(f'[完成]','green','black',1)
			break
		else:
			percent=int(dstSize / srcSize  * 100)
			c.outC(b.progress(percent, 99, 'percent'),'yellow','black',1)
		time.sleep(1)

# copyTest('D:\\User\\JMRY\\Documents\\Tencent Files\\376509849\\CustomFace.db','D:\\git\\BackupData\\dist\\Test111')

of='D:\\User\\JMRY\\Documents\\Tencent Files\\376509849\\CustomFace.db'
tf='D:\\git\\BackupData\\dist\\Test111\\CustomFace.db'
for i in range(0,20):
	bt=time.time()
	try:
		os.remove(tf)
	except:
		pass
	c.outC(f'{tf} ','white','black',1)
	t = threading.Thread(target=copyProcess, args=(of, tf))
	t.start()
	shutil.copy2(of,tf)
	et=time.time()
	ut=b.formatSeconds(et - bt)
	c.outlnC(f'[完成，用时{ut}]','green','black',1)