
class plop(object):

    r"""
    >>> from netzob.all import *
    >>> f0 = Field(uint8le(0), name="f0")
    >>> f1 = Field(uint8le(0), name="f1")
    >>> f2 = Field(name="len")
    >>> f3 = Field(uint32le(0), name="f3")
    >>> f4 = Field(Raw(nbBytes=(0,28)), name="f4")
    >>> f2.domain = Size([f0, f1, f2, f3, f4], dataType=int16())
    >>> symbol = Symbol([f0, f1, f2, f3, f4])
    >>> data = next(symbol.specialize())
    >>> data

    >>> print()
    >>> print()
    >>> print()

    >>> symbol.abstract(data)
    """
