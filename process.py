#!/usr/bin/env python

#pylint:disable=broad-except,logging-fstring-interpolation

import contextlib
import logging
import stopit
import angr

for some_logger in [ logging.getLogger(name) for name in logging.root.manager.loggerDict ]:
    some_logger.setLevel(logging.CRITICAL)

l = logging.getLogger('MEGATEST')
l.setLevel('INFO')

class Abort(Exception): pass

@contextlib.contextmanager
def catcher(s, stop=True):
    try:
        yield
    except stopit.utils.TimeoutException:
        raise
    except Exception:
        awesome_error(s, exc_info=True)
        if stop:
            raise Abort()

reasons = { }

def awesome_log(lvl, msg, **kwargs):
    l.log(lvl, msg, **kwargs)
    reason = msg.split(":")[0]
    reasons.setdefault(reason, 0)
    reasons[reason] += 1

def awesome_info(msg, **kwargs):
    awesome_log(logging.INFO, msg, **kwargs)
def awesome_warning(msg, **kwargs):
    awesome_log(logging.WARNING, msg, **kwargs)
def awesome_error(msg, **kwargs):
    awesome_log(logging.ERROR, msg, **kwargs)

@stopit.signal_timeoutable(default="TIMEOUT")
def doit_raw(pkg_name, elf_path, dbg_path):
    with catcher(f"ELF_OPEN_FAIL: elf={elf_path} pkg={pkg_name}"):
        elf = angr.Project(elf_path, auto_load_libs=False)
        awesome_info(f"ELF_OPEN_SUCCESS: elf={elf_path} pkg={pkg_name}")

    with catcher(f"DBG_OPEN_FAIL: dbg={dbg_path} pkg={pkg_name}"):
        dbg = angr.Project(dbg_path, auto_load_libs=False)
        awesome_info(f"DBG_OPEN_SUCCESS: elf={elf_path} pkg={pkg_name}")

    with catcher(f"SYMBOLS_FAIL: elf={elf_path} dbg={dbg_path} pkg={pkg_name}"):
        symbols = [ (s.name, s.rebased_addr) for s in dbg.loader.symbols if not s.is_import and s.is_function ]
        awesome_info(f"SYMBOLS_SUCCESS: elf={elf_path} pkg={pkg_name}")

    with catcher(f"CFG_FAIL: elf={elf_path} pkg={pkg_name}"):
        cfg = elf.analyses.CFG(data_references=True, cross_references=True)
        awesome_info(f"CFG_SUCCESS: elf={elf_path} pkg={pkg_name}")

    l.info("Checking functions...")
    for i,(s,a) in enumerate(symbols):
        id_str = f"function={s} address={hex(a)} progress={i}/{len(symbols)} elf={elf_path} dbg={dbg_path} pkg={pkg_name}"
        if a in cfg.functions:
            awesome_info(f"FUNCTION_PRESENT_SUCCESS: {id_str}")
        else:
            awesome_warning(f"FUNCTION_PRESENT_FAIL: {id_str}")
            continue

        with stopit.SignalTimeout(5) as t:
            with catcher(f"DECOMPILER_FAIL: {id_str}", stop=False):
                decompilation = elf.analyses.Decompiler(cfg.functions[a], cfg=cfg)
                with catcher(f"CODEGEN_FAIL: {id_str}", stop=False):
                    text = decompilation.codegen.text
                    assert text
                    if "None" in text:
                        awesome_warning(f"CODEGEN_WARNING: 'None': present {id_str}")
                    awesome_info(f"DECOMPILER_SUCCESS: {id_str}")
        if not t:
            awesome_warning(f"DECOMPILER_TIMEOUT: {id_str}")

def doit(pkg_name, elf_path, dbg_path, timeout=3600):
    try:
        return doit_raw(pkg_name, elf_path, dbg_path, timeout=timeout) #pylint:disable=unexpected-keyword-arg
    except Abort:
        return None
    except Exception:
        awesome_error("MYSTERY_FAIL: elf={elf_path} dbg={dbg_path} pkg={pkg_name}", exc_info=True)

if __name__ == '__main__':
    import sys
    _pkg_name = sys.argv[1]
    _elf_path = sys.argv[2]
    _dbg_path = sys.argv[3]

    if doit(_pkg_name, _elf_path, _dbg_path) == "TIMEOUT":
        awesome_error(f"ELF_TIMEOUT: elf={_elf_path} dbg={_dbg_path} pkg={_pkg_name}")
    l.info(f"RESULTS: elf={_elf_path} dbg={_dbg_path} pkg={_pkg_name} reasons={reasons}")
