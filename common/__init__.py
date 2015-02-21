import threading

def async(func):
	thread = threading.Thread(target=func)
	thread.setDaemon(True)
	thread.start()
	return thread
