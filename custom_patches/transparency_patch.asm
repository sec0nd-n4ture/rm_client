set_transparency:
    cmp ebx, bots_start_address
    jge stolen_branch1
    mov byte ptr ds:[ebx+0x21], 0xFF
stolen_branch1:
    cmp dword ptr ds:[ebx+0x44], 0x13
    jne stolen_branch3
stolen_branch2:
    mov byte ptr ds:[ebx+0x21], 0x05
stolen_branch3:
    cmp dword ptr ds:[ebx+0x44], 0x15
jmp AlphaHookContinue