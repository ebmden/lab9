"""
- CS2911 - 011
- Fall 2021
- Lab 9
- Names:
  - Lucas Gral
  - Eden Basso

16-bit RSA

Introduction: (Describe the lab in your own words) LG
The point of this lab is to gain experience in RSA encryption/decryption. We will implement the
parts of a program that can generate keys, encrypt/decrypt messages with keys, and break keys.
The keys we use will be 16-bit since they're easier to generate and break than longer keys.
Before the lab, we will complete an RSA exercise to get experience with creating keys, and using
keys with messages to encrypt/decrypt them (by hand).



Question 1: RSA Security
In this lab, Trudy is able to find the private key from the public key. Why is this not a problem for RSA in practice?

This isn't a problem, because RSA keys are much bigger than 16 bits in practice (usually over 1024 bits). This
means that there is an upper bound of over 2^1024 possibilities to test when factoring the modulus (n).
That many possibilities makes the task of factoring n "computationally infeasible," such that the time
it would take to crack such a key isn't worth it for anyone.




Question 2: Critical Step(s)
When creating a key, Bob follows certain steps. Trudy follows other steps to break a key. What is the difference between Bob’s steps and Trudy’s so that Bob is able to run his steps on large numbers, but Trudy cannot run her steps on large numbers?




Checksum Activity:
Provide a dicussion of your experiences as described in the activity.  Be sure to answer all questions.





Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)





"""
import math
import random
import sys

# Use these named constants as you write your code
MAX_PRIME = 0b11111111  # The maximum value a prime number can have
MIN_PRIME = 0b11000001  # The minimum value a prime number can have 
PUBLIC_EXPONENT = 17  # The default public exponent


def main():
    """ Provide the user with a variety of encryption-related actions """

    # Get chosen operation from the user.
    action = input("Select an option from the menu below:\n"
                   "(1-CK) create_keys\n"
                   "(2-CC) compute_checksum\n"
                   "(3-VC) verify_checksum\n"
                   "(4-EM) encrypt_message\n"
                   "(5-DM) decrypt_message\n"
                   "(6-BK) break_key\n "
                   "Please enter the option you want:\n")
    # Execute the chosen operation.
    if action in ['1', 'CK', 'ck', 'create_keys']:
        create_keys_interactive()
    elif action in ['2', 'CC', 'cc', 'compute_checksum']:
        compute_checksum_interactive()
    elif action in ['3', 'VC', 'vc', 'verify_checksum']:
        verify_checksum_interactive()
    elif action in ['4', 'EM', 'em', 'encrypt_message']:
        encrypt_message_interactive()
    elif action in ['5', 'DM', 'dm', 'decrypt_message']:
        decrypt_message_interactive()
    elif action in ['6', 'BK', 'bk', 'break_key']:
        break_key_interactive()
    else:
        print("Unknown action: '{0}'".format(action))


def create_keys_interactive():
    """
    Create new public keys

    :return: the private key (d, n) for use by other interactive methods
    """

    key_pair = create_keys()
    pub = get_public_key(key_pair)
    priv = get_private_key(key_pair)
    print("Public key: ")
    print(pub)
    print("Private key: ")
    print(priv)
    return priv


def compute_checksum_interactive():
    """
    Compute the checksum for a message, and encrypt it
    """

    priv = create_keys_interactive()

    message = input('Please enter the message to be checksummed: ')

    hash = compute_checksum(message)
    print('Hash:', "{0:04x}".format(hash))
    cipher = apply_key(priv, hash)
    print('Encrypted Hash:', "{0:04x}".format(cipher))


def verify_checksum_interactive():
    """
    Verify a message with its checksum, interactively
    """

    pub = enter_public_key_interactive()
    message = input('Please enter the message to be verified: ')
    recomputed_hash = compute_checksum(message)

    string_hash = input('Please enter the encrypted hash (in hexadecimal): ')
    encrypted_hash = int(string_hash, 16)
    decrypted_hash = apply_key(pub, encrypted_hash)
    print('Recomputed hash:', "{0:04x}".format(recomputed_hash))
    print('Decrypted hash: ', "{0:04x}".format(decrypted_hash))
    if recomputed_hash == decrypted_hash:
        print('Hashes match -- message is verified')
    else:
        print('Hashes do not match -- has tampering occured?')


def encrypt_message_interactive():
    """
    Encrypt a message
    """

    message = input('Please enter the message to be encrypted: ')
    pub = enter_public_key_interactive()
    encrypted = ''
    for c in message:
        encrypted += "{0:04x}".format(apply_key(pub, ord(c)))
    print("Encrypted message:", encrypted)


def decrypt_message_interactive(priv = None):
    """
    Decrypt a message
    """

    encrypted = input('Please enter the message to be decrypted: ')
    if priv is None:
        priv = enter_key_interactive('private')
    message = ''
    for i in range(0, len(encrypted), 4):
        enc_string = encrypted[i:i + 4]
        enc = int(enc_string, 16)
        dec = apply_key(priv, enc)
        if dec >= 0 and dec < 256:
            message += chr(dec)
        else:
            print('Warning: Could not decode encrypted entity: ' + enc_string)
            print('         decrypted as: ' + str(dec) + ' which is out of range.')
            print('         inserting _ at position of this character')
            message += '_'
    print("Decrypted message:", message)


def break_key_interactive():
    """
    Break key, interactively
    """

    pub = enter_public_key_interactive()
    priv = break_key(pub)
    print("Private key:")
    print(priv)
    decrypt_message_interactive(priv)


def enter_public_key_interactive():
    """
    Prompt user to enter the public modulus.

    :return: the tuple (e,n)
    """

    print('(Using public exponent = ' + str(PUBLIC_EXPONENT) + ')')
    string_modulus = input('Please enter the modulus (decimal): ')
    modulus = int(string_modulus)
    return (PUBLIC_EXPONENT, modulus)


def enter_key_interactive(key_type):
    """
    Prompt user to enter the exponent and modulus of a key

    :param key_type: either the string 'public' or 'private' -- used to prompt the user on how
                     this key is interpretted by the program.
    :return: the tuple (e,n)
    """
    string_exponent = input('Please enter the ' + key_type + ' exponent (decimal): ')
    exponent = int(string_exponent)
    string_modulus = input('Please enter the modulus (decimal): ')
    modulus = int(string_modulus)
    return (exponent, modulus)


def compute_checksum(string):
    """
    Compute simple hash

    Given a string, compute a simple hash as the sum of characters
    in the string.

    (If the sum goes over sixteen bits, the numbers should "wrap around"
    back into a sixteen bit number.  e.g. 0x3E6A7 should "wrap around" to
    0xE6A7)

    This checksum is similar to the internet checksum used in UDP and TCP
    packets, but it is a two's complement sum rather than a one's
    complement sum.

    :param str string: The string to hash
    :return: the checksum as an integer
    """

    total = 0
    for c in string:
        total += ord(c)
    total %= 0x8000  # Guarantees checksum is only 4 hex digits
    # How many bytes is that?
    #
    # Also guarantees that that the checksum will
    # always be less than the modulus.
    return total


# ---------------------------------------
# Do not modify code above this line
# ---------------------------------------

def is_prime(n):
    """
    Tests whether a number is prime
    :author: Lucas
    :param n: the number to test
    :return: whether it's prime or not
    """
    dividesAnything = False
    for i in range(2, int(n**0.5)+1):
        dividesAnything |= n%i==0

    return not dividesAnything

def find_pq(p):
    """
    calculates p or q
    :author: Lucas
    :param p: 0 if calculating p or what was previously calculated for p if calculating q -- p=find_pq(0), q=find_pq(p)
    :return: the value of p or q
    """

    qorp = 0b11000001 | random.randint(0, 1<<5)<<1 #generate number of the form 11_____1
    while not(
            is_prime(qorp) and
            qorp != p and
            (qorp-1)%PUBLIC_EXPONENT != 0 and
            ((qorp-1)%p != 0 if p != 0 else True)
    ):
        qorp += 2

    return qorp

def create_nz():
    """
    Calculates n and z from p and q
    :author: Lucas
    :rtype: tuple
    :return: n, z
    """
    p = find_pq(0)
    q = find_pq(p)

    return p*q, (p-1)*(q-1)

def create_keys():
    """
    Create the public and private keys.

    :return: the keys as a three-tuple: (e,d,n)
    """

    n, z = create_nz()
    d = 1 #should be such that  (PUBLIC_EXPONENT*d) mod z = 1

    while (PUBLIC_EXPONENT * d)%z != 1:
        d+=1

    return (PUBLIC_EXPONENT, d, n)


def apply_key(key, m):
    """
    Apply the key, given as a tuple (e,n) or (d,n) to the message.

    This can be used both for encryption and decryption.

    :param tuple key: (e,n) or (d,n)
    :param int m: the message as a number 1 < m < n (roughly)
    :return: the message with the key applied. For example,
             if given the public key and a message, encrypts the message
             and returns the ciphertext.
    :author: Eden Basso
    """
    # check key val to know if enc or dec, so if e then enc if d then dec -> is_public
    # k+(e,n) -> (m^e)%n=c
    # k-(d,n) -> (c^d)%n=m -or- (m^e)^d%n=m
    if is_public(key)[0]:  # if key is public -> return c
        return int((m ** PUBLIC_EXPONENT) % is_public(key)[1][1])
    else:
        return int((m ** is_public(key)[1][0]) % is_public(key)[1][1])


def is_public(key):
    """
    Verifies if key is public for function of enc and dec
    :param key: values to enc (e,n) or dec (d,n) cipher or message w/
    :type key: tuple
    :return: true if key is public, false if key is private & a list containing values for the key
    :rtype: list
    :author: Eden Basso
    """
    if key.count(PUBLIC_EXPONENT) == 0:  # if key !contain e ->
        return False, [key[0], key[1]]
    else:
        return True, [key[0], key[1]]


def break_key(pub):
    """
    Break a key.  Given the public key, find the private key.
    Factorizes the modulus n to find the prime numbers p and q.

    You can follow the steps in the "optional" part of the in-class
    exercise.

    :param pub: a tuple containing the public key (e,n)
    :return: a tuple containing the private key (d,n)
    """

    n = pub[1]
    q = 2
    while n%q != 0:
        q+=1
    p = n/q
    z = (p-1)*(q-1)

    d = 1  # should be such that  (PUBLIC_EXPONENT*d) mod z = 1

    while (PUBLIC_EXPONENT * d) % z != 1:
        d += 1

    return d,n



# Your code and additional functions go here. (Replace this line.)

# ---------------------------------------
# Do not modify code below this line
# ---------------------------------------


def get_public_key(key_pair):
    """
    Pulls the public key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (e,n)
    """

    return (key_pair[0], key_pair[2])


def get_private_key(key_pair):
    """
    Pulls the private key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (d,n)
    """

    return (key_pair[1], key_pair[2])


main()
