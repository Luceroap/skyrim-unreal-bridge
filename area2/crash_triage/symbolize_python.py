"""Map python311.dll RVAs from a UE crash callstack to the nearest exported symbol and
disassemble the faulting instruction (read-only; needs `pip install capstone` for disassembly).

python area2/crash_triage/symbolize_python.py d8b0d cb2a c795 ...
"""
import struct
import sys

DLL = r"D:\UE_5.8\Engine\Binaries\ThirdParty\Python3\Win64\python311.dll"


def pe_info(d):
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    nsec = struct.unpack_from("<H", d, pe + 6)[0]
    sopt = struct.unpack_from("<H", d, pe + 20)[0]
    opt = pe + 24
    exp_rva = struct.unpack_from("<I", d, opt + 112)[0]
    secs = []
    o = opt + sopt
    for i in range(nsec):
        name, vs, va, rs, rp = struct.unpack_from("<8sIIII", d, o + 40 * i)
        secs.append((name.rstrip(b"\0").decode(), va, vs, rp, rs))
    return exp_rva, secs


def rva2off(secs, rva):
    for _, va, vs, rp, rs in secs:
        if va <= rva < va + max(vs, rs):
            return rva - va + rp
    raise ValueError(hex(rva))


def exports(d, secs, exp_rva):
    o = rva2off(secs, exp_rva)
    (nfun, nnames, afun, aname, aord) = struct.unpack_from("<IIIII", d, o + 20)
    funs = [struct.unpack_from("<I", d, rva2off(secs, afun) + 4 * i)[0] for i in range(nfun)]
    out = []
    for i in range(nnames):
        nr = struct.unpack_from("<I", d, rva2off(secs, aname) + 4 * i)[0]
        ordi = struct.unpack_from("<H", d, rva2off(secs, aord) + 2 * i)[0]
        no = rva2off(secs, nr)
        name = d[no:d.index(b"\0", no)].decode()
        out.append((funs[ordi], name))
    out.sort()
    return out


def dis_at(d, secs, rva, n=0x60):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    off = rva2off(secs, rva)
    print("bytes before +%x: %s" % (rva, d[off - 16:off].hex()))
    for ins in md.disasm(d[off:off + n], rva):
        print("  %x: %s %s" % (ins.address, ins.mnemonic, ins.op_str))


def main():
    d = open(DLL, "rb").read()
    exp_rva, secs = pe_info(d)
    if sys.argv[1] == "--dis":
        dis_at(d, secs, int(sys.argv[2], 16))
        return
    ex = exports(d, secs, exp_rva)
    for a in sys.argv[1:]:
        rva = int(a, 16)
        best = None
        for fr, n in ex:
            if fr <= rva:
                best = (fr, n)
            else:
                break
        sec = next((s[0] for s in secs if s[1] <= rva < s[1] + s[2]), "?")
        print("+%-8s %-6s nearest export: %s+0x%x" % (a, sec, best[1] if best else "?", rva - best[0] if best else 0))
    try:
        import capstone
        rva = int(sys.argv[1], 16)
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        off = rva2off(secs, rva - 0x30)
        print("\nDisassembly around +%s:" % sys.argv[1])
        for ins in md.disasm(d[off:off + 0x50], 0x180000000 + rva - 0x30):
            mark = "  <== fault" if ins.address == 0x180000000 + rva else ""
            print("  %x: %s %s%s" % (ins.address - 0x180000000, ins.mnemonic, ins.op_str, mark))
    except ImportError:
        print("(capstone not installed; skipping disassembly)")


if __name__ == "__main__":
    main()
