import zlib

from django.core.signing import JSONSerializer, Signer, b64_decode, b64_encode
from django.utils.encoding import force_bytes


def fixed_dumps(obj, key=None, salt='core.signing', serializer=JSONSerializer, compress=False):
    """
    The code is extracted from django.core.signing.loads

    Returns URL-safe, sha1 signed base64 compressed JSON string. If key is
    None, settings.SECRET_KEY is used instead.
    If compress is True (not the default) checks if compressing using zlib can
    save some space. Prepends a '.' to signify compression. This is included
    in the signature, to protect against zip bombs.
    Salt can be used to namespace the hash, so that a signed string is
    only valid for a given namespace. Leaving this at the default
    value or re-using a salt value across different parts of your
    application without good cause is a security risk.
    The serializer is expected to return a bytestring.
    """
    data = serializer().dumps(obj)

    # Flag for if it's been compressed or not
    is_compressed = False

    if compress:
        # Avoid zlib dependency unless compress is being used
        compressed = zlib.compress(data)
        if len(compressed) < (len(data) - 1):
            data = compressed
            is_compressed = True
    base64d = b64_encode(data)
    if is_compressed:
        base64d = b'.' + base64d
    return Signer(key, salt=salt).sign(base64d)


def fixed_loads(s, key=None, salt='core.signing', serializer=JSONSerializer):
    """
    The code is extracted from django.core.signing.dumps

    Reverse of dumps(), raises BadSignature if signature fails.
    The serializer is expected to accept a bytestring.
    """
    # TimestampSigner.unsign always returns unicode but base64 and zlib
    # compression operate on bytes.
    base64d = force_bytes(Signer(key, salt=salt).unsign(s))
    decompress = False
    if base64d[:1] == b'.':
        # It's compressed; uncompress it first
        base64d = base64d[1:]
        decompress = True
    data = b64_decode(base64d)
    if decompress:
        data = zlib.decompress(data)
    return serializer().loads(data)
