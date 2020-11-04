'''
pure_nrng - This package is used to generate non-deterministic random Numbers.
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

from typing import Callable
import gmpy2
import rng_util_package.rng_util_module as rng_util

__all__ = ['pure_nrng', 'rng_util']

class pure_nrng:
    '''
        Generate multi-precision non-deterministic random Numbers.  生成多精度非确定随机数。
        
        pure_nrng() -> Using the system's true random entropy source.  用系统真随机熵源。
        
        pure_nrng(true_randbits) -> Use an external source of true random entropy.  用外部真随机熵源。
        
        Note
        ----
        The generated instance is thread-safe.
    '''
    
    version = '0.8.2'
    
    initial_test_size = 2 ** 13  #The units are bits.
    count_queue_maxlen = 31
    
    def __init__(self, *true_randbits_tuple: Callable[[int], int]) -> None:
        '''
            Create an instance of a true random number generator.  创建一个真随机数生成器的实例。
            
            Parameters
            ----------
            *true_randbits_tuple: Callable
                Some callable external true random source objects. Like: secrets.randbits(bit_size) 一些可调用的外部真随机源对象。形如：secrets.randbits(bit_size)
                If it does not exist, the default is to call the true random source provided by the operating system. 如果不存在的话，则默认调用操作系统提供的真随机源。
        '''
        for true_randbits in true_randbits_tuple:
            assert isinstance(true_randbits, Callable), f'true_randbits must be an Callable, got type {type(true_randbits).__name__}'
        
        from collections import deque
        
        if true_randbits_tuple == ():
            from secrets import randbits
            true_randbits_tuple = (randbits,)
        
        initial_test_size = self.__class__.initial_test_size
        count_queue_maxlen = self.__class__.count_queue_maxlen
        self.raw_entropy_dict = dict()
        
        for true_randbits in true_randbits_tuple:
            raw_entropy_data = true_randbits(initial_test_size)
            number_of_1 = gmpy2.popcount(raw_entropy_data)
            number_of_0 = initial_test_size - number_of_1
            
            count_queue_of_0 = deque([number_of_0], maxlen = count_queue_maxlen)
            count_queue_of_1 = deque([number_of_1], maxlen = count_queue_maxlen)
            
            sum_of_0, sum_of_1 = 0, 0
            sum_of_0 += number_of_0
            sum_of_1 += number_of_1
            
            min_entropy_value = rng_util.min_entropy(sum_of_0, sum_of_1)
            
            self.raw_entropy_dict.update({true_randbits: {'count_queue_of_0': count_queue_of_0, 'count_queue_of_1': count_queue_of_1, 'sum_of_0': sum_of_0, 'sum_of_1': sum_of_1, 'min_entropy_value': min_entropy_value}})
    
    
    def true_rand_bits(self, bit_size: int, unbias: bool = True) -> int:
        '''
            Get a true random binary number.  得到一个真随机二进制数。
            
            Parameters
            ----------
            bit_size: int
                Sets the true random number that takes the specified bit length.  设定取指定比特长度的真随机数。
            
            unbias: bool, default True
                Set to true, and enable unbiased processing for the true random Numbers used. 设为真，则对用到的真随机数启用无偏处理。
            
            Returns
            -------
            true_rand_bits: int
                Returns a true random number of the specified bit length. 返回一个指定比特长度真随机数。
        '''
        assert isinstance(bit_size, int), f'bit_size must be an int, got type {type(bit_size).__name__}'
        assert isinstance(unbias, bool), f'unbias must be an bool, got type {type(unbias).__name__}'
        if bit_size <= 0: raise ValueError('bit_size must be > 0')
        
        initial_test_size = self.__class__.initial_test_size
        count_queue_maxlen = self.__class__.count_queue_maxlen
        
        if unbias:
            unbias_entropy_data = 0
            
            for true_randbits, binary_statistics_dict in self.raw_entropy_dict.items():
                min_entropy_value = binary_statistics_dict['min_entropy_value']
                if min_entropy_value != 0:
                    read_raw_length = int(gmpy2.ceil(bit_size * 2 / min_entropy_value))  #the amount of entropy input is twice the number of bits output from them, that output can be considered essentially fully random.
                else:
                    read_raw_length = initial_test_size
                for _ in range(3):  #The entropy source is re-read when the "minimum entropy" of the source is zero. Try twice at most.  当熵源发生“最小熵”为0的异常，就会重新读熵源。最多重试两次。
                    raw_entropy_data = true_randbits(read_raw_length)
                    number_of_1 = gmpy2.popcount(raw_entropy_data)
                    number_of_0 = read_raw_length - number_of_1
                    
                    if len(binary_statistics_dict['count_queue_of_0']) == count_queue_maxlen:
                        binary_statistics_dict['sum_of_0'] -= binary_statistics_dict['count_queue_of_0'].popleft()
                    binary_statistics_dict['sum_of_0'] += number_of_0
                    binary_statistics_dict['count_queue_of_0'].append(number_of_0)
                    
                    if len(binary_statistics_dict['count_queue_of_1']) == count_queue_maxlen:
                        binary_statistics_dict['sum_of_1'] -= binary_statistics_dict['count_queue_of_1'].popleft()
                    binary_statistics_dict['sum_of_1'] += number_of_1
                    binary_statistics_dict['count_queue_of_1'].append(number_of_1)
                    
                    min_entropy_value = rng_util.min_entropy(binary_statistics_dict['sum_of_0'], binary_statistics_dict['sum_of_1'])
                    if min_entropy_value != 0:
                        binary_statistics_dict['min_entropy_value'] = min_entropy_value
                        break
                    else:
                        read_raw_length = initial_test_size
                else:
                    raise RuntimeError(f'Entropy source [{true_randbits}] exception!')
                unbias_entropy_data ^= rng_util.randomness_extractor(raw_entropy_data, bit_size)
            
            return unbias_entropy_data
        else:
            raw_entropy_data = 0
            for true_randbits in self.raw_entropy_dict.keys():
                raw_entropy_data ^= true_randbits(bit_size)
            return raw_entropy_data
    
    
    def true_rand_float(self, bit_size: int, unbias: bool = True) -> gmpy2.mpfr:
        '''
            Get a true random real number. 得到一个真随机实数。
            
            Parameters
            ----------
            bit_size: int
                Sets the true random number that takes the specified bit length.  设定取指定比特长度的真随机数。
            
            unbias: bool, default True
                Set to true, and enable unbiased processing for the true random Numbers used. 设为真，则对用到的真随机数启用无偏处理。
            
            Returns
            -------
            true_rand_float: gmpy2.mpfr
                Returns a true random real number in [0, 1), with 0 included and 1 excluded.
                The output float length is bit_size+1. 输出浮点长度是bit_size+1。
        '''
        assert isinstance(bit_size, int), f'bit_size must be an int, got type {type(bit_size).__name__}'
        assert isinstance(unbias, bool), f'unbias must be an bool, got type {type(unbias).__name__}'
        
        with gmpy2.local_context(gmpy2.context(), precision = bit_size + 1):
            return gmpy2.mpfr(self.true_rand_bits(bit_size, unbias)) / gmpy2.mpfr(1 << bit_size)
    
    
    def true_rand_int(self, b: int, a: int = 0, unbias: bool = True) -> gmpy2.mpz:
        '''
            Get a true random integer within a specified interval. 得到一个指定区间内的真随机整数。
            
            Parameters
            ----------
            b: int
                Upper bound on the range including 'b'.
            
            a: int, default 0
                Lower bound on the range including 'a'.
            
            unbias: bool, default True
                Set to true, and enable unbiased processing for the true random Numbers used. 设为真，则对用到的真随机数启用无偏处理。
            
            Returns
            -------
            true_rand_int: gmpy2.mpz
                Returns an integer true random number in the range [a, b]
        '''
        assert isinstance(b, int), f'b must be an int, got type {type(b).__name__}'
        assert isinstance(a, int), f'a must be an int, got type {type(a).__name__}'
        assert isinstance(unbias, bool), f'unbias must be an bool, got type {type(unbias).__name__}'
        if a > b: raise ValueError('a must be <= b')
        
        scale = b - a
        bit_size = scale.bit_length()
        
        random_number_masked = self.true_rand_bits(bit_size, unbias)
        while not (random_number_masked <= scale):
            random_number_masked = self.true_rand_bits(bit_size, unbias)
        
        return a + random_number_masked
