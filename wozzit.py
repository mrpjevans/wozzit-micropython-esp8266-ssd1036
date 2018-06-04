import ujson as json  # pylint: disable=all
import urequests

class Server:

    # Send a haver to another node
    def send(self, msg, to):
        
        # Send request
        r = urequests.post(url = to, json = msg.toDict())
        
        # Attempt to parse response into haver message
        try:
            json = r.json()
        except:
            return False

        response = Message().load(json)

        return response
        

class Message:
    # A message past from Wozzit node to Wozzit node
    # This class' concerns are parsing, validating and rendering messages

    def __init__(self):
        self._reset()

    # Set up instance-scoped variables
    def _reset(self):

        # Protocol allows for future versions of Havers. Uses semantic versioning in tuple form.
        # Min and max represent the boundaries of what we can support.
        self.protocol = (0, 0, 1)
        self.minProtocol = (0, 0, 1)
        self.maxProtocol = (0, 0, 1)

        # Schema is a reverse-domain notation identifying what we can expect from the payload.
        # The default is wozzit.null which means 'nothing'.
        self.schema = "wozzit.null"

        # Schemas can be versioned. Whether the version is supported or not is out-of-scope.
        self.version = 1

        # For incoming havers, this records the IP address of the sender
        self.ip = None

        # Pre-shared key. Provides a layer of security. Content is unrestricted.
        self.psk = None

        # Payload: The actual data (if any) - the content is dictated by the schema.
        self.payload = None        
    
    # Serialise this instance into a dict object
    def toDict(self):
        output = {'wozzit': {'protocol': self.protocol, 'schema': self.schema, 'version': self.version}}
        if self.payload is not None:
            output['payload'] = self.payload
        return output

    # Serialize this instance into JSON
    def toJSON(self):
        output = self.toDict()
        return json.dumps(output)
        
    # Parse raw JSON-formatted data into this instance, sanity checking as we go
    def load(self, raw_data, ip=None):

        self._reset()
        if type(raw_data) is dict:
            data = raw_data
        else:
            data = json.loads(raw_data)
        
        if 'wozzit' not in data:
            return ErrorMessage(400, 'Bad request')
        
        msg = data['wozzit']

        if 'protocol' not in msg:
            return ErrorMessage(400, "No protocol")

        self.protocol = tuple(msg['protocol'])
        if self.protocol < self.minProtocol or self.protocol > self.maxProtocol:
            return ErrorMessage(400, "Unsupported protocol")

        if 'schema' not in msg:
            return ErrorMessage(400, "No schema")

        self.schema = msg['schema']

        if 'version' not in msg:
            return ErrorMessage(400, "No version")

        self.version = msg['version']

        if 'psk' in msg:
            self.psk = msg['psk']

        if 'payload' in msg:
            self.payload = msg['payload']

        if ip is not None:
            self.ip = ip

        return self

#
# The following are shortcuts to creating certain types of messages
#

class ErrorMessage(Message):
    # Override to create an 'error' Haver
    def __init__(self, code=500, message="Error"):
        self._reset()
        self.schema = 'wozzit.error'
        self.payload = {'code': code, 'message': message}

class NotFoundMessage(ErrorMessage):
    # Not found
    def __init__(self):
        self._reset()
        self.schema = 'wozzit.error'
        self.payload = {'code': 404, 'message': 'Not found'}

class NotImplementedMessage(Message):
    # HTTP method not implemented
    def __init__(self):
        self._reset()
        self.schema = 'wozzit.error'
        self.payload = {'code': 501, 'message': 'Not implemented'}

class ReceiptMessage(Message):
    # Acknowledgement of a haver received
    # I expect this to become more useful in future
    def __init__(self):
        self._reset()
        self.schema = 'wozzit.receipt'

