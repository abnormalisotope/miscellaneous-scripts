import sys
import json

def remove_garbage(data):
    for i in range(len(data), 0, -1):
        try:
            json.loads(data[:i].decode())
            return data[:i]
        except:
            continue

def decrypt(data):
    #header specifications on encryption method as. theyre irrelevant here
    header = data[:16]
    magic = header[:4]
    product = header[4:6]
    version = header[6:12]
    key = header[12:]
    
    #my guesses for the acronyms.
    #V can also be Voice instead of VOCALOID. or VOCALOID6. who knows
    #VTBR = VOCALOID Timbre
    #VTB2 = VOCALOID Timbre... 2? (exclusively a file extension, VTBR internally)
    #VCTB = VOCALO CHANGER Timbre (exclusively a file extension, VTBR internally)
    #VPIT = VOCALOID Pitch
    #VTMG = VOCALOID Timing
    #VPNV = used exclusively on vocalo changer but no clue abt the acronym itself
    #VHNV = only available on vxb 2.0 and ^^^^
    #notes: VHNV is ~5mb, while 2.0 VTBRs are ~4mb...
    #       .vctb and .vtb2 are identical, only difference is their key
    #       vxb and v6.5 timing models are identical
    #and yes all of these use the exact same encryption with the same exact header
    if magic not in [b'VTBR', b'VPIT', b'VTMG', b'VPNV', b'VHNV']:
        raise ValueError('[!] Invalid magic. Quitting...')
    
    v8 = int.from_bytes(key, 'little')
    v12 = 88675123
    v17 = 362436069
    v18 = 521288629
    
    encrypted_data = data[16:]
    length = len(encrypted_data)
    decrypted_data = bytearray(length)
    tail = length % 4
    
    if tail:
        encrypted_data = encrypted_data + encrypted_data[-4:]
        length = len(encrypted_data)
        decrypted_data = bytearray(length)
        #i know this is not the most optimal way to deal w tail bytes but idgaf ok.
        #IF IT WORKS IT WORKS !!!!!!!!
    
    chunks = length // 4
    for i in range(chunks):
        v19 = v8 ^ ((v8 << 11) & 0xFFFFFFFF)
        v8, v17, v18 = v17, v18, v12
        v12 ^= (v19 ^ ((v19 ^ (v12 >> 11)) >> 8)) & 0xFFFFFFFF
        encrypted_chunk = int.from_bytes(encrypted_data[i*4:i*4+4], 'little')
        decrypted_chunk = (encrypted_chunk ^ v12) & 0xFFFFFFFF
        decrypted_data[i*4:i*4+4] = decrypted_chunk.to_bytes(4, 'little')
    
    return remove_garbage(decrypted_data)
    
def encrypt(data):
    #varies between model type
    magic = b'VTBR'
    #can be whatever u want. just needs to match with the drp i guess?
    #is NOT the same between vtbr and vpit so maybe it isnt the drp after all...?
    #but it makes sense to be different and still work, only vtbr ever gets checked
    product = b'ly'
    #value there is for vtbr v6.3, heres the other ones i found
    #0x71 -> 0x70 && 0x03 -> 0x02 for vtbr v6.1
    #0x71 -> 0x72 && 0x03 -> 0x01 for vtbr v6.0 and... VXB? WHAT?
    #makes sense... before 6.5 the Only thing stopping you from loading other banks was this version identification
    #although... vxb banks still wont load given V6s voicebanks have some trash bytes? at the end that are just. cut off during decryption
    #i wont remember specific numbers right now but i think it skips the last 128 bytes....?
    #so you could just repeat the last full block until u fill these 128 bytes and then itd work
    #0x71 -> 0x9B for vpit v6.3
    #0x71 -> 0xC2 && 0x01 -> 0x01 for vpit v6.0
    #0x71 -> 0x9B && 0x03 -> 0x01 for vpit vxb
    #0x71 -> 0x02 && 0x03 -> 0x01 for vtmg v6.3
    #0x71 -> 0x12 for vpnv v6.3
    #ultimately idt version is relevant outside of vtb2................
    version = bytes([0x71, 0x00, 0x03, 0x00, 0x00, 0x00])
    #also can be whatever you want
    #does change the hash so youll have to recalculate the Product in registry. if youre messing with vtb2 that is
    key = bytes([0x01, 0x02, 0x03, 0x04])
    header = magic + product + version + key
    #aside from this idk anything else. just that 1a314735bf3ab7b6a72db7427319eb09 inside the model is NPIdx (i think)
    
    v8 = int.from_bytes(key, 'little')
    v12 = 88675123
    v17 = 362436069
    v18 = 521288629
    
    length = len(data)
    encrypted_data = bytearray(length)
    tail = length % 4
    
    if tail:
        data = data + data[-4:]
    
    length2 = len(data)
    chunks = length2 // 4
    for i in range(chunks):
        v19 = v8 ^ ((v8 << 11) & 0xFFFFFFFF)
        v8, v17, v18 = v17, v18, v12
        v12 ^= (v19 ^ ((v19 ^ (v12 >> 11)) >> 8)) & 0xFFFFFFFF
        decrypted_chunk = int.from_bytes(data[i*4:i*4+4], 'little')
        encrypted_chunk = (decrypted_chunk ^ v12) & 0xFFFFFFFF
        encrypted_data[i*4:i*4+4] = encrypted_chunk.to_bytes(4, 'little')
    
    res = -(len(encrypted_data) - length)
    if (res):
        encrypted_data = encrypted_data[:-(len(encrypted_data) - length)]
    return header + encrypted_data
    
if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, 'rb') as f:
        data = f.read()
    if (path[-5:] == '.json'):
        result_data = encrypt(data)
        with open(path[:-5],'wb') as f:
            f.write(result_data)
        print(f"Encryption complete!")
    else:
        result_data = decrypt(data)
        with open(path + '.json','wb') as f:
            f.write(result_data)
        print(f"Decryption complete!")