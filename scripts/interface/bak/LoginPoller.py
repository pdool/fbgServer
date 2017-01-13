# -*- coding: utf-8 -*-
import KBEngine
import Functor
import socket
from KBEDebug import *
import json

class LoginPoller:
    def __init__(self, _callback, _host, _page, _port, _overtime = 5):
        """
        @param _callback: 数据处理完毕之后调用的外部回调, 注意不可在外部回调中销毁这个LoginPoller自己
        @param _host: 主机地址, 可以是域名也可以是ip地址
        @param _page: 请求页面
        @param _port: 请求端口
        @param _overtime: 超时秒数
        """
        self._socket = None
        self._request_str = ""
        self._recv_str = ""
        self._recv_data = {}
        self._callback = _callback
        self._host = _host
        self._page = _page
        self._port = _port
        self._overtime = _overtime
        self._registerRead = False
        self._registerWrite = False

    def start(self, _commitName, _realAccountName, _datas, _param_data, _tid):
        """
        @param _commitName, _realAccountName, _datas: 这三个参数来自于requestAccountLogin,记在这个LoginPoller中,
        数据请求完毕之后可以从外部重新拿到这些数据
        @param _param_data: http请求参数
        @param _tid: 可视为这个LoginPoller的Id, 回调时会返回这个id, 便于外部管理
        """
        self._commitName = _commitName
        self._realAccountName = _realAccountName
        self._datas = _datas
        self._tid = _tid

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        DEBUG_MSG("self._host: %s, self._port: %d" % (self._host, self._port))
        self._socket.connect((self._host, self._port))

        self.registerRead()

        # _rstr = "GET " + self._page + "?" + 'username=chongxin&password=111111' + " HTTP/1.1\r\n"
        _rstr = "GET " + self._page + " HTTP/1.1\r\n"
        _rstr += "Host: %s\r\n" % self._host
        _rstr += "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:43.0) Gecko/20100101 Firefox/43.0\r\n"
        _rstr += "Connection: close\r\n"
        _rstr += "\r\n"
        self._request_str = _rstr.encode()
        _sendAll = self.send()
        DEBUG_MSG("_request_str: %s" % (_rstr))
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
        _sendAll = self.send()

        if _sendAll == True:
            self.deregisterWrite()

    def onRecv(self, fileno):
        _data = self._socket.recv(2048)
        DEBUG_MSG("onRecv: %s" % _data)
        # if self.checkRecv(_data) == True:
        self.processData()
        self.stop()
        self._callback(self._tid)

    def checkRecv(self, _data):
        self._recv_str += _data.decode()
        DEBUG_MSG("checkRecv: %s" % self._recv_str)
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
        DEBUG_MSG("_bodyStr: %s" % _bodyStr)
        self._recv_data = json.loads(_bodyStr)
        DEBUG_MSG("self._recv_data: %s" % str(self._recv_data))
        KBEngine.accountLoginResponse('chongxin','chongxin', KBEngine.SERVER_ERR_LOCAL_PROCESSING)
        # KBEngine.createAccountResponse(self._commitName, self._realAccountName, self.datas, KBEngine.SERVER_SUCCESS)


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
