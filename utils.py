from models import *

def convertSize(bytes): 
	i = 0 
	while(bytes >= 1024.0): 
		bytes = bytes/1024.0 
		i += 1 
		if(i == 4): 
			break 
	units = ["Bytes", "KB", "MB", "GB", "TB"]; 
	newsize = '%.2f ' % (bytes) 
	return newsize + units[i]

def recordError(module, message, detail):
	error = Error_History()
	error.error_module = module
	error.error_message = message
	error.error_detail = detail
	error.save()
