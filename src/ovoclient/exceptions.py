"""
Exceptions
==========

Specialized error types raised from OVO.
"""
__all__ = ['OvoClientError', ]


class OvoClientExceptionBase(Exception):
    pass


class OvoAPINotContactable(OvoClientExceptionBase):
    """ Raised when the HTTP client cannot communicate with KGX.
    """
    pass


class OvoClientError(OvoClientExceptionBase):
    """ Raised when the AkuLaku API
    """
    pass
