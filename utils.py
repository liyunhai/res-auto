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