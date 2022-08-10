# Key Deprecation Notice

#### Master Signing Key 20BB 6616 A328 2A9F 8F15 9A53 4BB8 D801 C141 7BDC will be deprecated effective [canary#15-Nov-2022](../../canaries/2022/canary#15-Nov-2022.txt)

### What Happened?

TLDR: The "certify" private key for 7BDC has been lost. Signing, Encryption, and Authentication private keys are still available.  
This essentially means no new signing keys can be cryptographically signed/Authorized.  
This is not sustainable for the future.  
The canaries can still be signed by key 7BDC and will continue to be signed by this key into the future.  
Special note should not be taken if a 7BDC signature is missing from a canary after [canary#15-Nov-2022](../../canaries/2022/canary#15-Nov-2022.txt) 

----------

The Keys for 7BDC were generated back in 2018 with the intent to keep these keys as secret as reasonably possible.  
Essentially different keys were generated in an attempt to segregate gpg options as much as possible.  
The Master Key and accompanying keys were generated on an air-gapped machine.  
The Subkeys Sign, Enc, and Auth were generated and certified by the Master Key.  
These Subkeys were then moved to a Smart Card.  
The only place these subkeys exist is that one single Smart Card.  
The Master Signing Private key and Revocation Certificate existed on a single luks encrypted thumb drive.  
An image of that thumb drive was captured and backed up to a second drive as well as a cloud storage provider.  
The original thumb drive was accidentally destroyed.  
The backup drive is unable to be located at this time.  
The cloud provider is no longer in business  
3-2-1 backup practices have failed me  
That Smart Card containing the subkeys still exists and is usable today however, if anything happens to that Smart Card I am unable to sign canaries.  
This is not sustainable for the future.  
There is still a chance of recovering the private key via the lost drive at the future date.  
If the Master Private Key for 7BDC is recovered at a later date a special statement will be published and the new 1E03 key will be signed properly.  

New canaries will be signed with both new and legacy signing keys as long as the legacy signing keys still exist.  
No special note should be made if canaries after [canary#15-Nov-2022](../../canaries/2022/canary#15-Nov-2022.txt) are missing signatures from the legacy 7BDC Master Key.  


### New Key Generation

A new key has been generated.  

Master Signing Key: [9CAF 2256 61DA 2385 BBA2  4CFD 782F B8F3 3924 1E02](../Signing_key_1E02.asc)  
With this new key, we have changed key algorithms to ed25519 in an attempt to resist future computing technologies  

### New Key Proof Of Ownership

The certify private key for 7BDC no longer exists so signing the new [Master Signing Key](../Signing_key_1E02.asc) the proper way is not possible.  
However, we can sign files and cleartext messages with the Sign Subkey for 7BDC.  
You can find that detached signature [here](1E03_Proof_of_Ownership.sig)  
You can find a clear text signature below.  
```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

- -----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEYu8ZwhYJKwYBBAHaRw8BAQdAkH1mfnMpQNvaQxwXiXIJOHlJc5lz/Cs0PxNY
5RjKGiy0MHdpbnhwNTQyMSAoTWFzdGVyIFNpZ25pbmcgS2V5KSA8YWRtaW5AcmVp
ZnIubmV0PoiOBBMWCgA2FiEEnK8iVmHaI4W7okz9eC+48zkkHgIFAmLvGcICGwEE
CwkIBwQVCgkIBRYCAwEAAh4BAheAAAoJEHgvuPM5JB4CfFoA/A61c8nG4RTLVwo9
evyxWQHdI1j+sV7+NRNJUt3JpLUVAQCDFMnXOSThyoXLibKoV05dAf/O2iaN9bKU
ooPq09hXAbgzBGLvG6IWCSsGAQQB2kcPAQEHQH4KeYBeTF/sNF+WJl2br/pXR3E9
53PsL3p/MnVOh8cWiO8EGBYKACAWIQScryJWYdojhbuiTP14L7jzOSQeAgUCYu8b
ogIbAgCBCRB4L7jzOSQeAnYgBBkWCgAdFiEEIYj/i4VvLUcxwHPgcwEZJcLjmd0F
AmLvG6IACgkQcwEZJcLjmd2YugD9Ff/7HtVYLGzGUe+CxDGn/zgU1vnwMpcY1/A6
tSI9Lj4A/3kuniFH2uUajxTxlf2BhiZANNd9sPaZfXz74Bfq84QO69IA/2GccZLV
qRwrdfgIwPP2lfJpKuITlJWNsR7lfvwdA50lAP43s8GlW75DY2Fi1j5BjjQVaOjo
c5kBMo9L6HE8/Z9VAbg4BGLvG9ESCisGAQQBl1UBBQEBB0CizyVNtQ3vVKJRUUWw
WYlj2Gs67/Ohk92uJr40vGGFDAMBCAeIeAQYFgoAIBYhBJyvIlZh2iOFu6JM/Xgv
uPM5JB4CBQJi7xvRAhsMAAoJEHgvuPM5JB4Cn20A/iz+Gj1Leijx4skokeWmfDa+
+PCzFWfYpgw+IXA2C3iCAQCFh0iuc8+HcGW7mVqCGmJI8S82UrA873vZJX+WRzY+
ArgzBGLvG+sWCSsGAQQB2kcPAQEHQIx2CxcasXoukbjWGvB0wwDWpo4RaCj996kp
p57/tqlkiHgEGBYKACAWIQScryJWYdojhbuiTP14L7jzOSQeAgUCYu8b6wIbIAAK
CRB4L7jzOSQeAp9UAPwM4U2ZpWU6XJi2xvEfS3b2LYV2K/xev2TN05ffzEL07AEA
grnRrxVdM0BPzxuC8gAiW4lhjKvsfqhhAbkiWILrBQ0=
=Q6ar
- -----END PGP PUBLIC KEY BLOCK-----
-----BEGIN PGP SIGNATURE-----

iQIzBAEBCgAdFiEESNxnlOvEyudOAwh4k9a+v2Va2NwFAmLz33cACgkQk9a+v2Va
2Nz8Nw//RptxFDMTjspFFN4B4MxRl83rTLhAbHvdge0DuAxbyDsmbhXJXFuCnreF
pSsj/Z3QzHvESXttxjxiY73ZydWANybGn8UTRJGyodARFrjwMGnPmsFvU2d9Lslr
oOflW5xWRzynuIwVWfh8xG2WW8/dBo3Hi3138h4VUX3L461oBBshbJvQHTYkBGxj
WDLfDidnMCPfZ9twn9cKjAJ5XXzMLHIoS7qRsC5WEMhiYREzSYWjwdghzF33kes1
mKEWAr3FbqjZdLlPoxzv9hNtFEb+pPGytgQxTYUABVKrxaPvxhTGitRlpvCt4mtG
dMRNazZv42cQ3Sd/1VSf5zc6CbsLrMsdc+EYsfHfQSaieYjKuUpXALp/AKmFAgOH
i65oZbzWiM5cmJov2wwCUPlD9xAl0J0978/6Q6jRw0xZR23DLakvXcjHe0QDy6XV
1+kiVvgj2X98J8vZwH5O1+uwBSjo1mbzM5UYBOt807aaZMEsgRDcf5wMybd3v2GH
kkurKIefi6pf9XVSO8qtfcKFc5wgi+HtIAsSlMLcJUE7/IgZCLUTiB3fvGOgMaKn
MsWV+yEIMmB/VCxYREn7DEXbNgxgjrs7PAlJ2IjHj/cJrP/2fkxpKKPrd5gv+1eb
9P2ii8bK4HZbB57V7STRaXD+VQzF1e01JiW0Vj9Eo7NXENXHJks=
=liyi
-----END PGP SIGNATURE-----
```

### 
