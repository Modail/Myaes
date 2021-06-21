from .aes import AESBlockModeOfOperation, AESSegmentModeOfOperation
from .util import append_PKCS7_padding, strip_PKCS7_padding, to_bufferable

#首先，我们向每种操作模式注入三个函数
# _can_consume(大小)
# 给定一个大小，确定可以消耗多少字节
# 对解密或加密方法的单独调用
#
# final_encrypt(data, padding = PADDING_DEFAULT)
# 调用并返回加密对这个(最后)数据块，
# 填充必要时;它总是至少等于16字节，除非传入的总输入小于16字节

# final_decrypt(data, padding = PADDING_DEFAULT)
# -与_final_encrypt相同，除了decrypt去掉填充

PADDING_NONE = 'none'
PADDING_DEFAULT = 'default'

# CBC是块密码


def _block_can_consume(self, size):
    if size >= 16: return 16
    return 0


# 在填充之后，可能有多个块
def _block_final_encrypt(self, data, padding=PADDING_DEFAULT):
    if padding == PADDING_DEFAULT:
        data = append_PKCS7_padding(data)

    elif padding == PADDING_NONE:
        if len(data) != 16:
            raise Exception('invalid data length for final block')
    else:
        raise Exception('invalid padding option')

    if len(data) == 32:
        return self.encrypt(data[:16]) + self.encrypt(data[16:])

    return self.encrypt(data)


def _block_final_decrypt(self, data, padding=PADDING_DEFAULT):
    if padding == PADDING_DEFAULT:
        return strip_PKCS7_padding(self.decrypt(data))

    if padding == PADDING_NONE:
        if len(data) != 16:
            raise Exception('invalid data length for final block')
        return self.decrypt(data)

    raise Exception('invalid padding option')


AESBlockModeOfOperation._can_consume = _block_can_consume
AESBlockModeOfOperation._final_encrypt = _block_final_encrypt
AESBlockModeOfOperation._final_decrypt = _block_final_decrypt

# CFB是段密码


def _segment_can_consume(self, size):
    return self.segment_bytes * int(size // self.segment_bytes)


# CFB可以使用剩余的密码块在末端处理一个非段大小的块
def _segment_final_encrypt(self, data, padding=PADDING_DEFAULT):
    if padding != PADDING_DEFAULT:
        raise Exception('invalid padding option')

    faux_padding = (chr(0) * (self.segment_bytes -
                              (len(data) % self.segment_bytes)))
    padded = data + to_bufferable(faux_padding)
    return self.encrypt(padded)[:len(data)]


# CFB可以使用剩余的密码块在末端处理一个非段大小的块
def _segment_final_decrypt(self, data, padding=PADDING_DEFAULT):
    if padding != PADDING_DEFAULT:
        raise Exception('invalid padding option')

    faux_padding = (chr(0) * (self.segment_bytes -
                              (len(data) % self.segment_bytes)))
    padded = data + to_bufferable(faux_padding)
    return self.decrypt(padded)[:len(data)]


AESSegmentModeOfOperation._can_consume = _segment_can_consume
AESSegmentModeOfOperation._final_encrypt = _segment_final_encrypt
AESSegmentModeOfOperation._final_decrypt = _segment_final_decrypt


class BlockFeeder(object):
    '''对象的超类，用于处理将字节流分块为适合底层操作模式的块大小，并根据需要应用(或剥离)填充'''
    def __init__(self, mode, feed, final, padding=PADDING_DEFAULT):
        self._mode = mode
        self._feed = feed
        self._final = final
        self._buffer = to_bufferable("")
        self._padding = padding

    def feed(self, data=None):
        '''提供要加密(或解密)的字节，返回任何字节（可能是这次call或是之前的call）。

           用None或空字符串调用以刷新模式操作并返回任何最终字节;没有更多的call可以进行feed。'''

        if self._buffer is None:
            raise ValueError('already finished feeder')

        # 最终; 处理我们保留的空闲字节
        if data is None:
            result = self._final(self._buffer, self._padding)
            self._buffer = None
            return result

        self._buffer += to_bufferable(data)

        # 保留16个字节，以便确定填充
        result = to_bufferable('')
        while len(self._buffer) > 16:
            can_consume = self._mode._can_consume(len(self._buffer) - 16)
            if can_consume == 0: break
            result += self._feed(self._buffer[:can_consume])
            self._buffer = self._buffer[can_consume:]

        return result


class Encrypter(BlockFeeder):
    '接受明文字节并返回加密的密文'

    def __init__(self, mode, padding=PADDING_DEFAULT):
        BlockFeeder.__init__(self, mode, mode.encrypt, mode._final_encrypt,
                             padding)


class Decrypter(BlockFeeder):
    '接受字节的密文并返回解密的明文'

    def __init__(self, mode, padding=PADDING_DEFAULT):
        BlockFeeder.__init__(self, mode, mode.decrypt, mode._final_decrypt,
                             padding)


# 8kb blocks
BLOCK_SIZE = (1 << 13)


def _feed_stream(feeder, in_stream, out_stream, block_size=BLOCK_SIZE):
    '使用feeder读取和转换从in_stream和写入到out_stream'

    while True:
        chunk = in_stream.read(block_size)
        if not chunk:
            break
        converted = feeder.feed(chunk)
        out_stream.write(converted)
    converted = feeder.feed()
    out_stream.write(converted)


def encrypt_stream(mode,
                   in_stream,
                   out_stream,
                   block_size=BLOCK_SIZE,
                   padding=PADDING_DEFAULT):
    '使用模式从in_stream加密字节流到out_stream'

    encrypter = Encrypter(mode, padding=padding)
    _feed_stream(encrypter, in_stream, out_stream, block_size)


def decrypt_stream(mode,
                   in_stream,
                   out_stream,
                   block_size=BLOCK_SIZE,
                   padding=PADDING_DEFAULT):
    '使用模式从in_stream解密字节流到out_stream'

    decrypter = Decrypter(mode, padding=padding)
    _feed_stream(decrypter, in_stream, out_stream, block_size)
