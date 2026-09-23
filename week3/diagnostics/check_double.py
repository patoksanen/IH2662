from pathlib import Path
source=Path(__file__).with_name('silicon_baseline.py')
code=source.read_text()
code=code.replace('ds.set_parameter(name=option,value=True)','ds.set_parameter(name=option,value=False)')
code=code.replace('absolute_error=1e-2','absolute_error=1e4')
code=code.replace('relative_error=1e-9','relative_error=1e-7').replace('relative_error=1e-8','relative_error=1e-7')
code=code.replace('p=settings()','p=settings(); p["max_voltage_V"]=15; p["critical_field_V_cm"]=30000')
code=code.replace('"planar" if opt.planar else "baseline"','"diagnostic_double" if opt.planar else "diagnostic_edge"')
exec(compile(code,str(source),'exec'),{'__name__':'__main__','__file__':str(source)})