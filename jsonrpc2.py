#!/usr/bin/env python2
from __future__ import division, print_function
import time, sys, json

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory, Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import log


def ParseError():
	return json.dumps(Response(error=Error(-32700, message="Parse error.")))
def InvalidRequest():
	return json.dumps(Response(error=Error(-32600, message="Invalid request.")))
def MethodNotFound(id=None):
	return json.dumps(Response(error=Error(-32601, message="Method not found."), id=id))
def InvalidParams(id=None):
	return json.dumps(Response(error=Error(-32602, message="Invalid params."), id=id))
def InternalError(id=None):
	return json.dumps(Response(error=Error(-32603, message="Internal error."), id=id))


def Request(method, params=None, id=None):
	req = {
		"jsonrpc": "2.0",
		"method": method
	}
	
	if not params is None:
		if not isinstance(params, (list, tuple, set, dict)):
			raise ValueError("params cannot be %s" % type(params))
		req['params'] = params
	
	if not id is None:
		if isinstance(id, (str, unicode, int, float)):
			req['id'] = id
		else:
			raise ValueError("id cannot contain %s" % type(id))

	return req

	
def Response(result=None, error=None, id=None):
	if result and id is None:
		raise ValueError("id cannot be null in a response")
	
	resp = {
		"jsonrpc": "2.0",
		"id": id
	}
	
	if bool(result) != bool(error):
		if result:
			resp['result'] = result
		elif error:
			resp['error'] = error

	return resp
	
def Error(code, message, data=None):
	if not isinstance(code, int):
		raise ValueError("code must be an integer")
	if not isinstance(message, (unicode, str)):
		raise ValueError("message must be a string")
	err = {
		'code': code,
		'message': message
	}
	if data:
		err['data'] = data
	return err


class JSONRPC2Protocol(LineReceiver):
	
		
		
	def _request_handler(self, message):
		pass
	
	def _response_handler(self, message):
		pass

	def _detect_message_type(self, message):
		if isinstance(message, list):
			if len(message) == 0:
				self.sendLine(InvalidRequest())
			else:
				self.sendLine(self._batch_handler(message))
		
		elif isinstance(message, dict):
			if "method" in message:
				self._request_handler(message)
			elif "result" in message or "error" in message:
				self._response_handler(message)
			
		else:
			self.sendLine(InvalidRequest())
		
	def _batch_handler(self, batch):
		pass
		
	def _line_handler(self):
		if request.get("jsonrpc") != "2.0":
			return InvalidRequest()

		method = getattr(self, request.get("method"), None)
		if not method or method in dir(LineReceiver) or \
				request.get("method").startswith("_"):
			return MethodNotFound()
		
		result = None
		params = request.get("params")
		if isinstance(params, list):
			result = method(*params)
		elif isinstance(params, dict):
			result = method(**params)
		else:
			self.sendLine(InvalidParams())
			return
		
		try:
			response = json.dumps(Response(result=result, id=id))
			self.sendLine(response)
		except:
			self.sendLine(ParseError())
		
	def receiveLine(self, line):
		try:
			message = json.dumps(line)
		except:
			self.sendLine(ParseError())
		
		self._detect_message_type(message)
		return
		
			
		

class JSONRPC2ServerFactory(Factory):
	protocol = JSONRPC2Protocol
	def __init__(self):
		pass


class JSONRPC2ClientFactory(ReconnectingClientFactory):
	protocol = JSONRPC2Protocol
	def __init__(self):
		pass
	
	def startedConnecting(self, connector):
        print 'Started to connect.'

	#def buildProtocol

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
	

class Server(object):
	def __init__(self, port, ssl=False):
		if ssl:
			reactor.listenSSL(port, JSONRPC2ServerFactory())
		else:
			reactor.listenTCP(port, JSONRPC2ServerFactory())

			
class Client(object):
	def __init__(self, host, port, ssl=False):
		if ssl:
			reactor.connectSSL(host, port, JSONRPC2ClientFactory())
		else:
			reactor.connectTCP(host, port, JSONRPC2ClientFactory())
