cmp ebx, bots_start_address
jge exit
mov byte ptr ds:[ebx+0x21], 0xFF
exit:
    cmp dword ptr ds:[ebx+0x44], 0x13
    jmp AlphaHookContinue