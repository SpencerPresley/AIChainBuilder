from __future__ import annotations

from typing import Final, TYPE_CHECKING

if TYPE_CHECKING:
    from ..enums import _BaseErrorReference

from ..messages import (
    INPUT_ERROR_MESSAGE,
    MAIN_CHAIN_JSON_ERROR_MESSAGE,
    FALLBACK_CHAIN_JSON_ERROR_MESSAGE,
    MAIN_CHAIN_VALIDATION_ERROR_MESSAGE,
    FALLBACK_CHAIN_VALIDATION_ERROR_MESSAGE,
    MAIN_CHAIN_VALUE_ERROR_MESSAGE,
    FALLBACK_CHAIN_VALUE_ERROR_MESSAGE,
    MAIN_CHAIN_TYPE_ERROR_MESSAGE,
    FALLBACK_CHAIN_TYPE_ERROR_MESSAGE,
    UNKNOWN_ERROR_MESSAGE,
)

from ..enums import (
    _ChainBuilderErrorReference,
    _ChainComposerErrorReference,
    _ChainWrapperErrorReference,
    _ChainManagerErrorReference,
    _ErrorType,
)

_ERROR_MESSAGE_MAP: Final[dict[_BaseErrorReference, dict[_ErrorType, str]]] = {
    _ChainWrapperErrorReference.INPUT_ERROR: {
        _ErrorType.VALUE_ERROR: INPUT_ERROR_MESSAGE,
    },
    
    _ChainWrapperErrorReference.MAIN_CHAIN_ERROR: {
        _ErrorType.JSON_ERROR: MAIN_CHAIN_JSON_ERROR_MESSAGE,
        
        _ErrorType.VALIDATION_ERROR: MAIN_CHAIN_VALIDATION_ERROR_MESSAGE,
        
        _ErrorType.VALUE_ERROR: MAIN_CHAIN_VALUE_ERROR_MESSAGE,
        
        _ErrorType.TYPE_ERROR: MAIN_CHAIN_TYPE_ERROR_MESSAGE,
        
        _ErrorType.UNKNOWN_ERROR: UNKNOWN_ERROR_MESSAGE,
    },
    
    _ChainWrapperErrorReference.FALLBACK_CHAIN_ERROR: {
        _ErrorType.JSON_ERROR: FALLBACK_CHAIN_JSON_ERROR_MESSAGE,
        
        _ErrorType.VALIDATION_ERROR: FALLBACK_CHAIN_VALIDATION_ERROR_MESSAGE,
        
        _ErrorType.VALUE_ERROR: FALLBACK_CHAIN_VALUE_ERROR_MESSAGE,
        
        _ErrorType.TYPE_ERROR: FALLBACK_CHAIN_TYPE_ERROR_MESSAGE,
        
        _ErrorType.UNKNOWN_ERROR: UNKNOWN_ERROR_MESSAGE,
    },
}
