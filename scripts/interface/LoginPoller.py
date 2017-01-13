# -*- coding: utf-8 -*-
import KBEngine
import Functor
import socket
from KBEDebug import *
import json
import http.client

class LoginPoller:

	def __init__(self, _callback, _host, _port, _overtime = 200):
		"""
		@param _callback: 数据处理完毕之后调用的外部回调, 注意不可在外部回调中销毁这个LoginPoller自己
		@param _host: 主机地址, 可以是域名也可以是ip地址
		@param _page: 请求页面
		@param _port: 请求端口
		@param _overtime: 超时秒数
		"""
		DEBUG_MSG("======================= LoginPoller .__init__ =======================")
		
		self._socket = None
		self._request_str = ""
		self._recv_str = ""
		self._recv_data = {}
		self._callback = _callback
		self._host = _host
		self._port = _port
		self._overtime = _overtime
		self._registerRead = False
		self._registerWrite = False

		DEBUG_MSG("======================= LoginPoller .__init__ TEST START ↓ =======================")
		
		# （http.client）此种 Http请求可用
		# conn = http.client.HTTPConnection("123.56.240.25:8989")
		# payload = "data=%7B%22username%22%3A%22iteming%22%2C%22password%22%3A%22123456%22%2C%22gameid%22%3A%221%22%2C%22clientid%22%3A%20%22%22%7D"
		# headers = { 'content-type': "application/x-www-form-urlencoded" }
		# conn.request("POST", "/auth/login", payload, headers)
		# res = conn.getresponse()
		# data = res.read()
		# DEBUG_MSG(data.decode("utf-8"))
		
		# （requests.request）此种 http请求,因未引入 requests库，无法使用
		# url = "http://123.56.240.25:8989/auth/login"
		# payload = "data=%7B%22username%22%3A%22iteming%22%2C%22password%22%3A%22123456%22%2C%22gameid%22%3A%221%22%2C%22clientid%22%3A%20%22%22%7D"
		# headers = { 'content-type': "application/x-www-form-urlencoded" }
		# response = requests.request("POST", url, data=payload, headers=headers)
		# DEBUG_MSG(response.text)
		
		DEBUG_MSG("======================= LoginPoller .__init__ TEST END ↑ =======================")
		
		
		
	def start(self, _commitName, _realAccountName, _datas, _page, _param_data, _tid, _get_post):
		"""
		@param _commitName, _realAccountName, _datas: 这三个参数来自于requestAccountLogin,记在这个LoginPoller中,
		数据请求完毕之后可以从外部重新拿到这些数据
		@param _param_data: http请求参数
		@param _tid: 可视为这个LoginPoller的Id, 回调时会返回这个id, 便于外部管理
		"""
		DEBUG_MSG("======================= LoginPoller .start =======================")
		
		self._commitName = _commitName
		self._realAccountName = _realAccountName
		self._datas = _datas
		self._tid = _tid

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		DEBUG_MSG("self._host: "+ str(self._host) +", self._port: " + str(self._port))
		self._socket.connect((self._host, self._port))

		self.registerRead()

		if _get_post == "GET":
			_rstr = "GET " + _page + "?" + _param_data + " HTTP/1.1\r\n"
			_rstr += "Host: "+ self._host +"\r\n"
			_rstr += "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:43.0) Gecko/20100101 Firefox/43.0\r\n"
			_rstr += "Connection: close\r\n"
			_rstr += "\r\n"
		elif _get_post == "POST":
			
			_rstr = "POST " + _page + " HTTP/1.1\r\n"
			_rstr += "Host: "+ self._host +"\r\n"
			_rstr += "Content-Type: application/x-www-form-urlencoded\r\n"
			_rstr += "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:43.0) Gecko/20100101 Firefox/43.0\r\n"
			_rstr += "Content-Length: "+ str(len(_param_data)) +"\r\n"
			_rstr += "Connection: close\r\n"
			_rstr += "\r\n" + _param_data + "\r\n"
			_rstr += "\r\n"
		
		DEBUG_MSG("checkRequests_rstr: " + _rstr)
		
		self._request_str = _rstr.encode()
		_sendAll = self.send()

		if _sendAll != True:
			self.registerWrite()

	def stop(self):
		self.deregisterRead()
		self.deregisterWrite()
		if self._socket != None:
			self._socket.close()
			self._socket = None

	def send(self):
		_send_lenth = self._socket.send(self._request_str)
		self._request_str = self._request_str[_send_lenth:]

		if len(self._request_str) == 0:
			return True
		else:
			return False

	def checkValidity(self):
		# 检查有效性, 超时检查
		if self._overtime > 0 and self._socket != None:
			self._overtime -= 1
			return True
		else:
			return False

	def onWrite(self, fileno):
		DEBUG_MSG("onWrite start")
		_sendAll = self.send()

		if _sendAll == True:
			self.deregisterWrite()

	def onRecv(self, fileno):
		DEBUG_MSG("onRecv start")
		_data = self._socket.recv(2048)
		# DEBUG_MSG("onRecv: " + json.dumps(_data) )
		if self.checkRecv(_data) == True:
			self.processData()
			self.stop()
			self._callback(self._tid,self._commitName)

	def checkRecv(self, _data):
		self._recv_str += _data.decode()
		DEBUG_MSG("checkRecv: " + self._recv_str)
		_count1 = self._recv_str.count('{')
		_count2 = self._recv_str.count('}')
		if _count1 == _count2 and _count1 > 0:
			return True

		return False

	def processData(self):
		"""
		处理接收数据
		从接收数据中截取json串并解析
		"""
		_index1 = self._recv_str.find('{')
		_index2 = self._recv_str.rfind('}')

		_bodyStr = self._recv_str[_index1: _index2 + 1]
		DEBUG_MSG("_bodyStr: " + _bodyStr)
		self._recv_data = json.loads(_bodyStr)
		DEBUG_MSG("self._recv_data: " + str(self._recv_data))

	def getPollerInfos(self):
		return self._commitName, self._realAccountName, self._datas, self._recv_data

	def registerRead(self):
		if self._registerRead == False:
			KBEngine.registerReadFileDescriptor(self._socket.fileno(), self.onRecv)
			self._registerRead = True

	def registerWrite(self):
		if self._registerWrite == False:
			KBEngine.registerWriteFileDescriptor(self._socket.fileno(), self.onWrite)
			self._registerWrite = True

	def deregisterRead(self):
		if self._registerRead == True:
			KBEngine.deregisterReadFileDescriptor(self._socket.fileno())
			self._registerRead = False

	def deregisterWrite(self):
		if self._registerWrite == True:
			KBEngine.deregisterWriteFileDescriptor(self._socket.fileno())
			self._registerWrite = False
