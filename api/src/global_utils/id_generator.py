import random
import time


def generate_short_id(length: int = 6) -> int:
    """
    Gera um ID numérico com o número especificado de casas.

    Args:
        length: Número de dígitos do ID (padrão: 6)

    Returns:
        int: ID numérico com 'length' dígitos

    Examples:
        >>> generate_short_id(6)
        123456
        >>> generate_short_id(8)
        87654321
    """
    if length < 1:
        raise ValueError('O comprimento deve ser pelo menos 1')

    # Define o range baseado no número de dígitos
    # Ex: para 6 dígitos -> 100000 a 999999
    min_value = 10 ** (length - 1)
    max_value = (10**length) - 1

    return random.randint(min_value, max_value)
