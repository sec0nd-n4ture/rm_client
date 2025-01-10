cmp edx, 0x15
jl execute_stolen
mov edx, 0x1d
execute_stolen:
    push ebx
    push esi
    mov esi, ecx
    cmp byte ptr ds:[eax+0x02], 0x05
jmp ColHookContinue