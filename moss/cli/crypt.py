#! /usr/bin/env python

import click
import sys

from moss.framework.core.crypt import MossCrypt
from moss.framework.utils import print_data_in_json

@click.command(short_help = 'Edit a currently encrypted file')
@click.option('-j', '--json', is_flag=True, help = 'Output in JSON format')
@click.option('-k', '--key', default=None, help = 'Key to be used for encryption')
@click.option('-c', '--crypt-file', default=None, help = 'Target encrypted file to be edited')
def edit(json, key, crypt_file):
    '''
    Summary:
    Controls editing of an encrypted file between the cli interface
    and operations from MossCrypt.
    '''

    if not key:
        print '-k/--key is a required argument.'
        sys.exit(1)

    if not crypt_file:
        print '-c/--crypt-file is a required argument.'
        sys.exit(1)

    result = MossCrypt().edit_encrypted_file(key, crypt_file)

    if result['result'] == 'fail' and not json:
        print 'Edit failed: {}'.format(result['reason'])
        sys.exit(1)

    if json:
        print_data_in_json(result)


@click.command(short_help = 'Generate an 256 bit key for encryption')
def generate_key():
    '''
    Summary:
    Returns a random key that can be used for encryption.
    '''

    print MossCrypt().generate_aes_encryption_key()


@click.command(short_help = 'Encrypt a plaintext file with AES-256')
@click.option('-j', '--json', is_flag=True, help = 'Output in JSON format')
@click.option('-k', '--key', default=None, help = 'Key to be used for encryption')
@click.option('-p', '--plaintext-file', default=None, help = 'Target file to be encrypted')
def lock(json, key, plaintext_file):
    '''
    Summary:
    Controls decryption of an encrypted file between the cli interface
    and operations from MossCrypt.
    '''

    if not plaintext_file:
        print '-p/--plaintext-file is a required argument.'
        sys.exit(1)

    result = MossCrypt().encrypt_file(key, plaintext_file)

    if result['result'] == 'fail' and not json:
        print 'Encryption failed: {}'.format(result['reason'])
        sys.exit(1)

    if not json:
        print 'Encryption {}'.format(result['result'])
        print 'Output file: {}'.format(result['data']['output_file'])
        sys.exit(0)

    print_data_in_json(result)


@click.command(short_help = 'Decrypt an encrypted file')
@click.option('-j', '--json', is_flag=True, help = 'Output in JSON format')
@click.option('-k', '--key', default=None, help = 'Key to be used for encryption')
@click.option('-c', '--crypt-file', default=None, help = 'Target file to be decrypted')
def unlock(json, key, crypt_file):
    '''
    Summary:
    Controls encryption of a plaintext file between the cli interface
    and operations from MossCrypt.
    '''

    if not key:
        print '-k/--key is a required argument.'
        sys.exit(1)

    if not crypt_file:
        print '-c/--crypt-file is a required argument.'
        sys.exit(1)

    result = MossCrypt().decrypt_file(key, crypt_file)

    if result['result'] == 'fail' and not json:
        print 'Decryption failed: {}'.format(result['reason'])
        sys.exit(1)

    if not json:
        print 'Decryption {}'.format(result['result'])
        print 'Output file: {}'.format(result['data']['output_file'])
        sys.exit(0)

    print_data_in_json(result)


@click.group(short_help = 'Control encryption, decryption, and editing for files')
def crypt():
    pass


crypt.add_command(edit)
crypt.add_command(generate_key, name = 'generate-key')
crypt.add_command(lock)
crypt.add_command(unlock)
