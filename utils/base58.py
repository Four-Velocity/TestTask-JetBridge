import os
import qrcode
import qrcode.image.svg
from .other import create_folder

symbols = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
try:
    from jb_test.settings import MEDIA_ROOT
    QR_FOLDER = os.path.join(MEDIA_ROOT, 'qr_codes')
except ImportError:
    QR_FOLDER = os.path.dirname(os.path.abspath(__file__))


class Encoder:
    """
    Encode user id/company id/host integer/ to invitation URL, stores it in `self.encoded`
    The format of Invitation URL is 'URL/CODE', where code is 'XXXXXX_S': XXXXXX - encoded integer, S - one letter type
    Also generates qrcode with invitation link

    :param url: URL to which the invitation code will be added
    :param pk: Integer that will be encoded
    :param sort: Integer that indicates ownership of the code. 1 for Personal, 2 for Enterprise, 3 for owned by the Host
    :param path: path to qrcode

    >>> example = Encoder("http://example.com", 153, 1)
    >>> example.invitation_code
    '11113e_P'
    >>> example.encoded_url
    'http://example.com/11113e_P'
    >>> example
    'http://example.com/11113e_P'
    """
    _template = dict(enumerate(symbols))
    _sort_translator = {1: 'P', 2: 'E', 3: 'H'}

    def __init__(self, url: str, pk: int, sort: int, path: str = QR_FOLDER):
        self.url = url
        self.pk = pk
        self.sort = self._sort_translator[sort]
        self.folder = path
        self.invitation_code = self.encode()
        if self.url[-1] == '/':
            tmp_code = f'{self.invitation_code}/'
        else:
            tmp_code = f'/{self.invitation_code}/'
        self.encoded_url = self.url + tmp_code

    def __str__(self):
        return self.encoded_url

    def to_58(self, value: int = None) -> str:
        """
        Converts an integer with from the decimal numeral system to the numeral system with safe base 58.
        Read more https://en.wikipedia.org/wiki/Base58

        :param value: Integer in decimal numeral system. By default it's class `pk` attribute
        :return: Integer in numeral system with base 58

        >>> self.to_58(641835)
        '4Ho8'
        """
        if value is None:
            value = self.pk
        if value <= 57:
            return self._template[value]
        else:
            total = value // 58
            reminder = value % 58
            return self.to_58(total) + self._template[reminder]

    def encode(self):
        """
        Encode pk and sort into invitation code

        :return: Invitation code with a format XXXXXX_S, where 'XXXXXX' is encoded pk and 'S' is sort integer
        """
        code = self.to_58().rjust(6, "1")
        return f'{code}_{self.sort}'

    def qr(self):
        """
        Generates qr code in svg format with invitation link

        :return: path to qr code
        """
        factory = qrcode.image.svg.SvgPathImage
        img = qrcode.make(self.encoded_url, image_factory=factory)
        destination = os.path.join(self.folder, f'{self.invitation_code}.svg')
        relative_path = os.path.join(self.folder.split('/')[-1], f'{self.invitation_code}.svg')
        create_folder(self.folder)
        img.save(destination)
        return destination, relative_path


class Decoder:
    """
    Gets id and type encoded in invitation code.
    Stores them in `pk` and `sort` attributes

    :param code: invitation code in a format XXXXXX_S: XXXXXX - encoded integer, S - one letter type

    >>>example = Decoder('11113e_P')
    >>>example.pk
    153
    >>>example.sort
    1
    """
    _template = dict((i[1], i[0]) for i in enumerate(symbols))
    _sort_translator = {'P': 1, 'E': 2, 'H': 3}

    def __init__(self, code: str):
        self.code = code
        decoded = self.decode()
        self.pk = decoded[0]
        self.sort = decoded[1]

    def __str__(self):
        return f'ID: {self.pk}\nType: {self.sort}'

    def to_dec(self, value: str, step: int = 0) -> int:
        """
            Converts an integer with from the numeral system with base 58 to the decimal numeral system

            :param value: Integer in numeral system with base 58
            :param step: Based on the conversation algorithm `step` is the power to which the base is raised. By default is 0, do NOT change the default value
            :return: Integer in decimal numeral system

            >>> self.to_dec('ZaD1')
            6355292
        """
        length = len(value) - 1
        if not value:
            return 0
        else:
            dec = self._template[value[length]] * (58 ** step)
            return dec + self.to_dec(value[:length], step + 1)

    def decode(self) -> tuple:
        """
        Translate code into two integers: id and type

        :return: id and type encoded in invitation code
        """
        pk, sort = self.code.split('_')
        pk = self.to_dec(pk)
        return pk, sort