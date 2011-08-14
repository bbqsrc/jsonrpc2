#!/usr/bin/env python2
from __future__ import division, print_function
import time, sys, json

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory, Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import log


def ParseError():
	return Response(error=Error(-32700, message="Parse error."))
def InvalidRequest():
	return Response(error=Error(-32600, message="Invalid request."))
def MethodNotFound(id=None):
	return Response(error=Error(-32601, message="Method not found."), id=id)
def InvalidParams(id=None):
	return Response(error=Error(-32602, message="Invalid params."), id=id)
def InternalError(id=None):
	return Response(error=Error(-32603, message="Internal error."), id=id)


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
		method = getattr(self, request.get("method"), None)
		if not method or method in dir(LineReceiver) or \
				request.get("method").startswith("_"):
			return MethodNotFound()
		
		result = None
		params = request.get("params")
		try:
			if isinstance(params, list):
				result = method(*params)
			elif isinstance(params, dict):
				result = method(**params)
			else:
				return InvalidParams()
		except:
			#STUB 
			# TODO make it pass exception
			return InvalidRequest()

		
		try:
			if not request.get('id') is None:
				return Response(result, id=request.get('id'))
		except:
			return InvalidRequest()
	
	def _response_handler(self, message):
		pass

	def _detect_message_type(self, message):
		if isinstance(message, list):
			return self._batch_handler(message)
		
		elif isinstance(message, dict):
			if "method" in message:
				return self._request_handler(message)
			elif "result" in message or "error" in message:
				return self._response_handler(message)
		
	def _batch_handler(self, batch):
		pass
		
	def _send(self, message):
		self.sendLine(json.dumps(message))

	def receiveLine(self, line):
		try:
			message = json.dumps(line)
		except:
			self._send(ParseError())
		
		if message.get("jsonrpc") != "2.0":
			self._send(InvalidRequest())
		
		return self._detect_message_type(message)
		
			
		

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
