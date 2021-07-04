import sys
import math
import os
from random import randint
from math import gcd as bltin_gcd

def is_prime(num, test_count):
    if num == 1:
        return False
    if test_count >= num:
        test_count = num - 1
    for x in range(test_count):
        val = randint(1, num - 1)
        if pow(val, num-1, num) != 1:
            return False
    return True

def generate_big_prime(n):
    found_prime = False
    while not found_prime:
        p = randint(2**(n-1), 2**n)
        if is_prime(p, 1000):
            return p

def isNotPrime(possible):
    # We only test this here to protect people who copy and paste
    # the code without reading the first sentence of the answer.
    # In an application where you know the numbers are prime you
    # will remove this function (and the call). If you need to
    # test for primality, look for a more efficient algorithm, see
    # for example Joseph F's answer on this page.
    i = 2
    while i*i <= possible:
        if (possible % i) == 0:
            return True
        i = i + 1
    return False

def primRoots(theNum):
    if isNotPrime(theNum):
        raise ValueError("Sorry, the number must be prime.")
    o = 1
    roots = []
    r = 2
    while r < theNum:
        k = pow(r, o, theNum)
        while (k > 1):
            o = o + 1
            k = (k * r) % theNum

        if o == (theNum - 1):
            roots.append(r)
        o = 1
        r = r + 1
    return roots

