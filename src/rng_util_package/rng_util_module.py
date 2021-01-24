'''
rng_util - This is the common function package of random number generator.  这个是随机数发生器的公共函数包。
Copyright (C) 2020  sosei
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from typing import TypeVar
from hashlib import shake_256
from gmpy2 import mpfr, mpz, local_context as gmpy2_local_context, context as gmpy2_get_context, num_digits as gmpy2_num_digits, c_div as gmpy2_c_div, log2 as gmpy2_log2

__all__ = ['bit_length_mask', 'min_entropy', 'randomness_extractor']

Integer = TypeVar('Integer', int, mpz)

def bit_length_mask(x: Integer, bit_length: Integer) -> Integer:
    '''
        Intercepts the lowest binary digit of a specified length from the number x.  对数字x截取指定长度的最低二进制位。
        
        Parameters
        ----------
        x: Integer
            The number to be masked.  要被掩码的数
        
        bit_length: Integer
            All 1 mask lengths.  全1掩码长度。
        
        Returns
        -------
        bit_length_mask: Integer
            Returns the mask result.  返回掩码结果。
        
        Examples
        --------
        >>> binary_number = '1010101010'
        >>> format(bit_length_mask(int(binary_number, 2), 6), 'b')
        '101010'
    '''
    assert isinstance(x, (int, type(mpz(0)))), f'x must be an Integer, got type {type(x).__name__}'
    assert isinstance(bit_length, (int, type(mpz(0)))), f'bit_length must be an Integer, got type {type(bit_length).__name__}'
    if x < 0: raise ValueError('x must be >= 0')
    if bit_length <= 0: raise ValueError('bit_length must be > 0')
    
    x &= (1 << bit_length) - 1
    return x


def min_entropy(number_of_0: Integer, number_of_1: Integer) -> mpfr:
    '''
        The minimum entropy of a binary sequence is calculated based on the number of zeros and ones in the sequence.  根据二进制序列中0与1的数目，计算此序列的最小熵值。
        
        Parameters
        ----------
        number_of_0: Integer
            The number of zeros in a binary sequence.  二进制序列中0的数目。
        
        number_of_1: Integer
            The number of ones in a binary sequence.  二进制序列中1的数目。
        
        Returns
        -------
        min_entropy: gmpy2.mpfr
            Returns the minimum entropy.  返回最小熵值。
        
        Examples
        --------
        >>> min_entropy(6, 4)
        mpfr('0.73682',11)
    '''
    assert isinstance(number_of_0, (int, type(mpz(0)))), f'number_of_0 must be an Integer, got type {type(number_of_0).__name__}'
    assert isinstance(number_of_1, (int, type(mpz(0)))), f'number_of_1 must be an Integer, got type {type(number_of_1).__name__}'
    if number_of_0 < 0: raise ValueError('number_of_0 must be >= 0')
    if number_of_1 < 0: raise ValueError('number_of_1 must be >= 0')
    
    length = number_of_0 + number_of_1
    if length == 0: raise ValueError('(number_of_0 + number_of_1) must be > 0')
    
    with gmpy2_local_context(gmpy2_get_context(), precision = length + 1):
        return -gmpy2_log2(mpfr(max(number_of_0, number_of_1)) / mpfr(length))


def randomness_extractor(raw_entropy_data: Integer, output_bit_size: Integer) -> Integer:
    '''
        The biased weak random entropy source is treated to extract the highly random output with uniform distribution.  对有偏的弱随机熵源处理提取成均匀分布的高度随机输出。
        
        Parameters
        ----------
        raw_entropy_data: Integer
            Raw entropy data.
        
        output_bit_size: Integer
            The bit length of the output entropy.  输出熵的比特长度。
        
        Returns
        -------
        randomness_extractor: Integer
            Returns an unbiased source of entropy.  返回一个无偏的熵源。
        
        Note
        ----
        the only restriction on possible sources is that there is no way they can be fully controlled, calculated or predicted, and that a lower bound on their entropy rate can be established.
        
        Examples
        --------
        >>> binary_number = '1'*66 + '0'*11
        >>> binary_number
        '11111111111111111111111111111111111111111111111111111111111111111100000000000'
        >>> format(randomness_extractor(int(binary_number, 2), 20), 'b')
        '11100001100100110010'
    '''
    assert isinstance(raw_entropy_data, (int, type(mpz(0)))), f'raw_entropy_data must be an Integer, got type {type(raw_entropy_data).__name__}'
    assert isinstance(output_bit_size, (int, type(mpz(0)))), f'output_bit_size must be an Integer, got type {type(output_bit_size).__name__}'
    if raw_entropy_data < 0: raise ValueError('raw_entropy_data must be >= 0')
    if output_bit_size <= 0: raise ValueError('output_bit_size must be > 0')
    
    raw_entropy_byte_length = gmpy2_c_div(gmpy2_num_digits(raw_entropy_data, 2), 8)
    digest_byte_length = int(gmpy2_c_div(output_bit_size, 8))
    hash_raw_entropy_bytes = shake_256(int(raw_entropy_data).to_bytes(raw_entropy_byte_length, byteorder = 'little')).digest(digest_byte_length)
    return bit_length_mask(int.from_bytes(hash_raw_entropy_bytes, byteorder = 'little'), output_bit_size)
