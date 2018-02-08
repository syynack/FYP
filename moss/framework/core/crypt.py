#! /usr/bin/env python

import os
import random
import struct
import socket
import getpass
import tempfile
import subprocess
import sys

from Crypto.Cipher import AES
from datetime import datetime
from moss.framework.utils import timer, runtime

class MossCrypt():

    def generate_aes_encryption_key(self):
        '''
        Summary:
        returns random 16 byte hex encoded string
        '''

        return os.urandom(16).encode('hex')


    def encrypt_file(self, key, in_file, chunksize = 64*8192):
        '''
        Summary:
        Handles file encryption with AES 256 and returns related information

        Arguments:
        key             string, to be used for encryption
        in_file         string, target file to be encrypted
        chunksize       int, size of chunks to be encrypted

        Returns:
        dict
        '''

        start_run_time = timer()
        start_date_time = str(datetime.now())
        initialisation_vector = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))

        if not key:
            key = self.generate_aes_encryption_key()

        aes = AES.new(key, AES.MODE_CBC, initialisation_vector)
        chunks_encrypted = 0
        out_file = in_file + '.crypt'

        with open(in_file, 'rb') as plaintext:
            with open(out_file, 'wb') as encrypted_file:
                try:
                    encrypted_file.write(struct.pack('<Q', os.path.getsize(in_file)))
                    encrypted_file.write(initialisation_vector)

                    while True:
                        plaintext_chunk = plaintext.read(chunksize)
                        chunks_encrypted += 1
                        if len(plaintext_chunk) == 0:
                            break
                        elif len(plaintext_chunk) % 16 != 0:
                            plaintext_chunk += ' ' * (16 - len(plaintext_chunk) % 16)

                        encrypted_file.write(aes.encrypt(plaintext_chunk))
                except:
                    return {
                        'result': 'fail',
                        'reason': sys.exc_info()[0]
                    }

        end_run_time = timer()

        return {
            'result': 'success',
            'data' : {
                'key': key,
                'iv': initialisation_vector.encode('hex'),
                'encrypted_file_size': os.path.getsize(out_file),
                'plaintext_file_size': os.path.getsize(in_file),
                'chunks_encrypted': chunks_encrypted,
                'output_file': out_file
            },
            'start_time': start_date_time,
            'end_time': str(datetime.now()),
            'run_time': runtime(start_run_time, end_run_time),
            'user': getpass.getuser(),
            'hostname': socket.gethostname()
        }


    def decrypt_file(self, key, in_file, chunksize = 64*8192):
        '''
        Summary:
        Handles file decryption with AES 256 and returns related information

        Arguments:
        key             string, to be used for decryption
        in_file         string, target file to be decrypted
        chunksize       int, size of chunks to be decrypted

        Returns:
        dict
        '''

        start_run_time = timer()
        start_date_time = str(datetime.now())

        if in_file.split('.')[-1] != 'crypt':
            return {
                'result': 'fail',
                'reason': 'File is not a .crypt file'
            }

        out_file = '.'.join(in_file.split('.')[:-1])

        with open(in_file, 'rb') as encrypted_file:
            original_size = struct.unpack('<Q', encrypted_file.read(struct.calcsize('Q')))[0]
            initialisation_vector = encrypted_file.read(16)
            aes = AES.new(key, AES.MODE_CBC, initialisation_vector)

            chunks_decrypted = 0

            if not out_file:
                out_file = in_file.split('.')[0]

            with open(out_file, 'wb') as plaintext:
                try:
                    while True:
                        encrypted_chunk = encrypted_file.read(chunksize)
                        chunks_decrypted += 1
                        if len(encrypted_chunk) == 0:
                            break

                        plaintext.write(aes.decrypt(encrypted_chunk))

                    plaintext.truncate(original_size)
                except:
                    return {
                        'result': 'fail',
                        'reason': sys.exc_info()[0]
                    }

        end_run_time = timer()

        return {
            'result': 'success',
            'data': {
                'key': key,
                'iv': initialisation_vector.encode('hex'),
                'encrypted_file_size': os.path.getsize(in_file),
                'plaintext_file_size': os.path.getsize(out_file),
                'chunks_decrypted': chunks_decrypted,
                'output_file': out_file
            },
            'start_time': start_date_time,
            'end_time': str(datetime.now()),
            'run_time': runtime(start_run_time, end_run_time),
            'user': getpass.getuser(),
            'hostname': socket.gethostname()
        }


    def edit_encrypted_file(self, key, filename, chunksize = 64*8192):
        '''
        Summary:
        Handles file decryption, dumps decrypted contents into a temp file, opens
        vim on the temp file, dumps back into encrypted file.

        Arguments:
        key             string, to be used for encryption and decryption
        filename        string, target file to be edited
        chunksize       int, size of chunks to be used for encryption and decryption

        Returns:
        dict
        '''

        if filename.split('.')[-1] != 'crypt':
            return {
                'result': 'fail',
                'reason': 'File is not a .crypt file'
            }

        with open(filename, 'r+b') as encrypted_file:
            original_size = struct.unpack('<Q', encrypted_file.read(struct.calcsize('Q')))[0]
            initialisation_vector = encrypted_file.read(16)
            aes = AES.new(key, AES.MODE_CBC, initialisation_vector)

            with tempfile.NamedTemporaryFile(mode = 'r+b', suffix = '.tmp', delete = False) as temp_file:
                while True:
                    encrypted_chunk = encrypted_file.read(chunksize)
                    if len(encrypted_chunk) == 0:
                        break
                    elif len(encrypted_chunk) % 16 != 0:
                        encrypted_chunk += ' ' * (16 - len(encrypted_chunk) % 16)

                    temp_file.write(aes.decrypt(encrypted_chunk))

                temp_file.flush()
                subprocess.call(['vim', temp_file.name])
                temp_file.close()

                with open(temp_file.name) as tmp:
                    encrypted_file.truncate()
                    encrypted_file.seek(0)

                    initialisation_vector = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
                    aes = AES.new(key, AES.MODE_CBC, initialisation_vector)

                    encrypted_file.write(struct.pack('<Q', os.path.getsize(tmp.name)))
                    encrypted_file.write(initialisation_vector)

                    while True:
                        plaintext_chunk = tmp.read(chunksize)
                        if len(plaintext_chunk) == 0:
                            break
                        elif len(plaintext_chunk) % 16 != 0:
                            plaintext_chunk += ' ' * (16 - len(plaintext_chunk) % 16)

                        encrypted_file.write(aes.encrypt(plaintext_chunk))

                os.unlink(tmp.name)

        return {
            'result': 'success'
        }
